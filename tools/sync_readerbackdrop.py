#!/usr/bin/env python3
"""
tools/sync_readerbackdrop.py

Fetches the complete public catalog of wallpapers from ReaderBackdrop (https://www.readerbackdrop.com),
normalizes entries into the Storefront screensaver schema, and generates:
  - readerbackdrop.json: Full metadata catalog
  - readerbackdrop.lite.json: Lightweight feed for KOReader e-readers
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Set

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FULL_JSON = os.path.join(REPO_ROOT, "readerbackdrop.json")
OUT_LITE_JSON = os.path.join(REPO_ROOT, "readerbackdrop.lite.json")

API_BASE_URL = "https://www.readerbackdrop.com/api/images"
USER_AGENT = "Storefront-Screensaver-Sync/1.0 (+https://github.com/ultimatejimmy/storefront-screensavers)"


def map_category(tags: List[str], device: str) -> str:
    """Maps ReaderBackdrop tags and device info to Storefront categories."""
    tag_str = " ".join(t.lower() for t in tags)
    device_lower = device.lower()

    if "transparent" in tag_str or "overlay" in tag_str:
        return "Transparent"
    if any(k in tag_str for k in ["space", "astronomy", "sci-fi", "scifi", "cyberpunk", "futuristic", "galaxy"]):
        return "Sci-Fi"
    if any(k in tag_str for k in ["anime", "manga", "ghibli", "pokemon", "zelda", "pixel art"]):
        return "Anime"
    if any(k in tag_str for k in ["quote", "typography", "text", "poem", "poetry", "reading", "words"]):
        return "Quotes"
    if any(k in tag_str for k in ["nature", "landscape", "mountain", "forest", "tree", "ocean", "sea", "beach", "botanical", "flower", "cat", "dog", "animal", "bird", "wildlife", "lake"]):
        return "Nature"
    if any(k in tag_str for k in ["minimalist", "minimal", "simple", "clean", "black and white", "monochrome", "silhouette", "line art"]):
        return "Minimalist"
    if any(k in tag_str for k in ["architecture", "building", "city", "urban", "street", "bridge", "house", "interior"]):
        return "Architecture"
    if any(k in tag_str for k in ["fantasy", "dragon", "magic", "mythology", "castle", "medieval"]):
        return "Fantasy"
    if any(k in tag_str for k in ["abstract", "geometric", "pattern", "dark", "texture"]):
        return "Abstract"
    if any(k in tag_str for k in ["art", "illustration", "painting", "drawing", "woodblock", "traditional", "fine art", "sketch", "vintage"]):
        return "Art"

    return "Art"


def map_compatibility(device: str) -> List[str]:
    """Infers device compatibility based on ReaderBackdrop device metadata."""
    if not device:
        return ["Kindle", "Kobo", "Boox", "PocketBook"]

    dev_lower = device.lower()
    comp = []
    if "kindle" in dev_lower:
        comp.append("Kindle")
    if "kobo" in dev_lower:
        comp.append("Kobo")
    if "boox" in dev_lower:
        comp.append("Boox")
    if "pocketbook" in dev_lower:
        comp.append("PocketBook")

    if not comp:
        comp = ["Kindle", "Kobo", "Boox", "PocketBook"]
    elif len(comp) == 1:
        # Most e-reader screensavers are interchangeable if aspect ratios are similar
        if "Kindle" in comp and "Kobo" not in comp:
            comp.extend(["Kobo", "Boox", "PocketBook"])
        elif "Kobo" in comp and "Kindle" not in comp:
            comp.extend(["Kindle", "Boox", "PocketBook"])

    return comp


def fetch_page(page: int, limit: int = 50, retries: int = 3) -> Dict[str, Any]:
    url = f"{API_BASE_URL}?sortBy=downloads&limit={limit}&page={page}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
    )

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(1.5 * attempt)
            else:
                raise e
    return {}


def sync_all(max_pages: int = None) -> bool:
    print(f"Starting ReaderBackdrop sync from {API_BASE_URL}...")
    page = 1
    limit = 50
    total_images_processed = 0
    seen_ids: Set[str] = set()
    full_items: List[Dict[str, Any]] = []
    lite_items: List[Dict[str, Any]] = []

    while True:
        try:
            data = fetch_page(page, limit)
        except Exception as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)
            break

        images = data.get("images", [])
        total = data.get("total", 0)
        total_pages = data.get("totalPages", 1)

        if not images:
            break

        for img in images:
            img_id = str(img.get("id", "")).strip()
            if not img_id or img_id in seen_ids:
                continue

            # Filter out NSFW entries
            if img.get("isNSFW", False):
                continue

            raw_tags = img.get("tags") or []
            tag_names = []
            is_nsfw_tag = False
            for t in raw_tags:
                if isinstance(t, dict):
                    name = str(t.get("name", "")).strip().lower()
                else:
                    name = str(t).strip().lower()
                if name:
                    if name == "nsfw":
                        is_nsfw_tag = True
                        break
                    tag_names.append(name)

            if is_nsfw_tag:
                continue

            seen_ids.add(img_id)

            title = str(img.get("title", "")).strip()
            if not title:
                title = f"ReaderBackdrop #{img_id}"

            user_obj = img.get("user") or {}
            user_name = str(user_obj.get("name", "")).strip()
            author = f"{user_name} (ReaderBackdrop)" if user_name else "Community (ReaderBackdrop)"

            device = str(img.get("device", "")).strip()
            category = map_category(tag_names, device)
            compatibility = map_compatibility(device)

            image_url = str(img.get("imageUrl", "")).strip()
            if not image_url:
                image_url = f"https://www.readerbackdrop.com/api/images/{img_id}/download"

            thumb_url = str(img.get("thumbnailUrl", "")).strip()
            if not thumb_url:
                thumb_url = image_url

            ext = "png" if (image_url.lower().endswith(".png") or category == "Transparent") else "jpg"
            downloads = int(img.get("downloads") or 0)
            views = int(img.get("views") or 0)

            item_id = f"rb-{img_id}"

            full_entry = {
                "id": item_id,
                "title": title,
                "author": author,
                "category": category,
                "compatibility": compatibility,
                "thumbnailUrl": thumb_url,
                "fullUrl": image_url,
                "license": "ReaderBackdrop Community Share",
                "attribution": author,
                "source": "ReaderBackdrop",
                "tags": tag_names,
                "downloads": downloads,
                "views": views,
                "device": device,
                "ext": ext,
                "createdAt": img.get("createdAt", ""),
            }
            full_items.append(full_entry)

            lite_entry = {
                "id": item_id,
                "title": title,
                "author": author,
                "category": category,
                "tags": tag_names,
                "fullUrl": image_url,
                "downloads": downloads,
                "ext": ext,
                "source": "ReaderBackdrop",
            }
            if thumb_url and thumb_url != image_url:
                lite_entry["thumbnailUrl"] = thumb_url
            lite_items.append(lite_entry)
            total_images_processed += 1

        print(f"Processed page {page}/{total_pages} ({len(full_items)} items total)...")

        if max_pages and page >= max_pages:
            break
        if page >= total_pages:
            break

        page += 1
        time.sleep(0.12)  # Polite throttle

    print(f"\nSync finished. Writing {len(full_items)} items to disk...")

    with open(OUT_FULL_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(full_items, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(OUT_LITE_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lite_items, f, separators=(",", ":"), ensure_ascii=False)

    full_mb = os.path.getsize(OUT_FULL_JSON) / (1024 * 1024)
    lite_kb = os.path.getsize(OUT_LITE_JSON) / 1024

    print(f"Generated {OUT_FULL_JSON} ({full_mb:.2f} MB)")
    print(f"Generated {OUT_LITE_JSON} ({lite_kb:.1f} KB)")
    return True


if __name__ == "__main__":
    max_p = int(sys.argv[1]) if len(sys.argv) > 1 else None
    sync_all(max_pages=max_p)
