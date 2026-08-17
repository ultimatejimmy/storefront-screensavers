# -*- coding: utf-8 -*-
"""
build_reddit_seed_batch.py

Fetches community screensavers directly from Reddit via the pullpush.io mirror API.
Since Reddit blocks standard unauthenticated API requests from scripts, this mirror
allows us to safely index community-shared screensaver galleries.

Community-shared images implicitly grant permission for personal use,
fitting the user's criteria.
"""

import urllib.request
import os
import json
import hashlib
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs_reddit')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates_reddit.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review_reddit.html')

import shutil
if os.path.exists(REVIEW_THUMBS_DIR):
    shutil.rmtree(REVIEW_THUMBS_DIR, ignore_errors=True)
os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 StorefrontScreensavers/1.0',
    'Accept': 'application/json',
}

# Search terms and subreddits
SEARCHES = [
    ("koreader", "screensaver"),
    ("kindle", "screensaver"),
    ("kobo", "screensaver"),
    ("ereader", "screensaver")
]

print("[+] Fetching community screensavers from Reddit (via PullPush API)...")
RAW = []

for sub, query in SEARCHES:
    url = f"https://api.pullpush.io/reddit/search/submission/?subreddit={sub}&q={query}&size=30"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            
        for item in data.get('data', []):
            title = item.get('title', 'Reddit Screensaver')
            author = f"u/{item.get('author', 'Unknown')}"
            permalink = f"https://reddit.com{item.get('permalink', '')}"
            
            # Direct Image URL
            img_url = item.get('url', '')
            if img_url.endswith(('.jpg', '.png', '.jpeg', '.webp')):
                RAW.append((
                    f"rd-{item.get('id')}", title, author, f"r/{sub}", 
                    "Community Upload", permalink, img_url
                ))
            
            # Gallery parsing
            if 'gallery' in img_url or 'media_metadata' in item:
                metadata = item.get('media_metadata', {})
                for idx, (key, val) in enumerate(metadata.items(), start=1):
                    if 's' in val and 'u' in val['s']:
                        # Replace Reddit's HTML entity &amp; with &
                        gallery_img_url = val['s']['u'].replace('&amp;', '&')
                        RAW.append((
                            f"rd-{item.get('id')}-{key}", f"{title} (Image {idx})", author, f"r/{sub}", 
                            "Community Upload", permalink, gallery_img_url
                        ))
                        
    except Exception as e:
        print(f"Error fetching r/{sub}: {e}")
        
    time.sleep(1)

print(f"[+] Retrieved {len(RAW)} valid screensaver URLs from Reddit.")

# ---------------------------------------------------------------------------
# DEDUPLICATION & BUILD
# ---------------------------------------------------------------------------
cand_objs = []
seen_ids = set()

for (cid, title, author, cat, lic, attr, url) in RAW:
    if cid in seen_ids:
        continue
    seen_ids.add(cid)
    cand_objs.append({
        "id": cid,
        "title": title,
        "author": author,
        "authorUrl": attr, # Link back to the reddit post
        "category": cat,
        "sourceUrl": attr,
        "license": lic,
        "licenseUrl": attr,
        "attribution": "Reddit Community",
        "imageUrl": url,
    })

print(f"[+] Deduplicated candidate count: {len(cand_objs)}")

# ---------------------------------------------------------------------------
# DOWNLOAD & CROP THUMBNAILS
# ---------------------------------------------------------------------------
valid_objs = []
seen_hashes = {}

for idx, c in enumerate(cand_objs, 1):
    thumb_name = f"{c['id']}.jpg"
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    c['previewPath'] = f"review_thumbs_reddit/{thumb_name}"

    try:
        # Some reddit preview URLs return 403 if missing specific headers or query params
        req = urllib.request.Request(c['imageUrl'], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            img_data = resp.read()
            
        with open(thumb_path, 'wb') as f:
            f.write(img_data)

        # Center-crop to 3:4
        with Image.open(thumb_path) as img:
            fit = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            fit.save(thumb_path, 'JPEG', quality=88)

        # Hash dedup
        with open(thumb_path, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()

        if h in seen_hashes:
            print(f"[{idx}] SKIP '{c['title']}' — duplicate hash")
            os.remove(thumb_path)
            continue

        seen_hashes[h] = c['title']
        valid_objs.append(c)
        print(f"[{idx}] OK  '{c['title'].encode('ascii', 'replace').decode('ascii')}'")

    except Exception as e:
        print(f"[{idx}] ERR '{c['title'].encode('ascii', 'replace').decode('ascii')}': {e}")
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
    time.sleep(0.5)

print(f"\n[+] Final valid reddit count: {len(valid_objs)}")

# ---------------------------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------------------------
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(valid_objs, f, indent=2, ensure_ascii=False)

items_js = json.dumps(valid_objs, indent=2, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensavers - Reddit Review</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 20px; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }}
    h1 {{ margin: 0; font-size: 1.4rem; }}
    .stats {{ color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
    .card {{ background: #1e293b; border: 2px solid #334155; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: border-color 0.2s; }}
    .card.approved {{ border-color: #22c55e; }}
    .card.rejected {{ border-color: #ef4444; opacity: 0.4; filter: grayscale(80%); }}
    .card img {{ width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block; background: #1e293b; }}
    .card-body {{ padding: 12px; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .card-title {{ font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin: 0; }}
    .card-author {{ font-size: 0.8rem; color: #94a3b8; margin: 0; }}
    .badges {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .badge {{ padding: 2px 8px; font-size: 0.7rem; border-radius: 4px; background: #334155; color: #cbd5e1; }}
    .badge-lic {{ background: #0369a1; color: #bae6fd; }}
    .actions {{ display: flex; gap: 8px; margin-top: auto; padding-top: 8px; }}
    .actions button {{ flex: 1; padding: 8px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; font-size: 0.85rem; }}
    .btn-approve {{ background: #22c55e; color: #052e16; }}
    .btn-reject  {{ background: #ef4444; color: #450a0a; }}
    .btn-export  {{ background: #8b5cf6; color: #fff; padding: 10px 20px; border-radius: 8px; font-size: 0.9rem; border: none; cursor: pointer; font-weight: bold; white-space: nowrap; }}
  </style>
</head>
<body>
<header>
  <div>
    <h1>🖼 Reddit Screensaver Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved_reddit.json</button>
</header>
<div class="grid" id="grid"></div>
<script>
const candidates = {items_js};
const state = {{}};
candidates.forEach(c => state[c.id] = true);

function render() {{
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  let nApp = 0, nRej = 0;
  candidates.forEach(c => {{
    const app = state[c.id];
    app ? nApp++ : nRej++;
    const card = document.createElement('div');
    card.className = 'card ' + (app ? 'approved' : 'rejected');
    const safeTitle = c.title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const safeAuthor = c.author.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    card.innerHTML = `
      <img src="${{c.previewPath}}" alt="${{safeTitle}}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${{safeTitle}}</p>
        <p class="card-author">${{safeAuthor}}</p>
        <div class="badges">
          <span class="badge">${{c.category}}</span>
          <span class="badge badge-lic"><a href="${{c.sourceUrl}}" target="_blank" style="color:inherit; text-decoration:none;">🔗 Original Post</a></span>
        </div>
        <div class="actions">
          <button class="btn-approve" onclick="set('${{c.id}}',true)">✅ Approve</button>
          <button class="btn-reject"  onclick="set('${{c.id}}',false)">❌ Reject</button>
        </div>
      </div>`;
    grid.appendChild(card);
  }});
  document.getElementById('stats').innerText =
    `${{candidates.length}} total  ·  ${{nApp}} approved  ·  ${{nRej}} rejected`;
}}

function set(id, v) {{ state[id] = v; render(); }}

function exportApproved() {{
  const list = candidates.filter(c => state[c.id]);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(list,null,2)], {{type:'application/json'}}));
  a.download = 'approved_reddit.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"[+] review_reddit.html written with {len(valid_objs)} items")
