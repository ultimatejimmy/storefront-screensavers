import os
import json
import base64
import urllib.request
import urllib.error
import time
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get('GEMINI_API_KEY')
MODEL_NAME = "gemini-2.5-flash"

def get_ai_title_and_filter(image_path):
    if not API_KEY:
        return None
        
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img.thumbnail((256, 256))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return None

    prompt = (
        "Analyze this image carefully.\n"
        "1. Is it a photograph of a physical e-reader/tablet device (like a Kindle, Kobo, Boox) sitting on a desk, being held by hands, or shown in a room? "
        "If it is a photo of a physical device/hardware, reply EXACTLY with: DEVICE_PHOTO\n"
        "2. If it is a direct digital graphic, artwork, illustration, or wallpaper file, reply ONLY with a short, descriptive 2-to-5 word title for the image. "
        "Do NOT include quotes, tags, or extra words."
    )

    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }],
        "generationConfig": {"temperature": 0.2}
    }
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}'
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_data = json.loads(resp.read())
                res = resp_data['candidates'][0]['content']['parts'][0]['text'].strip()
                if res.startswith('"') and res.endswith('"'):
                    res = res[1:-1]
                return res
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_sec = (attempt + 1) * 5
                print(f"Rate limited (429). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                print(f"HTTP error {e.code} for {image_path}: {e}")
                return None
        except Exception as e:
            print(f"Failed to analyze {image_path}: {e}")
            return None
            
    return None

def update_files(json_path, html_path, script_path, cands):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(cands, f, indent=2, ensure_ascii=False)
        
    items_js = json.dumps(cands, indent=2, ensure_ascii=False)
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    html_start = content.find('HTML = f"""') + 11
    html_end = content.find('"""', html_start)
    html_template = content[html_start:html_end]
    html_out = html_template.replace('{items_js}', items_js).replace('{{', '{').replace('}}', '}')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_out)

def process_reddit_gallery():
    print(f"\n[+] Filtering physical devices and renaming Reddit screensavers using Gemini Vision API...")
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'candidates_reddit.json')
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'review_reddit.html')
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_reddit_seed_batch.py')
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        cands = json.load(f)
        
    print(f"Processing all {len(cands)} images to filter devices and standardize titles.")
    
    # We mutate a list copy so all elements remain present during processing
    to_remove = []
    
    for idx, c in enumerate(cands, 1):
        # Skip if already AI-renamed (title doesn't end with index or generic pattern)
        # We check if title contains "Image " or "Gallery"
        if not ("Image " in c['title'] or "(Gallery)" in c['title'] or "Reddit" in c['title']):
            continue

        img_path = os.path.join(os.path.dirname(json_path), c['previewPath'])
        if os.path.exists(img_path):
            res = get_ai_title_and_filter(img_path)
            if res:
                if "DEVICE_PHOTO" in res or "device_photo" in res.lower() or "physical device" in res.lower():
                    clean_t = c['title'].encode('ascii', 'replace').decode('ascii')
                    print(f"[{idx}/{len(cands)}] REMOVED DEVICE PHOTO: '{clean_t}'")
                    to_remove.append(c)
                    try:
                        os.remove(img_path)
                    except:
                        pass
                else:
                    clean_t = c['title'].encode('ascii', 'replace').decode('ascii')
                    clean_r = res.encode('ascii', 'replace').decode('ascii')
                    print(f"[{idx}/{len(cands)}] KEPT & RENAMED: '{clean_t}' -> '{clean_r}'")
                    c['title'] = res
            else:
                clean_t = c['title'].encode('ascii', 'replace').decode('ascii')
                print(f"[{idx}/{len(cands)}] API failed, keeping original: '{clean_t}'")
        
        # Remove any flagged device photos from active list
        cands_filtered = [item for item in cands if item not in to_remove]
        
        # Save updated list to disk after each item processed
        update_files(json_path, html_path, script_path, cands_filtered)
        time.sleep(2.0)
        
    print(f"\n[+] Complete! Removed {len(to_remove)} physical device photos.")

if __name__ == '__main__':
    process_reddit_gallery()
