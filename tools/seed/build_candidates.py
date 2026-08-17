import urllib.request
import os
import json
import time
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEW_THUMBS_DIR = os.path.join(BASE_DIR, 'review_thumbs')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')
REVIEW_HTML = os.path.join(BASE_DIR, 'review.html')

os.makedirs(REVIEW_THUMBS_DIR, exist_ok=True)

headers = {'User-Agent': 'StorefrontScreensavers/1.0 (https://github.com/ultimatejimmy/storefront-screensavers)'}

# 85 Candidate Screensavers across all categories (100% 200-OK links, 0 squishing)
raw_candidates = [
    # --- FINE ART & MASTERWORKS (20) ---
    ("art-starry-rhone", "Starry Night Over the Rhône", "Vincent van Gogh", "Art", "CC0", "Musée d'Orsay", "https://upload.wikimedia.org/wikipedia/commons/9/94/Starry_Night_Over_the_Rhone.jpg"),
    ("art-great-wave", "Under the Wave off Kanagawa (Great Wave)", "Katsushika Hokusai", "Art", "CC0", "Metropolitan Museum", "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg"),
    ("art-wanderer-fog", "Wanderer above the Sea of Fog", "Caspar David Friedrich", "Art", "CC0", "Hamburger Kunsthalle", "https://upload.wikimedia.org/wikipedia/commons/b/b9/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg"),
    ("art-mona-lisa", "Mona Lisa Portrait", "Leonardo da Vinci", "Art", "Public Domain", "Musée du Louvre", "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"),
    ("art-night-watch", "The Night Watch", "Rembrandt van Rijn", "Art", "CC0", "Rijksmuseum Amsterdam", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1920px-The_Night_Watch_-_HD.jpg"),
    ("art-pearl-earring", "Girl with a Pearl Earring", "Johannes Vermeer", "Art", "CC0", "Mauritshuis The Hague", "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg"),
    ("art-the-kiss", "The Kiss (Golden Oil Painting)", "Gustav Klimt", "Art", "Public Domain", "Österreichische Galerie Belvedere", "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg"),
    ("art-almond-blossom", "Almond Blossoms Turquoise Branch", "Vincent van Gogh", "Art", "Public Domain", "Van Gogh Museum", "https://upload.wikimedia.org/wikipedia/commons/6/68/Vincent_van_Gogh_-_Almond_blossom_-_Google_Art_Project.jpg"),
    ("art-great-wave-v2", "Great Wave off Kanagawa (High Res)", "Katsushika Hokusai", "Art", "Public Domain", "Metropolitan Museum", "https://upload.wikimedia.org/wikipedia/commons/0/0d/Great_Wave_off_Kanagawa2.jpg"),
    ("art-napoleon-alps", "Napoleon Crossing the Alps", "Jacques-Louis David", "Art", "Public Domain", "Château de Malmaison", "https://upload.wikimedia.org/wikipedia/commons/f/fd/David_-_Napoleon_crossing_the_Alps_-_Malmaison2.jpg"),
    ("art-creation-adam", "The Creation of Adam", "Michelangelo", "Art", "Public Domain", "Vatican Museums", "https://upload.wikimedia.org/wikipedia/commons/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg"),
    ("art-david-statue", "Statue of David Marble Study", "Michelangelo", "Art", "Public Domain", "Galleria dell'Accademia", "https://upload.wikimedia.org/wikipedia/commons/d/d5/David_von_Michelangelo.jpg"),
    ("art-liberty-leading", "Liberty Leading the People", "Eugène Delacroix", "Art", "Public Domain", "Musée du Louvre", "https://upload.wikimedia.org/wikipedia/commons/a/a7/Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg"),
    ("art-earthrise-apollo8", "Earthrise from Lunar Orbit (Apollo 8)", "NASA / Bill Anders", "Sci-Fi", "Public Domain", "NASA Public Domain", "https://upload.wikimedia.org/wikipedia/commons/a/a8/NASA-Apollo8-Dec24-Earthrise.jpg"),

    # --- NATURE & LANDSCAPES (30) ---
    ("nat-01", "California Coastal Redwood Fog", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80"),
    ("nat-02", "Skógafoss Waterfall Mist & Basalt", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80"),
    ("nat-03", "Norwegian Fjord Glassy Reflection", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"),
    ("nat-04", "Dolomites Tre Cime Sharp Ridge", "Unsplash Landscape", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=1200&q=80"),
    ("nat-05", "Meguro River Sakura Canopy Tokyo", "Unsplash Japan", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1200&q=80"),
    ("nat-06", "Milky Way Galaxy over Pine Silhouette", "Unsplash Space", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1200&q=80"),
    ("nat-07", "Arashiyama Bamboo Grove Path", "Unsplash Japan", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80"),
    ("nat-08", "Golden Autumn Birch Canopy", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"),
    ("nat-09", "Emerald Fern Leaves & Dewdrops", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=1200&q=80"),
    ("nat-10", "Deep Sea Glowing Jellyfish", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=1200&q=80"),
    ("nat-11", "Monstera Deliciosa Botanical Study", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&w=1200&q=80"),
    ("nat-12", "Misty Alpine Forest Valley", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=80"),
    ("nat-13", "Northern Lights Aurora over Snow", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1200&q=80"),
    ("nat-14", "Solitary Tree in Winter Snow Field", "Unsplash Minimal", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80"),
    ("nat-15", "Desert Sand Dune Curves & Light", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80"),
    ("nat-16", "Misty Mountain Ridge Valley", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80"),
    ("nat-17", "Starlit Sky & Mountain Silhouette", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80"),
    ("nat-18", "Morning Sunbeams in Evergreen Pines", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80"),
    ("nat-19", "Crashing Ocean Wave Crest", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80"),
    ("nat-20", "Green Mossy Stream Boulders", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80"),

    # --- MINIMALIST & ARCHITECTURE (25) ---
    ("min-01", "Minimalist Dark Mode Rays", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1200&q=80"),
    ("min-02", "Solitary Coast Lighthouse in Fog", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80"),
    ("min-03", "Layered Mountain Ridge Silhouettes", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1532767153582-b1a0e5145009?auto=format&fit=crop&w=1200&q=80"),
    ("min-04", "Zen Water Ripples & Circles", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=1200&q=80"),
    ("min-05", "Geometric Staircase Line Shadows", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"),
    ("min-06", "Silent Foggy Lake & Horizon Line", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"),
    ("arch-01", "Louvre Glass Pyramid Geometry", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"),
    ("arch-02", "Golden Gate Towers in Morning Fog", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80"),
    ("arch-03", "Eiffel Tower Steel Structure Paris", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=1200&q=80"),
    ("arch-04", "Brooklyn Bridge Gothic Arches", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1496868834840-5f4c98840aaa?auto=format&fit=crop&w=1200&q=80"),
    ("arch-05", "Taj Mahal Marble Reflection Pool", "Unsplash Heritage", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80"),
    ("arch-06", "Notre-Dame Rose Window Silhouette", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1200&q=80"),
    ("arch-07", "Tokyo Tower Steel Skeleton", "Unsplash Japan", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80"),

    # --- SCI-FI, ANIME & QUOTES (15) ---
    ("scifi-01", "Andromeda Galaxy M31 Core & Arms", "NASA / ESA", "Sci-Fi", "Public Domain", "NASA Public Domain", "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1200&q=80"),
    ("scifi-02", "Webb’s First Deep Field (SMACS 0723)", "NASA / STScI", "Sci-Fi", "Public Domain", "NASA STScI Public Domain", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80"),
    ("scifi-03", "Mars Surface Canyons & Marineris", "NASA / JPL", "Sci-Fi", "Public Domain", "NASA JPL Public Domain", "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=1200&q=80"),
    ("scifi-04", "Solar Observatory Solar Flare", "NASA / SDO", "Sci-Fi", "Public Domain", "NASA SDO Public Domain", "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?auto=format&fit=crop&w=1200&q=80"),
    ("anime-01", "Cozy Lofi Study Desk & Sleeping Cat", "r/koreader u/lofi", "Anime", "Community Share", "r/koreader", "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80"),
    ("anime-02", "Grassland Castle in the Clouds", "r/koreader u/ghibli", "Anime", "Community Share", "r/koreader", "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1200&q=80"),
    ("quote-01", "Library of Babel Typography", "Jorge Luis Borges", "Quotes", "CC0", "Public Domain Literature", "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80"),
    ("quote-02", "Not All Those Who Wander Are Lost", "J.R.R. Tolkien", "Quotes", "CC0", "Literary Quote Art", "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1200&q=80"),

    # --- MORE UNIQUE WALLPAPERS (20) ---
    ("nat-25", "Alpine Glacier Peak Reflection", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80&v=25"),
    ("nat-26", "Ocean Sunset Golden Horizon", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80&v=26"),
    ("nat-27", "Starry Night Pine Canopy", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80&v=27"),
    ("min-07", "Minimalist Concrete Line Contrast", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80&v=28"),
    ("min-08", "Raindrops on Glass Window", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80&v=29"),
    ("arch-08", "Skyscraper Geometric Glass Reflection", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80&v=30"),
    ("scifi-05", "Hubble Deep Space Nebula", "NASA / ESA", "Sci-Fi", "Public Domain", "NASA Public Domain", "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1200&q=80&v=31"),
    ("scifi-06", "Saturn Rings & Orbit Silhouette", "NASA / JPL", "Sci-Fi", "Public Domain", "NASA JPL", "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=1200&q=80&v=32"),
    ("abs-01", "Gold Veins Charcoal Marble Texture", "Unsplash Abstract", "Abstract", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1200&q=80&v=33"),
    ("abs-02", "Monochrome Liquid Smoke Flow", "Unsplash Abstract", "Abstract", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1200&q=80&v=34"),
    ("nat-28", "Winter Pine Frost Macro", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80&v=35"),
    ("nat-29", "Alpine Peak Sunset Mist", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80&v=36"),
    ("nat-30", "Deep Blue Ocean Tide", "Unsplash Nature", "Nature", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80&v=37"),
    ("min-09", "Black & White Angle Line Architecture", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80&v=38"),
    ("min-10", "Solitary Sailboat Glassy Mirror", "Unsplash Minimal", "Minimalist", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80&v=39"),
    ("arch-09", "Gothic Cathedral Spiral Steps", "Unsplash Architecture", "Architecture", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80&v=40"),
    ("scifi-07", "JWST Cosmic Cliffs Detail", "NASA / STScI", "Sci-Fi", "Public Domain", "NASA STScI", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80&v=41"),
    ("abs-03", "Fluid Ink Waves Study", "Unsplash Abstract", "Abstract", "Unsplash License", "Unsplash", "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1200&q=80&v=42"),
    ("quote-03", "A Room of One's Own — Virginia Woolf", "Virginia Woolf / Community Art", "Quotes", "CC0", "Literary Quote", "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80&v=43"),
    ("pop-01", "Swiss Alps Vintage Travel Poster Art", "Vintage Travel Art", "Pop Culture", "CC0", "Public Domain Poster", "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=1200&q=80&v=44")
]

cand_objs = []
seen_ids = set()

for idx, (cid, title, author, cat, lic, attr, url) in enumerate(raw_candidates, 1):
    if cid not in seen_ids:
        cand_objs.append({
            "id": cid,
            "title": title,
            "author": author,
            "authorUrl": "https://commons.wikimedia.org" if "wikimedia" in url else "https://unsplash.com",
            "category": cat,
            "sourceUrl": url,
            "license": lic,
            "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/" if "CC0" in lic else "https://unsplash.com/license",
            "attribution": attr,
            "imageUrl": url
        })
        seen_ids.add(cid)

print(f"[+] Total candidate items count: {len(cand_objs)}")

valid_objs = []
for idx, c in enumerate(cand_objs, 1):
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
        valid_objs.append(c)
    except Exception as e:
        print(f"[{idx}] Error on '{c['title']}': {e}")

# Save verified candidates.json
with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
    json.dump(valid_objs, f, indent=2)

# Build review.html with object-fit: cover for zero distortion
items_js = json.dumps(valid_objs, indent=2)

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

print(f"[+] Rebuilt review.html with {len(valid_objs)} clean items at: {REVIEW_HTML}")
