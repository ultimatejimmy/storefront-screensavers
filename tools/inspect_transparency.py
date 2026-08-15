import os
from PIL import Image
import json

with open('screensavers.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

for title_search in ['Solitary Mountain Peak', 'Forest Canopy Starlight', 'Misty Pine Ridge', 'Lunar Celestial Eclipse']:
    item = next((x for x in catalog if x.get('title') == title_search), None)
    if item:
        item_id = item['id']
        print(f"=== {item.get('title')} ({item_id}) ===")
        print(f"Category: {item.get('category')}")
        print(f"Thumbnail URL: {item.get('thumbnailUrl')}")
        for ext in ['png', 'jpg', 'jpeg']:
            p = f'images/{item_id}.{ext}'
            if os.path.exists(p):
                with Image.open(p) as img:
                    extrema = img.getextrema() if img.mode == 'RGBA' else None
                    print(f"  Master {p}: mode={img.mode}, size={img.size}, alpha_extrema={extrema[3] if extrema else None}")
            t = f'images/thumbnails/{item_id}.{ext}'
            if os.path.exists(t):
                with Image.open(t) as img:
                    extrema = img.getextrema() if img.mode == 'RGBA' else None
                    print(f"  Thumb {t}: mode={img.mode}, size={img.size}, alpha_extrema={extrema[3] if extrema else None}")
