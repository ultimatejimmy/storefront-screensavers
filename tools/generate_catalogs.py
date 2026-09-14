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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_JSON = os.path.join(REPO_ROOT, "screensavers.json")
LITE_JSON = os.path.join(REPO_ROOT, "screensavers.lite.json")
MIN_JSON = os.path.join(REPO_ROOT, "screensavers.min.json")

BASE_IMG_URL = "https://raw.githubusercontent.com/ultimatejimmy/storefront-screensavers/main/images"

def generate_catalogs():
    if not os.path.exists(SRC_JSON):
        print(f"Error: {SRC_JSON} not found.", file=sys.stderr)
        return False

    with open(SRC_JSON, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    if not isinstance(catalog, list):
        print("Error: Expected catalog to be a JSON list.", file=sys.stderr)
        return False

    print(f"Loaded {len(catalog)} screensavers from {SRC_JSON}")

    cleaned_full = []
    lite_items = []

    for item in catalog:
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

        cleaned_full.append(cleaned_item)

        lite_item = {
            "id": item["id"],
            "title": item.get("title") or item.get("name") or item["id"],
        }
        if item.get("author"):
            lite_item["author"] = item["author"]
        if item.get("category"):
            lite_item["category"] = item["category"]
        if item.get("tags"):
            lite_item["tags"] = item["tags"]
        if ext != "jpg":
            lite_item["ext"] = ext

        lite_items.append(lite_item)

    with open(SRC_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cleaned_full, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(MIN_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cleaned_full, f, separators=(",", ":"), ensure_ascii=False)

    with open(LITE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lite_items, f, separators=(",", ":"), ensure_ascii=False)

    raw_size = os.path.getsize(SRC_JSON)
    min_size = os.path.getsize(MIN_JSON)
    lite_size = os.path.getsize(LITE_JSON)

    with open(LITE_JSON, "rb") as f_in:
        gz_lite = gzip.compress(f_in.read(), 9)

    print("\n--- Catalog Generation Summary ---")
    print(f"screensavers.json      : {raw_size:,} bytes ({raw_size/1024:.1f} KB)")
    print(f"screensavers.min.json  : {min_size:,} bytes ({min_size/1024:.1f} KB) - Savings: {(1 - min_size/raw_size)*100:.1f}%")
    print(f"screensavers.lite.json : {lite_size:,} bytes ({lite_size/1024:.1f} KB) - Savings: {(1 - lite_size/raw_size)*100:.1f}%")
    print(f"screensavers.lite.json (gzipped): {len(gz_lite):,} bytes ({len(gz_lite)/1024:.1f} KB) - Savings: {(1 - len(gz_lite)/raw_size)*100:.1f}%\n")

    return True

if __name__ == "__main__":
    success = generate_catalogs()
    sys.exit(0 if success else 1)
