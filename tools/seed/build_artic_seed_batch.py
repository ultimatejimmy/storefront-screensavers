# -*- coding: utf-8 -*-
"""
build_artic_seed_batch.py

Automatically fetches 100 Public Domain (CC0) artworks directly from the 
Art Institute of Chicago (ARTIC) API. 
Because we pull directly from the museum's JSON API, the titles, artists, 
and images are 100% guaranteed to match with ZERO hallucination or mismatches.

All images are officially designated as Public Domain (CC0).
"""

import urllib.request
import os
import json
import hashlib
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

# Clear old thumbs to ensure a clean slate
import shutil
if os.path.exists(REVIEW_THUMBS_DIR):
    shutil.rmtree(REVIEW_THUMBS_DIR, ignore_errors=True)
os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'application/json, image/*',
}

print("[+] Fetching top 100 Public Domain artworks from Art Institute of Chicago API...")

API_URL = "https://api.artic.edu/api/v1/artworks/search?query[term][is_public_domain]=true&limit=100&fields=id,title,artist_display,image_id,artwork_type_title"

req = urllib.request.Request(API_URL, headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read())

RAW = []
for art in data.get('data', []):
    if not art.get('image_id'):
        continue
    
    # Clean up title and artist text
    title = art.get('title', 'Unknown Title').strip()
    artist = art.get('artist_display', 'Unknown Artist').split('\n')[0].strip()
    
    # We use a reasonably high-res IIIF URL suitable for 3:4 e-ink screens (843px width)
    # The API format is: https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg
    image_id = art['image_id']
    url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    
    RAW.append((
        f"artic-{art['id']}",
        title,
        artist,
        art.get('artwork_type_title', 'Art'),
        "CC0 / Public Domain",
        "Art Institute of Chicago",
        url
    ))

print(f"[+] Retrieved {len(RAW)} valid artworks from API.")

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
        "authorUrl": "https://www.artic.edu",
        "category": cat,
        "sourceUrl": url,
        "license": lic,
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": attr,
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
    c['previewPath'] = f"review_thumbs/{thumb_name}"

    try:
        req = urllib.request.Request(c['imageUrl'], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            img_data = resp.read()
        with open(thumb_path, 'wb') as f:
            f.write(img_data)

        # Center-crop to 3:4 — no squishing or stretching
        with Image.open(thumb_path) as img:
            fit = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            fit.save(thumb_path, 'JPEG', quality=88)

        # Hash-based duplicate check
        with open(thumb_path, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()

        if h in seen_hashes:
            print(f"[{idx}] SKIP '{c['title']}' — same image as '{seen_hashes[h]}'")
            os.remove(thumb_path)
            continue

        seen_hashes[h] = c['title']
        valid_objs.append(c)
        print(f"[{idx}] OK  '{c['title']}'")

    except Exception as e:
        print(f"[{idx}] ERR '{c['title']}': {e}")

print(f"\n[+] Final valid count: {len(valid_objs)}")

# ---------------------------------------------------------------------------
# SAVE candidates.json
# ---------------------------------------------------------------------------
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(valid_objs, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# BUILD review.html
# ---------------------------------------------------------------------------
items_js = json.dumps(valid_objs, indent=2, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensaver Seeding Review</title>
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
    <h1>🖼 Storefront Screensaver Seeding Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved.json</button>
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
    // Ensure text is safely escaped in HTML rendering
    const safeTitle = c.title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const safeAuthor = c.author.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    card.innerHTML = `
      <img src="${{c.previewPath}}" alt="${{safeTitle}}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${{safeTitle}}</p>
        <p class="card-author">${{safeAuthor}}</p>
        <div class="badges">
          <span class="badge">${{c.category}}</span>
          <span class="badge badge-lic">${{c.license}}</span>
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
  a.download = 'approved.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"[+] review.html written with {len(valid_objs)} items -> {REVIEW_HTML}")
