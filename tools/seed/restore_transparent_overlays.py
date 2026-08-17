import os
import json
import urllib.request
from PIL import Image, ImageOps
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 StorefrontScreensavers/1.0'
}

with open(os.path.join(BASE_DIR, 'candidates_transparent.json'), 'r', encoding='utf-8') as f:
    cands = json.load(f)

print("[+] Re-downloading and properly formatting transparent overlays...")

for c in cands:
    item_id = c['id']
    url = c['imageUrl']
    print(f"Processing {item_id} ({c['title']})...")
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            img_data = resp.read()
            
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        
        # 1. Convert near-white background pixels (R>238, G>238, B>238) to alpha=0
        r, g, b, a = img.split()
        w_r = Image.eval(r, lambda p: 255 if p > 238 else 0)
        w_g = Image.eval(g, lambda p: 255 if p > 238 else 0)
        w_b = Image.eval(b, lambda p: 255 if p > 238 else 0)
        
        is_white = Image.eval(Image.composite(w_r, Image.new("L", r.size, 0), w_g), lambda p: p)
        is_white = Image.eval(Image.composite(is_white, Image.new("L", r.size, 0), w_b), lambda p: p)
        
        new_a = Image.composite(Image.new("L", r.size, 0), a, is_white)
        img.putalpha(new_a)

        # 2. Preserve original creator layout & proportion inside 3:4 canvas
        # Master 1860x2480
        master_img = Image.new("RGBA", (1860, 2480), (0, 0, 0, 0))
        img_master = img.copy()
        img_master.thumbnail((1860, 2480), Image.Resampling.LANCZOS)
        mx = (1860 - img_master.width) // 2
        my = (2480 - img_master.height) // 2
        master_img.paste(img_master, (mx, my), img_master)
        master_img.save(os.path.join(IMAGES_DIR, f"{item_id}.png"), 'PNG')

        # Thumb 600x800
        thumb_img = Image.new("RGBA", (600, 800), (0, 0, 0, 0))
        img_thumb = img.copy()
        img_thumb.thumbnail((600, 800), Image.Resampling.LANCZOS)
        tx = (600 - img_thumb.width) // 2
        ty = (800 - img_thumb.height) // 2
        thumb_img.paste(img_thumb, (tx, ty), img_thumb)
        thumb_img.save(os.path.join(THUMBS_DIR, f"{item_id}.png"), 'PNG')

        print(f"  -> Saved {item_id}.png in 600x800 & 1860x2480")

    except Exception as e:
        print(f"  -> Error on {item_id}: {e}")

print("[+] Done restoring transparent overlays!")
