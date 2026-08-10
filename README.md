# E-Reader Screensavers & Wallpaper Catalog

A community-driven, curated catalog of e-ink screensavers and lock screen wallpapers for Kindle, Kobo, Boox, PocketBook, and other e-readers. Powered by the [Storefront KOReader Plugin](https://github.com/ultimatejimmy/storefront.koplugin).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![GitHub Pages](https://img.shields.io/badge/hosted--on-GitHub%20Pages-purple.svg)

---

## 📖 Overview

This repository serves two main purposes:
1. **Catalog Source of Truth (`screensavers.json`)**: An automated JSON catalog consumed directly by the Storefront KOReader plugin to browse and install screensavers on e-readers.
2. **Catalog Website & Web Gallery**: A modern, responsive web application for users to browse wallpapers, preview designs, and submit new community screensavers.

---

## 🎨 Features

- **Optimized for E-Ink**: High contrast, minimal grayscale imagery curated specifically for e-paper screens.
- **Categorized Browsing**: Filter wallpapers by `Nature`, `Minimalist`, `Sci-Fi`, `Anime`, and more.
- **Automated Submission Workflow**: Users submit wallpapers via GitHub Issues, which triggers a GitHub Actions workflow to parse the entry and generate a Pull Request.
- **DMCA & Copyright Compliance**: Built-in legal disclaimers and clear takedown procedures.

---

## 📤 How to Submit a Screensaver

1. Visit the web gallery or open a new issue using our submission template.
2. Fill out the details:
   - **Title**: A descriptive name for the wallpaper
   - **Creator**: Artist / Author credit
   - **Category**: Minimalist, Nature, Sci-Fi, Anime, etc.
   - **Direct Image URL**: Link to a high-resolution PNG or JPG image
3. Submitting the issue automatically triggers our GitHub Actions workflow, which validates the metadata, updates `screensavers.json`, and opens a PR for maintainer review.

---

## ⚖️ Legal & Takedown Policy (DMCA)

All screensavers hosted or linked in this repository are submitted by the community. We respect intellectual property rights and handle copyright claims promptly.

To request removal of a copyrighted image:
- File a GitHub Issue labeled `dmca-takedown` with the image title and proof of ownership.

Takedown requests are reviewed and processed promptly.

---

## 🚀 GitHub Pages Setup

To enable the web gallery on your fork/repo:
1. Go to **Settings** -> **Pages**.
2. Select **Source**: `Deploy from a branch`.
3. Choose branch `main` and folder `/ (root)`.
4. Click **Save**.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
