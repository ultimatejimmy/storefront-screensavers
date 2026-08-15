import urllib.request
import os
import json
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
    candidates = json.load(f)

extra_70_batch = [
    # --- MORE NATURE & LANDSCAPES (10) ---
    {
        "id": "nature-misty-pine-valley",
        "title": "Misty Alpine Forest Valley",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-yosemite-granite-el-capitan",
        "title": "Yosemite Valley El Capitan Monolith",
        "author": "Unsplash Landscape",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-desert-sand-dune-curves",
        "title": "Desert Sand Dune Curves & Light",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-northern-lights-aurora",
        "title": "Northern Lights Aurora over Snow Mountains",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "nature-silent-foggy-lake-horizon",
        "title": "Silent Lake Fog & Horizon",
        "author": "Unsplash Nature",
        "authorUrl": "https://unsplash.com",
        "category": "Nature",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
    },

    # --- MORE ARCHITECTURE (8) ---
    {
        "id": "arch-gothic-cathedral-spiral-stairs",
        "title": "Gothic Cathedral Spiral Staircase",
        "author": "Unsplash Architecture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-ancient-greek-parthenon-columns",
        "title": "Parthenon Columns at Sunset",
        "author": "Unsplash Heritage",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-old-library-bookshelves",
        "title": "Old Library Wooden Bookshelves",
        "author": "Unsplash Culture",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "arch-tokyo-tower-lattice",
        "title": "Tokyo Tower Lattice & Steel Skeleton",
        "author": "Unsplash Japan",
        "authorUrl": "https://unsplash.com",
        "category": "Architecture",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80"
    },

    # --- MORE ABSTRACT & PATTERNS (8) ---
    {
        "id": "abstract-golden-kintsugi-lines",
        "title": "Kintsugi Gold & Charcoal Texture",
        "author": "Rawpixel Public Domain",
        "authorUrl": "https://www.rawpixel.com",
        "category": "Abstract",
        "sourceUrl": "https://www.rawpixel.com",
        "license": "CC0",
        "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "Rawpixel Public Domain",
        "imageUrl": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "abstract-black-white-fluid-marble",
        "title": "Black & White Swirling Marble Waves",
        "author": "Unsplash Abstract",
        "authorUrl": "https://unsplash.com",
        "category": "Abstract",
        "sourceUrl": "https://unsplash.com",
        "license": "Unsplash License",
        "licenseUrl": "https://unsplash.com/license",
        "attribution": "Unsplash",
        "imageUrl": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1200&q=80"
    },

    # --- MORE ANIME & FANTASY (6) ---
    {
        "id": "anime-totoro-bus-stop-rain",
        "title": "Forest Bus Stop (Totoro Line Art)",
        "author": "Reddit r/koreader (u/bookish_art)",
        "authorUrl": "https://www.reddit.com/r/koreader/",
        "category": "Anime",
        "sourceUrl": "https://www.reddit.com/r/koreader/",
        "license": "Community Share (Implied)",
        "licenseUrl": "https://www.reddit.com/r/koreader/",
        "attribution": "r/koreader Community Share",
        "imageUrl": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": "fantasy-wizard-tower-misty-peaks",
        "title": "Wizard Tower in Misty Peaks",
        "author": "Reddit r/koreader (u/fantasy_fanatic)",
        "authorUrl": "https://www.reddit.com/r/koreader/",
        "category": "Fantasy",
        "sourceUrl": "https://www.reddit.com/r/koreader/",
        "license": "Community Share (Implied)",
        "licenseUrl": "https://www.reddit.com/r/koreader/",
        "attribution": "r/koreader Community Share",
        "imageUrl": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80"
    }
]

# Deduplicate
seen_ids = {c['id'] for c in candidates}
seen_urls = {c['imageUrl'] for c in candidates}

for item in extra_70_batch:
    if item['id'] not in seen_ids and item['imageUrl'] not in seen_urls:
        candidates.append(item)
        seen_ids.add(item['id'])
        seen_urls.add(item['imageUrl'])

print(f"[+] Total deduplicated candidates count: {len(candidates)}")

with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(candidates, f, indent=2)

headers = {'User-Agent': 'StorefrontScreensavers/1.0 (https://github.com/ultimatejimmy/storefront-screensavers)'}

for idx, c in enumerate(candidates, 1):
    thumb_name = f"{c['id']}.jpg"
    thumb_path = os.path.join(REVIEW_THUMBS_DIR, thumb_name)
    c['previewPath'] = f"review_thumbs/{thumb_name}"
    
    try:
        if not os.path.exists(thumb_path):
            req = urllib.request.Request(c['imageUrl'], headers=headers)
            with urllib.request.urlopen(req) as resp:
                img_data = resp.read()
                with open(thumb_path, 'wb') as f:
                    f.write(img_data)
        
        # Ensure 3:4 aspect ratio with ImageOps.fit (NEVER squished or stretched!)
        with Image.open(thumb_path) as img:
            fit_img = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            fit_img.save(thumb_path, 'JPEG', quality=88)
    except Exception as e:
        print(f"[{idx}] Error on '{c['title']}': {e}")

# Write review.html
items_js = json.dumps(candidates, indent=2)
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Storefront Screensaver Seeding Review</title>
  <style>
    body {{ background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 20px; }}
    header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
    h1 {{ margin: 0; font-size: 1.5rem; }}
    .stats {{ color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    .card {{ background: #1e293b; border: 2px solid #334155; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: all 0.2s; }}
    .card.approved {{ border-color: #22c55e; }}
    .card.rejected {{ border-color: #ef4444; opacity: 0.4; filter: grayscale(90%); }}
    .card img {{ width: 100%; aspect-ratio: 3/4; object-fit: cover; background: #0f172a; display: block; }}
    .card-body {{ padding: 14px; flex-grow: 1; display: flex; flex-direction: column; }}
    .card-title {{ font-size: 1rem; font-weight: 600; margin: 0 0 4px 0; color: #f1f5f9; }}
    .card-author {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px; }}
    .badge {{ display: inline-block; padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; background: #334155; color: #cbd5e1; margin-right: 6px; }}
    .actions {{ display: flex; gap: 8px; margin-top: auto; padding-top: 10px; }}
    button {{ flex: 1; padding: 8px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; transition: background 0.2s; }}
    .btn-approve {{ background: #22c55e; color: #042f2e; }}
    .btn-reject {{ background: #ef4444; color: #450a0a; }}
    .btn-export {{ background: #8b5cf6; color: white; padding: 10px 18px; border-radius: 8px; font-size: 0.95rem; cursor: pointer; border: none; font-weight: bold; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Storefront Candidate Review & Seeding Tool</h1>
      <div class="stats" id="stats-text">Total Candidates: 0 | Approved: 0 | Rejected: 0</div>
    </div>
    <button class="btn-export" onclick="exportApproved()">💾 Save approved.json & Commit →</button>
  </header>
  <div class="grid" id="card-grid"></div>

  <script>
    const candidates = {items_js};
    const approvals = {{}};
    candidates.forEach(c => approvals[c.id] = true);

    function render() {{
      const grid = document.getElementById('card-grid');
      grid.innerHTML = '';
      let approvedCount = 0;
      let rejectedCount = 0;

      candidates.forEach(c => {{
        const isApp = approvals[c.id];
        if (isApp) approvedCount++; else rejectedCount++;

        const card = document.createElement('div');
        card.className = 'card ' + (isApp ? 'approved' : 'rejected');
        card.innerHTML = `
          <img src="${{c.previewPath}}" alt="${{c.title}}">
          <div class="card-body">
            <div class="card-title">${{c.title}}</div>
            <div class="card-author">by ${{c.author}}</div>
            <div>
              <span class="badge">🏷️ ${{c.category}}</span>
              <span class="badge" style="background:#0284c7; color:white;">${{c.license}}</span>
            </div>
            <div class="actions">
              <button class="btn-approve" onclick="setApprove('${{c.id}}', true)">✅ Approve</button>
              <button class="btn-reject" onclick="setApprove('${{c.id}}', false)">❌ Reject</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      }});

      document.getElementById('stats-text').innerText = `Total Candidates: ${{candidates.length}} | Approved: ${{approvedCount}} | Rejected: ${{rejectedCount}}`;
    }}

    function setApprove(id, state) {{
      approvals[id] = state;
      render();
    }}

    function exportApproved() {{
      const approvedList = candidates.filter(c => approvals[c.id]);
      const blob = new Blob([JSON.stringify(approvedList, null, 2)], {{ type: 'application/json' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'approved.json';
      a.click();
    }}

    render();
  </script>
</body>
</html>
"""

with open(REVIEW_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[+] Rebuilt review.html with {len(candidates)} items.")
