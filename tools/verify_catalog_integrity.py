import os
import json

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SCREENSAVERS_JSON = os.path.join(REPO_ROOT, 'screensavers.json')
CREDITS_MD = os.path.join(REPO_ROOT, 'CREDITS.md')
IMAGES_DIR = os.path.join(REPO_ROOT, 'images')
THUMBS_DIR = os.path.join(IMAGES_DIR, 'thumbnails')
PLUGIN_THUMBS_DIR = os.path.join(THUMBS_DIR, 'plugin')

with open(SCREENSAVERS_JSON, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog items: {len(catalog)}")

outchy_items = [item for item in catalog if item.get('author') == 'outchy']
print(f"Total outchy items: {len(outchy_items)}")

errors = []
missing_masters = 0
missing_thumbs = 0
missing_plugin_thumbs = 0

for item in catalog:
    item_id = item.get('id')
    if not item_id:
        errors.append("Item missing ID")
        continue

    # Verify master file on disk
    ext = 'png' if (item_id.startswith('outchy-') and item_id != 'outchy-knight-reading-sleeping-cat') else ('jpg' if item_id == 'outchy-knight-reading-sleeping-cat' else None)
    
    # Check fullUrl
    full_url = item.get('fullUrl', '')
    full_file = full_url.split('/images/')[-1]
    if not os.path.exists(os.path.join(IMAGES_DIR, full_file)):
        missing_masters += 1
        errors.append(f"Missing master image: {full_file} for {item_id}")

    # Check thumbUrl
    thumb_url = item.get('thumbnailUrl', '')
    thumb_file = thumb_url.split('/thumbnails/')[-1]
    if not os.path.exists(os.path.join(THUMBS_DIR, thumb_file)):
        missing_thumbs += 1
        errors.append(f"Missing thumbnail: {thumb_file} for {item_id}")

    # Check pluginThumbUrl if present
    plugin_thumb_url = item.get('pluginThumbnailUrl')
    if plugin_thumb_url:
        plugin_file = plugin_thumb_url.split('/thumbnails/plugin/')[-1]
        if not os.path.exists(os.path.join(PLUGIN_THUMBS_DIR, plugin_file)):
            missing_plugin_thumbs += 1
            errors.append(f"Missing plugin thumbnail: {plugin_file} for {item_id}")

    # Check categories
    cat = item.get('category')
    if not cat:
        errors.append(f"Item {item_id} has empty category")

    # Check tags
    tags = item.get('tags')
    if not tags or not isinstance(tags, list) or len(tags) == 0:
        errors.append(f"Item {item_id} has empty or invalid tags")

print(f"\n--- Verification Summary ---")
print(f"Missing master images: {missing_masters}")
print(f"Missing thumbnails: {missing_thumbs}")
print(f"Missing plugin thumbnails: {missing_plugin_thumbs}")
print(f"Total validation errors: {len(errors)}")

# Verify CREDITS.md
with open(CREDITS_MD, 'r', encoding='utf-8') as f:
    credits_content = f.read()

credits_lines = [l for l in credits_content.splitlines() if l.startswith('| ') and not l.startswith('| Title') and not l.startswith('|---')]
print(f"Total entries in CREDITS.md: {len(credits_lines)}")

if len(errors) == 0 and len(credits_lines) == len(catalog):
    print("\n[SUCCESS] Catalog integrity 100% verified!")
else:
    print(f"\n[FAILURE] Found {len(errors)} issues.")
    for err in errors[:10]:
        print("  -", err)
