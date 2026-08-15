# -*- coding: utf-8 -*-
"""
build_readerbackdrop_seed_batch.py

Fetches transparent KOReader screensavers from ReaderBackdrop.com.
Extracts utfs.io (UploadThing) URLs from the site's HTML, downloads them,
checks for actual alpha transparency, and saves them as PNGs.
"""

import urllib.request
import os
import json
import hashlib
import time
from html.parser import HTMLParser
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs_transparent')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates_transparent.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review_transparent.html')

import shutil
if os.path.exists(REVIEW_THUMBS_DIR):
    shutil.rmtree(REVIEW_THUMBS_DIR, ignore_errors=True)
os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 StorefrontScreensavers/1.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

class RBParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.utfs_images = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            for attr in attrs:
                if attr[0] == 'src' and 'utfs.io' in attr[1]:
                    self.utfs_images.append(attr[1])

print("[+] Fetching ReaderBackdrop HTML...")

try:
    req = urllib.request.Request('https://readerbackdrop.com/', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8')
        
    parser = RBParser()
    parser.feed(html)
    utfs_urls = list(set(parser.utfs_images)) # Deduplicate URLs
    
except Exception as e:
    print(f"Error fetching HTML: {e}")
    utfs_urls = []

print(f"[+] Found {len(utfs_urls)} UploadThing images on the page.")

RAW = []
for i, url in enumerate(utfs_urls):
    # readerbackdrop images don't have explicit titles in the HTML usually,
    # so we give them a generic but nice name.
    RAW.append((
        f"rb-{hashlib.md5(url.encode()).hexdigest()[:8]}",
        f"Transparent KOReader Overlay {i+1}",
        "ReaderBackdrop Community",
        "Transparent Overlay",
        "Community Upload",
        "ReaderBackdrop.com",
        url
    ))

print(f"[+] Retrieved {len(RAW)} valid transparent wallpaper URLs.")

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
        "authorUrl": "https://readerbackdrop.com/",
        "category": cat,
        "sourceUrl": url,
        "license": lic,
        "licenseUrl": "https://readerbackdrop.com/",
        "attribution": attr,
        "imageUrl": url,
    })

print(f"[+] Deduplicated candidate count: {len(cand_objs)}")

# ---------------------------------------------------------------------------
# DOWNLOAD & PROCESS THUMBNAILS
# ---------------------------------------------------------------------------
valid_objs = []
seen_hashes = {}

def has_transparency(img):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        extrema = img.getextrema()
        if img.mode == 'RGBA':
            if extrema[3][0] < 255:
                return True
        elif img.mode == 'LA':
            if extrema[1][0] < 255:
                return True
    return False

for idx, c in enumerate(cand_objs, 1):
    # MUST SAVE AS PNG to preserve transparency
    thumb_name = f"{c['id']}.png"
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    c['previewPath'] = f"review_thumbs_transparent/{thumb_name}"

    try:
        req = urllib.request.Request(c['imageUrl'], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            img_data = resp.read()
            
        with open(thumb_path, 'wb') as f:
            f.write(img_data)

        # Check transparency before keeping
        with Image.open(thumb_path) as img:
            is_transparent = has_transparency(img)
            
            if not is_transparent:
                print(f"[{idx}] SKIP '{c['title']}' — Not actually transparent")
                os.remove(thumb_path)
                continue
                
            # Resize while preserving aspect ratio and alpha channel
            img = img.convert("RGBA")
            img.thumbnail((450, 600), Image.Resampling.LANCZOS)
            
            # Create a new blank 3:4 transparent image
            new_img = Image.new("RGBA", (450, 600), (0, 0, 0, 0))
            
            # Paste the resized image into the center
            x = (450 - img.width) // 2
            y = (600 - img.height) // 2
            new_img.paste(img, (x, y), img)
            
            new_img.save(thumb_path, 'PNG')

        with open(thumb_path, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()

        if h in seen_hashes:
            print(f"[{idx}] SKIP '{c['title']}' — duplicate hash")
            os.remove(thumb_path)
            continue

        seen_hashes[h] = c['title']
        valid_objs.append(c)
        print(f"[{idx}] OK  '{c['title']}' (Transparent PNG)")

    except Exception as e:
        print(f"[{idx}] ERR '{c['title']}': {e}")
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
    time.sleep(0.5)

print(f"\n[+] Final valid transparent count: {len(valid_objs)}")

# ---------------------------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------------------------
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(valid_objs, f, indent=2, ensure_ascii=False)

items_js = json.dumps(valid_objs, indent=2, ensure_ascii=False)

# HTML adds a checkerboard background so the user can easily see the transparency!
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensavers - Transparent Overlay Review</title>
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
    .card img {{ 
        width: 100%; 
        aspect-ratio: 3/4; 
        object-fit: contain; 
        display: block; 
        /* Checkerboard background to show transparency! */
        background-color: #e5e5f7;
        background-image:  repeating-linear-gradient(45deg, #c4c4cd 25%, transparent 25%, transparent 75%, #c4c4cd 75%, #c4c4cd), repeating-linear-gradient(45deg, #c4c4cd 25%, #e5e5f7 25%, #e5e5f7 75%, #c4c4cd 75%, #c4c4cd);
        background-position: 0 0, 10px 10px;
        background-size: 20px 20px;
    }}
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
    <h1>🖼 Transparent Overlay Screensaver Review</h1>
    <div class="stats" id="stats">Loading…</div>
  </div>
  <button class="btn-export" onclick="exportApproved()">💾 Export approved_transparent.json</button>
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
  a.download = 'approved_transparent.json';
  a.click();
}}

render();
</script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"[+] review_transparent.html written with {len(valid_objs)} items")
