#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

import gspread
from google.oauth2.service_account import Credentials

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor, ImageChops
import math

TYPE_COLORS = {
  # Vestigium New Types
  "hellish": "#7b1d1d",
  "furniture": "#7B5B41",
  "fluid": "#1f6f7a",
  "feral": "#6B8E23",
  "digital": "#2b7a78",
  "anomaly": "#5A3E9C",
  "hollow": "#444444",
  "horror": "#8B0000",
  "humanoid": "#3b6ea5",
  "luminous": "#cfa300",
  "mechanical": "#6c757d",
  "mineral": "#4b5563",
  "mutation": "#9d4edd",
  "pest": "#7f8c00",
  "shadow": "#222831",
  "spectral": "#5f7fff",
  "structure": "#495057",
  "vegetal": "#2e7d32",

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
  "humanoid_srd": "#3B6EA5",    # keep SRD humanoid visually distinct if you like
  "monstrosity": "#6B8E23",
  "ooze": "#0F766E",
  "plant": "#2E7D32",
  "undead": "#6A1B9A",
}

SRD_TYPES = {
  "aberration","beast","celestial","construct","dragon","elemental","fey",
  "fiend","giant","humanoid","monstrosity","ooze","plant","undead"
}

def safe_name(s: str) -> str:
  return re.sub(r"[^\w\d\-_.]+", "_", str(s)).strip("_")[:80] or "token"

def extract_srd_type_from_Type_field(type_field: str) -> str:
  if not type_field:
    return ""
  s = str(type_field).lower()
  m = re.search(r"\b(" + "|".join(sorted(SRD_TYPES)) + r")\b", s)
  return m.group(1) if m else ""

def pick_color_from_row(row: Dict[str, Any]) -> str:
  """
  Color priority:
    1) New Type (exact, case-insensitive) mapped in TYPE_COLORS
    2) SRD 'Type' extraction (e.g., 'undead' inside 'Medium undead, neutral')
    3) Default gray
  """
  new_type = str(row.get("New Type") or "").strip().lower().rstrip(",")
  if new_type:
    # SRD 'humanoid' has a separate key above to avoid confusion with Vestigium 'Humanoid' color.
    key = "humanoid_srd" if new_type == "humanoid" and "Type" in row else new_type
    if key in TYPE_COLORS:
      return TYPE_COLORS[key]

  srd = extract_srd_type_from_Type_field(str(row.get("Type") or ""))
  if srd:
    key = "humanoid_srd" if srd == "humanoid" else srd
    if key in TYPE_COLORS:
      return TYPE_COLORS[key]

  return "#444444"

def get_name_from_row(row: Dict[str, Any]) -> str:
  name = str(row.get("Name") or "").strip()
  return name or "Unknown"

def get_cr_from_row(row: Dict[str, Any]) -> str:
  raw = row.get("CR") or row.get("cr") or row.get("Challenge") or ""
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

def load_portrait(images_dir: Path, base: str, suffix: str = "") -> Optional[Path]:
  """
  Look for a portrait file using the monster's name exactly as given in the sheet.
  The sheet's 'Name' column is assumed to match the portrait file's Sentence Case.
  """
  for ext in (".png", ".jpg", ".jpeg", ".webp"):
    filename = f"{base}{suffix}{ext}" if suffix else f"{base}{ext}"
    p = images_dir / filename
    if p.exists():
      return p
  return None

def ImageColor_safe(hex_or_rgb: str):
  hex_or_rgb = str(hex_or_rgb).strip()
  if hex_or_rgb.startswith("#") and len(hex_or_rgb) in (4, 7):
    return ImageColor.getrgb(hex_or_rgb) + (255,)
  return (68, 68, 68, 255)

def text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
  left, top, right, bottom = font.getbbox(text)
  return int(right) - int(left)

def draw_text_center(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font: ImageFont.FreeTypeFont, fill):
  bbox = font.getbbox(text)
  tw = bbox[2] - bbox[0]
  th = bbox[3] - bbox[1]
  draw.text((x - tw // 2, y - th // 2), text, font=font, fill=fill)

def best_font(font_path: Optional[Path], size: int) -> ImageFont.FreeTypeFont:
  if font_path and Path(font_path).exists():
    try:
      return ImageFont.truetype(str(font_path), size=size)
    except Exception:
      pass
  try:
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
  except Exception:
    return ImageFont.load_default()

def fill_round_rect(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, r: int, fill):
  r = min(r, w // 2, h // 2)
  draw.rectangle((x + r, y, x + w - r, y + h), fill=fill)
  draw.rectangle((x, y + r, x + w, y + h - r), fill=fill)
  draw.pieslice((x, y, x + 2 * r, y + 2 * r), 180, 270, fill=fill)
  draw.pieslice((x + w - 2 * r, y, x + w, y + 2 * r), 270, 360, fill=fill)
  draw.pieslice((x, y + h - 2 * r, x + 2 * r, y + h), 90, 180, fill=fill)
  draw.pieslice((x + w - 2 * r, y + h - 2 * r, x + w, y + h), 0, 90, fill=fill)

def draw_text_ring(
    base_img: Image.Image,
    center: tuple[int, int],
    radius: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    *,
    fill=(255, 255, 255, 255),
    stroke_fill=(0, 0, 0, 180),
    stroke_width=3,
    start_angle_deg: float = -90.0,   # 12 o'clock
    clockwise: bool = True,
    equal_angle: bool = True,         # even angular spacing around full circle
    angle_step_deg: float | None = None,  # set a fixed step if you want
    offset_px: int = 0,
    show_debug_dots: bool = False,
) -> None:
  n = len(text)
  if n == 0:
    return

  # per-char angle step
  if angle_step_deg is not None:
    step = float(angle_step_deg)
  elif equal_angle:
    step = 360.0 / n
  else:
    step = 360.0 / n  # fallback

  eff_r = max(1, radius - int(offset_px))

  for i, ch in enumerate(text.upper()):
    theta_deg = start_angle_deg + (i * step if clockwise else -i * step)
    theta = math.radians(theta_deg)
    cx, cy = center
    x = cx + eff_r * math.cos(theta)
    y = cy + eff_r * math.sin(theta)

    if show_debug_dots:
      ImageDraw.Draw(base_img).ellipse((x-2, y-2, x+2, y+2), fill=(255,0,0,255))

    # render glyph on a padded canvas, then rotate tangentially
    pad = max(int(font.size * 2.5) + 16, 64)
    glyph = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glyph)
    gd.text((pad//2, pad//2), ch, font=font, fill=fill,
            stroke_width=stroke_width, stroke_fill=stroke_fill, anchor="mm")

    tangent_deg = theta_deg + 90 if clockwise else theta_deg - 90
    rotated = glyph.rotate(-tangent_deg, resample=Image.Resampling.BICUBIC, expand=True)

    base_img.paste(rotated, (int(x-rotated.width/2), int(y-rotated.height/2)), rotated)

def make_metal_texture(size: int) -> Image.Image:
  """Return a grayscale brushed metal texture."""
  import random
  img = Image.new("L", (size, size), 0)
  d = ImageDraw.Draw(img)
  # horizontal brushed effect
  for y in range(size):
    gray = int(180 + 40 * math.sin(y / size * math.pi * 8))
    d.line((0, y, size, y), fill=gray)
  # speckles
  px = img.load()
  for _ in range(size * size // 40):
    x = random.randint(0, size - 1)
    y = random.randint(0, size - 1)
    val = random.randint(200, 255)
    px[x, y] = val
  return img

def add_ring_lighting(size: int, ring_width: int) -> Image.Image:
  highlight = Image.new("RGBA", (size, size), (0,0,0,0))
  d = ImageDraw.Draw(highlight)
  # soft white glow from top-left
  grad = Image.new("L", (size, size), 0)
  gd = ImageDraw.Draw(grad)
  gd.ellipse((0, 0, size, size), fill=180)
  inset = ring_width
  gd.ellipse((inset, inset, size-inset, size-inset), fill=0)
  highlight = ImageOps.colorize(grad, black=(0,0,0,0), white=(255,255,255,100)).convert("RGBA")
  return highlight

def tint_texture(img: Image.Image, hex_color: str) -> Image.Image:
  """Tint a grayscale texture by a given hex color."""
  base = Image.new("RGBA", img.size, ImageColor_safe(hex_color))
  # multiply the grayscale texture with the base color
  return ImageChops.multiply(base.convert("RGBA"), img.convert("L").convert("RGBA"))

def texture_for_ring(size: int, ring_width: int, hex_color: str) -> Image.Image:
  tex = make_metal_texture(size)  # grayscale metal
  annulus = make_annulus_mask(size, ring_width)
  tinted = tint_texture(tex, hex_color)  # apply type color
  return Image.composite(tinted, Image.new("RGBA", (size, size), (0,0,0,0)), annulus)


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
  token = Image.new("RGBA", (size, size), (0, 0, 0, 0))
  draw = ImageDraw.Draw(token)

  # Background
  bg_color = ImageColor_safe(bg_hex)
  draw.ellipse((0, 0, size, size), fill=bg_color)

  # Outer ring base
  ring_bb = (border // 2, border // 2, size - border // 2, size - border // 2)
  draw.ellipse(ring_bb, outline=bg_color, width=border)

  # CR-based frame texture overlay
  if cr:
      cr_tex = texture_for_cr(size, border, cr)
      color_layer = Image.new("RGBA", (size, size), bg_color)
      token.alpha_composite(Image.composite(color_layer, Image.new("RGBA", (size, size), (0,0,0,0)), cr_tex))

  # Inner stroke
  inner_bb = (
    border + stroke // 2,
    border + stroke // 2,
    size - border - stroke // 2,
    size - border - stroke // 2,
  )
  draw.ellipse(inner_bb, outline=(255, 255, 255, int(0.6 * 255)), width=stroke)

  # Portrait or monogram
  inner_diam = size - 2 * (border + stroke)
  content_top_left = (border + stroke, border + stroke)
  if portrait_path and portrait_path.exists():
    img = Image.open(portrait_path).convert("RGBA")
    img_fit = ImageOps.fit(img, (inner_diam, inner_diam), method=Image.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new("L", (inner_diam, inner_diam), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner_diam, inner_diam), fill=255)
    img_fit.putalpha(mask)
    token.alpha_composite(img_fit, content_top_left)
  else:
    mono = name_to_monogram(name)
    font = best_font(font_path, int(size * 0.34))
    W = int(size * 0.55)
    while font.size > 10 and text_width(mono, font) > W:
      font = best_font(font_path, font.size - 2)
    cx, cy = size // 2, size // 2
    draw_text_center(draw, mono, cx + 3, cy + 3, font, fill=(0, 0, 0, int(0.65 * 255)))
    draw_text_center(draw, mono, cx, cy, font, fill=(243, 246, 255, 255))

  W, H = token.size
  center = (W//2, H//2)
  portrait_radius = min(W, H)//2  # full portrait radius
  
  # ~25–30% inward from the portrait edge usually looks right
  offset_px = int(border * 1.8)
  
  font_ring = best_font(font_path, max(10, int(W * 0.08)))

  draw_text_ring(
    token, center, portrait_radius,
    name, font_ring,
    fill=(255,255,255,255),
    stroke_fill=(0,0,0,180),
    stroke_width=2,
    start_angle_deg=90,        # start at top
    clockwise=False,             # reading direction
    equal_angle=True,           # coin-style even spacing
    angle_step_deg=3,        # let it fill the full circle
    offset_px=offset_px,        # pulls it onto the portrait
    show_debug_dots=False,      # set True once to verify placement
  )

  # CR badge
  if show_badge and cr:
    badge_w = int(size * 0.34)
    badge_h = int(size * 0.18)
    pad = int(size * 0.03)
    x = size - badge_w - pad
    y = size - badge_h - pad
    rr = int(badge_h * 0.35)
    fill_round_rect(draw, x, y, badge_w, badge_h, rr, fill=(0, 0, 0, int(0.6 * 255)))
    label = f"CR {cr}" if badge_label_cr else str(cr)
    font = best_font(font_path, int(badge_h * 0.5))
    draw_text_center(draw, label, x + badge_w // 2, y + badge_h // 2, font, fill=(255, 255, 255, 255))

  return token

# New helper functions for CR-based texture

def parse_cr_to_float(cr: str) -> float:
  """Convert CR strings like '1/2', '1/4', '—', '' to a float for tiering."""
  s = str(cr).strip()
  if not s or s in {"—", "-", "—-"}:
    return 0.0
  try:
    if "/" in s:
      num, den = s.split("/", 1)
      return float(num) / float(den)
    return float(s)
  except Exception:
    return 0.0

def cr_to_texture_kind(cr: str) -> str:
  """
  Map CR to a texture kind.
    0–2   -> 'dots'
    3–8   -> 'diag'
    9–16  -> 'cross'
    17+   -> 'noise'
  """
  v = parse_cr_to_float(cr)
  if v <= 2:
    return "dots"
  if v <= 8:
    return "diag"
  if v <= 16:
    return "cross"
  return "noise"

def make_tile_dots(size: int = 12, radius: int = 2) -> Image.Image:
  tile = Image.new("L", (size, size), 0)
  d = ImageDraw.Draw(tile)
  cx = size // 2
  cy = size // 2
  d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=200)
  return tile

def make_tile_diag(size: int = 16, spacing: int = 6, thickness: int = 2) -> Image.Image:
  tile = Image.new("L", (size, size), 0)
  d = ImageDraw.Draw(tile)
  # draw multiple diagonals across the tile
  for offset in range(-size, size + spacing, spacing):
    d.line((offset, 0, offset + size, size), fill=160, width=thickness)
  return tile

def make_tile_cross(size: int = 16, spacing: int = 6, thickness: int = 2) -> Image.Image:
  a = make_tile_diag(size=size, spacing=spacing, thickness=thickness)
  b = make_tile_diag(size=size, spacing=spacing, thickness=thickness)
  b = b.transpose(Image.FLIP_LEFT_RIGHT)
  # combine with max
  return ImageChops.lighter(a, b)

def make_tile_noise(size: int = 12, density: float = 0.12) -> Image.Image:
  import random
  tile = Image.new("L", (size, size), 0)
  px = tile.load()
  count = int(size * size * density)
  for _ in range(count):
    x = random.randint(0, size - 1)
    y = random.randint(0, size - 1)
    px[x, y] = 180
  return tile

def tile_to_size(tile: Image.Image, w: int, h: int) -> Image.Image:
  """Repeat the tile to fill a WxH canvas."""
  out = Image.new("L", (w, h), 0)
  tw, th = tile.size
  for y in range(0, h, th):
    for x in range(0, w, tw):
      out.paste(tile, (x, y))
  return out

def make_annulus_mask(size: int, ring_width: int) -> Image.Image:
  """
  Create a mask for the outer frame area (the white ring),
  approximated as the difference between the full circle and an inner circle
  inset by ring_width.
  """
  m = Image.new("L", (size, size), 0)
  d = ImageDraw.Draw(m)
  # Outer full circle
  d.ellipse((0, 0, size - 1, size - 1), fill=255)
  # Punch inner hole
  inset = ring_width
  d.ellipse((inset, inset, size - 1 - inset, size - 1 - inset), fill=0)
  return m

def texture_for_cr(size: int, ring_width: int, cr: str) -> Image.Image:
  """Return an 'L' mask with texture for the frame based on CR."""
  kind = cr_to_texture_kind(cr)
  if kind == "dots":
    tile = make_tile_dots()
  elif kind == "diag":
    tile = make_tile_diag()
  elif kind == "cross":
    tile = make_tile_cross()
  else:
    tile = make_tile_noise()
  pattern = tile_to_size(tile, size, size)
  # Slightly reduce intensity
  pattern = pattern.point(lambda p: int(p * 0.7))
  # Clip to the annulus area (frame)
  annulus = make_annulus_mask(size, ring_width)
  return ImageChops.multiply(pattern, annulus)

# ---------- Google Sheets ----------

def open_sheet(service_account_json: Path, spreadsheet_id: str, worksheet: Optional[str]) -> gspread.Worksheet:
  scopes = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
  ]
  creds = Credentials.from_service_account_file(str(service_account_json), scopes=scopes)
  gc = gspread.authorize(creds)
  sh = gc.open_by_key(spreadsheet_id)
  return sh.worksheet(worksheet) if worksheet else sh.sheet1

def read_rows(ws: gspread.Worksheet) -> List[Dict[str, Any]]:
  # Reads as list of dicts keyed by header row
  return ws.get_all_records(default_blank="")

# ---------- CLI / Main ----------

def main():
  ap = argparse.ArgumentParser(description="Generate circular VTT tokens from a Google Sheet.")
  ap.add_argument("--sheet_id", required=True, help="Google Spreadsheet ID (the long key in the URL).")
  ap.add_argument("--worksheet", help="Worksheet/tab name (defaults to the first sheet).")
  ap.add_argument("--sa_json", required=True, help="Path to a Google service account JSON with read access.")
  ap.add_argument("--images_dir", required=True, help="Folder containing portrait images (optional).")
  ap.add_argument("--out_dir", required=True, help="Output folder for tokens.")
  ap.add_argument("--size", type=int, default=512, help="Token size in px (default 512).")
  ap.add_argument("--border", type=int, default=18, help="Outer ring thickness in px (default 18).")
  ap.add_argument("--stroke", type=int, default=6, help="Inner stroke thickness in px (default 6).")
  ap.add_argument("--badge", action="store_true", help="Render CR badge.")
  ap.add_argument("--crlabel", action="store_true", help="Prefix 'CR ' on badge.")
  ap.add_argument("--font", help="Path to a TTF/OTF font to use (optional).")
  ap.add_argument("--name_filter", help="Optional substring filter on Name column (case-insensitive).")
  ap.add_argument(
    "--suffix",
    default="",
    help="Optional suffix required in the portrait filename before the extension (e.g. '.alt')."
  )

  args = ap.parse_args()
  images_dir = Path(args.images_dir)
  out_dir = Path(args.out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  font_path = Path(args.font) if args.font else None

  # Open & read the sheet
  ws = open_sheet(Path(args.sa_json), args.sheet_id, args.worksheet)
  rows = read_rows(ws)

  if not rows:
    print("No rows found in the sheet.")
    return

  # Optional filter
  if args.name_filter:
    nf = args.name_filter.lower()
    rows = [r for r in rows if nf in str(r.get("Name","")).lower()]

  print(f"Found {len(rows)} rows.")
  for row in rows:
    try:
      name = get_name_from_row(row)
      cr = get_cr_from_row(row)
      color = pick_color_from_row(row)
      portrait = load_portrait(images_dir, name, args.suffix)

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
      print(f"Error in row '{row.get('Name','(no name)')}': {e}")

if __name__ == "__main__":
  main()
# New helper functions for CR-based texture