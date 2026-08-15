import os
import json
import glob
import urllib.request
from PIL import Image, ImageOps
from io import BytesIO

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)
os.makedirs(os.path.join(THUMBS_DIR, 'plugin'), exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 StorefrontScreensavers/1.0'
}

raw_base = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/"

def save_catalog_and_credits(catalog):
    # Save updated screensavers.json
    with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Generate CREDITS.md
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

def commit_all():
    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    existing_ids = set(item['id'] for item in catalog)
    print(f"[+] Loaded existing catalog with {len(catalog)} items.")

    approved_files = glob.glob(os.path.join(BASE_DIR, 'approved_*.json'))
    print(f"[+] Found {len(approved_files)} approved JSON files.")

    to_commit = []
    seen_commit_ids = set()

    for fpath in approved_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            items = json.load(f)
            for item in items:
                item_id = item['id']
                if item_id not in existing_ids and item_id not in seen_commit_ids:
                    to_commit.append(item)
                    seen_commit_ids.add(item_id)

    print(f"[+] Total new unique items to commit: {len(to_commit)}")

    for idx, item in enumerate(to_commit, 1):
        item_id = item['id']
        is_png = item.get('category') == 'Transparent' or item_id.startswith('rb-') or item['imageUrl'].lower().endswith('.png')
        ext = '.png' if is_png else '.jpg'
        
        full_rel_path = f"images/{item_id}{ext}"
        thumb_web_rel = f"images/thumbnails/{item_id}{ext}"
        thumb_plugin_rel = f"images/thumbnails/plugin/{item_id}.png" if is_png else None
        
        full_abs_path = os.path.join(REPO_ROOT, full_rel_path)
        thumb_web_abs = os.path.join(REPO_ROOT, thumb_web_rel)
        thumb_plugin_abs = os.path.join(REPO_ROOT, thumb_plugin_rel) if thumb_plugin_rel else None

        clean_t = item['title'].encode('ascii', 'replace').decode('ascii')
        print(f"[{idx}/{len(to_commit)}] Processing '{clean_t}'...")

        img_data = None
        
        # Try local preview file first for maximum speed
        if 'previewPath' in item:
            prev_path = os.path.join(BASE_DIR, item['previewPath'])
            if os.path.exists(prev_path):
                try:
                    with open(prev_path, 'rb') as pf:
                        img_data = pf.read()
                except Exception as e:
                    print(f"  -> Warning reading local preview: {e}")

        # Fallback to downloading fullUrl
        if not img_data:
            try:
                req = urllib.request.Request(item['imageUrl'], headers=headers)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    img_data = resp.read()
            except Exception as e:
                print(f"  -> Error downloading full image ({e})")

        if not img_data:
            print(f"  -> SKIP: Failed to retrieve image data for {item_id}")
            continue

        try:
            img = Image.open(BytesIO(img_data))
            
            CHECKERBOARD_TILE = 12
            CB_LIGHT = (255, 255, 255, 255)
            CB_DARK  = (210, 210, 210, 255)

            def make_checkerboard(w, h):
                bg = Image.new('RGBA', (w, h))
                pixels = bg.load()
                for y in range(h):
                    cy = y // CHECKERBOARD_TILE
                    for x in range(w):
                        cx = x // CHECKERBOARD_TILE
                        pixels[x, y] = CB_LIGHT if (cx + cy) % 2 == 0 else CB_DARK
                return bg

            if is_png:
                img_rgba = img.convert("RGBA")

                # Full-res master: transparent RGBA PNG (1860x2480)
                master_img = Image.new("RGBA", (1860, 2480), (0, 0, 0, 0))
                img_resized = img_rgba.copy()
                img_resized.thumbnail((1860, 2480), Image.Resampling.LANCZOS)
                x = (1860 - img_resized.width) // 2
                y = (2480 - img_resized.height) // 2
                master_img.paste(img_resized, (x, y), img_resized)
                master_img.save(full_abs_path, 'PNG')

                # Web thumbnail: transparent RGBA PNG (600x800)
                web_thumb = Image.new("RGBA", (600, 800), (0, 0, 0, 0))
                thumb_resized = img_rgba.copy()
                thumb_resized.thumbnail((600, 800), Image.Resampling.LANCZOS)
                tx = (600 - thumb_resized.width) // 2
                ty = (800 - thumb_resized.height) // 2
                web_thumb.paste(thumb_resized, (tx, ty), thumb_resized)
                web_thumb.save(thumb_web_abs, 'PNG')

                # Plugin thumbnail: checkerboard-composited RGB PNG (600x800)
                bg = make_checkerboard(600, 800)
                plugin_thumb_src = img_rgba.copy()
                plugin_thumb_src.thumbnail((600, 800), Image.Resampling.LANCZOS)
                px = (600 - plugin_thumb_src.width) // 2
                py = (800 - plugin_thumb_src.height) // 2
                bg.paste(plugin_thumb_src, (px, py), plugin_thumb_src)
                bg.convert('RGB').save(thumb_plugin_abs, 'PNG')
                
            else:
                img_rgb = img.convert("RGB")
                master_img = ImageOps.fit(img_rgb, (1860, 2480), Image.Resampling.LANCZOS)
                master_img.save(full_abs_path, 'JPEG', quality=92)

                thumb_img = ImageOps.fit(img_rgb, (600, 800), Image.Resampling.LANCZOS)
                thumb_img.save(thumb_web_abs, 'JPEG', quality=85)

            plugin_thumb_url = (raw_base + thumb_plugin_rel) if thumb_plugin_rel else (raw_base + thumb_web_rel)

            new_entry = {
                "id": item_id,
                "title": item['title'],
                "author": item['author'],
                "authorUrl": item.get('authorUrl', ''),
                "category": item['category'],
                "compatibility": ["Kindle", "Kobo", "Boox", "PocketBook"],
                "license": item.get('license', 'CC0 / Public Domain'),
                "licenseUrl": item.get('licenseUrl', ''),
                "sourceUrl": item.get('sourceUrl', ''),
                "attribution": item.get('attribution', ''),
                "thumbnailUrl": raw_base + thumb_web_rel,
                "pluginThumbnailUrl": plugin_thumb_url,
                "fullUrl": raw_base + full_rel_path,
                "downloads": 0,
                "likes": 1
            }

            catalog.append(new_entry)
            save_catalog_and_credits(catalog)
            print(f"  -> Added {item_id} to catalog (Total catalog count: {len(catalog)})")

        except Exception as e:
            print(f"  -> ERROR processing image {item_id}: {e}")

    print(f"\n[+] Complete! Final catalog items count: {len(catalog)}")

if __name__ == '__main__':
    commit_all()
