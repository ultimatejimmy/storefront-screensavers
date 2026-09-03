#!/usr/bin/env python3
"""
Consolidate Open Submission PRs into a Single Review PR
Combines open fragmented submission branches into a single consolidated PR
so the maintainer can review all pending wallpapers in one place and merge with 1 click.
"""

import os
import sys
import json
import subprocess
import re

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')


def run(cmd, cwd=REPO_ROOT, check=True):
    res = subprocess.run(cmd, cwd=cwd, shell=True, text=True, encoding='utf-8', errors='replace', capture_output=True)
    if check and res.returncode != 0:
        print(f"Command failed: {cmd}\nStdout: {res.stdout}\nStderr: {res.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return res


def main():
    repo = os.environ.get('GITHUB_REPOSITORY', 'ultimatejimmy/storefront-screensavers')
    print("Fetching open submission PRs...")

    # Ensure clean repo on main
    run('git fetch origin main')
    run('git checkout main')
    run('git pull origin main')

    prs_out = run(f'gh pr list -R {repo} --state open --limit 100 --json number,title,headRefName,url,body').stdout
    open_prs = json.loads(prs_out)

    submission_prs = [p for p in open_prs if p.get('headRefName', '').startswith('submission-')]
    # Sort by PR number ascending
    submission_prs.sort(key=lambda p: p['number'])

    if not submission_prs:
        print("No open submission PRs found.")
        return

    print(f"Found {len(submission_prs)} open submission PR(s): {[p['number'] for p in submission_prs]}")

    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
        main_catalog = json.load(f)

    main_ids = {x.get('id') for x in main_catalog}
    consolidated_items = []
    branches_to_process = []

    for pr in submission_prs:
        pr_num = pr['number']
        branch = pr['headRefName']
        print(f"Inspecting PR #{pr_num} ({branch})...")
        run(f'git fetch origin {branch}')

        try:
            b_raw = run(f'git show origin/{branch}:screensavers.json').stdout
            b_data = json.loads(b_raw)
        except Exception as e:
            print(f"Warning: Could not read screensavers.json on {branch}: {e}")
            continue

        new_on_branch = [x for x in b_data if x.get('id') not in main_ids]
        if not new_on_branch:
            print(f"No new items on {branch} compared to main.")
            continue

        for it in new_on_branch:
            if it.get('id') not in [c['id'] for c in consolidated_items]:
                it['_source_pr'] = pr_num
                it['_source_branch'] = branch
                consolidated_items.append(it)
                branches_to_process.append((branch, pr_num))

    if not consolidated_items:
        print("No new unique items found across open PRs.")
        return

    print(f"Consolidating {len(consolidated_items)} unique items:")
    for idx, it in enumerate(consolidated_items, 1):
        print(f"  #{idx}: {it.get('title')} ({it.get('id')}) from PR #{it.get('_source_pr')}")

    target_branch = "submission-batch-review"
    print(f"\nCreating clean consolidated branch: {target_branch} from origin/main...")
    run(f'git checkout -B {target_branch} origin/main')

    # Pull image files from each branch
    files_added = set()
    for branch, pr_num in branches_to_process:
        diff_out = run(f'git diff --name-only --diff-filter=A origin/main...origin/{branch}').stdout.splitlines()
        for f in diff_out:
            if f.startswith('images/'):
                run(f'git checkout origin/{branch} -- "{f}"')
                files_added.add(f)

    # Append new items to screensavers.json
    curr_catalog = list(main_catalog)
    for it in consolidated_items:
        clean_it = {k: v for k, v in it.items() if not k.startswith('_')}
        curr_catalog.append(clean_it)

    with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(curr_catalog, f, indent=2, ensure_ascii=False)

    # Rebuild CREDITS.md
    try:
        sys.path.insert(0, os.path.join(REPO_ROOT, 'tools'))
        from catalog_studio import rebuild_credits_file
        rebuild_credits_file(curr_catalog)
        print("Rebuilt CREDITS.md successfully.")
    except Exception as e:
        print(f"Warning rebuilding credits: {e}")

    # Commit all
    run('git add images/ screensavers.json CREDITS.md')
    commit_msg = f"Consolidate {len(consolidated_items)} pending screensavers for review ({', '.join(f'#{p}' for p in [pr['number'] for pr in submission_prs])})"
    run(f'git commit -m "{commit_msg}"')

    print(f"Pushing {target_branch} to origin...")
    run(f'git push origin {target_branch} --force')

    # Construct Consolidated PR Body
    pr_body_lines = [
        f"## 📋 Consolidated Screensaver Batch Review ({len(consolidated_items)} Wallpapers)",
        "",
        f"This pull request consolidates {len(consolidated_items)} pending screensaver submissions from {len(submission_prs)} separate PRs into a single reviewable batch.",
        "",
        "> 💡 **Maintainer Curation Instructions:**",
        "> - **To reject an individual wallpaper:** Comment `/reject <#>` or `/reject <item-id> [reason]` (e.g. `/reject 4 low quality`).",
        "> - **To approve & merge:** When you are satisfied with the items, simply click **Merge pull request** once!",
        "",
        "---",
        "",
        "### 🖼️ Wallpapers in this Batch",
        "",
        "| # | Preview | Title | Author | Category | Target ID | Original PR |",
        "|---|---|---|---|---|---|---|"
    ]

    for idx, it in enumerate(consolidated_items, 1):
        item_id = it.get('id')
        title = it.get('title', 'Untitled')
        author = it.get('author', 'Community')
        cats = it.get('category')
        cat_str = ', '.join(cats) if isinstance(cats, list) else str(cats)
        thumb_url = it.get('thumbnailUrl', '')
        src_pr = it.get('_source_pr')
        preview_md = f"<img src='{thumb_url}' width='90' />" if thumb_url else "N/A"
        pr_body_lines.append(f"| **#{idx}** | {preview_md} | **{title}** | {author} | {cat_str} | `{item_id}` | #{src_pr} |")

    pr_body_lines.extend([
        "",
        "---",
        "### Visual Previews",
        ""
    ])

    for idx, it in enumerate(consolidated_items, 1):
        title = it.get('title', 'Untitled')
        thumb_url = it.get('thumbnailUrl', '')
        full_url = it.get('fullUrl', '')
        pr_body_lines.extend([
            f"#### #{idx}: {title} (`{it.get('id')}`)",
            f"- **Author:** {it.get('author')}",
            f"- **Category:** {', '.join(it.get('category')) if isinstance(it.get('category'), list) else it.get('category')}",
            f"- **Tags:** {', '.join(it.get('tags', []))}",
            f"- **Master Image:** [{it.get('id')}]({full_url})",
            f"![{title}]({thumb_url})",
            ""
        ])

    issues_referenced = set()
    for pr in submission_prs:
        pr_body = pr.get('body', '')
        closes_m = re.findall(r'Closes\s+#(\d+)', pr_body, re.IGNORECASE)
        for c in closes_m:
            issues_referenced.add(c)

    if issues_referenced:
        pr_body_lines.extend([
            "---",
            f"Closes {', '.join(f'#{i}' for i in sorted(issues_referenced, key=int))}",
            ""
        ])

    with open('consolidated_pr_body.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(pr_body_lines))

    titles_sample = ', '.join(it.get('title') for it in consolidated_items[:3])
    pr_title = f"Batch Screensaver Review: {len(consolidated_items)} Wallpapers ({titles_sample} +{len(consolidated_items)-3} more)"

    print("Opening Consolidated Pull Request...")
    pr_create_res = run(f'gh pr create --title "{pr_title}" --body-file consolidated_pr_body.md --head {target_branch} --base main -R {repo}')
    new_pr_url = pr_create_res.stdout.strip()
    print(f"\n[SUCCESS] Successfully created Consolidated PR: {new_pr_url}")

    # Close individual PRs with note
    print("\nClosing fragmented individual PRs...")
    for pr in submission_prs:
        pr_num = pr['number']
        close_msg = f"This submission has been consolidated into {new_pr_url} for unified review and 1-click approval."
        try:
            run(f'gh pr comment {pr_num} --body "{close_msg}" -R {repo}')
            run(f'gh pr close {pr_num} -R {repo}')
            print(f"Closed PR #{pr_num}")
        except Exception as e:
            print(f"Warning closing PR #{pr_num}: {e}")

    # Return to main
    run('git checkout main')
    print("\nAll done! You can now review all wallpapers in the consolidated PR.")


if __name__ == '__main__':
    main()
