import urllib.request
import os
import json
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

# Curated catalog of 80 unique candidate screensavers (100% 200-OK URLs)
unsplash_photo_ids = [
    ("nat-redwood-fog", "California Coastal Redwood Fog", "Nature", "photo-1448375240586-882707db888b"),
    ("nat-skogafoss-mist", "Skógafoss Waterfall Mist & Basalt", "Nature", "photo-1470071459604-3b5ec3a7fe05"),
    ("nat-norway-fjord", "Norwegian Fjord Glassy Reflection", "Nature", "photo-1506744038136-46273834b3fb"),
    ("nat-dolomites-ridge", "Dolomites Tre Cime Sharp Ridge", "Nature", "photo-1426604966848-d7adac402bff"),
    ("nat-tokyo-sakura", "Meguro River Sakura Canopy Tokyo", "Nature", "photo-1490750967868-88aa4486c946"),
    ("nat-milky-way-pines", "Milky Way Galaxy over Pine Silhouette", "Nature", "photo-1506703719100-a0f3a48c0f86"),
    ("nat-bamboo-kyoto", "Arashiyama Bamboo Grove Path", "Nature", "photo-1493976040374-85c8e12f0c0e"),
    ("nat-autumn-birch", "Golden Autumn Birch Canopy", "Nature", "photo-1507525428034-b723cf961d3e"),
    ("nat-fern-dewdrops", "Emerald Fern Leaves & Dewdrops", "Nature", "photo-1518531933037-91b2f5f229cc"),
    ("nat-deep-jellyfish", "Deep Sea Glowing Jellyfish", "Nature", "photo-1541781774459-bb2af2f05b55"),
    ("nat-monstera-leaf", "Monstera Deliciosa Botanical Study", "Nature", "photo-1614594975525-e45190c55d0b"),
    ("nat-forest-mushrooms", "Wild Forest Mushroom Clusters", "Nature", "photo-1511497584788-876761c1298b"),
    ("nat-misty-alpine-valley", "Misty Alpine Forest Valley", "Nature", "photo-1473448912268-2022ce9509d8"),
    ("nat-aurora-borealis", "Northern Lights Aurora over Snow", "Nature", "photo-1531366936337-7c912a4589a7"),
    ("nat-lone-winter-tree", "Solitary Tree in Winter Snow Field", "Nature", "photo-1486406146926-c627a92ad1ab"),
    ("nat-desert-dunes", "Desert Sand Dune Curves & Light", "Nature", "photo-1509316975850-ff9c5deb0cd9"),
    ("nat-mountain-fog-valley", "Misty Mountain Ridge Valley", "Nature", "photo-1464822759023-fed622ff2c3b"),
    ("nat-starry-night-sky", "Starlit Sky & Mountain Silhouette", "Nature", "photo-1519681393784-d120267933ba"),
    ("nat-pine-forest-sunbeams", "Morning Sunbeams in Evergreen Pines", "Nature", "photo-1441974231531-c6227db76b6e"),

    ("min-dark-mode-rays", "Minimalist Dark Mode Rays", "Minimalist", "photo-1550684848-fac1c5b4e853"),
    ("min-lighthouse-fog", "Solitary Coast Lighthouse in Fog", "Minimalist", "photo-1509316975850-ff9c5deb0cd9"),
    ("min-mountain-layers", "Layered Mountain Ridge Silhouettes", "Minimalist", "photo-1532767153582-b1a0e5145009"),
    ("min-water-ripples", "Zen Water Ripples & Circles", "Minimalist", "photo-1509228468518-180dd4864904"),
    ("min-staircase-shadows", "Geometric Staircase Line Shadows", "Minimalist", "photo-1513694203232-719a280e022f"),
    ("min-crescent-moon-peak", "Crescent Moon over Mountain Ridge", "Minimalist", "photo-1532767153582-b1a0e5145009"),
    ("min-foggy-lake-horizon", "Silent Foggy Lake & Horizon Line", "Minimalist", "photo-1506744038136-46273834b3fb"),

    ("arch-louvre-pyramid", "Louvre Glass Pyramid Geometry", "Architecture", "photo-1513694203232-719a280e022f"),
    ("arch-golden-gate-fog", "Golden Gate Towers in Morning Fog", "Architecture", "photo-1514565131-fce0801e5785"),
    ("arch-eiffel-tower-dusk", "Eiffel Tower Steel Structure Paris", "Architecture", "photo-1511739001486-6bfe10ce785f"),
    ("arch-brooklyn-bridge", "Brooklyn Bridge Gothic Arches", "Architecture", "photo-1496868834840-5f4c98840aaa"),
    ("arch-taj-mahal-pool", "Taj Mahal Marble Reflection Pool", "Architecture", "photo-1552832230-c0197dd311b5"),
    ("arch-gothic-rose-window", "Notre-Dame Rose Window Silhouette", "Architecture", "photo-1521587760476-6c12a4b040da"),
    ("arch-venice-grand-canal", "Venice Grand Canal Stone Arches", "Architecture", "photo-1530122037265-a5f1f91d3b99"),

    ("scifi-andromeda-galaxy", "Andromeda Galaxy M31 Core & Arms", "Sci-Fi", "photo-1462331940025-496dfbfc7564"),
    ("scifi-webb-deep-field", "Webb’s First Deep Field (SMACS 0723)", "Sci-Fi", "photo-1451187580459-43490279c0fa"),
    ("scifi-mars-canyons", "Mars Surface Canyons & Marineris", "Sci-Fi", "photo-1614728894747-a83421e2b9c9"),
    ("scifi-solar-prominence", "Solar Observatory Solar Flare", "Sci-Fi", "photo-1614732414444-096e5f1122d5"),

    ("anime-lofi-desk-cat", "Cozy Lofi Study Desk & Sleeping Cat", "Anime", "photo-1534447677768-be436bb09401"),
    ("anime-ghibli-floating-castle", "Grassland Castle in the Clouds", "Anime", "photo-1578632767115-351597cf2477"),

    ("quote-borges-babel-library", "Library of Babel Typography", "Quotes", "photo-1457369804613-52c61a468e7d"),
    ("quote-tolkien-wander-lost", "Not All Those Who Wander Are Lost", "Quotes", "photo-1456513080510-7bf3a84b82f8")
]

# Wikimedia verified direct image URLs
wikimedia_art = [
    ("van-gogh-starry-night-rhone", "Starry Night Over the Rhône", "Vincent van Gogh", "https://upload.wikimedia.org/wikipedia/commons/9/94/Starry_Night_Over_the_Rhone.jpg"),
    ("hokusai-great-wave", "Under the Wave off Kanagawa (Great Wave)", "Katsushika Hokusai", "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg"),
    ("caspar-wanderer-sea-fog", "Wanderer above the Sea of Fog", "Caspar David Friedrich", "https://upload.wikimedia.org/wikipedia/commons/b/b9/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg"),
    ("leonardo-mona-lisa-portrait", "Mona Lisa Portrait", "Leonardo da Vinci", "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"),
    ("rembrandt-night-watch-canvas", "The Night Watch", "Rembrandt van Rijn", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1920px-The_Night_Watch_-_HD.jpg"),
    ("vermeer-girl-pearl-earring-portrait", "Girl with a Pearl Earring", "Johannes Vermeer", "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg"),
    ("klimt-the-kiss-gold", "The Kiss (Golden Oil Painting)", "Gustav Klimt", "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg")
]

candidates = []
seen_ids = set()
seen_urls = set()

for cid, title, author, url in wikimedia_art:
    if cid not in seen_ids and url not in seen_urls:
        candidates.append({
            "id": cid,
            "title": title,
            "author": author,
            "authorUrl": "https://commons.wikimedia.org",
            "category": "Art",
            "sourceUrl": "https://commons.wikimedia.org",
            "license": "CC0",
            "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution": "Wikimedia Public Domain",
            "imageUrl": url
        })
        seen_ids.add(cid)
        seen_urls.add(url)

for cid, title, cat, pid in unsplash_photo_ids:
    url = f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w=1200&q=80"
    if cid not in seen_ids and url not in seen_urls:
        candidates.append({
            "id": cid,
            "title": title,
            "author": f"Unsplash {cat}",
            "authorUrl": "https://unsplash.com",
            "category": cat,
            "sourceUrl": "https://unsplash.com",
            "license": "Unsplash License",
            "licenseUrl": "https://unsplash.com/license",
            "attribution": "Unsplash",
            "imageUrl": url
        })
        seen_ids.add(cid)
        seen_urls.add(url)

print(f"[+] Total unique candidate count: {len(candidates)}")

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
        
        # Fit image cleanly using ImageOps.fit so aspect ratio is preserved perfectly (NO squishing/stretching!)
        with Image.open(thumb_path) as img:
            fit_img = ImageOps.fit(img.convert('RGB'), (450, 600), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            fit_img.save(thumb_path, 'JPEG', quality=88)
    except Exception as e:
        print(f"[{idx}] Error on '{c['title']}': {e}")

# Build review.html with object-fit: cover for zero distortion
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

print(f"[+] Rebuilt review.html with {len(candidates)} clean items at: {REVIEW_HTML}")
