#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher

from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    import cv2
except Exception:
    cv2 = None


@dataclass
class Word:
    text: str
    conf: int
    left: int
    top: int
    width: int
    height: int
    line_id: tuple


def normalize_text(text: str, case_sensitive: bool) -> str:
    text = re.sub(r"\s+", "", text)
    if not case_sensitive:
        text = text.lower()
    return text


def check_tesseract() -> None:
    try:
        subprocess.run(["tesseract", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("Error: tesseract is required but not found in PATH.", file=sys.stderr)
        sys.exit(1)


def run_tesseract_tsv(image_path: str, lang: str, psm: int, oem: int) -> str:
    cmd = [
        "tesseract",
        image_path,
        "stdout",
        "-l",
        lang,
        "--psm",
        str(psm),
        "--oem",
        str(oem),
        "tsv",
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip(), file=sys.stderr)
        print("Error: tesseract failed to run.", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_tsv(tsv_text: str, min_conf: int) -> list[Word]:
    lines = tsv_text.splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    words = []
    for row in lines[1:]:
        cols = row.split("\t")
        if len(cols) != len(header):
            continue
        data = dict(zip(header, cols))
        text = data.get("text", "").strip()
        if not text:
            continue
        try:
            conf = int(float(data.get("conf", "-1")))
        except ValueError:
            conf = -1
        if conf < min_conf:
            continue
        left = int(data.get("left", 0))
        top = int(data.get("top", 0))
        width = int(data.get("width", 0))
        height = int(data.get("height", 0))
        line_id = (
            int(data.get("block_num", 0)),
            int(data.get("par_num", 0)),
            int(data.get("line_num", 0)),
        )
        words.append(Word(text=text, conf=conf, left=left, top=top, width=width, height=height, line_id=line_id))
    return words


def group_words_by_line(words: list[Word]) -> dict[tuple, list[Word]]:
    lines: dict[tuple, list[Word]] = {}
    for word in words:
        lines.setdefault(word.line_id, []).append(word)
    for line_words in lines.values():
        line_words.sort(key=lambda w: w.left)
    return lines


def build_line_compact(words: list[Word], case_sensitive: bool):
    compact = ""
    comps = []
    for word in words:
        comp = normalize_text(word.text, case_sensitive)
        if not comp:
            continue
        start = len(compact)
        compact += comp
        end = len(compact)
        comps.append((word, start, end))
    return compact, comps


def words_bbox(words: list[Word]):
    x1 = min(w.left for w in words)
    y1 = min(w.top for w in words)
    x2 = max(w.left + w.width for w in words)
    y2 = max(w.top + w.height for w in words)
    return x1, y1, x2, y2


def find_exact_matches(lines: dict[tuple, list[Word]], old_text: str, case_sensitive: bool):
    matches = []
    old_compact = normalize_text(old_text, case_sensitive)
    if not old_compact:
        return matches
    for line_id, words in lines.items():
        line_compact, comps = build_line_compact(words, case_sensitive)
        if not line_compact:
            continue
        start_idx = 0
        while True:
            pos = line_compact.find(old_compact, start_idx)
            if pos == -1:
                break
            end_pos = pos + len(old_compact)
            matched_words = [w for (w, s, e) in comps if s < end_pos and e > pos]
            if matched_words:
                bbox = words_bbox(matched_words)
                avg_conf = sum(w.conf for w in matched_words) / len(matched_words)
                line_text = " ".join(w.text for w in words)
                matches.append(
                    {
                        "bbox": bbox,
                        "boxes": [
                            (w.left, w.top, w.left + w.width, w.top + w.height) for w in matched_words
                        ],
                        "line_text": line_text,
                        "score": avg_conf,
                        "method": "exact",
                        "line_id": line_id,
                    }
                )
            start_idx = pos + 1
    return matches


def best_fuzzy_window(line_compact: str, old_compact: str):
    if len(line_compact) < len(old_compact):
        return None
    best = (0.0, None)
    for i in range(0, len(line_compact) - len(old_compact) + 1):
        window = line_compact[i : i + len(old_compact)]
        ratio = SequenceMatcher(None, window, old_compact).ratio()
        if ratio > best[0]:
            best = (ratio, i)
    return best


def find_fuzzy_matches(lines: dict[tuple, list[Word]], old_text: str, case_sensitive: bool, threshold: float):
    matches = []
    old_compact = normalize_text(old_text, case_sensitive)
    if not old_compact:
        return matches
    for line_id, words in lines.items():
        line_compact, comps = build_line_compact(words, case_sensitive)
        if not line_compact:
            continue
        best = best_fuzzy_window(line_compact, old_compact)
        if not best:
            continue
        ratio, pos = best
        if ratio < threshold or pos is None:
            continue
        end_pos = pos + len(old_compact)
        matched_words = [w for (w, s, e) in comps if s < end_pos and e > pos]
        if matched_words:
            bbox = words_bbox(matched_words)
            line_text = " ".join(w.text for w in words)
            matches.append(
                {
                    "bbox": bbox,
                    "boxes": [
                        (w.left, w.top, w.left + w.width, w.top + w.height) for w in matched_words
                    ],
                    "line_text": line_text,
                    "score": ratio,
                    "method": "fuzzy",
                    "line_id": line_id,
                }
            )
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


def parse_bbox(value: str):
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise ValueError("bbox must be x,y,w,h")
    x, y, w, h = [int(float(p)) for p in parts]
    return x, y, x + w, y + h


def build_mask(image_size: tuple[int, int], boxes: list[tuple[int, int, int, int]], pad: int):
    width, height = image_size
    mask = np.zeros((height, width), dtype=np.uint8)
    for x1, y1, x2, y2 in boxes:
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(width, x2 + pad)
        y2 = min(height, y2 + pad)
        mask[y1:y2, x1:x2] = 255
    return mask


def auto_text_color(img_rgb: np.ndarray, bbox: tuple[int, int, int, int]):
    x1, y1, x2, y2 = bbox
    region = img_rgb[y1:y2, x1:x2]
    if region.size == 0:
        return (0, 0, 0)
    gray = region.mean(axis=2)
    ring_pad = 6
    x1r = max(0, x1 - ring_pad)
    y1r = max(0, y1 - ring_pad)
    x2r = min(img_rgb.shape[1], x2 + ring_pad)
    y2r = min(img_rgb.shape[0], y2 + ring_pad)
    ring = img_rgb[y1r:y2r, x1r:x2r]
    ring_gray = ring.mean(axis=2) if ring.size else gray
    bg_level = float(np.median(ring_gray))
    region_level = float(np.median(gray))
    if region_level < bg_level:
        cutoff = np.percentile(gray, 20)
        mask = gray <= cutoff
    else:
        cutoff = np.percentile(gray, 80)
        mask = gray >= cutoff
    if mask.sum() < 10:
        color = np.median(region.reshape(-1, 3), axis=0)
    else:
        color = np.median(region[mask], axis=0)
    return tuple(int(c) for c in color)


def pick_font_path(font_path: str | None):
    if font_path:
        if not os.path.exists(font_path):
            print(f"Error: font not found: {font_path}", file=sys.stderr)
            sys.exit(1)
        return font_path
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def fit_font_size(text: str, font_path: str | None, box_w: int, box_h: int):
    if font_path is None:
        return None
    min_size = 4
    max_size = max(min_size, box_h * 2)
    best = min_size
    lo, hi = min_size, max_size
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(font_path, mid)
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= box_w and h <= box_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def parse_color(value: str | None):
    if not value or value.lower() == "auto":
        return None
    value = value.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) not in (6, 3):
        raise ValueError("color must be hex like #112233 or #123")
    if len(value) == 3:
        value = "".join([c * 2 for c in value])
    r = int(value[0:2], 16)
    g = int(value[2:4], 16)
    b = int(value[4:6], 16)
    return (r, g, b)


def render_text(img_rgb: np.ndarray, bbox: tuple[int, int, int, int], text: str, font_path: str | None,
                font_size: int | None, color: tuple[int, int, int]):
    x1, y1, x2, y2 = bbox
    box_w = x2 - x1
    box_h = y2 - y1
    if font_path:
        size = font_size or fit_font_size(text, font_path, box_w, box_h)
        font = ImageFont.truetype(font_path, size)
    else:
        font = ImageFont.load_default()
    img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img)
    text_bbox = font.getbbox(text)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    x = x1 + (box_w - text_w) / 2 - text_bbox[0]
    y = y1 + (box_h - text_h) / 2 - text_bbox[1]
    draw.text((x, y), text, font=font, fill=color)
    return np.array(img)


def print_matches(matches):
    for idx, match in enumerate(matches):
        x1, y1, x2, y2 = match["bbox"]
        score = match["score"]
        method = match["method"]
        line_text = match["line_text"].strip()
        print(f"[{idx}] {method} score={score:.2f} bbox=({x1},{y1},{x2},{y2}) text='{line_text}'")


def main():
    parser = argparse.ArgumentParser(description="Replace text in an image using OCR + inpaint + redraw.")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", help="Output image path (default: input name with .edited)")
    parser.add_argument("--old-text", help="Text to replace (required unless --bbox is set)")
    parser.add_argument("--new-text", required=True, help="Replacement text")
    parser.add_argument("--lang", default="chi_sim+eng", help="Tesseract language(s)")
    parser.add_argument("--psm", type=int, default=6, help="Tesseract PSM mode")
    parser.add_argument("--oem", type=int, default=3, help="Tesseract OEM mode")
    parser.add_argument("--min-conf", type=int, default=40, help="Minimum OCR confidence")
    parser.add_argument("--fuzzy", type=float, default=0.0, help="Fuzzy match threshold (0-1). 0 disables.")
    parser.add_argument("--index", type=int, help="Pick a match by index")
    parser.add_argument("--bbox", help="Manual bbox x,y,w,h (skip OCR)")
    parser.add_argument("--pad", type=int, default=3, help="Expand mask in pixels")
    parser.add_argument("--inpaint-method", default="telea", choices=["telea", "ns"], help="Inpaint method")
    parser.add_argument("--inpaint-radius", type=int, default=3, help="Inpaint radius")
    parser.add_argument("--font", help="Font path (recommended for Chinese)")
    parser.add_argument("--font-size", type=int, help="Font size override")
    parser.add_argument("--color", default="auto", help="Text color: auto or hex (#112233)")
    parser.add_argument("--case-sensitive", action="store_true", help="Case-sensitive match")
    parser.add_argument("--dry-run", action="store_true", help="Only list matches")

    args = parser.parse_args()

    if args.bbox is None and not args.old_text:
        parser.error("--old-text is required unless --bbox is set")

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Error: input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}.edited{ext or '.png'}"

    img = Image.open(input_path).convert("RGB")
    img_rgb = np.array(img)

    if args.bbox:
        try:
            bbox = parse_bbox(args.bbox)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        matches = [{
            "bbox": bbox,
            "boxes": [bbox],
            "line_text": "(manual bbox)",
            "score": 1.0,
            "method": "manual",
        }]
    else:
        check_tesseract()
        tsv_text = run_tesseract_tsv(input_path, args.lang, args.psm, args.oem)
        words = parse_tsv(tsv_text, args.min_conf)
        lines = group_words_by_line(words)
        matches = find_exact_matches(lines, args.old_text, args.case_sensitive)
        if not matches and args.fuzzy > 0:
            matches = find_fuzzy_matches(lines, args.old_text, args.case_sensitive, args.fuzzy)

    if not matches:
        print("No matches found.")
        sys.exit(2)

    print_matches(matches)

    if args.dry_run:
        print("Dry run complete. Re-run with --index to apply.")
        return

    if len(matches) > 1 and args.index is None:
        print("Multiple matches found. Re-run with --index to select one.")
        sys.exit(2)

    if args.index is not None:
        if args.index < 0 or args.index >= len(matches):
            print("Error: --index out of range.", file=sys.stderr)
            sys.exit(1)
        match = matches[args.index]
    else:
        match = matches[0]

    if cv2 is None:
        print("Error: opencv-python is required for inpainting.", file=sys.stderr)
        sys.exit(1)

    mask = build_mask((img.width, img.height), match["boxes"], args.pad)
    color = parse_color(args.color)
    if color is None:
        color = auto_text_color(img_rgb, match["bbox"])

    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    method_flag = cv2.INPAINT_TELEA if args.inpaint_method == "telea" else cv2.INPAINT_NS
    inpainted = cv2.inpaint(img_bgr, mask, args.inpaint_radius, method_flag)
    inpainted_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)

    font_path = pick_font_path(args.font)
    if font_path is None:
        print("Warning: no font found; falling back to default font.")

    result = render_text(
        inpainted_rgb,
        match["bbox"],
        args.new_text,
        font_path,
        args.font_size,
        color,
    )

    Image.fromarray(result).save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
