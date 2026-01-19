---
name: image-text-replace
description: OCR-based text replacement in raster images (PNG/JPG/TIFF), including locating target text, masking, inpainting, and redrawing new text. Use when users ask to replace or edit words/phrases inside an image and the text is part of the pixels.
---

# Image Text Replace

## Overview

Use `scripts/replace_text_in_image.py` to locate text with Tesseract OCR, remove it via inpainting, and draw replacement text with similar size and color. Prefer this for raster images where text is baked into the pixels.

## Workflow

1. Collect inputs: image path, old text, new text, language, font path (especially for Chinese), and whether multiple matches are acceptable.
2. Run a dry scan to list matches:
   - `python scripts/replace_text_in_image.py --input ... --old-text ... --new-text ... --dry-run`
3. If multiple matches appear, ask the user to pick an index or provide a manual bbox, then re-run with `--index` or `--bbox`.
4. Run the edit with inpainting and save the output.
5. Validate visually; if artifacts remain, adjust `--pad` or `--inpaint-radius`, or request a manual bbox.

## Script: replace_text_in_image.py

Required: `tesseract` CLI, Python `Pillow`, `numpy`, `opencv-python`.

Key options:
- `--lang` OCR language (e.g., `chi_sim+eng`).
- `--index` choose a match when multiple results are found.
- `--bbox x,y,w,h` skip OCR and edit a user-provided region.
- `--pad` expand mask to fully cover original text.
- `--inpaint-method` `telea` or `ns`.
- `--font` path to a font that supports the target language.
- `--color` `auto` or hex (e.g., `#111111`).

Example:
```
python scripts/replace_text_in_image.py \
  --input /path/to/image.png \
  --output /path/to/image.edited.png \
  --old-text "xx" \
  --new-text "yy" \
  --lang chi_sim+eng \
  --font /System/Library/Fonts/PingFang.ttc
```

## Decision points

- If OCR confidence is low or multiple matches appear, ask the user to confirm the target (index or bbox).
- If the background is complex and inpainting artifacts are visible, prefer a manual bbox or skip automation.
