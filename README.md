![GitHub Pages](https://img.shields.io/badge/hosted--on-GitHub%20Pages-purple.svg)
# Storefront E-Reader Screensavers & Wallpaper Catalog

A community-driven, curated catalog of e-ink screensavers and lock screen wallpapers for Kindle, Kobo, Boox, PocketBook, and other e-readers. Powered by the [Storefront KOReader Plugin](https://github.com/ultimatejimmy/storefront.koplugin).

🌐 **[Browse the Web Gallery & Catalog Page](https://ultimatejimmy.github.io/storefront-screensavers/)**



---

## Overview

This repository serves two main purposes:
1. **Catalog Source of Truth (`screensavers.json`)**: An automated JSON catalog consumed directly by the Storefront KOReader plugin to browse and install screensavers on e-readers.
2. **[Catalog Website & Web Gallery](https://ultimatejimmy.github.io/storefront-screensavers/)**: A modern, responsive web application for users to browse wallpapers, preview designs, and submit new community screensavers.

---

## Features

- **Optimized for E-Ink & Color E-Readers**: High contrast, minimal grayscale & vibrant color wallpapers curated specifically for e-paper screens (Kindle, Kobo, Boox Color, etc.).
- **Categorized Browsing**: Filter wallpapers by `Nature`, `Minimalist`, `Architecture`, `Sci-Fi`, `Anime`, `Fantasy`, `Abstract`, `Art`, `Religion`, and `Quotes`.
- **Bulk Upload Support**: Submit multiple wallpapers (up to 10) in a single batch, queueing items, setting titles/authors/categories per image, and automatically opening individual GitHub Issues for independent maintainer approval.
- **Suggest Changes & Feedback**: Submit corrections to titles, artists, categories, or flag low-quality entries directly via the ✏️ slide-in drawer on any wallpaper card.
- **Open Access & CC0 Sourcing**: Curated collection featuring high-resolution masterworks from The Metropolitan Museum of Art, Rijksmuseum, Old Book Illustrations, Rawpixel, and NASA. All attributed in [`CREDITS.md`](CREDITS.md).
- **Maintainer Review & Seeding Tool**: Local HTML approval gallery (`tools/seed/review.html`) allowing maintainers to visually approve/reject candidate screensavers before committing.
- **Catalog Management Studio**: Local interactive UI (`start_studio.bat` or `python tools/catalog_studio.py`) for editing titles, metadata, replacing images with automatic e-reader resizing, adding new wallpapers, deleting entries, and syncing `CREDITS.md`.

---

## Catalog Management Studio (Local Web UI)

For maintaining, editing, and expanding the catalog locally with an interactive graphical interface:

1. **Launch**: Double click [`start_studio.bat`](start_studio.bat) or run:
   ```bash
   python tools/catalog_studio.py
   ```
2. The Studio opens automatically in your browser at `http://127.0.0.1:5173`.
3. **Capabilities**:
   - **Edit Titles & Metadata**: Click any item card to edit its title, slug ID, artist, category, device compatibility tags, license, and attribution.
   - **Replace Images**: Drag and drop a new image or paste a URL to automatically regenerate the master 1860×2480 image and 600×800 thumbnail.
   - **Add New Wallpapers**: Upload new wallpapers with automatic ID slugging, category presets, and metadata formatting.
   - **Delete & Cleanup**: Permanently remove items from the catalog with optional deletion of orphan image files.
   - **Sync Credits**: 1-click regeneration of [`CREDITS.md`](CREDITS.md) to keep attribution in sync with `screensavers.json`.
   - **Automatic Backups**: Every modification creates a timestamped backup in `tools/backups/` with 1-click restore.

---

## How to Submit Screensaver(s)

1. Visit the web gallery submit tab.
2. Choose **Single Submission** or **Bulk Upload (Batch)**.
3. For bulk upload:
   - Select multiple image files at once.
   - Set the title, artist credit, and category for each queued image.
   - Click **Submit All** to open individual GitHub Issues for independent PR creation and maintainer review.

---

## Sourcing & Attribution

All open access, Public Domain, CC0, and community-shared screensavers are credited with source links, creator names, and license types in [`CREDITS.md`](CREDITS.md).

---

## Legal, Ownership & Community Policy

This project is a 100% free, open-source, and non-commercial community initiative:
- **No Ownership Claimed:** The maintainers do not own or claim copyright over community-submitted wallpapers. Artwork remains the intellectual property of its original creators.
- **Strictly Non-Profit:** No revenue, ads, or monetization are associated with this catalog.
- **Community Commons:** All submissions are contributed freely for personal, non-commercial e-ink reader use.
- **DMCA / Takedown:** We respect intellectual property rights. To request image removal, open an issue labeled `dmca-takedown` with the wallpaper title and proof of ownership. Takedown requests are reviewed and processed within 24–48 hours.

For complete details, please see our [Legal Disclaimers, Submission Terms & DMCA Policy](LEGAL.md).
