import os
import json
import base64
import urllib.request
import urllib.error
import time
from PIL import Image
from io import BytesIO
import concurrent.futures

API_KEY = os.environ.get('GEMINI_API_KEY')

def get_ai_title(image_path):
    if not API_KEY:
        return None
        
    try:
        # Resize image to save tokens
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail((256, 256))
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        data = {
            "contents": [{
                "parts": [
                    {"text": "Provide a short, descriptive, 2-to-5 word title for this image. Output ONLY the title, no quotes or extra text."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                ]
            }],
            "generationConfig": {"temperature": 0.4}
        }
        
        req = urllib.request.Request(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read())
            title = resp_data['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean up quotes if the model added them
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            return title
            
    except Exception as e:
        print(f"Failed to generate title for {image_path}: {e}")
        return None

def process_gallery(json_path, html_path, script_path, generic_keyword, name_label):
    print(f"\n[+] Processing {name_label}...")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        cands = json.load(f)
        
    to_process = [c for c in cands if generic_keyword in c['title']]
    print(f"Found {len(to_process)} generic titles to rename.")
    
    # Process sequentially with small delay to avoid rate limits
    for idx, c in enumerate(to_process, 1):
        img_path = os.path.join(os.path.dirname(json_path), c['previewPath'])
        if os.path.exists(img_path):
            new_title = get_ai_title(img_path)
            if new_title:
                print(f"[{idx}/{len(to_process)}] Renamed: '{c['title']}' -> '{new_title}'")
                c['title'] = new_title
        time.sleep(1.5) # Sleep to avoid 429 Too Many Requests
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(cands, f, indent=2, ensure_ascii=False)
        
    # Rebuild HTML
    items_js = json.dumps(cands, indent=2, ensure_ascii=False)
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    html_start = content.find('HTML = f"""') + 11
    html_end = content.find('"""', html_start)
    html_template = content[html_start:html_end]
    html_out = html_template.replace('{items_js}', items_js).replace('{{', '{').replace('}}', '}')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
        
    print(f"[+] Rebuilt {html_path} with new titles!")

if __name__ == '__main__':
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        exit(1)
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    process_gallery(
        os.path.join(base_dir, 'candidates_transparent.json'),
        os.path.join(base_dir, 'review_transparent.html'),
        os.path.join(base_dir, 'build_readerbackdrop_seed_batch.py'),
        'Overlay',
        'Transparent Overlays'
    )
    
    process_gallery(
        os.path.join(base_dir, 'candidates_wallhaven.json'),
        os.path.join(base_dir, 'review_wallhaven.html'),
        os.path.join(base_dir, 'build_wallhaven_seed_batch.py'),
        'Wallpaper',
        'Wallhaven'
    )
