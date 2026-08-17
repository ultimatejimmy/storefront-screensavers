import os
import json
import glob
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')

with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"[+] Fast scanning {len(catalog)} screensavers for transparency & edge-to-edge scaling...")

transparent_count = 0

for idx, item in enumerate(catalog, 1):
    item_id = item['id']
    
    thumb_path = None
    for ext in ['.png', '.jpg']:
        p = os.path.join(THUMBS_DIR, f"{item_id}{ext}")
        if os.path.exists(p):
            thumb_path = p
            break

    full_path = None
    for ext in ['.png', '.jpg']:
        p = os.path.join(IMAGES_DIR, f"{item_id}{ext}")
        if os.path.exists(p):
            full_path = p
            break

    if not thumb_path or not full_path:
        continue

    try:
        # Inspect thumbnail for transparency (fast 600x800 image)
        with Image.open(thumb_path) as timg:
            timg = timg.convert("RGBA")
            a_channel = timg.split()[3]
            min_a, max_a = a_channel.getextrema()
            
            # Check if actual transparent pixels exist
            is_transparent = min_a < 220
            
            if is_transparent:
                transparent_count += 1
                # Enforce single category: Transparent Overlay
                item['category'] = "Transparent Overlay"
                
                clean_t = item['title'].encode('ascii', 'replace').decode('ascii')
                print(f"[{idx}/{len(catalog)}] Transparent Overlay: '{clean_t}' ({item_id})")

                # Crop empty outer transparent padding
                tbbox = timg.getbbox()
                tcropped = timg.crop(tbbox) if tbbox else timg

                # Scale artwork to FILL 3:4 canvas (600x800) edge-to-edge
                thumb_canvas = ImageOps.fit(tcropped, (600, 800), Image.Resampling.LANCZOS)
                
                if thumb_path.endswith('.jpg'):
                    os.remove(thumb_path)
                    thumb_path = os.path.join(THUMBS_DIR, f"{item_id}.png")
                    item['thumbnailUrl'] = f"https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/images/thumbnails/{item_id}.png"

                thumb_canvas.save(thumb_path, "PNG")

                # Also process full image (1860x2480)
                if os.path.exists(full_path):
                    with Image.open(full_path) as fimg:
                        fimg = fimg.convert("RGBA")
                        fbbox = fimg.getbbox()
                        fcropped = fimg.crop(fbbox) if fbbox else fimg
                        full_canvas = ImageOps.fit(fcropped, (1860, 2480), Image.Resampling.LANCZOS)
                        
                        if full_path.endswith('.jpg'):
                            os.remove(full_path)
                            full_path = os.path.join(IMAGES_DIR, f"{item_id}.png")
                            item['fullUrl'] = f"https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/images/{item_id}.png"

                        full_canvas.save(full_path, "PNG")

    except Exception as e:
        print(f"Error on {item_id}: {e}")

# Save updated screensavers.json
with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"\n[+] Updated screensavers.json with {transparent_count} Transparent Overlays.")

# Re-generate CREDITS.md
credits_md_lines = [
    "# External Sourcing & Attribution Credits",
    "",
    "All open access, Public Domain, CC0, and community-shared screensavers in this catalog are credited below in accordance with their respective licenses and attribution requirements.",
    "",
    "| Title | Creator / Artist | Category | License | Source & Attribution |",
    "|---|---|---|---|---|"
]

for item in catalog:
    src_link = f"[{item.get('attribution') or 'Link'}]({item.get('sourceUrl')})" if item.get('sourceUrl') else (item.get('attribution') or 'N/A')
    credits_md_lines.append(f"| {item['title']} | {item['author']} | {item['category']} | {item['license']} | {src_link} |")

credits_md_lines.extend([
    "",
    "---",
    "",
    "## License Definitions",
    "",
    "- **CC0 (Creative Commons Zero)**: Dedicated to the public domain worldwide with no legal attribution requirement.",
    "- **Public Domain**: Works whose copyright has expired (pre-1928 engravings/lithographs) or US Government works.",
    "- **Unsplash License / Pexels License**: Free for commercial and non-commercial use.",
    "- **Wallhaven / Personal Use**: Shared publicly by creators on Wallhaven/ReaderBackdrop with permission for community e-reader use.",
    ""
])

with open(CREDITS_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(credits_md_lines))

print(f"[+] Re-generated CREDITS.md cleanly!")
