#!/usr/bin/env python3
"""
tools/build_collection_covers.py

Generates professional, e-ink optimized covers for screensaver collections.
Outputs:
  - images/collections/<id>.jpg (600x800 full size)
  - images/collections/thumbnails/<id>.jpg (180x240 plugin & web thumb)

Layout options:
  - 'fan': 3 overlapping tilted cards with soft shadows (default)
  - 'grid': 2x2 mosaic of top wallpapers
  - 'hero': Large lead image with bottom thumbnails strip
"""

import os
import sys
import json
import math
import hashlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(REPO_ROOT, "images")
THUMBS_DIR = os.path.join(IMAGES_DIR, "thumbnails")
COLLECTIONS_JSON = os.path.join(REPO_ROOT, "collections.json")
COL_IMAGES_DIR = os.path.join(IMAGES_DIR, "collections")
COL_THUMBS_DIR = os.path.join(COL_IMAGES_DIR, "thumbnails")
FONTS_DIR = os.path.join(REPO_ROOT, "tools", "fonts")

TARGET_W = 600
TARGET_H = 800
THUMB_W = 180
THUMB_H = 240

os.makedirs(COL_IMAGES_DIR, exist_ok=True)
os.makedirs(COL_THUMBS_DIR, exist_ok=True)

def get_title_font(size, bold=True):
    font_name = "TitleFont-Bold.ttf" if bold else "TitleFont-Regular.ttf"
    font_path = os.path.join(FONTS_DIR, font_name)
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    try:
        return ImageFont.truetype("arial.ttf" if not bold else "arialbd.ttf", size)
    except Exception:
        return ImageFont.load_default()

def find_wallpaper_path(item_id):
    """Find local high-res master or thumbnail for an item id."""
    for ext in ["png", "jpg", "jpeg", "webp"]:
        master = os.path.join(IMAGES_DIR, f"{item_id}.{ext}")
        if os.path.exists(master):
            return master
    for ext in ["png", "jpg", "jpeg"]:
        thumb = os.path.join(THUMBS_DIR, f"{item_id}.{ext}")
        if os.path.exists(thumb):
            return thumb
    return None

def compute_collection_cover_hash(col):
    """Compute deterministic hash to detect if a cover needs rebuilding."""
    items_part = ",".join((col.get("items") or [])[:5])
    raw = f"v3_large_text:{col.get('id')}:{col.get('title')}:{col.get('coverMode')}:{col.get('coverLayout')}:{col.get('coverItemId')}:{items_part}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]

def extract_dominant_color(img, fallback=(24, 30, 42)):
    """Extract a pleasing muted dark background tone from the lead image."""
    try:
        small = img.convert("RGB").resize((48, 48), Image.Resampling.BOX)
        # Quantize to find dominant color
        pal = small.quantize(colors=8)
        palette = pal.getpalette()
        # Find dark-to-medium tones (avoid pure white or pure black)
        r, g, b = palette[0], palette[1], palette[2]
        # Darken tone for contrast
        r = int(r * 0.35 + 15)
        g = int(g * 0.35 + 20)
        b = int(b * 0.35 + 30)
        return (max(12, min(r, 60)), max(16, min(g, 65)), max(24, min(b, 85)))
    except Exception:
        return fallback

def load_and_fit_card(item_id, card_w, card_h):
    """Load an item image and fit it into a rounded card with a clean border."""
    path = find_wallpaper_path(item_id)
    if not path:
        # Fallback card
        card = Image.new("RGBA", (card_w, card_h), (35, 45, 60, 255))
        d = ImageDraw.Draw(card)
        d.text((card_w//2, card_h//2), "Storefront", fill=(120, 140, 160), anchor="mm")
        return card

    try:
        raw = Image.open(path)
        # If RGBA, flatten over neutral gray for transparent items
        if raw.mode == "RGBA":
            bg = Image.new("RGBA", raw.size, (240, 240, 245, 255))
            raw = Image.alpha_composite(bg, raw).convert("RGB")
        else:
            raw = raw.convert("RGB")

        fitted = ImageOps.fit(raw, (card_w, card_h), Image.Resampling.LANCZOS)
        card = fitted.convert("RGBA")

        # Draw a subtle inner border for crispness on dark/light backdrops
        draw = ImageDraw.Draw(card)
        draw.rectangle([(0, 0), (card_w - 1, card_h - 1)], outline=(255, 255, 255, 80), width=2)
        return card
    except Exception:
        card = Image.new("RGBA", (card_w, card_h), (35, 45, 60, 255))
        return card

def render_drop_shadow(size, offset=(0, 12), radius=16, shadow_color=(0, 0, 0, 140)):
    """Creates a soft blurred shadow matching the rotated card shape."""
    w, h = size
    shadow = Image.new("RGBA", (w + radius * 3, h + radius * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    d.rectangle([(radius, radius), (radius + w, radius + h)], fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
    return shadow

def fit_title_lines(draw, title, max_w, max_size=76, min_size=42):
    """Calculates maximized font size and wraps onto 2 lines if needed to stay large and readable."""
    # First try single line from max_size down to 48
    for sz in range(max_size, 46, -2):
        f = get_title_font(sz, bold=True)
        bbox = draw.textbbox((0, 0), title, font=f)
        if (bbox[2] - bbox[0]) <= max_w:
            return [title], f

    # If too long for 1 line, attempt a clean 2-line break with high font size (64px down to min_size)
    words = title.split()
    if len(words) > 1:
        for sz in range(64, min_size - 1, -2):
            f = get_title_font(sz, bold=True)
            for i in range(1, len(words)):
                l1 = " ".join(words[:i])
                l2 = " ".join(words[i:])
                b1 = draw.textbbox((0, 0), l1, font=f)
                b2 = draw.textbbox((0, 0), l2, font=f)
                if (b1[2] - b1[0]) <= max_w and (b2[2] - b2[0]) <= max_w:
                    return [l1, l2], f

    # Fallback to single line scaled
    for sz in range(46, 32, -2):
        f = get_title_font(sz, bold=True)
        bbox = draw.textbbox((0, 0), title, font=f)
        if (bbox[2] - bbox[0]) <= max_w:
            return [title], f
    return [title], get_title_font(32, bold=True)

def overlay_title_banner(base_img, title, count_text, curator=None):
    """Draws a bold, high-contrast title band at the bottom with crystal-clear e-ink legibility."""
    w, h = base_img.size
    banner_h = 260
    banner_y = h - banner_h

    # Pure solid high-contrast dark banner (zero semi-transparent dithering on e-ink)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([(0, banner_y), (w, h)], fill=(10, 12, 16, 255))
    # Crisp 4px top separator line (accent cyan / white)
    d.line([(0, banner_y), (w, banner_y)], fill=(56, 189, 248, 255), width=4)

    composited = Image.alpha_composite(base_img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(composited)

    pad_x = 32
    max_text_w = w - (pad_x * 2)

    # 1. Kicker / Badge (e.g. "C U R A T E D   C O L L E C T I O N")
    kicker_font = get_title_font(22, bold=True)
    kicker_text = "C U R A T E D   C O L L E C T I O N"
    kicker_y = banner_y + 22
    draw.text((pad_x, kicker_y), kicker_text, font=kicker_font, fill=(56, 189, 248, 255))

    # 2. Large Bold Title (starts at 76px!)
    title_lines, title_font = fit_title_lines(draw, title, max_text_w, max_size=76, min_size=42)

    line_height = title_font.size + 8
    if len(title_lines) == 1:
        title_y = banner_y + 58
        draw.text((pad_x, title_y), title_lines[0], font=title_font, fill=(255, 255, 255, 255))
        next_y = title_y + title_font.size + 18
    else:
        title_y = banner_y + 54
        for l_idx, line in enumerate(title_lines):
            draw.text((pad_x, title_y + (l_idx * line_height)), line, font=title_font, fill=(255, 255, 255, 255))
        next_y = title_y + (len(title_lines) * line_height) + 14

    # 3. Subtitle / Metadata (Large 28px bold high-contrast text)
    curator_str = f"Curated by {curator}" if curator and curator.lower() != "maintainer" else "Featured Set"
    meta_text = f"{count_text}  •  {curator_str}"
    meta_font = get_title_font(28, bold=True)
    draw.text((pad_x, next_y), meta_text, font=meta_font, fill=(240, 244, 252, 255))

    return composited.convert("RGB")

def build_fan_cover(col, items):
    """Layout: Fan of 3 overlapping cards with gentle rotation."""
    base = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 20, 30, 255))

    # Background gradient
    lead_path = find_wallpaper_path(items[0]) if items else None
    dom = (20, 26, 38)
    if lead_path:
        try:
            with Image.open(lead_path) as im:
                dom = extract_dominant_color(im)
        except Exception:
            pass

    # Draw vertical subtle gradient
    d = ImageDraw.Draw(base)
    for y in range(TARGET_H):
        ratio = y / float(TARGET_H)
        r = int(dom[0] * (1.2 - ratio * 0.5))
        g = int(dom[1] * (1.2 - ratio * 0.5))
        b = int(dom[2] * (1.2 - ratio * 0.5))
        d.line([(0, y), (TARGET_W, y)], fill=(r, g, b, 255))

    card_w, card_h = 240, 340
    center_x = TARGET_W // 2
    center_y = 270

    cards_to_show = items[:3]
    while len(cards_to_show) < 3 and len(cards_to_show) > 0:
        cards_to_show.append(cards_to_show[0])

    if cards_to_show:
        # Card 1 (Left, rotated -9 deg)
        c1 = load_and_fit_card(cards_to_show[0], card_w, card_h)
        rot1 = c1.rotate(9, expand=True, resample=Image.Resampling.BICUBIC)
        # Card 2 (Right, rotated +9 deg)
        c2 = load_and_fit_card(cards_to_show[1] if len(cards_to_show) > 1 else cards_to_show[0], card_w, card_h)
        rot2 = c2.rotate(-9, expand=True, resample=Image.Resampling.BICUBIC)
        # Card 3 (Center, slight tilt -1 deg, on top)
        c3 = load_and_fit_card(cards_to_show[2] if len(cards_to_show) > 2 else cards_to_show[0], card_w, card_h)
        rot3 = c3.rotate(1, expand=True, resample=Image.Resampling.BICUBIC)

        # Paste 1 (left)
        pos1 = (center_x - 175 - rot1.width // 2, center_y - rot1.height // 2 + 10)
        base.paste(rot1, pos1, rot1)

        # Paste 2 (right)
        pos2 = (center_x + 175 - rot2.width // 2, center_y - rot2.height // 2 + 10)
        base.paste(rot2, pos2, rot2)

        # Paste 3 (center top)
        pos3 = (center_x - rot3.width // 2, center_y - rot3.height // 2 - 10)
        base.paste(rot3, pos3, rot3)

    title = col.get("title") or "Collection"
    count_text = f"{len(items)} Screensavers"
    curator = col.get("curator")
    return overlay_title_banner(base, title, count_text, curator)

def build_grid_cover(col, items):
    """Layout: 2x2 grid of wallpapers."""
    base = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 20, 30, 255))
    gw = 276
    gh = 245
    pad = 16

    top_items = items[:4]
    while len(top_items) < 4 and len(top_items) > 0:
        top_items.append(top_items[0])

    coords = [
        (pad, pad),
        (pad + gw + pad, pad),
        (pad, pad + gh + pad),
        (pad + gw + pad, pad + gh + pad),
    ]

    for idx, i_id in enumerate(top_items[:4]):
        card = load_and_fit_card(i_id, gw, gh)
        base.paste(card, coords[idx], card)

    title = col.get("title") or "Collection"
    count_text = f"{len(items)} Screensavers"
    curator = col.get("curator")
    return overlay_title_banner(base, title, count_text, curator)

def build_hero_cover(col, items):
    """Layout: Large lead image covering top 60% with strip below."""
    base = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 20, 30, 255))

    lead_id = items[0] if items else None
    if lead_id:
        lead_card = load_and_fit_card(lead_id, TARGET_W - 32, 345)
        base.paste(lead_card, (16, 16), lead_card)

    # Strip of next 3 wallpapers
    strip_items = items[1:4]
    if strip_items:
        sw = (TARGET_W - 48) // 3
        sh = 140
        for idx, sid in enumerate(strip_items):
            thumb_c = load_and_fit_card(sid, sw, sh)
            base.paste(thumb_c, (16 + idx * (sw + 8), 377), thumb_c)

    title = col.get("title") or "Collection"
    count_text = f"{len(items)} Screensavers"
    curator = col.get("curator")
    return overlay_title_banner(base, title, count_text, curator)

def build_item_cover(col, items):
    """Layout: Single chosen wallpaper with title banner overlay."""
    base = Image.new("RGBA", (TARGET_W, TARGET_H), (15, 20, 30, 255))
    target_id = col.get("coverItemId") or (items[0] if items else None)
    if target_id:
        card = load_and_fit_card(target_id, TARGET_W, TARGET_H)
        base.paste(card, (0, 0), card)

    title = col.get("title") or "Collection"
    count_text = f"{len(items)} Screensavers"
    curator = col.get("curator")
    return overlay_title_banner(base, title, count_text, curator)

def generate_cover_for_collection(col, force=False):
    """Generates 600x800 and 180x240 covers for a collection if hash changed."""
    col_id = col.get("id")
    if not col_id:
        return False, None

    out_full = os.path.join(COL_IMAGES_DIR, f"{col_id}.jpg")
    out_thumb = os.path.join(COL_THUMBS_DIR, f"{col_id}.jpg")

    new_hash = compute_collection_cover_hash(col)
    if not force and col.get("coverHash") == new_hash and os.path.exists(out_full) and os.path.exists(out_thumb):
        return False, new_hash

    mode = col.get("coverMode") or "auto"
    layout = col.get("coverLayout") or "fan"
    items = col.get("items") or []

    # If mode is upload and full image already exists, just regenerate thumbnail
    if mode == "upload" and os.path.exists(out_full):
        try:
            with Image.open(out_full) as im:
                thumb = im.convert("RGB").resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
                thumb.save(out_thumb, "JPEG", quality=82, optimize=True)
            return True, new_hash
        except Exception as e:
            print(f"Error making thumb for uploaded cover {col_id}: {e}")

    # Generate full cover based on mode and layout
    if mode == "item":
        full_img = build_item_cover(col, items)
    elif layout == "grid":
        full_img = build_grid_cover(col, items)
    elif layout == "hero":
        full_img = build_hero_cover(col, items)
    else:  # default 'fan'
        full_img = build_fan_cover(col, items)

    # Save 600x800 full cover
    full_img.save(out_full, "JPEG", quality=85, optimize=True)

    # Generate and save 180x240 thumbnail
    thumb_img = full_img.resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
    thumb_img.save(out_thumb, "JPEG", quality=82, optimize=True)

    return True, new_hash

def build_all_collection_covers(force=False):
    """Scan collections.json and generate covers for all collections."""
    if not os.path.exists(COLLECTIONS_JSON):
        return 0

    with open(COLLECTIONS_JSON, "r", encoding="utf-8") as f:
        collections = json.load(f)

    if not isinstance(collections, list):
        return 0

    updated_count = 0
    modified = False

    for col in collections:
        did_build, new_hash = generate_cover_for_collection(col, force=force)
        if did_build:
            col["coverHash"] = new_hash
            updated_count += 1
            modified = True
            print(f"[Cover] Generated {col.get('id')} ({col.get('coverLayout', 'fan')})")

    if modified:
        with open(COLLECTIONS_JSON, "w", encoding="utf-8", newline="\n") as f_out:
            json.dump(collections, f_out, indent=2, ensure_ascii=False)
            f_out.write("\n")

    print(f"Collection covers built: {updated_count} updated, {len(collections)} total")
    return updated_count

def build_ai_prompt_for_collection(col, catalog_map=None):
    title = col.get("title") or "Collection"
    desc = col.get("description") or ""
    tags = set()
    categories = set()
    if catalog_map:
        for item_id in (col.get("items") or [])[:8]:
            it = catalog_map.get(item_id)
            if it:
                for t in it.get("tags") or []:
                    tags.add(t)
                cat = it.get("category")
                if isinstance(cat, list):
                    categories.update(cat)
                elif isinstance(cat, str):
                    categories.add(cat)

    tag_str = ", ".join(list(tags)[:6])
    cat_str = ", ".join(list(categories)[:3])

    prompt = f"Minimalist, elegant book cover illustration for a theme called '{title}'."
    if desc:
        prompt += f" Theme context: {desc}."
    if cat_str:
        prompt += f" Style influences: {cat_str}."
    if tag_str:
        prompt += f" Visual elements: {tag_str}."
    prompt += " High-contrast composition, striking silhouettes, clean fine lines, beautiful typography-ready background, vertical 3:4 portrait poster, no text, no lettering, no words, no signatures."
    return prompt

def generate_ai_cover(col, api_key=None, catalog_map=None):
    """Generate cover image using Gemini Image API and composite title overlay."""
    key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
    prompt = build_ai_prompt_for_collection(col, catalog_map)
    if not key:
        return False, "GEMINI_API_KEY environment variable is not configured on the studio host.", prompt

    # Try the newest Flash image models in order
    candidate_models = [
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-lite-image",
        "gemini-2.5-flash-image"
    ]

    import urllib.request
    import urllib.error
    import base64
    from io import BytesIO

    last_error = None
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates") or []
            b64_bytes = None
            for cand in candidates:
                parts = (cand.get("content") or {}).get("parts") or []
                for part in parts:
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline and inline.get("data"):
                        b64_bytes = inline["data"]
                        break
                if b64_bytes:
                    break

            if not b64_bytes:
                continue

            img_raw = Image.open(BytesIO(base64.b64decode(b64_bytes))).convert("RGB")
            img_fitted = ImageOps.fit(img_raw, (TARGET_W, TARGET_H), Image.Resampling.LANCZOS)

            title = col.get("title") or "Collection"
            items = col.get("items") or []
            count_text = f"{len(items)} Screensavers"
            curator = col.get("curator")
            full_img = overlay_title_banner(img_fitted, title, count_text, curator)

            col_id = col["id"]
            out_full = os.path.join(COL_IMAGES_DIR, f"{col_id}.jpg")
            out_thumb = os.path.join(COL_THUMBS_DIR, f"{col_id}.jpg")

            full_img.save(out_full, "JPEG", quality=85, optimize=True)
            thumb_img = full_img.resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
            thumb_img.save(out_thumb, "JPEG", quality=82, optimize=True)

            new_hash = compute_collection_cover_hash(col)
            return True, new_hash, prompt
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_body = e.read().decode("utf-8")
                err_data = json.loads(err_body)
                err_msg = err_data.get("error", {}).get("message", "")
            except Exception:
                pass

            if e.code == 429 or "quota" in err_msg.lower() or "resource_exhausted" in err_msg.lower():
                last_error = f"Google Gemini API quota limit is 0 for image generation on the free tier. To enable, link a billing account in Google AI Studio, or use 'Copy AI Prompt' to generate artwork in Gemini Web / Midjourney and upload with 'Upload Image'."
            elif e.code == 404:
                last_error = f"Model {model_name} is not enabled on your API key."
            else:
                last_error = f"Gemini API error ({e.code}): {err_msg or e.reason}"
        except Exception as e:
            last_error = f"AI generation error: {e}"

    return False, last_error or "Failed to generate image with Gemini Image models.", prompt

if __name__ == "__main__":
    force_build = "--force" in sys.argv
    build_all_collection_covers(force=force_build)
