#!/usr/bin/env python3
import argparse
import json
import math
import re
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps

TYPE_COLORS = {
  # Vestigium New Types
  "Hellish": "#7b1d1d",
  "Furniture": "#7B5B41",
  "Fluid": "#1f6f7a",
  "Feral": "#6B8E23",
  "Digital": "#2b7a78",
  "Anomaly": "#5A3E9C",
  "Hollow": "#444444",
  "Horror": "#8B0000",
  "Humanoid": "#3b6ea5",
  "Luminous": "#cfa300",
  "Mechanical": "#6c757d",
  "Mineral": "#4b5563",
  "Mutation": "#9d4edd",
  "Pest": "#7f8c00",
  "Shadow": "#222831",
  "Spectral": "#5f7fff",
  "Structure": "#495057",
  "Vegetal": "#2e7d32",

  # SRD fallback
  "aberration": "#8246AF",
  "beast": "#8D8741",
  "celestial": "#CDA434",
  "construct": "#6C757D",
  "dragon": "#4B6584",
  "elemental": "#0EA5E9",
  "fey": "#7C3AED",
  "fiend": "#A4161A",
  "giant": "#9C6644",
  "humanoid": "#3B6EA5",
  "monstrosity": "#6B8E23",
  "ooze": "#0F766E",
  "plant": "#2E7D32",
  "undead": "#6A1B9A",
}

def safe_name(s: str) -> str:
  return re.sub(r"[^\w\d\-_.]+", "_", s).strip("_")[:80] or "token"

SRD_TYPES = {
  "aberration","beast","celestial","construct","dragon","elemental","fey",
  "fiend","giant","humanoid","monstrosity","ooze","plant","undead"
}

def extract_srd_type_from_Type_field(type_field: str) -> str:
  if not type_field:
    return ""
  s = str(type_field).lower()
  m = re.search(r"\b(" + "|".join(sorted(SRD_TYPES)) + r")\b", s)
  return m.group(1) if m else ""

def pick_color(mon: Dict[str, Any], fallback: str) -> str:
  t = (mon.get("type") or "").strip().lower().rstrip(",")
  return TYPE_COLORS.get(t, fallback)
  combined_type = mon.get("Type")
  if combined_type:
    srd = extract_srd_type_from_Type_field(combined_type)
    if srd and srd in TYPE_COLORS:
      return TYPE_COLORS[srd]
def get_name(mon: Dict[str, Any], file_stem: str) -> str:
  name = mon.get("name") or mon.get("Name") or ""
  name = str(name).strip()
  if not name:
    return file_stem
  return name

def get_cr(mon: Dict[str, Any]) -> str:
  raw = mon.get("cr") or mon.get("CR") or mon.get("Challenge") or ""
  return str(raw).strip()

def name_to_monogram(name: str) -> str:
  words = re.sub(r"[^A-Za-z0-9\s]", " ", name).split()
  if not words:
    return "??"
  if len(words) == 1:
    return words[0][:2].upper()
  stop = {"of","the","and","a","an","la","le","de","du","das","dos"}
  picks = []
  for w in words:
    lw = w.lower()
    if lw in stop:
      continue
    picks.append(w[0].upper())
    if len(picks) == 2:
      break
  return "".join(picks) or words[0][:2].upper()

def load_portrait(images_dir: Path, base) -> Optional[Path]:
  # Fallback: by sanitized name
  for ext in (".png", ".jpg", ".jpeg", ".webp"):
    p = images_dir / f"{base}{ext}"
    if p.exists():
      return p
  return None

def draw_circle_token(
    size: int,
    bg_hex: str,
    border: int,
    stroke: int,
    portrait_path: Optional[Path],
    name: str,
    cr: str,
    show_badge: bool,
    badge_label_cr: bool,
    font_path: Optional[Path] = None,
) -> Image.Image:
  """
  Returns a Pillow Image (RGBA) of the token.
  """
  # Base canvas
  token = Image.new("RGBA", (size, size), (0, 0, 0, 0))
  draw = ImageDraw.Draw(token)

  # Background circle
  bg_color = ImageColor_safe(bg_hex)
  draw.ellipse((0, 0, size, size), fill=bg_color)

  # Outer ring (white)
  ring_r = size - border
  ring_bb = (border // 2, border // 2, size - border // 2, size - border // 2)
  draw.ellipse(ring_bb, outline=(255, 255, 255, 255), width=border)

  # Inner stroke
  inner_r = size - 2 * border - stroke
  inner_bb = (
    border + stroke // 2,
    border + stroke // 2,
    size - border - stroke // 2,
    size - border - stroke // 2,
  )
  draw.ellipse(inner_bb, outline=(255, 255, 255, int(0.6 * 255)), width=stroke)

  # Portrait (circle-cropped) OR monogram
  inner_diam = size - 2 * (border + stroke)
  content_top_left = (border + stroke, border + stroke)

  if portrait_path and portrait_path.exists():
    img = Image.open(portrait_path).convert("RGBA")
    # cover-fit to square
    img_fit = ImageOps.fit(img, (inner_diam, inner_diam), method=Image.LANCZOS, centering=(0.5, 0.5))
    # circle mask
    mask = Image.new("L", (inner_diam, inner_diam), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner_diam, inner_diam), fill=255)
    img_fit.putalpha(mask)
    token.alpha_composite(img_fit, content_top_left)
  else:
    # monogram
    mono = name_to_monogram(name)
    # find a font
    font = best_font(font_path, int(size * 0.34))
    # shrink font until it fits ~0.55 width
    W = int(size * 0.55)
    while font.size > 10 and text_width(mono, font) > W:
      font = best_font(font_path, font.size - 2)

    # shadow
    cx, cy = size // 2, size // 2
    draw_text_center(draw, mono, cx + 3, cy + 3, font, fill=(0, 0, 0, int(0.65 * 255)))
    draw_text_center(draw, mono, cx, cy, font, fill=(243, 246, 255, 255))

  # CR badge
  if show_badge and cr:
    badge_w = int(size * 0.34)
    badge_h = int(size * 0.18)
    pad = int(size * 0.03)
    x = size - badge_w - pad
    y = size - badge_h - pad

    # rounded rect
    rr = int(badge_h * 0.35)
    fill_round_rect(draw, x, y, badge_w, badge_h, rr, fill=(0, 0, 0, int(0.6 * 255)))

    # text
    label = f"CR {cr}" if badge_label_cr else str(cr)
    font = best_font(font_path, int(badge_h * 0.5))
    draw_text_center(draw, label, x + badge_w // 2, y + badge_h // 2, font, fill=(255, 255, 255, 255))

  return token

def ImageColor_safe(hex_or_rgb: str):
  """Convert hex like #aabbcc to RGBA tuple."""
  hex_or_rgb = str(hex_or_rgb).strip()
  if hex_or_rgb.startswith("#") and len(hex_or_rgb) in (4, 7):
    return ImageColor.getrgb(hex_or_rgb) + (255,)
  # fallback gray
  return (68, 68, 68, 255)

# Pillow’s ImageColor import (delayed to keep top imports tidy)
from PIL import ImageColor

def text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
  bbox = font.getbbox(text)
  return bbox[2] - bbox[0]

def draw_text_center(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font: ImageFont.FreeTypeFont, fill):
  bbox = font.getbbox(text)
  tw = bbox[2] - bbox[0]
  th = bbox[3] - bbox[1]
  draw.text((x - tw // 2, y - th // 2), text, font=font, fill=fill)

def best_font(font_path: Optional[Path], size: int) -> ImageFont.FreeTypeFont:
  """Try provided font, fallback to a PIL default that scales."""
  if font_path and Path(font_path).exists():
    try:
      return ImageFont.truetype(str(font_path), size=size)
    except Exception:
      pass
  try:
    # DejaVu is bundled with Pillow in many envs; try it
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
  except Exception:
    return ImageFont.load_default()

def fill_round_rect(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, r: int, fill):
  r = min(r, w // 2, h // 2)
  # center rect
  draw.rectangle((x + r, y, x + w - r, y + h), fill=fill)
  draw.rectangle((x, y + r, x + w, y + h - r), fill=fill)
  # corners
  draw.pieslice((x, y, x + 2 * r, y + 2 * r), 180, 270, fill=fill)
  draw.pieslice((x + w - 2 * r, y, x + w, y + 2 * r), 270, 360, fill=fill)
  draw.pieslice((x, y + h - 2 * r, x + 2 * r, y + h), 90, 180, fill=fill)
  draw.pieslice((x + w - 2 * r, y + h - 2 * r, x + w, y + h), 0, 90, fill=fill)

def main():
  ap = argparse.ArgumentParser(description="Generate circular VTT tokens from monster JSON files.")
  ap.add_argument("--json_dir", required=True, help="Folder containing one JSON per monster.")
  ap.add_argument("--images_dir", required=True, help="Folder containing portrait images (optional).")
  ap.add_argument("--out_dir", required=True, help="Output folder for tokens.")
  ap.add_argument("--size", type=int, default=512, help="Token size in px (default 512).")
  ap.add_argument("--border", type=int, default=18, help="Outer ring thickness in px (default 18).")
  ap.add_argument("--stroke", type=int, default=6, help="Inner stroke thickness in px (default 6).")
  ap.add_argument("--badge", action="store_true", help="Render CR badge.")
  ap.add_argument("--crlabel", action="store_true", help="Prefix 'CR ' on badge.")
  ap.add_argument("--font", help="Path to a TTF/OTF font to use (optional).")

  args = ap.parse_args()
  json_dir = Path(args.json_dir)
  images_dir = Path(args.images_dir)
  out_dir = Path(args.out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  font_path = Path(args.font) if args.font else None

  json_files = sorted([p for p in json_dir.glob("*.json") if p.is_file()])
  if not json_files:
    print("No JSON files found in:", json_dir)
    return

  print(f"Found {len(json_files)} monsters.")
  for jf in json_files:
    try:
      data = json.loads(jf.read_text(encoding="utf-8"))
      # Accept either a single monster object, or a 5eTools-like wrapper { "monster": [ ... ] }
      if isinstance(data, dict) and "monster" in data and isinstance(data["monster"], list) and data["monster"]:
        monsters = data["monster"]
      elif isinstance(data, dict):
        monsters = [data]
      elif isinstance(data, list):
        monsters = data
      else:
        print(f"Skipping {jf.name}: unrecognized JSON shape.")
        continue

      for mon in monsters:
        name = get_name(mon, jf.stem)
        cr = get_cr(mon)
        color = pick_color(mon, "#444444")
        portrait = load_portrait(images_dir, name)

        token = draw_circle_token(
          size=args.size,
          bg_hex=color,
          border=args.border,
          stroke=args.stroke,
          portrait_path=portrait,
          name=name,
          cr=cr,
          show_badge=args.badge,
          badge_label_cr=args.crlabel,
          font_path=font_path,
        )

        fname = safe_name(name) + ".png"
        token.save(out_dir / fname, format="PNG")
        print("✔", name)
    except Exception as e:
      print(f"Error in {jf.name}: {e}")

if __name__ == "__main__":
  main()