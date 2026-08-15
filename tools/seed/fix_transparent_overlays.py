import os
import glob
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..', '..'))

IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')

print("[+] Fast processing and scaling transparent overlays...")

def process_transparent_image(file_path, target_size):
    try:
        with Image.open(file_path) as raw_img:
            img = raw_img.convert("RGBA")
            
            # Fast PIL alpha transparency for white backgrounds (R>235, G>235, B>235)
            r, g, b, a = img.split()
            w_r = Image.eval(r, lambda p: 255 if p > 235 else 0)
            w_g = Image.eval(g, lambda p: 255 if p > 235 else 0)
            w_b = Image.eval(b, lambda p: 255 if p > 235 else 0)
            
            is_white = Image.eval(Image.composite(w_r, Image.new("L", r.size, 0), w_g), lambda p: p)
            is_white = Image.eval(Image.composite(is_white, Image.new("L", r.size, 0), w_b), lambda p: p)
            
            new_a = Image.composite(Image.new("L", r.size, 0), a, is_white)
            img.putalpha(new_a)

            # Crop to content bounding box
            bbox = img.getbbox()
            if bbox:
                cropped = img.crop(bbox)
            else:
                cropped = img

            # Canvas & Scale to fill 3:4 canvas edge-to-edge
            canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
            cw, ch = cropped.size
            tw, th = target_size
            
            scale = max(tw / cw, th / ch)
            nw, nh = int(cw * scale), int(ch * scale)
            
            scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
            
            x = (tw - nw) // 2
            y = (th - nh) // 2
            
            canvas.paste(scaled, (x, y), scaled)
            canvas.save(file_path, "PNG")
            print(f"  -> Successfully aligned {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  -> Error on {file_path}: {e}")

rb_thumbs = glob.glob(os.path.join(THUMBS_DIR, 'rb-*.png'))
for thumb_path in rb_thumbs:
    process_transparent_image(thumb_path, (600, 800))
    full_name = os.path.basename(thumb_path)
    full_path = os.path.join(IMAGES_DIR, full_name)
    if os.path.exists(full_path):
        process_transparent_image(full_path, (1860, 2480))

print("[+] All transparent overlays re-aligned successfully!")
