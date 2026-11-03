#!/usr/bin/env python3
"""
Manage Batch PR Items (Slash Command Handler)
Handles maintainer slash commands on Pull Requests (e.g. `/reject 3 low quality` or `/reject 2 4` or `/drop vocaloid-5`).
Removes the rejected image files, updates screensavers.json and CREDITS.md, updates the PR body,
and pushes the update to the PR branch.
"""

import os
import sys
import json
import subprocess
import re
import argparse
import urllib.request
import urllib.error

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')


def run(cmd, cwd=REPO_ROOT, check=True):
    """
    Executes a command safely.
    If cmd is a list, subprocess runs with shell=False (no bash injection/backtick evaluation).
    If cmd is a string, shell=True is used.
    """
    if isinstance(cmd, list):
        res = subprocess.run(cmd, cwd=cwd, text=True, encoding='utf-8', errors='replace', capture_output=True)
    else:
        res = subprocess.run(cmd, cwd=cwd, shell=True, text=True, encoding='utf-8', errors='replace', capture_output=True)
    if check and res.returncode != 0:
        print(f"Command failed: {cmd}\nStdout: {res.stdout}\nStderr: {res.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return res


def gh_comment(pr_num, repo, body):
    """Posts a comment to a PR via gh CLI or GitHub REST API."""
    res = run(['gh', 'pr', 'comment', str(pr_num), '--body', body, '-R', repo], check=False)
    if res.returncode == 0:
        return
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Notice: No GitHub token available for comment fallback.")
        return
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }
        data = json.dumps({'body': body}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as resp:
            print(f"Posted comment via API (HTTP {resp.status})")
    except Exception as err:
        print(f"Failed to post comment via API: {err}")


def gh_edit_body(pr_num, repo, body):
    """Updates PR body via gh CLI or GitHub REST API."""
    temp_path = os.path.join(REPO_ROOT, 'updated_pr_body.md')
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(body)
        res = run(['gh', 'pr', 'edit', str(pr_num), '--body-file', temp_path, '-R', repo], check=False)
        if res.returncode == 0:
            return
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Notice: No GitHub token available for PR edit fallback.")
        return
    try:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }
        data = json.dumps({'body': body}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
        with urllib.request.urlopen(req) as resp:
            print(f"Updated PR body via API (HTTP {resp.status})")
    except Exception as err:
        print(f"Failed to update PR body via API: {err}")


def parse_command(comment_text):
    """
    Parses maintainer slash commands such as:
      `/reject 2`
      `/reject 2 4`
      `/reject 2, 4`
      `/reject #2, #4 low quality`
      `/reject lingerie-model blonde-mermaid inappropriate`
      `/drop 3 blurry`
    Returns (targets_list, reason).
    """
    m = re.match(r'^\s*/(?:reject|drop|remove)\s+(.+)$', comment_text.strip(), re.IGNORECASE)
    if not m:
        return [], None
    rest = m.group(1).strip()
    tokens = rest.split()
    targets = []
    reason_tokens = []
    collecting_targets = True

    for t in tokens:
        clean_t = t.rstrip(',').strip()
        num_match = re.match(r'^#?(\d+)$', clean_t)
        if collecting_targets and num_match:
            targets.append(num_match.group(1))
            continue
        if collecting_targets and not targets:
            targets.append(clean_t)
            continue
        elif collecting_targets and targets and (t.endswith(',') or '-' in clean_t):
            targets.append(clean_t)
            continue
        else:
            collecting_targets = False
            reason_tokens.append(t)

    reason = ' '.join(reason_tokens).strip() if reason_tokens else "Not specified"
    return targets, reason


def parse_pr_table(pr_body):
    """
    Extracts item information from the PR body markdown table.
    Returns dict mapping 1-based table index to item metadata:
      {idx: {'idx': int, 'title': str, 'id': str, 'is_rejected': bool}}
    """
    items_by_idx = {}
    for line in pr_body.splitlines():
        # Match markdown table row: | **<idx>** | <preview> | <title> | <author> | <cat> | `<id>` |
        m = re.search(r'\|\s*\*\*#?(\d+)\*\*\s*\|[^\|]*\|\s*(.*?)\s*\|[^\|]*\|[^\|]*\|\s*\x60([^\x60]+)\x60\s*\|', line)
        if m:
            idx = int(m.group(1))
            raw_title = m.group(2)
            item_id = m.group(3).strip()
            is_rejected = ('~~' in raw_title) or ('❌' in raw_title) or ('Rejected' in raw_title)
            title = re.sub(r'[*~]', '', raw_title)
            title = re.sub(r'\s*\(❌\s*Rejected:.*?\)', '', title, flags=re.IGNORECASE).strip()
            items_by_idx[idx] = {
                'idx': idx,
                'title': title,
                'id': item_id,
                'is_rejected': is_rejected
            }
    return items_by_idx


def main():
    parser = argparse.ArgumentParser(description="Manage Batch PR items")
    parser.add_argument('--pr', type=int, help="PR number")
    parser.add_argument('--comment', type=str, help="Comment body containing command")
    parser.add_argument('--target', type=str, help="Item index or ID to reject")
    parser.add_argument('--reason', type=str, help="Rejection reason")
    args = parser.parse_args()

    repo = os.environ.get('GITHUB_REPOSITORY', 'ultimatejimmy/storefront-screensavers')
    pr_num = args.pr or os.environ.get('PR_NUM') or os.environ.get('ISSUE_NUM')
    comment_text = args.comment or os.environ.get('COMMENT_BODY', '')

    targets = [args.target] if args.target else []
    reason = args.reason

    if not targets and comment_text:
        parsed_targets, parsed_reason = parse_command(comment_text)
        targets = parsed_targets
        if not reason:
            reason = parsed_reason

    if not reason:
        reason = "Not specified"

    if not pr_num or not targets:
        print("Error: Missing PR number or target item(s) to reject.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing reject command on PR #{pr_num}: targets={targets}, reason='{reason}'")

    # Fetch PR details
    pr_info = {}
    try:
        pr_info_raw = run(['gh', 'pr', 'view', str(pr_num), '-R', repo, '--json', 'headRefName,baseRefName,body,title,state,mergedAt']).stdout
        pr_info = json.loads(pr_info_raw)
    except Exception as gh_err:
        print(f"Notice: gh CLI view failed ({gh_err}), querying GitHub API directly...")
        token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = f'token {token}'
        try:
            req = urllib.request.Request(f'https://api.github.com/repos/{repo}/pulls/{pr_num}', headers=headers)
            with urllib.request.urlopen(req) as resp:
                gh_pr = json.load(resp)
            pr_info = {
                'headRefName': gh_pr['head']['ref'],
                'baseRefName': gh_pr['base']['ref'],
                'body': gh_pr.get('body') or '',
                'title': gh_pr.get('title') or '',
                'state': 'MERGED' if gh_pr.get('merged') else gh_pr.get('state', '').upper(),
                'mergedAt': gh_pr.get('merged_at')
            }
        except Exception as api_err:
            print(f"Failed to fetch PR via API: {api_err}", file=sys.stderr)
            sys.exit(1)

    branch = pr_info.get('headRefName')
    base_branch = pr_info.get('baseRefName', 'main')
    pr_body = pr_info.get('body', '')
    pr_state = pr_info.get('state', '').upper()
    is_merged = (pr_state == 'MERGED') or bool(pr_info.get('mergedAt'))

    if is_merged:
        err_msg = (
            f"⚠️ **Cannot reject item(s):** Pull Request #{pr_num} has already been merged into `{base_branch}`.\n\n"
            f"Because the PR is already merged, changes can no longer be made to the PR branch. "
            f"To remove unwanted wallpapers from `{base_branch}`, please remove them via Catalog Studio or submit a removal commit directly to `{base_branch}`."
        )
        print(err_msg)
        gh_comment(pr_num, repo, err_msg)
        return

    if pr_state == 'CLOSED':
        err_msg = f"⚠️ **Cannot reject item(s):** Pull Request #{pr_num} is closed."
        print(err_msg)
        gh_comment(pr_num, repo, err_msg)
        return

    print(f"PR branch is '{branch}', base is '{base_branch}'")

    # Fetch origin base and PR branch
    run(['git', 'fetch', 'origin', base_branch])
    run(['git', 'fetch', 'origin', branch])

    # Find merge base between base_branch and branch
    try:
        merge_base = run(['git', 'merge-base', f'origin/{base_branch}', f'origin/{branch}']).stdout.strip()
    except Exception:
        merge_base = f'origin/{base_branch}'

    # Read catalog from merge_base and branch
    try:
        base_cat_raw = run(['git', 'show', f'{merge_base}:screensavers.json']).stdout
        base_cat = json.loads(base_cat_raw)
        base_ids = {x.get('id') for x in base_cat}
    except Exception:
        base_ids = set()

    branch_cat_raw = run(['git', 'show', f'origin/{branch}:screensavers.json']).stdout
    branch_cat = json.loads(branch_cat_raw)

    # Active items currently remaining on branch
    branch_new_items = [x for x in branch_cat if x.get('id') not in base_ids]
    print(f"Found {len(branch_new_items)} active submission items on branch {branch}:")
    for idx, it in enumerate(branch_new_items, 1):
        print(f"  #{idx}: {it.get('title')} ({it.get('id')})")

    # Parse table items from PR body
    table_items = parse_pr_table(pr_body)

    items_to_reject = []
    unmatched_targets = []
    already_rejected_targets = []

    for target in targets:
        matched_item = None
        matched_idx = None
        clean_target = target.lstrip('#')

        # 1. Match by numeric index against PR body table
        if clean_target.isdigit():
            idx_val = int(clean_target)
            if idx_val in table_items:
                t_item = table_items[idx_val]
                if t_item['is_rejected']:
                    already_rejected_targets.append(f"#{idx_val} ('{t_item['title']}')")
                    continue
                matched_idx = idx_val
                # Find in branch_cat
                for it in branch_cat:
                    if it.get('id') == t_item['id']:
                        matched_item = it
                        break
                if not matched_item:
                    # Item exists in table but already missing from screensavers.json
                    already_rejected_targets.append(f"#{idx_val} ('{t_item['title']}')")
                    continue

        # 2. Match by 1-based index on branch_new_items if not matched yet
        if not matched_item and clean_target.isdigit():
            idx_val = int(clean_target)
            if 1 <= idx_val <= len(branch_new_items):
                matched_item = branch_new_items[idx_val - 1]
                # Find corresponding index in table
                for t_idx, t_item in table_items.items():
                    if t_item['id'] == matched_item.get('id'):
                        matched_idx = t_idx
                        break
                if matched_idx is None:
                    matched_idx = idx_val

        # 3. Match by item ID
        if not matched_item:
            target_lower = target.lower()
            for it in branch_cat:
                if it.get('id', '').lower() == target_lower:
                    matched_item = it
                    for t_idx, t_item in table_items.items():
                        if t_item['id'].lower() == target_lower:
                            matched_idx = t_idx
                            break
                    break

        # 4. Match by title substring
        if not matched_item:
            target_lower = target.lower()
            for it in branch_new_items:
                if target_lower in it.get('title', '').lower():
                    matched_item = it
                    for t_idx, t_item in table_items.items():
                        if t_item['id'] == it.get('id'):
                            matched_idx = t_idx
                            break
                    break

        if matched_item:
            # Check duplicate in items_to_reject
            if not any(x['item']['id'] == matched_item['id'] for x in items_to_reject):
                items_to_reject.append({
                    'item': matched_item,
                    'idx': matched_idx or (len(items_to_reject) + 1)
                })
        else:
            unmatched_targets.append(target)

    # If nothing could be rejected
    if not items_to_reject:
        err_lines = []
        if unmatched_targets:
            avail_str = f"#1 to #{len(table_items) if table_items else len(branch_new_items)}"
            err_lines.append(f"⚠️ Could not find item(s) matching `{', '.join(unmatched_targets)}` in PR #{pr_num}. Available items are {avail_str}.")
        if already_rejected_targets:
            err_lines.append(f"ℹ️ Item(s) already rejected: {', '.join(already_rejected_targets)}.")
        full_err = '\n\n'.join(err_lines)
        print(full_err)
        gh_comment(pr_num, repo, full_err)
        return

    # Checkout PR branch
    run(['git', 'checkout', '-B', branch, f'origin/{branch}'])

    # Process all rejections
    rejected_ids = {x['item']['id'] for x in items_to_reject}
    for entry in items_to_reject:
        item = entry['item']
        item_id = item['id']
        files_to_remove = [
            f"images/{item_id}.jpg",
            f"images/{item_id}.png",
            f"images/thumbnails/{item_id}.jpg",
            f"images/thumbnails/{item_id}.png",
            f"images/thumbnails/plugin/{item_id}.jpg",
            f"images/thumbnails/plugin/{item_id}.png"
        ]
        for f in files_to_remove:
            p = os.path.join(REPO_ROOT, f)
            if os.path.exists(p):
                run(['git', 'rm', '-f', f])
                print(f"Removed {f}")

    # Remove items from screensavers.json
    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as sf:
        curr_cat = json.load(sf)

    updated_cat = [x for x in curr_cat if x.get('id') not in rejected_ids]
    with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as sf:
        json.dump(updated_cat, sf, indent=2, ensure_ascii=False)

    # Rebuild CREDITS.md
    try:
        sys.path.insert(0, os.path.join(REPO_ROOT, 'tools'))
        from catalog_studio import rebuild_credits_file
        rebuild_credits_file(updated_cat)
        print("Rebuilt CREDITS.md.")
    except Exception as e:
        print(f"Warning rebuilding credits: {e}")

    try:
        from generate_catalogs import generate_catalogs
        generate_catalogs(fetch_remote=False)
        print("Generated optimized catalogs.")
    except Exception as e:
        print(f"Warning generating optimized catalogs: {e}")

    # Stage, commit and push
    run(['git', 'add', 'screensavers.json', 'screensavers.lite.json', 'screensavers.min.json', 'screensavers.unified.lite.json', 'CREDITS.md'])

    titles_str = ', '.join([f"'{e['item'].get('title', e['item']['id'])}'" for e in items_to_reject])
    indices_str = ', '.join([f"#{e['idx']}" for e in items_to_reject])
    commit_msg = f"Drop {titles_str} ({indices_str}) per maintainer reject command: {reason}"
    run(['git', 'commit', '-m', commit_msg])
    run(['git', 'push', 'origin', branch, '--force'])
    print(f"Pushed commit '{commit_msg}' to origin/{branch}")

    # Update PR body markdown
    updated_pr_body = pr_body
    for entry in items_to_reject:
        idx_val = entry['idx']
        item_title = entry['item'].get('title', entry['item']['id'])
        # Table strike-through
        table_pattern = rf"(\|\s*\*\*(?:#|Item\s+)?{idx_val}\*\*\s*\|[^\|]*\|\s*)\*\*({re.escape(item_title)})\*\*"
        updated_pr_body = re.sub(table_pattern, rf"\1~~**\2**~~ *(❌ Rejected: {reason})*", updated_pr_body)

        # Visual preview rejection notice
        preview_pattern = rf"(####\s+(?:#|Item\s+)?{idx_val}:\s+{re.escape(item_title)}[^\n]*\n)"
        updated_pr_body = re.sub(preview_pattern, rf"\1> ❌ **Rejected by maintainer:** {reason}\n\n", updated_pr_body)

    gh_edit_body(pr_num, repo, updated_pr_body)

    # Calculate remaining active count
    remaining_active = len(branch_new_items) - len(items_to_reject)
    if remaining_active < 0:
        remaining_active = 0

    # Post confirmation comment
    confirm_lines = [
        f"🗑️ **Rejected {len(items_to_reject)} Item{'s' if len(items_to_reject) != 1 else ''} from PR #{pr_num}:**"
    ]
    for entry in items_to_reject:
        it = entry['item']
        confirm_lines.append(f"- **Item #{entry['idx']}: '{it.get('title', it['id'])}' (`{it['id']}`)** — *{reason}*")
    confirm_lines.extend([
        "",
        f"The images and catalog entries have been removed from branch `{branch}`.",
        f"**Status:** {remaining_active} wallpaper{'s' if remaining_active != 1 else ''} remaining in this PR are ready to merge!"
    ])

    if unmatched_targets:
        confirm_lines.extend([
            "",
            f"*(Notice: Target(s) `{', '.join(unmatched_targets)}` could not be matched and were skipped.)*"
        ])

    gh_comment(pr_num, repo, '\n'.join(confirm_lines))

    # Return to base_branch
    run(['git', 'checkout', base_branch])
    print("Done!")


if __name__ == '__main__':
    main()
