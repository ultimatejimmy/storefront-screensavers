#!/usr/bin/env python3
"""
Manage Batch PR Items (Slash Command Handler)
Handles maintainer slash commands on Pull Requests (e.g. `/reject 3 low quality` or `/drop vocaloid-5`).
Removes the rejected image files, updates screensavers.json and CREDITS.md, updates the PR body,
and pushes the update to the PR branch.
"""

import os
import sys
import json
import subprocess
import re
import argparse

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')


def run(cmd, cwd=REPO_ROOT, check=True):
    res = subprocess.run(cmd, cwd=cwd, shell=True, text=True, encoding='utf-8', errors='replace', capture_output=True)
    if check and res.returncode != 0:
        print(f"Command failed: {cmd}\nStdout: {res.stdout}\nStderr: {res.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return res


def parse_command(comment_text):
    """
    Parses `/reject <item> [reason]` or `/drop <item> [reason]`.
    Returns (target, reason) or (None, None).
    """
    m = re.match(r'^\s*/(?:reject|drop|remove)\s+(\S+)(?:\s+([\s\S]+))?$', comment_text.strip(), re.IGNORECASE)
    if not m:
        return None, None
    target = m.group(1).strip()
    reason = m.group(2).strip() if m.group(2) else "Not specified"
    return target, reason


def main():
    parser = argparse.ArgumentParser(description="Manage Batch PR items")
    parser.add_argument('--pr', type=int, help="PR number")
    parser.add_argument('--comment', type=str, help="Comment body containing command")
    parser.add_argument('--target', type=str, help="Item index or ID to reject")
    parser.add_argument('--reason', type=str, default="Not specified", help="Rejection reason")
    args = parser.parse_args()

    repo = os.environ.get('GITHUB_REPOSITORY', 'ultimatejimmy/storefront-screensavers')
    pr_num = args.pr or os.environ.get('PR_NUM') or os.environ.get('ISSUE_NUM')
    comment_text = args.comment or os.environ.get('COMMENT_BODY', '')

    target = args.target
    reason = args.reason

    if not target and comment_text:
        target, reason = parse_command(comment_text)

    if not pr_num or not target:
        print("Error: Missing PR number or target item to reject.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing reject command on PR #{pr_num}: target='{target}', reason='{reason}'")

    # Fetch PR details
    pr_info_raw = run(f'gh pr view {pr_num} -R {repo} --json headRefName,body,title').stdout
    pr_info = json.loads(pr_info_raw)
    branch = pr_info['headRefName']
    pr_body = pr_info['body']

    print(f"PR branch is '{branch}'")

    # Fetch origin main and PR branch
    run('git fetch origin main')
    run(f'git fetch origin {branch}')

    # Read items from main and branch
    main_cat_raw = run('git show origin/main:screensavers.json').stdout
    main_cat = json.loads(main_cat_raw)
    main_ids = {x.get('id') for x in main_cat}

    branch_cat_raw = run(f'git show origin/{branch}:screensavers.json').stdout
    branch_cat = json.loads(branch_cat_raw)

    # Branch items in order
    branch_new_items = [x for x in branch_cat if x.get('id') not in main_ids]
    print(f"Found {len(branch_new_items)} new items on branch {branch}:")
    for idx, it in enumerate(branch_new_items, 1):
        print(f"  #{idx}: {it.get('title')} ({it.get('id')})")

    # Resolve target item
    matched_item = None
    matched_idx = -1

    # Check if target is number (1-based index)
    target_clean = target.lstrip('#')
    if target_clean.isdigit():
        idx_val = int(target_clean)
        if 1 <= idx_val <= len(branch_new_items):
            matched_idx = idx_val
            matched_item = branch_new_items[idx_val - 1]

    # Check if target is ID
    if not matched_item:
        for idx, it in enumerate(branch_new_items, 1):
            if it.get('id') == target or it.get('id') == target.lower():
                matched_idx = idx
                matched_item = it
                break

    # Check if target is title substring
    if not matched_item:
        for idx, it in enumerate(branch_new_items, 1):
            if target.lower() in it.get('title', '').lower():
                matched_idx = idx
                matched_item = it
                break

    if not matched_item:
        err_msg = f"⚠️ Could not find item matching `{target}` in PR #{pr_num}. Available items are #1 to #{len(branch_new_items)}."
        print(err_msg)
        run(f'gh pr comment {pr_num} --body "{err_msg}" -R {repo}')
        return

    item_id = matched_item['id']
    item_title = matched_item.get('title', item_id)
    print(f"Matched item #{matched_idx}: '{item_title}' ({item_id})")

    # Checkout branch
    run(f'git checkout -B {branch} origin/{branch}')

    # Delete image files
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
            run(f'git rm -f "{f}"')
            print(f"Removed {f}")

    # Remove item from screensavers.json
    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as sf:
        curr_cat = json.load(sf)

    updated_cat = [x for x in curr_cat if x.get('id') != item_id]
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

    # Commit and push
    run(f'git add screensavers.json CREDITS.md')
    commit_msg = f"Drop '{item_title}' (#{matched_idx}) per maintainer reject command: {reason}"
    run(f'git commit -m "{commit_msg}"')
    run(f'git push origin {branch} --force')

    # Update PR body to strike through
    updated_pr_body = pr_body
    # Replace in table
    # Pattern: | **X** | ... or | **#X** | ... or | **Item X** | ...
    table_pattern = rf"(\|\s*\*\*(?:#|Item\s+)?{matched_idx}\*\*\s*\|[^\|]*\|\s*)\*\*({re.escape(item_title)})\*\*"
    updated_pr_body = re.sub(table_pattern, rf"\1~~**\2**~~ *(❌ Rejected: {reason})*", updated_pr_body)

    # Also add note under preview
    preview_pattern = rf"(####\s+(?:#|Item\s+)?{matched_idx}:\s+{re.escape(item_title)}[^\n]*\n)"
    updated_pr_body = re.sub(preview_pattern, rf"\1> ❌ **Rejected by maintainer:** {reason}\n\n", updated_pr_body)

    with open('updated_pr_body.md', 'w', encoding='utf-8') as pf:
        pf.write(updated_pr_body)

    try:
        run(f'gh pr edit {pr_num} --body-file updated_pr_body.md -R {repo}')
        print("Updated PR body with rejection marker.")
    except Exception as e:
        print(f"Warning updating PR body: {e}")

    # Post confirmation comment
    remaining_count = len(branch_new_items) - 1
    confirm_lines = [
        f"❌ **Removed Item #{matched_idx}: '{item_title}' (`{item_id}`)**",
        f"> **Reason:** {reason}",
        "",
        f"The image and catalog entry have been removed from branch `{branch}`.",
        f"**Status:** {remaining_count} wallpaper{'s' if remaining_count != 1 else ''} remaining in this PR are ready to merge!"
    ]
    confirm_msg = '\n'.join(confirm_lines)
    run(f'gh pr comment {pr_num} --body "{confirm_msg}" -R {repo}')
    print("Posted confirmation comment on PR.")

    # Return to main
    run('git checkout main')
    print("Done!")


if __name__ == '__main__':
    main()
