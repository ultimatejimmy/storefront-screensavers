#!/usr/bin/env python3
"""
tools/build_thumbnails.py

High-performance, e-ink optimized screensaver thumbnail generator.
Outsources all heavy image resizing, alpha compositing, and quantization
to GitHub Actions / CI and offline tools.

Outputs standardized 180x240 thumbnails:
- Native screensavers: images/thumbnails/<id>.jpg (and images/thumbnails/plugin/<id>.png)
- ReaderBackdrop: images/thumbnails/rb/<id>.jpg
Target file size: ~10-16 KB per thumbnail (down from 1.35 MB!).
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageOps

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(REPO_ROOT, "images")
THUMBS_DIR = os.path.join(IMAGES_DIR, "thumbnails")
PLUGIN_THUMBS_DIR = os.path.join(THUMBS_DIR, "plugin")
RB_THUMBS_DIR = os.path.join(THUMBS_DIR, "rb")

TARGET_W = 180
TARGET_H = 240
JPEG_QUALITY = 82
CHECKERBOARD_TILE = 8
CB_LIGHT = (255, 255, 255)
CB_DARK = (216, 216, 216)


def make_checkerboard(w, h, tile=CHECKERBOARD_TILE):
    bg = Image.new("RGB", (w, h), CB_LIGHT)
    pixels = bg.load()
    for y in range(h):
        cy = y // tile
        for x in range(w):
            cx = x // tile
            if (cx + cy) % 2 != 0:
                pixels[x, y] = CB_DARK
    return bg


def has_alpha_channel(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        # Check if any pixel is actually transparent
        im_rgba = im.convert("RGBA")
        alpha = im_rgba.split()[3]
        min_a, max_a = alpha.getextrema()
        return min_a < 250
    return False


def render_thumbnail(im, is_transparent=False):
    """Resizes and composites an image to standard 180x240 preserving full RGB color."""
    actual_trans = is_transparent or has_alpha_channel(im)
    if actual_trans and has_alpha_channel(im):
        im_rgba = im.convert("RGBA")
        # Fit inside 180x240 with aspect ratio preserved
        im_rgba.thumbnail((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
        bg = make_checkerboard(TARGET_W, TARGET_H)
        x = (TARGET_W - im_rgba.width) // 2
        y = (TARGET_H - im_rgba.height) // 2
        bg.paste(im_rgba, (x, y), im_rgba)
        return bg, True
    else:
        im_rgb = im.convert("RGB")
        # Direct resize if aspect ratio already matches 3:4 portrait (within 2%)
        if abs((im_rgb.width / im_rgb.height) - (TARGET_W / TARGET_H)) < 0.02:
            resized = im_rgb.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
            return resized, False
        else:
            # Aspect-preserving downscale without cropping away artwork
            im_rgb.thumbnail((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
            bg = Image.new("RGB", (TARGET_W, TARGET_H), (255, 255, 255))
            x = (TARGET_W - im_rgb.width) // 2
            y = (TARGET_H - im_rgb.height) // 2
            bg.paste(im_rgb, (x, y))
            return bg, False


def save_thumbnail(thumb_img, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    tmp_path = dest_path + ".tmp"
    if dest_path.lower().endswith(".png"):
        thumb_img.save(tmp_path, "PNG", optimize=True)
    else:
        thumb_img.save(tmp_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(tmp_path, dest_path)


def process_single_image(src_path, dest_path, is_transparent=False):
    try:
        with Image.open(src_path) as im:
            thumb_img, _ = render_thumbnail(im, is_transparent)
            save_thumbnail(thumb_img, dest_path)
        return True, None
    except Exception as e:
        return False, str(e)


def process_native_screensavers(force=False, limit=None):
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(PLUGIN_THUMBS_DIR, exist_ok=True)

    json_path = os.path.join(REPO_ROOT, "screensavers.json")
    transparent_ids = set()
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                cat = json.load(f)
            items = cat if isinstance(cat, list) else cat.get("screensavers", [])
            for it in items:
                cat_field = it.get("category", "")
                cat_str = " ".join(cat_field) if isinstance(cat_field, list) else str(cat_field)
                if "transparent" in cat_str.lower():
                    transparent_ids.add(str(it.get("id")))
        except Exception:
            pass

    candidates = []
    for f in os.listdir(IMAGES_DIR):
        src_path = os.path.join(IMAGES_DIR, f)
        if not os.path.isfile(src_path) or f.startswith("."):
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            continue

        item_id = os.path.splitext(f)[0]
        is_transparent = item_id in transparent_ids
        target_ext = ".png" if ext == ".png" else ".jpg"
        target_thumb = os.path.join(THUMBS_DIR, f"{item_id}{target_ext}")

        if force or not os.path.exists(target_thumb) or os.path.getmtime(src_path) > os.path.getmtime(target_thumb):
            candidates.append((src_path, target_thumb, is_transparent, item_id))

    if limit:
        candidates = candidates[:limit]

    print(f"[*] Processing {len(candidates)} native screensavers...")
    success = 0
    errors = 0
    for src_path, target_thumb, is_trans, item_id in candidates:
        ok, err = process_single_image(src_path, target_thumb, is_trans)
        if ok:
            success += 1
            if is_trans or target_thumb.endswith(".png"):
                # Also generate plugin checkerboard thumbnail
                plugin_dest = os.path.join(PLUGIN_THUMBS_DIR, f"{item_id}.png")
                process_single_image(src_path, plugin_dest, is_transparent=True)
        else:
            errors += 1
            print(f"[-] Error processing {src_path}: {err}")

    print(f"[+] Native processing complete: {success} generated, {errors} errors.")
    return success, errors


def download_and_process_rb_item(item, timeout=12):
    item_id = item.get("id")
    if not item_id:
        return False, "missing id"

    dest_path = os.path.join(RB_THUMBS_DIR, f"{item_id}.jpg")
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return True, "already exists"

    url = item.get("fullUrl")
    if not url:
        return False, "no fullUrl"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Storefront-Thumbnailer/2.0"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        import io
        with Image.open(io.BytesIO(data)) as im:
            thumb_img, _ = render_thumbnail(im, is_transparent=False)
            save_thumbnail(thumb_img, dest_path)
        return True, "success"
    except Exception as e:
        return False, f"{url}: {e}"


def process_readerbackdrop(workers=20, limit=None, force=False):
    os.makedirs(RB_THUMBS_DIR, exist_ok=True)
    rb_path = os.path.join(REPO_ROOT, "readerbackdrop.json")
    if not os.path.exists(rb_path):
        rb_path = os.path.join(REPO_ROOT, "readerbackdrop.lite.json")

    if not os.path.exists(rb_path):
        print(f"[-] ReaderBackdrop catalog not found at {rb_path}")
        return 0, 0

    with open(rb_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get("items", [])

    pending = []
    for it in items:
        item_id = it.get("id")
        if not item_id:
            continue
        dest_path = os.path.join(RB_THUMBS_DIR, f"{item_id}.jpg")
        if force or not os.path.exists(dest_path) or os.path.getsize(dest_path) < 1000:
            pending.append(it)

    total_pending = len(pending)
    if limit:
        pending = pending[:limit]

    print(f"[*] ReaderBackdrop: {total_pending} missing thumbnails out of {len(items)} items. Processing {len(pending)} with {workers} workers...")
    if not pending:
        print("[+] All ReaderBackdrop thumbnails are up to date.")
        return 0, 0

    success = 0
    failed = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(download_and_process_rb_item, it): it for it in pending}
        for idx, fut in enumerate(as_completed(futures), start=1):
            it = futures[fut]
            try:
                ok, status = fut.result()
                if ok:
                    success += 1
                else:
                    failed += 1
                    if failed <= 5 or failed % 50 == 0:
                        print(f"[-] Failed ({failed}): {status}")
            except Exception as e:
                failed += 1
                print(f"[-] Exception on {it.get('id')}: {e}")

            if idx % 50 == 0 or idx == len(pending):
                elapsed = time.time() - t0
                rate = idx / elapsed if elapsed > 0 else 0
                print(f"    [{idx}/{len(pending)}] {success} succeeded, {failed} failed ({rate:.1f} items/sec)")

    elapsed = time.time() - t0
    print(f"[+] ReaderBackdrop complete: {success} generated, {failed} failed in {elapsed:.1f}s.")
    return success, failed


def check_status():
    rb_thumbs = [f for f in os.listdir(RB_THUMBS_DIR) if os.path.isfile(os.path.join(RB_THUMBS_DIR, f))] if os.path.exists(RB_THUMBS_DIR) else []
    native_thumbs = [f for f in os.listdir(THUMBS_DIR) if os.path.isfile(os.path.join(THUMBS_DIR, f))] if os.path.exists(THUMBS_DIR) else []
    plugin_thumbs = [f for f in os.listdir(PLUGIN_THUMBS_DIR) if os.path.isfile(os.path.join(PLUGIN_THUMBS_DIR, f))] if os.path.exists(PLUGIN_THUMBS_DIR) else []

    print("=== Thumbnail Status Report ===")
    print(f"Native Thumbnails: {len(native_thumbs)}")
    print(f"Plugin Thumbnails: {len(plugin_thumbs)}")
    print(f"ReaderBackdrop Thumbnails: {len(rb_thumbs)}")

    # Check weights
    def stats(file_list, folder):
        if not file_list:
            return "N/A"
        sizes = [os.path.getsize(os.path.join(folder, f)) for f in file_list]
        avg = sum(sizes) / len(sizes) / 1024
        max_s = max(sizes) / 1024
        return f"avg {avg:.1f} KB, max {max_s:.1f} KB"

    print(f"Native Thumbnail Stats: {stats(native_thumbs, THUMBS_DIR)}")
    print(f"ReaderBackdrop Stats:   {stats(rb_thumbs, RB_THUMBS_DIR)}")


def main():
    parser = argparse.ArgumentParser(description="Build e-ink optimized screensaver thumbnails.")
    parser.add_argument("--native", action="store_true", help="Process native screensavers")
    parser.add_argument("--readerbackdrop", action="store_true", help="Process ReaderBackdrop screensavers")
    parser.add_argument("--all", action="store_true", help="Process both native and ReaderBackdrop")
    parser.add_argument("--check", action="store_true", help="Check thumbnail status and exit")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if thumbnail exists")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items to process")
    parser.add_argument("--workers", type=int, default=20, help="Number of concurrent download workers")

    args = parser.parse_args()

    if args.check:
        check_status()
        return

    if not args.native and not args.readerbackdrop and not args.all:
        args.all = True

    if args.native or args.all:
        process_native_screensavers(force=args.force, limit=args.limit)

    if args.readerbackdrop or args.all:
        process_readerbackdrop(workers=args.workers, limit=args.limit, force=args.force)

    check_status()


if __name__ == "__main__":
    main()
