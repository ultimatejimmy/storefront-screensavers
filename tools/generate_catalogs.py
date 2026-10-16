#!/usr/bin/env python3
"""
tools/generate_catalogs.py

Builds optimized screensaver catalogs:
1. screensavers.lite.json: Lightweight feed for KOReader e-readers (~115 KB)
   - Omits web-only URL fields (sourceUrl, licenseUrl, authorUrl, license, etc.)
   - Omits repeated full image URLs; stores only 'ext' if non-default ('png')
   - Omits empty strings, zero ratings, and default compatibility arrays
2. screensavers.min.json: Minified full catalog without whitespace
3. Cleans and normalizes screensavers.json (stripping empty string properties)
"""

import os
import json
import gzip
import sys
import urllib.request
import urllib.error
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_JSON = os.path.join(REPO_ROOT, "screensavers.json")
LITE_JSON = os.path.join(REPO_ROOT, "screensavers.lite.json")
MIN_JSON = os.path.join(REPO_ROOT, "screensavers.min.json")

BASE_IMG_URL = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/images"
RATINGS_API_URL = "https://storefront-vote.ultimatejimmy.workers.dev/ratings?fresh=1"

def fetch_live_ratings(timeout=10):
    try:
        req = urllib.request.Request(
            RATINGS_API_URL,
            headers={
                "User-Agent": "Storefront-Catalog-Generator/1.0",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict):
                    print(f"Fetched live ratings from worker ({len(data)} entries)")
                    return data
    except Exception as e:
        print(f"Warning: Could not fetch live ratings from worker ({e})", file=sys.stderr)
    return {}

def generate_catalogs(fetch_remote=True):
    if not os.path.exists(SRC_JSON):
        print(f"Error: {SRC_JSON} not found.", file=sys.stderr)
        return False

    with open(SRC_JSON, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    if not isinstance(catalog, list):
        print("Error: Expected catalog to be a JSON list.", file=sys.stderr)
        return False

    print(f"Loaded {len(catalog)} screensavers from {SRC_JSON}")

    ratings_map = {}
    if fetch_remote:
        ratings_map = fetch_live_ratings()

    cleaned_full = []
    lite_items = []

    for item in catalog:
        item_id = item.get("id", "")
        # Merge live download and rating metrics for Storefront screensavers
        r = ratings_map.get(item_id) or (ratings_map.get(item_id.lower()) if item_id else None)
        if r and isinstance(r, dict):
            live_dl = int(r.get("downloads") or 0)
            existing_dl = int(item.get("downloads") or 0)
            if live_dl > existing_dl:
                item["downloads"] = live_dl
            if "up" in r or "down" in r:
                up = int(r.get("up") or 0)
                down = int(r.get("down") or 0)
                item["likes"] = max(0, up - down)
            if "wilson" in r:
                item["wilson"] = r["wilson"]

        cleaned_item = {}
        for k, v in item.items():
            if v == "" or (k in ("downloads", "likes") and v == 0):
                continue
            cleaned_item[k] = v

        full_url = cleaned_item.get("fullUrl") or item.get("fullUrl") or ""
        ext = "png" if full_url.lower().endswith(".png") else "jpg"

        if "fullUrl" not in cleaned_item:
            cleaned_item["fullUrl"] = f"{BASE_IMG_URL}/{item['id']}.{ext}"
        if "thumbnailUrl" not in cleaned_item:
            cleaned_item["thumbnailUrl"] = f"{BASE_IMG_URL}/thumbnails/{item['id']}.{ext}"

        # Clean invalid pluginThumbnailUrl (e.g. pointing to jpg or not under /thumbnails/plugin/)
        plugin_url = cleaned_item.get("pluginThumbnailUrl")
        if plugin_url:
            if "/thumbnails/plugin/" not in plugin_url or plugin_url.lower().endswith(".jpg"):
                cleaned_item.pop("pluginThumbnailUrl", None)

        # Normalize category: merge Fine Art into Art and deduplicate
        cat = cleaned_item.get("category")
        if cat:
            if isinstance(cat, list):
                new_cat = []
                seen_cat = set()
                for c in cat:
                    c_str = str(c).strip()
                    if c_str.lower() == "fine art":
                        c_str = "Art"
                    if c_str and c_str.lower() not in seen_cat:
                        seen_cat.add(c_str.lower())
                        new_cat.append(c_str)
                cleaned_item["category"] = new_cat if len(new_cat) > 1 else (new_cat[0] if new_cat else "Art")
            elif isinstance(cat, str):
                cleaned_item["category"] = "Art" if cat.strip().lower() == "fine art" else cat.strip()

        # Handle featured and scheduled expiration
        today_str = datetime.now().strftime("%Y-%m-%d")
        is_featured = bool(cleaned_item.get("featured"))
        feat_until = cleaned_item.get("featuredUntil")
        if is_featured and feat_until:
            if str(feat_until).strip() < today_str:
                is_featured = False
                cleaned_item.pop("featured", None)
                cleaned_item.pop("featuredUntil", None)
                cleaned_item.pop("featuredPriority", None)

        if not is_featured:
            cleaned_item.pop("featured", None)
            cleaned_item.pop("featuredUntil", None)
            cleaned_item.pop("featuredPriority", None)

        cleaned_full.append(cleaned_item)

        lite_item = {
            "id": item["id"],
            "title": item.get("title") or item.get("name") or item["id"],
        }
        if item.get("author"):
            lite_item["author"] = item["author"]
        if cleaned_item.get("category"):
            lite_item["category"] = cleaned_item["category"]
        if item.get("tags"):
            lite_item["tags"] = item["tags"]
        if ext != "jpg":
            lite_item["ext"] = ext
        if cleaned_item.get("downloads"):
            lite_item["downloads"] = cleaned_item["downloads"]
        if cleaned_item.get("likes"):
            lite_item["likes"] = cleaned_item["likes"]
        if cleaned_item.get("dateAdded"):
            lite_item["dateAdded"] = cleaned_item["dateAdded"]
        if is_featured:
            lite_item["featured"] = 1
            if cleaned_item.get("featuredPriority"):
                lite_item["featuredPriority"] = cleaned_item["featuredPriority"]

        lite_items.append(lite_item)

    with open(SRC_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cleaned_full, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(MIN_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cleaned_full, f, separators=(",", ":"), ensure_ascii=False)

    # 4. Generate Unified Catalog if ReaderBackdrop is available
    rb_path = os.path.join(REPO_ROOT, "readerbackdrop.lite.json")
    if not os.path.exists(rb_path):
        rb_path = os.path.join(REPO_ROOT, "readerbackdrop.json")

    unified_items = list(lite_items)
    if os.path.exists(rb_path):
        try:
            with open(rb_path, "r", encoding="utf-8") as f_rb:
                rb_data = json.load(f_rb)
            if isinstance(rb_data, list) and len(rb_data) > 0:
                rb_items = []
                for rb_it in rb_data:
                    it_copy = dict(rb_it)
                    it_copy.pop("source", None)
                    it_id = it_copy.get("id")
                    # If thumbnailUrl is missing, identical to fullUrl, or matches the standard template,
                    # omit it from the lite feed because Storefront infers it automatically from id.
                    std_thumb = f"{BASE_IMG_URL}/thumbnails/rb/{it_id}.jpg" if it_id else ""
                    curr_thumb = it_copy.get("thumbnailUrl") or ""
                    if curr_thumb == std_thumb or curr_thumb == it_copy.get("fullUrl", ""):
                        it_copy.pop("thumbnailUrl", None)
                    rb_items.append(it_copy)

                sf_featured = [x for x in lite_items if x.get("featured") in (1, True)]
                sf_regular = [x for x in lite_items if x.get("featured") not in (1, True)]

                sf_featured.sort(
                    key=lambda x: (x.get("featuredPriority", 0), str(x.get("dateAdded", ""))),
                    reverse=True
                )
                sf_regular.sort(
                    key=lambda x: (x.get("downloads", 0), x.get("likes", 0)),
                    reverse=True
                )
                rb_items.sort(
                    key=lambda x: (x.get("downloads", 0), x.get("likes", 0)),
                    reverse=True
                )

                interleaved = []
                max_len = max(len(sf_regular), len(rb_items))
                for i in range(max_len):
                    if i < len(sf_regular):
                        interleaved.append(sf_regular[i])
                    if i < len(rb_items):
                        interleaved.append(rb_items[i])

                unified_items = sf_featured + interleaved
                print(f"Unified catalog generated: {len(unified_items)} total ({len(sf_featured)} featured, {len(sf_regular)} SF regular, {len(rb_items)} ReaderBackdrop)")
        except Exception as e:
            print(f"Warning: Failed to merge ReaderBackdrop: {e}", file=sys.stderr)

    UNIFIED_LITE_JSON = os.path.join(REPO_ROOT, "screensavers.unified.lite.json")
    with open(UNIFIED_LITE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(unified_items, f, separators=(",", ":"), ensure_ascii=False)

    # screensavers.lite.json provides the unified pre-sorted catalog
    with open(LITE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(unified_items, f, separators=(",", ":"), ensure_ascii=False)

    raw_size = os.path.getsize(SRC_JSON)
    min_size = os.path.getsize(MIN_JSON)
    lite_size = os.path.getsize(LITE_JSON)
    unified_size = os.path.getsize(UNIFIED_LITE_JSON)

    with open(LITE_JSON, "rb") as f_in:
        gz_lite = gzip.compress(f_in.read(), 9)

    print("\n--- Catalog Generation Summary ---")
    print(f"screensavers.json              : {raw_size:,} bytes ({raw_size/1024:.1f} KB)")
    print(f"screensavers.min.json          : {min_size:,} bytes ({min_size/1024:.1f} KB) - Savings: {(1 - min_size/raw_size)*100:.1f}%")
    print(f"screensavers.lite.json         : {lite_size:,} bytes ({lite_size/1024:.1f} KB)")
    print(f"screensavers.unified.lite.json : {unified_size:,} bytes ({unified_size/1024:.1f} KB)")
    print(f"screensavers.lite.json (gz)    : {len(gz_lite):,} bytes ({len(gz_lite)/1024:.1f} KB)\n")

    return True

if __name__ == "__main__":
    fetch_rem = "--no-remote" not in sys.argv
    success = generate_catalogs(fetch_remote=fetch_rem)
    sys.exit(0 if success else 1)
