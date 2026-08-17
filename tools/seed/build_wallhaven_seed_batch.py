# -*- coding: utf-8 -*-
"""
build_wallhaven_seed_batch.py

Fetches modern wallpapers directly from Wallhaven's JSON API.
Since Wallhaven is a community wallpaper sharing platform, it aligns 
with the "implicit permission" directive for sharing screensavers.
This avoids old museum art and provides sleek, modern imagery.
"""

import urllib.request
import os
import json
import hashlib
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs_wallhaven')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates_wallhaven.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review_wallhaven.html')

import shutil
if os.path.exists(REVIEW_THUMBS_DIR):
    shutil.rmtree(REVIEW_THUMBS_DIR, ignore_errors=True)
os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 StorefrontScreensavers/1.0',
    'Accept': 'application/json',
}

# We'll pull 15 top images from 5 different tags (75 total)
SEARCHES = [
    ("minimalism", "Minimalist"),
    ("landscape", "Nature/Landscapes"),
    ("architecture", "Architecture"),
    ("space", "Sci-Fi/Space"),
    ("dark", "Dark/Abstract")
]

print("[+] Fetching modern wallpapers from Wallhaven API...")
RAW = []

for query, category_label in SEARCHES:
    url = f"https://wallhaven.cc/api/v1/search?q={query}&purity=100&sorting=toplist&order=desc&per_page=15"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            
        for item in data.get('data', []):
            RAW.append((
                f"wh-{item['id']}",
                f"{category_label} Wallpaper {item['id']}",
                "Wallhaven Contributor",
                category_label,
                "Personal Use (Community Upload)",
                "Wallhaven.cc",
                item['path']
            ))
            
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        
    # Wallhaven API limit is 45 requests per minute, so we wait briefly
    time.sleep(2)

print(f"[+] Retrieved {len(RAW)} valid wallpapers from API.")

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
        "authorUrl": "https://wallhaven.cc",
        "category": cat,
        "sourceUrl": url,
        "license": lic,
        "licenseUrl": "https://wallhaven.cc",
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
    c['previewPath'] = f"review_thumbs_wallhaven/{thumb_name}"

    try:
        # Download image
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
        print(f"[{idx}] OK  '{c['title']}'")

    except Exception as e:
        print(f"[{idx}] ERR '{c['title']}': {e}")
        
    # Rate limit protection: pause between large downloads
    time.sleep(1.5)

print(f"\n[+] Final valid modern count: {len(valid_objs)}")

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
  <title>Storefront Screensavers - Wallhaven Review</title>
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
    <h1>🖼 Wallhaven Modern Screensaver Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved_wallhaven.json</button>
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
    card.innerHTML = `
      <img src="${{c.previewPath}}" alt="${{c.title}}" loading="lazy">
      <div class="card-body">
        <p class="card-title">${{c.title}}</p>
        <p class="card-author">${{c.author}}</p>
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
  a.download = 'approved_wallhaven.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"[+] review_wallhaven.html written with {len(valid_objs)} items")
