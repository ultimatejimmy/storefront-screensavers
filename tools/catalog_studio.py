"""
Storefront Catalog Management Studio - Local Server
Provides a local REST API & Web UI for managing the screensaver catalog,
uploading/replacing images, resizing thumbnails, and updating credits.
"""

import os
import sys
import json
import time
import shutil
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from io import BytesIO

# PIL for image processing
try:
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = None
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow (PIL) is not installed. Image resizing and format conversions will be limited.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..'))
STUDIO_DIR = os.path.join(BASE_DIR, 'studio')
BACKUPS_DIR = os.path.join(BASE_DIR, 'backups')
IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')

os.makedirs(STUDIO_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/"

def create_backup():
    """Create a timestamped backup of screensavers.json."""
    if not os.path.exists(SCREENSAVERS_JSON):
        return None
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUPS_DIR, f"screensavers_{timestamp}.json")
    try:
        shutil.copy2(SCREENSAVERS_JSON, backup_path)
        # Keep only last 30 backups
        backups = sorted([f for f in os.listdir(BACKUPS_DIR) if f.startswith("screensavers_") and f.endswith(".json")])
        while len(backups) > 30:
            oldest = os.path.join(BACKUPS_DIR, backups.pop(0))
            try:
                os.remove(oldest)
            except Exception:
                pass
        return os.path.basename(backup_path)
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def load_catalog():
    if not os.path.exists(SCREENSAVERS_JSON):
        return []
    with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_catalog(catalog_data):
    create_backup()
    with open(SCREENSAVERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)

def rebuild_credits_file(catalog):
    """Regenerate CREDITS.md from catalog data."""
    lines = [
        "# External Sourcing & Attribution Credits",
        "",
        "All open access, Public Domain, CC0, and community-shared screensavers in this catalog are credited below.",
        "",
        "| Title | Creator / Artist | Category | License | Source & Attribution |",
        "|---|---|---|---|---|"
    ]
    for item in catalog:
        title = (item.get('title') or '').replace('|', '\\|')
        author = (item.get('author') or 'Unknown').replace('|', '\\|')
        cat_val = item.get('category')
        if isinstance(cat_val, list):
            category_str = ', '.join(str(c) for c in cat_val if c)
        else:
            category_str = str(cat_val) if cat_val else 'General'
        category = category_str.replace('|', '\\|')
        license_name = (item.get('license') or 'Community Share').replace('|', '\\|')
        source_url = item.get('sourceUrl') or ''
        attribution = item.get('attribution') or author or 'Community Share'

        if source_url:
            source_md = f"[{attribution}]({source_url})".replace('|', '\\|')
        else:
            source_md = attribution.replace('|', '\\|')

        lines.append(f"| {title} | {author} | {category} | {license_name} | {source_md} |")

    lines.append("")
    with open(CREDITS_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def sync_all_catalog():
    """
    Comprehensive Catalog Sync:
    1. Normalizes all catalog metadata and category formats.
    2. Verifies on-disk master images and auto-generates any missing thumbnails.
    3. Normalizes URL pointers to match actual file extensions (.png vs .jpg).
    4. Detects unlinked/orphan images on disk.
    5. Regenerates CREDITS.md.
    6. Creates an automatic snapshot backup and saves cleaned screensavers.json.
    """
    catalog = load_catalog()
    create_backup()

    thumbnails_regenerated = 0
    urls_normalized = 0
    missing_images = []
    
    catalog_ids = set()

    for item in catalog:
        item_id = item.get('id')
        if not item_id:
            continue
        catalog_ids.add(item_id)

        # Normalize tags
        cur_tags = item.get('tags') or []
        if isinstance(cur_tags, str):
            cur_tags = [t.strip().lower() for t in cur_tags.split(',') if t.strip()]
        elif isinstance(cur_tags, list):
            cur_tags = [str(t).strip().lower() for t in cur_tags if str(t).strip()]
        else:
            cur_tags = []
        item['tags'] = sorted(list(set(cur_tags)))

        # Detect actual file extension on disk
        ext = None
        for candidate_ext in ['png', 'jpg', 'jpeg', 'webp']:
            if os.path.exists(os.path.join(IMAGES_DIR, f"{item_id}.{candidate_ext}")):
                ext = candidate_ext
                break

        if ext:
            expected_full_rel = f"images/{item_id}.{ext}"
            expected_thumb_rel = f"images/thumbnails/{item_id}.{ext}"
            expected_full_url = GITHUB_RAW_BASE + expected_full_rel
            expected_thumb_url = GITHUB_RAW_BASE + expected_thumb_rel

            # Normalize URLs if needed
            if item.get('fullUrl') != expected_full_url or item.get('thumbnailUrl') != expected_thumb_url:
                item['fullUrl'] = expected_full_url
                item['thumbnailUrl'] = expected_thumb_url
                urls_normalized += 1

            # Check if thumbnail exists, if not, auto-generate from master image
            thumb_path = os.path.join(REPO_ROOT, expected_thumb_rel)
            master_path = os.path.join(REPO_ROOT, expected_full_rel)

            if not os.path.exists(thumb_path) and PIL_AVAILABLE and os.path.exists(master_path):
                try:
                    with Image.open(master_path) as m_img:
                        if ext == 'png' and m_img.mode != 'RGBA':
                            m_img = m_img.convert('RGBA')
                        elif ext != 'png' and m_img.mode != 'RGB':
                            m_img = m_img.convert('RGB')
                        thumb_img = ImageOps.fit(m_img, (300, 400), Image.Resampling.LANCZOS)
                        if ext == 'png':
                            try:
                                thumb_quant = thumb_img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
                                thumb_quant.save(thumb_path, 'PNG', optimize=True)
                            except Exception:
                                thumb_img.save(thumb_path, 'PNG', optimize=True)
                        else:
                            thumb_img.save(thumb_path, 'JPEG', quality=78, optimize=True)
                        thumbnails_regenerated += 1
                except Exception as e:
                    print(f"Error regenerating thumbnail for {item_id}: {e}")
        else:
            missing_images.append(item_id)

    # Rebuild credits markdown
    rebuild_credits_file(catalog)

    # Clean up orphan images if they are no longer in the catalog
    orphan_images = []
    orphans_removed = 0
    if os.path.exists(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            p = os.path.join(IMAGES_DIR, f)
            if os.path.isfile(p):
                base_name = os.path.splitext(f)[0]
                if base_name not in catalog_ids:
                    orphan_images.append(f)
                    try:
                        os.remove(p)
                        orphans_removed += 1
                    except Exception:
                        pass

    if os.path.exists(THUMBS_DIR):
        for f in os.listdir(THUMBS_DIR):
            p = os.path.join(THUMBS_DIR, f)
            if os.path.isfile(p):
                base_name = os.path.splitext(f)[0]
                if base_name not in catalog_ids:
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    # Save cleaned catalog
    save_catalog(catalog)

    # Git commit and push (including deletions)
    git_result = {"committed": False, "pushed": False, "message": ""}
    import subprocess
    try:
        # Stage all catalog, credits, and image changes/deletions
        subprocess.run(['git', 'add', '-A', 'screensavers.json', 'CREDITS.md', 'images/'], cwd=REPO_ROOT, check=True)

        # Check if there are staged git changes
        status_proc = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO_ROOT, capture_output=True, text=True)
        has_changes = bool(status_proc.stdout.strip())
        
        if has_changes:
            # Commit
            commit_msg = f"Sync catalog, images, and credits ({len(catalog)} screensavers)"
            commit_proc = subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_ROOT, capture_output=True, text=True)
            git_result["committed"] = True
            
            # Push
            push_proc = subprocess.run(['git', 'push'], cwd=REPO_ROOT, capture_output=True, text=True)
            if push_proc.returncode == 0:
                git_result["pushed"] = True
                git_result["message"] = "Changes & removals successfully committed and pushed to GitHub!"
            else:
                git_result["message"] = f"Committed locally, but git push returned: {push_proc.stderr.strip() or push_proc.stdout.strip()}"
        else:
            # Try to push any existing unpushed commits if clean working tree
            push_proc = subprocess.run(['git', 'push'], cwd=REPO_ROOT, capture_output=True, text=True)
            if push_proc.returncode == 0:
                git_result["pushed"] = True
                git_result["message"] = "Working directory was clean. Pushed latest commits to GitHub!"
            else:
                git_result["message"] = "Working directory is already clean and in sync."
    except Exception as e:
        git_result["message"] = f"Git operation failed: {e}"

    return {
        "success": True,
        "total_items": len(catalog),
        "urls_normalized": urls_normalized,
        "thumbnails_regenerated": thumbnails_regenerated,
        "missing_master_images": missing_images,
        "orphan_image_files": orphan_images,
        "credits_synced": True,
        "git": git_result
    }

def process_and_save_image(image_bytes, item_id, is_png=False):
    """Resize image to master (1860x2480) and thumb (600x800) and save to disk."""
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow is required for image processing.")

    Image.MAX_IMAGE_PIXELS = 50_000_000
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'BMP', 'MPO'}
    img_stream = BytesIO(image_bytes)
    try:
        verify_img = Image.open(img_stream)
        detected_format = verify_img.format
        verify_img.verify()
    except Exception as exc:
        raise ValueError(f"Invalid or corrupted image structure: {exc}")

    if detected_format not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported format '{detected_format}'. Only standard raster images (JPEG, PNG, WebP) are allowed.")

    img_stream.seek(0)
    try:
        img = Image.open(img_stream)
        img.load()
    except Exception as exc:
        raise ValueError(f"Failed to decode image raster: {exc}")

    if img.width < 200 or img.height < 200:
        raise ValueError(f"Image dimensions ({img.width}x{img.height} px) are too small. Minimum resolution is 200x200 px.")
    
    # Determine if transparency should be preserved
    has_alpha = ('A' in img.getbands()) or (img.mode == 'RGBA') or (img.info.get('transparency') is not None) or is_png
    ext = "png" if (has_alpha or is_png) else "jpg"

    full_rel_path = f"images/{item_id}.{ext}"
    thumb_rel_path = f"images/thumbnails/{item_id}.{ext}"
    full_abs_path = os.path.join(REPO_ROOT, full_rel_path)
    thumb_abs_path = os.path.join(REPO_ROOT, thumb_rel_path)

    # Master: 1860 x 2480 (3:4 ratio)
    # Thumbnail: 300 x 400 (3:4 ratio) optimized for fast e-ink transfers
    if has_alpha:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        master_img = ImageOps.fit(img, (1860, 2480), Image.Resampling.LANCZOS)
        thumb_img = ImageOps.fit(img, (300, 400), Image.Resampling.LANCZOS)
        
        master_img.save(full_abs_path, 'PNG', optimize=True)
        # Quantize thumbnail to 8-bit palette with alpha for 85%+ smaller file size
        try:
            thumb_quant = thumb_img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
            thumb_quant.save(thumb_abs_path, 'PNG', optimize=True)
        except Exception:
            thumb_img.save(thumb_abs_path, 'PNG', optimize=True)
    else:
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        master_img = ImageOps.fit(img, (1860, 2480), Image.Resampling.LANCZOS)
        thumb_img = ImageOps.fit(img, (300, 400), Image.Resampling.LANCZOS)
        
        master_img.save(full_abs_path, 'JPEG', quality=92)
        thumb_img.save(thumb_abs_path, 'JPEG', quality=78, optimize=True)

    # If the extension changed (e.g. was jpg, now png or vice-versa), clean up old file if exists
    other_ext = "jpg" if ext == "png" else "png"
    for old_path in [os.path.join(REPO_ROOT, f"images/{item_id}.{other_ext}"),
                     os.path.join(REPO_ROOT, f"images/thumbnails/{item_id}.{other_ext}")]:
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    return {
        "fullRel": full_rel_path,
        "thumbRel": thumb_rel_path,
        "fullUrl": GITHUB_RAW_BASE + full_rel_path,
        "thumbnailUrl": GITHUB_RAW_BASE + thumb_rel_path,
        "format": ext
    }


class CatalogStudioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Default directory for static serving fallback
        super().__init__(*args, directory=REPO_ROOT, **kwargs)

    def end_headers(self):
        # Disable caching for API and image requests in the studio so changes show immediately
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: Catalog Data
        if path == '/api/catalog':
            catalog = load_catalog()
            # Calculate categories and stats (supporting both list and string categories)
            cat_set = {'Abstract', 'Anime', 'Architecture', 'Art', 'Fantasy', 'Minimalist', 'Nature', 'Pop Culture', 'Quotes', 'Religion', 'Sci-Fi', 'Transparent'}
            for item in catalog:
                cat = item.get('category')
                if isinstance(cat, list):
                    for c in cat:
                        if c and str(c).strip():
                            cat_set.add(str(c).strip())
                elif isinstance(cat, str) and cat.strip():
                    for c in cat.split(','):
                        if c.strip():
                            cat_set.add(c.strip())

            categories = sorted(list(cat_set))
            
            backups = []
            if os.path.exists(BACKUPS_DIR):
                for f in sorted(os.listdir(BACKUPS_DIR), reverse=True):
                    if f.startswith("screensavers_") and f.endswith(".json"):
                        backups.append(f)

            response_data = {
                "total": len(catalog),
                "categories": categories,
                "backups": backups,
                "items": catalog
            }
            self.send_json(response_data)
            return

        # Root goes to studio index.html
        if path == '/' or path == '/index.html' or path == '/studio' or path == '/studio/':
            studio_index = os.path.join(STUDIO_DIR, 'index.html')
            if os.path.exists(studio_index):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(studio_index, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # Check if file exists inside STUDIO_DIR (e.g. styles.css, app.js)
        # Strip leading slash or '/studio/' prefix
        rel_path = path.lstrip('/')
        if rel_path.startswith('studio/'):
            rel_path = rel_path[len('studio/'):]

        # Prioritize files in tools/studio/ (except for images/ or screensavers.json)
        if not path.startswith('/images/') and not path == '/screensavers.json':
            studio_file = os.path.join(STUDIO_DIR, rel_path)
            if os.path.isfile(studio_file):
                self.send_response(200)
                if studio_file.endswith('.css'):
                    self.send_header('Content-Type', 'text/css; charset=utf-8')
                elif studio_file.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                elif studio_file.endswith('.html'):
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                elif studio_file.endswith('.json'):
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                elif studio_file.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif studio_file.endswith('.jpg') or studio_file.endswith('.jpeg'):
                    self.send_header('Content-Type', 'image/jpeg')
                elif studio_file.endswith('.svg'):
                    self.send_header('Content-Type', 'image/svg+xml')
                self.end_headers()
                with open(studio_file, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # Fallback to serving images or static files from repo root
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Parse JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            payload = {}

        # API: Save full catalog
        if path == '/api/catalog/save':
            if 'items' in payload and isinstance(payload['items'], list):
                save_catalog(payload['items'])
                self.send_json({"success": True, "count": len(payload['items'])})
                return
            self.send_error(400, "Invalid catalog items payload")
            return

        # API: Add new catalog item
        if path == '/api/catalog/item':
            catalog = load_catalog()
            new_item = payload.get('item')
            if not new_item or not new_item.get('title'):
                self.send_error(400, "Item and Title are required")
                return

            item_id = new_item.get('id')
            if not item_id:
                # slugify title
                raw_slug = "".join(c.lower() if c.isalnum() else '-' for c in new_item['title']).strip('-')
                item_id = '-'.join(filter(None, raw_slug.split('-'))) or f"screensaver-{int(time.time())}"
                new_item['id'] = item_id

            # Ensure ID is unique
            existing_ids = {x.get('id') for x in catalog}
            original_id = item_id
            counter = 1
            while item_id in existing_ids:
                item_id = f"{original_id}-{counter}"
                counter += 1
            new_item['id'] = item_id

            # Handle image data if provided (base64 or remote URL)
            image_data = payload.get('imageData')
            image_url = payload.get('imageUrl')
            is_png = payload.get('isPng', False)

            if image_data:
                # Base64 string data:image/jpeg;base64,...
                import base64
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]
                raw_bytes = base64.b64decode(image_data)
                img_res = process_and_save_image(raw_bytes, item_id, is_png=is_png)
                new_item['thumbnailUrl'] = img_res['thumbnailUrl']
                new_item['fullUrl'] = img_res['fullUrl']
            elif image_url:
                req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw_bytes = resp.read()
                img_res = process_and_save_image(raw_bytes, item_id, is_png=image_url.lower().endswith('.png'))
                new_item['thumbnailUrl'] = img_res['thumbnailUrl']
                new_item['fullUrl'] = img_res['fullUrl']
            else:
                # Default URLs if images not uploaded yet
                new_item.setdefault('thumbnailUrl', f"{GITHUB_RAW_BASE}images/thumbnails/{item_id}.jpg")
                new_item.setdefault('fullUrl', f"{GITHUB_RAW_BASE}images/{item_id}.jpg")

            new_item.setdefault('downloads', 0)
            new_item.setdefault('likes', 1)
            new_item.setdefault('compatibility', ["Kindle", "Kobo", "Boox", "PocketBook"])
            new_item.setdefault('license', "Community Share")
            new_item.setdefault('category', "Nature")

            catalog.insert(0, new_item)
            save_catalog(catalog)
            self.send_json({"success": True, "item": new_item})
            return

        # API: Replace image for existing item
        if path.startswith('/api/catalog/item/') and path.endswith('/replace-image'):
            parts = path.split('/')
            # /api/catalog/item/<id>/replace-image
            item_id = urllib.parse.unquote(parts[4])
            catalog = load_catalog()
            item = next((x for x in catalog if x.get('id') == item_id), None)
            if not item:
                self.send_error(404, f"Item '{item_id}' not found")
                return

            image_data = payload.get('imageData')
            image_url = payload.get('imageUrl')
            is_png = payload.get('isPng', False)

            try:
                if image_data:
                    import base64
                    if ',' in image_data:
                        image_data = image_data.split(',', 1)[1]
                    raw_bytes = base64.b64decode(image_data)
                    img_res = process_and_save_image(raw_bytes, item_id, is_png=is_png)
                elif image_url:
                    req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        raw_bytes = resp.read()
                    img_res = process_and_save_image(raw_bytes, item_id, is_png=image_url.lower().endswith('.png'))
                else:
                    self.send_error(400, "No imageData or imageUrl provided")
                    return

                item['thumbnailUrl'] = img_res['thumbnailUrl']
                item['fullUrl'] = img_res['fullUrl']
                save_catalog(catalog)
                self.send_json({"success": True, "item": item, "image": img_res})
                return
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, status=500)
                return

        # API: Sync Everything
        if path == '/api/catalog/sync-all':
            result = sync_all_catalog()
            self.send_json(result)
            return

        # API: Rebuild CREDITS.md
        if path == '/api/catalog/rebuild-credits':
            catalog = load_catalog()
            rebuild_credits_file(catalog)
            self.send_json({"success": True, "count": len(catalog)})
            return

        # API: Restore Backup
        if path == '/api/catalog/restore-backup':
            backup_name = payload.get('backup')
            if not backup_name:
                self.send_error(400, "Backup filename required")
                return
            backup_file = os.path.join(BACKUPS_DIR, os.path.basename(backup_name))
            if not os.path.exists(backup_file):
                self.send_error(404, "Backup file not found")
                return
            create_backup()  # backup current state before restoring
            shutil.copy2(backup_file, SCREENSAVERS_JSON)
            catalog = load_catalog()
            self.send_json({"success": True, "count": len(catalog), "restored": backup_name})
            return

        # API: Batch updates
        if path == '/api/catalog/batch':
            action = payload.get('action')
            target_ids = set(payload.get('ids', []))
            catalog = load_catalog()

            if action == 'delete':
                delete_files = payload.get('deleteFiles', False)
                if delete_files:
                    for item_id in target_ids:
                        for ext in ['jpg', 'png', 'jpeg', 'webp']:
                            for p in [os.path.join(IMAGES_DIR, f"{item_id}.{ext}"),
                                      os.path.join(THUMBS_DIR, f"{item_id}.{ext}")]:
                                if os.path.exists(p):
                                    try:
                                        os.remove(p)
                                    except Exception:
                                        pass
                catalog = [x for x in catalog if x.get('id') not in target_ids]
            elif action == 'add_category' or action == 'add_categories':
                new_cats = payload.get('categories') or []
                if isinstance(new_cats, str):
                    new_cats = [new_cats]
                for x in catalog:
                    if x.get('id') in target_ids:
                        cur_cat = x.get('category')
                        cats = []
                        if isinstance(cur_cat, list):
                            cats = [str(c).strip() for c in cur_cat if str(c).strip()]
                        elif isinstance(cur_cat, str) and cur_cat.strip():
                            cats = [c.strip() for c in cur_cat.split(',') if c.strip()]
                        
                        for nc in new_cats:
                            nc_clean = str(nc).strip()
                            if nc_clean and nc_clean not in cats:
                                cats.append(nc_clean)
                        
                        x['category'] = cats if len(cats) > 1 else (cats[0] if cats else 'General')
            elif action == 'remove_category':
                rem_cat = (payload.get('category') or '').strip()
                for x in catalog:
                    if x.get('id') in target_ids:
                        cur_cat = x.get('category')
                        cats = []
                        if isinstance(cur_cat, list):
                            cats = [str(c).strip() for c in cur_cat if str(c).strip()]
                        elif isinstance(cur_cat, str) and cur_cat.strip():
                            cats = [c.strip() for c in cur_cat.split(',') if c.strip()]
                        cats = [c for c in cats if c != rem_cat]
                        x['category'] = cats if len(cats) > 1 else (cats[0] if cats else 'General')
            elif action == 'set_category':
                cat = payload.get('category')
                for x in catalog:
                    if x.get('id') in target_ids:
                        x['category'] = cat
            elif action == 'add_tags':
                new_tags = payload.get('tags') or []
                if isinstance(new_tags, str):
                    new_tags = [t.strip().lower() for t in new_tags.split(',') if t.strip()]
                for x in catalog:
                    if x.get('id') in target_ids:
                        cur_tags = x.get('tags') or []
                        if isinstance(cur_tags, str):
                            cur_tags = [t.strip().lower() for t in cur_tags.split(',') if t.strip()]
                        t_set = set(str(t).strip().lower() for t in cur_tags if str(t).strip())
                        for nt in new_tags:
                            nt_clean = str(nt).strip().lower()
                            if nt_clean:
                                t_set.add(nt_clean)
                        x['tags'] = sorted(list(t_set))
            elif action == 'remove_tag':
                rem_tag = (payload.get('tag') or '').strip().lower()
                for x in catalog:
                    if x.get('id') in target_ids:
                        cur_tags = x.get('tags') or []
                        if isinstance(cur_tags, str):
                            cur_tags = [t.strip().lower() for t in cur_tags.split(',') if t.strip()]
                        x['tags'] = [t for t in cur_tags if str(t).strip().lower() != rem_tag]
            elif action == 'set_license':
                license_val = payload.get('license')
                for x in catalog:
                    if x.get('id') in target_ids:
                        x['license'] = license_val

            save_catalog(catalog)
            self.send_json({"success": True, "updated": len(target_ids), "total": len(catalog)})
            return

        self.send_error(404, "Endpoint not found")

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: Update specific item /api/catalog/item/<id>
        if path.startswith('/api/catalog/item/'):
            item_id = urllib.parse.unquote(path[len('/api/catalog/item/'):])
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                updates = json.loads(body.decode('utf-8'))
            except Exception:
                self.send_error(400, "Invalid JSON")
                return

            catalog = load_catalog()
            idx = next((i for i, x in enumerate(catalog) if x.get('id') == item_id), None)
            if idx is None:
                self.send_error(404, f"Item '{item_id}' not found")
                return

            existing = catalog[idx]
            new_id = updates.get('id', item_id).strip()

            # Handle ID rename if requested
            if new_id and new_id != item_id:
                # Check for conflict
                if any(x.get('id') == new_id for i, x in enumerate(catalog) if i != idx):
                    self.send_json({"success": False, "error": f"ID '{new_id}' already exists in catalog."}, status=400)
                    return
                # Rename associated image files
                for ext in ['jpg', 'png', 'jpeg', 'webp']:
                    old_full = os.path.join(IMAGES_DIR, f"{item_id}.{ext}")
                    new_full = os.path.join(IMAGES_DIR, f"{new_id}.{ext}")
                    if os.path.exists(old_full):
                        try:
                            os.rename(old_full, new_full)
                        except Exception:
                            pass

                    old_thumb = os.path.join(THUMBS_DIR, f"{item_id}.{ext}")
                    new_thumb = os.path.join(THUMBS_DIR, f"{new_id}.{ext}")
                    if os.path.exists(old_thumb):
                        try:
                            os.rename(old_thumb, new_thumb)
                        except Exception:
                            pass

                # Update URL pointers
                if 'thumbnailUrl' in existing and item_id in existing['thumbnailUrl']:
                    updates['thumbnailUrl'] = existing['thumbnailUrl'].replace(f"/{item_id}.", f"/{new_id}.")
                if 'fullUrl' in existing and item_id in existing['fullUrl']:
                    updates['fullUrl'] = existing['fullUrl'].replace(f"/{item_id}.", f"/{new_id}.")

            # Apply updates
            existing.update(updates)
            catalog[idx] = existing
            save_catalog(catalog)
            self.send_json({"success": True, "item": existing})
            return

        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: Delete item /api/catalog/item/<id>?deleteFiles=1
        if path.startswith('/api/catalog/item/'):
            item_id = urllib.parse.unquote(path[len('/api/catalog/item/'):])
            query_params = urllib.parse.parse_qs(parsed.query)
            delete_files = query_params.get('deleteFiles', ['0'])[0] in ['1', 'true', 'yes']

            catalog = load_catalog()
            before_len = len(catalog)
            catalog = [x for x in catalog if x.get('id') != item_id]

            if len(catalog) == before_len:
                self.send_error(404, f"Item '{item_id}' not found")
                return

            if delete_files:
                for ext in ['jpg', 'png', 'jpeg', 'webp']:
                    for p in [os.path.join(IMAGES_DIR, f"{item_id}.{ext}"),
                              os.path.join(THUMBS_DIR, f"{item_id}.{ext}")]:
                        if os.path.exists(p):
                            try:
                                os.remove(p)
                            except Exception:
                                pass

            save_catalog(catalog)
            self.send_json({"success": True, "deletedId": item_id, "remaining": len(catalog)})
            return

        self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port=5173, auto_open=True):
    server_address = ('127.0.0.1', port)
    try:
        httpd = HTTPServer(server_address, CatalogStudioHandler)
    except OSError:
        # If port is occupied, pick 5174 or 8080
        port = 8080
        server_address = ('127.0.0.1', port)
        httpd = HTTPServer(server_address, CatalogStudioHandler)

    url = f"http://127.0.0.1:{port}/"
    print("=" * 60)
    print("  STOREFRONT SCREENSAVERS - CATALOG MANAGEMENT STUDIO")
    print("=" * 60)
    print(f"  Server running locally at: {url}")
    print(f"  Managing catalog: {SCREENSAVERS_JSON}")
    print(f"  Backups directory: {BACKUPS_DIR}")
    print(f"  Images directory: {IMAGES_DIR}")
    print("=" * 60)
    print("  Press Ctrl+C in this terminal to stop the server.\n")

    if auto_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Catalog Studio Server...")
        httpd.server_close()

if __name__ == '__main__':
    port = 5173
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    auto_open = '--no-open' not in sys.argv
    run_server(port=port, auto_open=auto_open)
