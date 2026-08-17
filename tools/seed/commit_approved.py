import os
import json
import requests
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

APPROVED_FILE = os.path.join(BASE_DIR, 'approved.json')
CANDIDATES_FILE = os.path.join(BASE_DIR, 'candidates.json')

IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

# Prefer approved.json if it exists, otherwise fall back to candidates.json
target_file = APPROVED_FILE if os.path.exists(APPROVED_FILE) else CANDIDATES_FILE
print(f"Reading approved items from: {target_file}")

with open(target_file, 'r', encoding='utf-8') as f:
    approved_items = json.load(f)

print(f"Processing {len(approved_items)} screensavers for catalog commit...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

raw_base = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/"

with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

credits_list = []

for idx, item in enumerate(approved_items):
    item_id = item['id']
    full_rel_path = f"images/{item_id}.jpg"
    thumb_rel_path = f"images/thumbnails/{item_id}.jpg"
    
    full_abs_path = os.path.join(REPO_ROOT, full_rel_path)
    thumb_abs_path = os.path.join(REPO_ROOT, thumb_rel_path)

    print(f"[{idx+1}/{len(approved_items)}] Downloading full-res '{item['title']}'...")

    try:
        r = requests.get(item['imageUrl'], headers=headers, timeout=30)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Master 3:4 e-reader resolution (1860 x 2480)
            master_img = ImageOps.fit(img, (1860, 2480), Image.Resampling.LANCZOS)
            master_img.save(full_abs_path, 'JPEG', quality=92)

            # Thumbnail 3:4 resolution (600 x 800)
            thumb_img = ImageOps.fit(img, (600, 800), Image.Resampling.LANCZOS)
            thumb_img.save(thumb_abs_path, 'JPEG', quality=85)

            new_entry = {
                "id": item_id,
                "title": item['title'],
                "author": item['author'],
                "authorUrl": item.get('authorUrl', ''),
                "category": item['category'],
                "compatibility": ["Kindle", "Kobo", "Boox", "PocketBook"],
                "license": item.get('license', 'CC0'),
                "licenseUrl": item.get('licenseUrl', ''),
                "sourceUrl": item.get('sourceUrl', ''),
                "attribution": item.get('attribution', ''),
                "thumbnailUrl": raw_base + thumb_rel_path,
                "fullUrl": raw_base + full_rel_path,
                "downloads": 0,
                "likes": 1
            }

            # Update if existing, or append
            updated = False
            for c_idx, c_item in enumerate(catalog):
                if c_item['id'] == item_id:
                    catalog[c_idx] = new_entry
                    updated = True
                    break
            if not updated:
                catalog.append(new_entry)

            credits_list.append({
                "title": item['title'],
                "author": item['author'],
                "category": item['category'],
                "license": item.get('license', 'CC0'),
                "sourceUrl": item.get('sourceUrl', ''),
                "attribution": item.get('attribution', '')
            })

            print(f"  -> Successfully processed and saved {item_id}")
        else:
            print(f"  -> HTTP Error {r.status_code} downloading full image.")
    except Exception as e:
        print(f"  -> Error processing {item_id}: {e}")

# Save updated screensavers.json
with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2)

print(f"\n[+] Updated screensavers.json (Total items now: {len(catalog)})")

# Generate CREDITS.md
credits_md_lines = [
    "# External Sourcing & Attribution Credits",
    "",
    "All open access, Public Domain, CC0, and community-shared screensavers in this catalog are credited below in accordance with their respective licenses and attribution requirements.",
    "",
    "| Title | Creator / Artist | Category | License | Source & Attribution |",
    "|---|---|---|---|---|"
]

for c in credits_list:
    src_link = f"[{c['attribution'] or 'Link'}]({c['sourceUrl']})" if c['sourceUrl'] else (c['attribution'] or 'N/A')
    credits_md_lines.append(f"| {c['title']} | {c['author']} | {c['category']} | {c['license']} | {src_link} |")

credits_md_lines.extend([
    "",
    "---",
    "",
    "## License Definitions",
    "",
    "- **CC0 (Creative Commons Zero)**: Dedicated to the public domain worldwide with no legal attribution requirement.",
    "- **Public Domain**: Works whose copyright has expired (pre-1928 engravings/lithographs) or US Government works.",
    "- **Unsplash License / Pexels License**: Free for commercial and non-commercial use.",
    "- **Community Share (Implied)**: Shared publicly by creators on r/koreader with permission for community use.",
    ""
])

with open(CREDITS_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(credits_md_lines))

print(f"[+] Generated CREDITS.md with {len(credits_list)} entry credits.")
