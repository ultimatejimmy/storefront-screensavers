#!/usr/bin/env python3
"""
Process Screensaver Catalog Change Suggestions
Automates handling of change suggestions (image replacements and metadata corrections)
submitted via GitHub Issues from the Storefront Screensaver Catalog Site.
"""

import os
import sys
import json
import re
import time
import argparse
import subprocess
from io import BytesIO
from urllib.parse import urljoin
import requests
from PIL import Image, ImageOps

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')
IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
PLUGIN_THUMBS_DIR = os.path.join(THUMBS_DIR, 'plugin')

CHECKERBOARD_TILE = 12
CB_LIGHT = (255, 255, 255, 255)
CB_DARK  = (210, 210, 210, 255)

MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 50_000_000
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'MPO'}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
}


def make_checkerboard(w, h):
    bg = Image.new('RGBA', (w, h))
    pixels = bg.load()
    for y in range(h):
        cy = y // CHECKERBOARD_TILE
        for x in range(w):
            cx = x // CHECKERBOARD_TILE
            pixels[x, y] = CB_LIGHT if (cx + cy) % 2 == 0 else CB_DARK
    return bg


def fit_transparent(img_rgba, target_w, target_h):
    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    img_rgba.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    x = (target_w - img_rgba.width) // 2
    y = (target_h - img_rgba.height) // 2
    canvas.paste(img_rgba, (x, y), img_rgba)
    return canvas


def composite_over_checkerboard(img_rgba, target_w, target_h):
    bg = make_checkerboard(target_w, target_h)
    img_rgba.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    x = (target_w - img_rgba.width) // 2
    y = (target_h - img_rgba.height) // 2
    bg.paste(img_rgba, (x, y), img_rgba)
    return bg.convert('RGB')


def download_and_resolve_image(img_url, token=None, max_retries=3):
    """
    Downloads image from direct link or resolves HTML landing pages (catbox, imgbb, tmpfiles, etc.).
    Returns (raw_bytes, error_message).
    """
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    if 'github.com/user-attachments' in img_url and token:
        session.headers['Authorization'] = f'token {token}'

    for attempt in range(max_retries):
        try:
            print(f"Downloading from {img_url} (attempt {attempt + 1}/{max_retries})...")
            try:
                resp = session.get(img_url, allow_redirects=True, timeout=35)
            except requests.exceptions.SSLError:
                # Fallback for environments with self-signed proxy certs
                print("SSL verification failed, retrying with verify=False...")
                resp = session.get(img_url, allow_redirects=True, timeout=35, verify=False)

            if resp.status_code == 404:
                return None, f"404 Not Found: Link expired or invalid on host ({img_url})"
            if resp.status_code != 200:
                time.sleep(2)
                continue

            c_type = resp.headers.get('Content-Type', '').lower()
            is_html = ('text/html' in c_type) or resp.content.strip().startswith(b'<!DOCTYPE') or resp.content.strip().startswith(b'<html')

            if is_html:
                print("URL returned HTML landing page. Parsing HTML to extract direct image stream...")
                html_text = resp.text
                patterns = [
                    r'<img[^>]+id=["\']img_preview["\'][^>]+src=["\']([^"\']+)["\']',
                    r'<a[^>]+class=["\']download["\'][^>]+href=["\']([^"\']+)["\']',
                    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
                    r'<img[^>]+src=["\'](https?://[^"\']+\.(?:png|jpg|jpeg|webp))["\']',
                    r'["\'](https?://[^\s"\']+/dl/[^\s"\']+)["\']',
                ]
                extracted_url = None
                for pat in patterns:
                    m = re.search(pat, html_text, re.IGNORECASE)
                    if m:
                        found_target = m.group(1)
                        if not found_target.startswith('http'):
                            found_target = urljoin(img_url, found_target)
                        if found_target != img_url:
                            extracted_url = found_target
                            break

                if extracted_url:
                    print(f"Resolved direct image URL: {extracted_url}")
                    try:
                        dl_resp = session.get(extracted_url, allow_redirects=True, timeout=35)
                    except requests.exceptions.SSLError:
                        dl_resp = session.get(extracted_url, allow_redirects=True, timeout=35, verify=False)
                    if dl_resp.status_code == 200:
                        if len(dl_resp.content) > MAX_DOWNLOAD_BYTES:
                            return None, "File size exceeded 25 MB limit."
                        return dl_resp.content, None
                    else:
                        return None, f"Resolved direct URL returned HTTP status {dl_resp.status_code}."
                else:
                    return None, "Provided link is an HTML webpage rather than a direct image, and no image could be extracted."

            if len(resp.content) > MAX_DOWNLOAD_BYTES:
                return None, "File size exceeded 25 MB limit."

            return resp.content, None
        except Exception as exc:
            print(f"Download attempt {attempt + 1} error: {exc}")
            if attempt < max_retries - 1:
                time.sleep(2)

    return None, "Failed to download image after multiple attempts."


def parse_change_suggestion(body, comment_body=''):
    """
    Parses change suggestion fields from issue markdown body.
    """
    data = {}

    target_id_m = re.search(r'\*\*Target Item ID:\*\*\s*`?([a-zA-Z0-9_-]+)`?', body)
    if target_id_m:
        data['target_id'] = target_id_m.group(1).strip()

    target_title_m = re.search(r'\*\*Target Title:\*\*\s*(.*)', body)
    if target_title_m:
        data['target_title'] = target_title_m.group(1).strip()

    type_m = re.search(r'\*\*Report/Change Type:\*\*\s*(.*)', body)
    if type_m:
        data['change_type'] = type_m.group(1).strip()
    else:
        data['change_type'] = 'Replacement Image' if 'Replacement Image' in body else 'Metadata Correction'

    prop_title_m = re.search(r'\*\*Proposed Title:\*\*\s*(.*)', body)
    if prop_title_m:
        data['proposed_title'] = prop_title_m.group(1).strip()

    prop_author_m = re.search(r'\*\*Proposed Author:\*\*\s*(.*)', body)
    if prop_author_m:
        data['proposed_author'] = prop_author_m.group(1).strip()

    prop_cat_m = re.search(r'\*\*Proposed Category:\*\*\s*(.*)', body)
    if prop_cat_m:
        data['proposed_category'] = prop_cat_m.group(1).strip()

    prop_tags_m = re.search(r'\*\*Proposed Tags:\*\*\s*(.*)', body)
    if prop_tags_m:
        data['proposed_tags'] = prop_tags_m.group(1).strip()

    filename_m = re.search(r'\*\*(?:Replacement Filename|Filename):\*\*\s*(.*)', body)
    if filename_m:
        data['filename'] = filename_m.group(1).strip()

    reason_m = re.search(r'\*\*Reason/Details:\*\*\s*([\s\S]*?)(?:\n---|---|\Z)', body)
    if reason_m:
        data['reason'] = reason_m.group(1).strip()

    # Image URL extraction
    img_url = None
    rep_img_m = re.search(r'\*\*(?:Replacement Image|Image):\*\*\s*(https?://[^\s\)\"]+)', body)
    if rep_img_m:
        img_url = rep_img_m.group(1).strip()

    if not img_url:
        preview_m = re.search(r'###\s+Replacement Preview\s*\n!\[.*?\]\((https?://[^\s\)]+)\)', body)
        if preview_m:
            img_url = preview_m.group(1).strip()

    if not img_url:
        any_url_m = re.search(r'https?://[^\s\)\"]+(?:user-attachments|\.png|\.jpg|\.jpeg|\.webp|catbox|tmpfiles|freeimage|imgbb|imgur|postimg)[^\s\)\"]*', body, re.IGNORECASE)
        if any_url_m:
            img_url = any_url_m.group(0).strip()

    if not img_url and comment_body:
        c_m = re.search(r'!\[.*?\]\((https?://[^\s\)]+)\)|(https?://[^\s\)\"]+(?:user-attachments|\.png|\.jpg|\.jpeg|\.webp|catbox|tmpfiles|freeimage|imgbb|imgur|postimg)[^\s\)\"]*)', comment_body, re.IGNORECASE)
        if c_m:
            img_url = (c_m.group(1) or c_m.group(2)).strip()

    data['img_url'] = img_url
    return data


def set_output(name, val):
    out_file = os.environ.get('GITHUB_OUTPUT')
    if out_file and os.path.exists(out_file):
        with open(out_file, 'a', encoding='utf-8') as f:
            f.write(f"{name}={val}\n")


def write_comment_file(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description="Process screensaver catalog change suggestion")
    parser.add_argument('--issue', type=int, help="Issue number to process locally using GitHub CLI")
    parser.add_argument('--no-push', action='store_true', help="Do not push git branch or create PR")
    args = parser.parse_args()

    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'ultimatejimmy/storefront-screensavers')
    issue_num = os.environ.get('ISSUE_NUM')
    body = os.environ.get('ISSUE_BODY', '')
    comment_body = os.environ.get('COMMENT_BODY', '')

    if args.issue:
        issue_num = str(args.issue)
        print(f"Fetching issue #{issue_num} from {repo} using gh CLI...")
        cmd = ['gh', 'issue', 'view', str(issue_num), '-R', repo, '--json', 'title,body,number,author']
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_data = json.loads(res.stdout)
        body = issue_data.get('body', '')

    if not issue_num or not body:
        print("Error: Missing issue number or issue body.", file=sys.stderr)
        sys.exit(1)

    parsed = parse_change_suggestion(body, comment_body)
    target_id = parsed.get('target_id')
    change_type = parsed.get('change_type', '')

    print(f"Processing Change Suggestion for issue #{issue_num}:")
    print(f"  Target ID: {target_id}")
    print(f"  Change Type: {change_type}")

    if not target_id:
        msg = f"⚠️ Could not detect a valid `Target Item ID` in issue #{issue_num}. Please make sure the issue includes `**Target Item ID:** <id>`."
        print(msg)
        write_comment_file('change_comment.md', [msg])
        set_output('valid', 'false')
        sys.exit(0)

    # Load catalog
    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    item_idx = -1
    existing_item = None
    for idx, it in enumerate(catalog):
        if it.get('id') == target_id:
            item_idx = idx
            existing_item = it
            break

    if item_idx == -1:
        msg = f"⚠️ Target screensaver `{target_id}` was not found in `screensavers.json`. It may have been removed or renamed."
        print(msg)
        write_comment_file('change_comment.md', [msg])
        set_output('valid', 'false')
        sys.exit(0)

    is_replacement = ('replacement' in change_type.lower()) or bool(parsed.get('img_url'))
    img_url = parsed.get('img_url')

    if is_replacement and not img_url:
        msg = f"⚠️ Change Suggestion for `{target_id}` requested an image replacement, but no valid image URL was found in the issue description or comments."
        print(msg)
        write_comment_file('change_comment.md', [msg])
        set_output('valid', 'false')
        sys.exit(0)

    # Track differences
    changes_made = []
    old_title = existing_item.get('title', '')
    old_author = existing_item.get('author', '')
    old_category = existing_item.get('category', 'General')
    old_tags = existing_item.get('tags', [])

    new_title = parsed.get('proposed_title') or old_title
    new_author = parsed.get('proposed_author') or old_author

    # Categories
    raw_cat = parsed.get('proposed_category')
    if raw_cat:
        cat_list = [c.strip() for c in raw_cat.split(',')] if isinstance(raw_cat, str) else list(raw_cat)
    else:
        cat_list = old_category if isinstance(old_category, list) else [old_category]

    # Tags
    raw_tags = parsed.get('proposed_tags')
    if raw_tags:
        tag_list = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
    else:
        tag_list = list(old_tags)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(PLUGIN_THUMBS_DIR, exist_ok=True)

    files_to_add = [SCREENSAVERS_JSON]
    files_to_remove = []

    is_transparent = False

    if is_replacement:
        raw_data, dl_err = download_and_resolve_image(img_url, token)
        if dl_err or not raw_data:
            err_msg = f"⚠️ Failed to download replacement image: {dl_err or 'Empty image stream'}"
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        # Security check: strictly reject vector SVG / XML / executable scripts
        raw_lead = raw_data[:512].lower()
        if raw_data.strip().startswith(b'<?xml') or b'<svg' in raw_lead or b'<script' in raw_lead:
            err_msg = "⚠️ Disallowed vector SVG or script file. Only raster JPG, PNG, or WebP images are permitted."
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        img_stream = BytesIO(raw_data)
        try:
            verify_img = Image.open(img_stream)
            detected_format = verify_img.format
            verify_img.verify()
        except Exception as val_err:
            err_msg = f"⚠️ Corrupted image file structure: {val_err}"
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        if detected_format not in ALLOWED_FORMATS:
            err_msg = f"⚠️ Unsupported image format '{detected_format}'. Please upload JPG, PNG, or WebP."
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        img_stream.seek(0)
        try:
            img = Image.open(img_stream)
            img.load()
            img = ImageOps.exif_transpose(img)
        except Exception as dec_err:
            err_msg = f"⚠️ Failed to decode image pixels: {dec_err}"
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        if img.width < 200 or img.height < 200:
            err_msg = f"⚠️ Image resolution ({img.width}×{img.height} px) is too small (minimum 200×200 px)."
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        if img.width > 12000 or img.height > 12000:
            err_msg = f"⚠️ Image resolution ({img.width}×{img.height} px) exceeds maximum limit of 12,000 px."
            print(err_msg)
            write_comment_file('change_comment.md', [err_msg])
            set_output('valid', 'false')
            sys.exit(0)

        # Transparency detection
        has_trans_tag = any(c.lower() == 'transparent' for c in cat_list) or any(t.lower() == 'transparent' for t in tag_list)
        has_alpha = ('A' in img.getbands()) or (img.mode in ('RGBA', 'LA')) or ('transparency' in img.info)
        has_real_trans = False
        if has_alpha:
            rgba_check = img.convert('RGBA')
            min_a, max_a = rgba_check.split()[-1].getextrema()
            if min_a < 250:
                has_real_trans = True

        is_transparent = has_trans_tag or has_real_trans

        # Determine target paths
        if is_transparent:
            full_rel = f"images/{target_id}.png"
            thumb_web_rel = f"images/thumbnails/{target_id}.png"
            thumb_plugin_rel = f"images/thumbnails/plugin/{target_id}.png"

            img_rgba = img.convert('RGBA')
            master_img = fit_transparent(img_rgba.copy(), 1860, 2480)
            master_img.save(os.path.join(REPO_ROOT, full_rel), 'PNG')

            web_thumb = fit_transparent(img_rgba.copy(), 600, 800)
            web_thumb.save(os.path.join(REPO_ROOT, thumb_web_rel), 'PNG')

            plugin_thumb = composite_over_checkerboard(img_rgba.copy(), 600, 800)
            plugin_thumb.save(os.path.join(REPO_ROOT, thumb_plugin_rel), 'PNG')

            files_to_add.extend([full_rel, thumb_web_rel, thumb_plugin_rel])

            # Cleanup old JPG if switched from jpg to png
            for old_f in [f"images/{target_id}.jpg", f"images/thumbnails/{target_id}.jpg"]:
                p = os.path.join(REPO_ROOT, old_f)
                if os.path.exists(p):
                    try:
                        os.remove(p)
                        files_to_remove.append(old_f)
                    except Exception:
                        pass
        else:
            full_rel = f"images/{target_id}.jpg"
            thumb_web_rel = f"images/thumbnails/{target_id}.jpg"
            thumb_plugin_rel = None

            img_rgb = img.convert('RGB')
            master_img = ImageOps.fit(img_rgb, (1860, 2480), Image.Resampling.LANCZOS)
            master_img.save(os.path.join(REPO_ROOT, full_rel), 'JPEG', quality=92)

            thumb_img = ImageOps.fit(img_rgb, (600, 800), Image.Resampling.LANCZOS)
            thumb_img.save(os.path.join(REPO_ROOT, thumb_web_rel), 'JPEG', quality=85)

            files_to_add.extend([full_rel, thumb_web_rel])

            # Cleanup old PNG / plugin thumb if switched from png to jpg
            for old_f in [f"images/{target_id}.png", f"images/thumbnails/{target_id}.png", f"images/thumbnails/plugin/{target_id}.png"]:
                p = os.path.join(REPO_ROOT, old_f)
                if os.path.exists(p):
                    try:
                        os.remove(p)
                        files_to_remove.append(old_f)
                    except Exception:
                        pass

        raw_base = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/"
        existing_item['fullUrl'] = raw_base + full_rel
        existing_item['thumbnailUrl'] = raw_base + thumb_web_rel
        existing_item['pluginThumbnailUrl'] = (raw_base + thumb_plugin_rel) if thumb_plugin_rel else existing_item['thumbnailUrl']

        changes_made.append(f"- **Image Replacement**: Processed {img.width}×{img.height} px source image into master (1860×2480) and thumbnails (600×800) [Transparent: `{is_transparent}`]")

    # Normalize categories & tags
    if is_transparent:
        if not any(c.lower() == 'transparent' for c in cat_list):
            cat_list.append('Transparent')
        if not any(t.lower() == 'transparent' for t in tag_list):
            tag_list.append('transparent')

    final_category = cat_list if len(cat_list) > 1 else (cat_list[0] if cat_list else "General")

    if new_title != old_title:
        changes_made.append(f"- **Title**: `{old_title}` → `{new_title}`")
    if new_author != old_author:
        changes_made.append(f"- **Author**: `{old_author}` → `{new_author}`")
    if final_category != old_category:
        changes_made.append(f"- **Category**: `{old_category}` → `{final_category}`")
    if tag_list != old_tags:
        changes_made.append(f"- **Tags**: `{old_tags}` → `{tag_list}`")

    # Update item in catalog
    existing_item['title'] = new_title
    existing_item['author'] = new_author
    existing_item['category'] = final_category
    existing_item['tags'] = tag_list

    catalog[item_idx] = existing_item

    # Save catalog
    with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Rebuild credits
    try:
        sys.path.insert(0, os.path.join(REPO_ROOT, 'tools'))
        from catalog_studio import rebuild_credits_file
        rebuild_credits_file(catalog)
        files_to_add.append('CREDITS.md')
        print("Regenerated CREDITS.md successfully.")
    except Exception as cred_err:
        print(f"Warning: Could not regenerate CREDITS.md: {cred_err}")

    branch = f"change-{issue_num}"
    pr_title = f"Catalog Change: {new_title} [{target_id}]"

    reason_text = parsed.get('reason') or 'No details specified.'

    pr_body = [
        f"Closes #{issue_num}",
        "",
        f"### Catalog Change Suggestion: {new_title} (`{target_id}`)",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| **Target Item ID** | `{target_id}` |",
        f"| **Change Type** | {change_type} |",
        f"| **Title** | {new_title} |",
        f"| **Author** | {new_author} |",
        f"| **Category** | {', '.join(cat_list) if isinstance(cat_list, list) else cat_list} |",
        f"| **Tags** | {', '.join(tag_list)} |",
        "",
        "### Changes Summary",
        '\n'.join(changes_made) if changes_made else "- Metadata updated according to suggestion",
        "",
        f"**Reason/Details from Submitter:**",
        f"> {reason_text}",
        ""
    ]

    if is_replacement and img_url:
        pr_body.extend([
            "### Replacement Visual Preview",
            f"![{new_title}]({img_url})",
            ""
        ])

    pr_body.extend([
        "---",
        f"*Automated PR generated from change suggestion issue #{issue_num} via Storefront Screensaver Catalog workflow.*"
    ])

    pr_url = f"https://github.com/{repo}/pulls"

    if not args.no_push:
        # Git operations
        subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], cwd=REPO_ROOT, check=True)
        subprocess.run(['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'], cwd=REPO_ROOT, check=True)

        print(f"Checking out branch {branch} from origin/main...")
        subprocess.run(['git', 'fetch', 'origin', 'main'], cwd=REPO_ROOT, check=True)
        subprocess.run(['git', 'checkout', '-B', branch, 'origin/main'], cwd=REPO_ROOT, check=True)

        # Re-apply changes on branch
        with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

        try:
            from catalog_studio import rebuild_credits_file
            rebuild_credits_file(catalog)
        except Exception:
            pass

        for f_rem in files_to_remove:
            subprocess.run(['git', 'rm', '-f', f_rem], cwd=REPO_ROOT, check=False)

        for f_add in files_to_add:
            subprocess.run(['git', 'add', f_add], cwd=REPO_ROOT, check=True)

        commit_msg = f"Update screensaver '{target_id}' for change suggestion #{issue_num}"
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_ROOT, check=True)

        print(f"Pushing branch {branch} to origin...")
        subprocess.run(['git', 'push', 'origin', branch, '--force'], cwd=REPO_ROOT, check=True)

        # Create or update PR
        with open(os.path.join(REPO_ROOT, 'pr_body_tmp.md'), 'w', encoding='utf-8') as pf:
            pf.write('\n'.join(pr_body))

        pr_cmd = [
            'gh', 'pr', 'create',
            '--title', pr_title,
            '--body-file', 'pr_body_tmp.md',
            '--head', branch,
            '--base', 'main',
            '-R', repo
        ]
        try:
            pr_out = subprocess.check_output(pr_cmd, cwd=REPO_ROOT, text=True).strip()
            pr_url = pr_out
            print(f"Created PR: {pr_url}")
        except subprocess.CalledProcessError as err:
            print(f"gh pr create returned non-zero (PR may already exist): {err}")
            # Try to fetch existing PR url for this branch
            try:
                prs_list = subprocess.check_output(['gh', 'pr', 'list', '--head', branch, '-R', repo, '--json', 'url'], cwd=REPO_ROOT, text=True)
                prs_data = json.loads(prs_list)
                if prs_data:
                    pr_url = prs_data[0]['url']
            except Exception:
                pass

    # Build Issue Comment
    comment_lines = [
        "🎉 **Change Suggestion Verified & Pull Request Created!**",
        "",
        f"An automated Pull Request has been prepared for review: [{pr_title}]({pr_url})",
        "",
        f"### Suggested Changes for `{target_id}`:",
        '\n'.join(changes_made) if changes_made else "- Metadata update applied",
        "",
        f"| Property | Value |",
        f"|---|---|",
        f"| **Target Item ID** | `{target_id}` |",
        f"| **Title** | {new_title} |",
        f"| **Author** | {new_author} |",
        f"| **Category** | {', '.join(cat_list) if isinstance(cat_list, list) else cat_list} |",
        f"| **Pull Request** | [View Pull Request]({pr_url}) |",
        ""
    ]

    if is_replacement and img_url:
        comment_lines.extend([
            "### Replacement Visual Preview",
            f"![{new_title}]({img_url})",
            ""
        ])

    comment_lines.extend([
        "**Review Status:** Pending maintainer review & approval. Once approved and merged into `main`, the changes will immediately update in the web catalog and KOReader Storefront plugin!"
    ])

    comment_path = os.path.join(REPO_ROOT, 'change_comment.md')
    write_comment_file(comment_path, comment_lines)
    set_output('valid', 'true')
    print(f"Done! Comment generated at {comment_path}")

    if args.issue and not args.no_push:
        try:
            print(f"Posting comment to issue #{issue_num} via gh CLI...")
            subprocess.run(['gh', 'issue', 'comment', str(issue_num), '-F', comment_path, '-R', repo], cwd=REPO_ROOT, check=True)
            print("Successfully commented on issue!")
        except Exception as c_err:
            print(f"Warning: Could not post comment via gh CLI: {c_err}")


if __name__ == '__main__':
    main()
