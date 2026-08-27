# Storefront Screensavers Catalog — Rules & Guidelines

## 1. Typography, Copywriting & Punctuation Rules

1. **No Spaces Around Slashes (/)**:
   - **Strict Rule**: Never place spaces around a slash in UI copy, labels, placeholders, option tags, button titles, or technical strings (e.g. Creator/Artist, Tags/Keywords, Import/Export, Ctrl+V/Cmd+V, Reason/Additional Notes, Report/Change Type).
   - *Exception*: Spaces around slashes are reserved strictly for poetry line breaks.

2. **Colons & Key-Value Formatting**:
   - No space before a colon; exactly one space after (Author: Jane Doe, not Author : Jane Doe).

3. **Ellipses (...)**:
   - Attach ellipsis directly without dangling punctuation (e.g. anime, landscape, dark...).

4. **Ampersands vs. "and"**:
   - Use & only for space-constrained buttons, chips, or badges (Edit & Crop (3:4)).
   - Use spelled-out "and" in full sentences and dialog text.

5. **Dashes**:
   - Use hyphen - for compound words (e-ink, high-res, multi-select).
   - Use em-dash — or spaced en-dash  –  for phrases/subtitles. Do not use spaced hyphens  -  as em-dashes.

## 2. Bulk & Single Submission Conventions

1. **Creator/Author Name Handling**:
   - Do NOT pre-fill or autofill "Community" into the author input field on bulk upload or single submission. Leave it blank with placeholder Creator/Artist.
   - On GitHub submission, if the user leaves the author field blank, fallback to "Community" for catalog metadata integrity.

2. **Categories**:
   - Always support multi-select categories using interactive category pills (.cat-pill).
   - Multiple categories are stored as comma-separated values (e.g. "Sci-Fi, Anime, Transparent").

3. **Transparent Mode Compatibility**:
   - Transparent wallpapers must support both **Checkerboard Grid** and **Book Text Mode** preview backgrounds.
   - Text overlays (author badges, buttons) must maintain high contrast (solid backdrop and blur) so simulated book text never clashes with attribution.
