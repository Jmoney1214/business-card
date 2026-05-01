"""
LED billboard wraparound ad: Moses the Jeweler x NY Knicks.
Output: 2100x420 MP4 (10s, 30fps, loops) + JPEG snapshot at ~4.5s.

Panels:
  Left  : 0    - 800
  Rear  : 800  - 1300
  Right : 1300 - 2100

90px safe padding from every panel edge. Text in left zone of each
side panel, QR in right zone. Rear panel: centered header + large QR.
"""

from __future__ import annotations

import math
import os
import subprocess
from pathlib import Path

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from qrcode.constants import ERROR_CORRECT_H

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

W, H = 2100, 420
FPS = 30
DURATION = 10.0
N_FRAMES = int(FPS * DURATION)  # 300

PANEL_LEFT = (0, 800)
PANEL_REAR = (800, 1300)
PANEL_RIGHT = (1300, 2100)
PAD = 90  # safe padding inside every panel edge

QR_URL = "https://mosesnyc.com"

# Knicks-meets-Mazal palette
BLACK = (10, 10, 12)
DEEP_BLUE = (0, 33, 71)        # Knicks navy
ROYAL_BLUE = (0, 107, 182)     # Knicks royal
ORANGE = (245, 132, 38)        # Knicks orange
WHITE = (255, 255, 255)
GOLD_LIGHT = (245, 217, 152)
GOLD = (212, 175, 55)
GOLD_DARK = (164, 122, 27)

ROOT = Path(__file__).parent
OUT_MP4 = ROOT / "moses_knicks_billboard.mp4"
OUT_JPG = ROOT / "moses_knicks_billboard.jpg"
QR_PNG = ROOT / "qr_mosesnyc.png"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_BLACK = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# QR code
# ---------------------------------------------------------------------------

def make_qr(url: str, size_px: int) -> Image.Image:
    """Solid black-on-white QR with H error correction. Crisp + scannable."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=2,  # quiet zone in modules
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size_px, size_px), Image.NEAREST)


def qr_card(qr: Image.Image, pad: int = 14) -> Image.Image:
    """Wrap the QR in a white card with subtle gold trim for contrast."""
    side = qr.size[0] + pad * 2
    card = Image.new("RGB", (side, side), WHITE)
    d = ImageDraw.Draw(card)
    # gold inner trim
    d.rectangle([0, 0, side - 1, side - 1], outline=GOLD, width=3)
    card.paste(qr, (pad, pad))
    return card


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def gradient_bg(t: float) -> Image.Image:
    """Animated background. Deep black with breathing blue-orange glows."""
    # Build at low res then upscale for speed + softness
    sw, sh = W // 6, H // 6
    arr = np.zeros((sh, sw, 3), dtype=np.float32)

    pulse = 0.5 + 0.5 * math.sin(t * 2.0 * math.pi / 2.5)  # 2.5s cycle
    pulse2 = 0.5 + 0.5 * math.sin(t * 2.0 * math.pi / 3.7 + 1.2)

    xs = np.linspace(0, W, sw)
    ys = np.linspace(0, H, sh)
    xg, yg = np.meshgrid(xs, ys)

    # Blue glow on left panel
    cx1, cy1 = 380, H / 2
    d1 = np.sqrt((xg - cx1) ** 2 + (yg - cy1) ** 2)
    g1 = np.exp(-(d1 ** 2) / (2 * 380 ** 2)) * (0.55 + 0.45 * pulse)

    # Orange glow on right panel
    cx2, cy2 = 1720, H / 2
    d2 = np.sqrt((xg - cx2) ** 2 + (yg - cy2) ** 2)
    g2 = np.exp(-(d2 ** 2) / (2 * 380 ** 2)) * (0.55 + 0.45 * pulse2)

    # Center gold glow on rear panel
    cx3, cy3 = 1050, H / 2
    d3 = np.sqrt((xg - cx3) ** 2 + (yg - cy3) ** 2)
    g3 = np.exp(-(d3 ** 2) / (2 * 280 ** 2)) * (0.55 + 0.45 * (1 - pulse))

    arr[..., 0] = BLACK[0] + ROYAL_BLUE[0] * g1 * 0.55 + ORANGE[0] * g2 * 0.55 + GOLD[0] * g3 * 0.35
    arr[..., 1] = BLACK[1] + ROYAL_BLUE[1] * g1 * 0.55 + ORANGE[1] * g2 * 0.55 + GOLD[1] * g3 * 0.35
    arr[..., 2] = BLACK[2] + ROYAL_BLUE[2] * g1 * 0.55 + ORANGE[2] * g2 * 0.55 + GOLD[2] * g3 * 0.35

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr).resize((W, H), Image.BILINEAR)
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    return img


def add_grain(img: Image.Image, t: float) -> Image.Image:
    """Subtle moving grain so an LED panel looks alive."""
    rng = np.random.default_rng(int(t * 1000) & 0xFFFF)
    noise = rng.integers(-6, 7, size=(H, W, 1), dtype=np.int16)
    arr = np.array(img, dtype=np.int16) + noise
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------------------
# Easing
# ---------------------------------------------------------------------------

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def ease_out_cubic(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x: float) -> float:
    x = clamp01(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_w(draw: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont) -> int:
    return draw.textbbox((0, 0), s, font=f)[2]


def text_h(draw: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont) -> int:
    bb = draw.textbbox((0, 0), s, font=f)
    return bb[3] - bb[1]


def draw_text_glow(canvas: Image.Image, xy, text: str, f, fill, glow=None,
                   glow_radius: int = 6, glow_alpha: int = 160):
    """Draw text with an optional soft glow halo."""
    if glow is not None:
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text(xy, text, font=f, fill=glow + (glow_alpha,))
        layer = layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        canvas.alpha_composite(layer)
    d = ImageDraw.Draw(canvas)
    d.text(xy, text, font=f, fill=fill + (255,) if len(fill) == 3 else fill)


# ---------------------------------------------------------------------------
# Panel composition
# ---------------------------------------------------------------------------

def render_side_panel(canvas: Image.Image, x0: int, x1: int, t: float,
                      qr_img: Image.Image):
    """
    Side panel layout (everything inside x0+PAD .. x1-PAD):
      text zone : x0+PAD .. text_right
      gutter    : 28px
      QR zone   : qr_x .. x1-PAD  (right-aligned)
    """
    text_left = x0 + PAD

    # QR sits right-aligned inside panel safe area
    qr_size = qr_img.size[0]
    qr_x = x1 - PAD - qr_size
    qr_y = (H - qr_size) // 2

    GUTTER = 28
    text_right = qr_x - GUTTER  # hard right boundary for any text

    # --- text animation (slide up + fade in) ---
    intro = clamp01((t - 0.30) / 0.55)
    intro_e = ease_out_cubic(intro)
    text_dy = int((1 - intro_e) * 70)
    text_alpha = int(255 * intro_e)

    f_eyebrow = font(FONT_BOLD, 20)
    f_head = font(FONT_BLACK, 50)
    f_brand = font(FONT_BOLD, 22)
    f_addr = font(FONT_BOLD, 18)

    draw = ImageDraw.Draw(canvas)

    def fits(s: str, f) -> bool:
        return text_w(draw, s, f) <= (text_right - text_left)

    # eyebrow line above headline (top of safe area is y=PAD=90)
    eyebrow = "MOSES  THE  JEWELER"
    line_y = 92
    draw_text_glow(
        canvas, (text_left, line_y + text_dy), eyebrow, f_eyebrow,
        fill=GOLD_LIGHT + (text_alpha,), glow=GOLD, glow_radius=4, glow_alpha=int(140 * intro_e)
    )

    # short orange rule under eyebrow
    rule_w = int(min(180, text_right - text_left) * intro_e)
    rule_y = line_y + 28
    if rule_w > 0:
        rule = Image.new("RGBA", (rule_w, 3), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rule)
        for i in range(rule_w):
            a = int(255 * (1 - abs(i - rule_w / 2) / (rule_w / 2 + 1)))
            rd.point((i, 1), fill=ORANGE + (a,))
        canvas.alpha_composite(rule, (text_left, rule_y + text_dy))

    # main headline across two lines
    h1_y = line_y + 40
    draw_text_glow(canvas, (text_left, h1_y + text_dy), "BRINGING", f_head,
                   fill=WHITE + (text_alpha,), glow=ROYAL_BLUE,
                   glow_radius=10, glow_alpha=int(200 * intro_e))
    h2_y = h1_y + 52
    chunk_x = text_left
    draw_text_glow(canvas, (chunk_x, h2_y + text_dy), "THE ", f_head,
                   fill=WHITE + (text_alpha,), glow=ROYAL_BLUE,
                   glow_radius=10, glow_alpha=int(200 * intro_e))
    chunk_x += text_w(draw, "THE ", f_head)
    draw_text_glow(canvas, (chunk_x, h2_y + text_dy), "MAZAL", f_head,
                   fill=ORANGE + (text_alpha,), glow=ORANGE,
                   glow_radius=14, glow_alpha=int(220 * intro_e))

    # × KNICKS sub line
    sub = "×  NEW  YORK  KNICKS"
    sub_y = h2_y + 60
    draw_text_glow(canvas, (text_left, sub_y + text_dy), sub, f_brand,
                   fill=GOLD + (text_alpha,), glow=GOLD_DARK,
                   glow_radius=6, glow_alpha=int(160 * intro_e))

    # bottom address / handle
    addr = "22A W 47TH ST · NYC"
    handle = "@MOSESJEWELRY"
    addr_y = sub_y + 32
    draw_text_glow(canvas, (text_left, addr_y + text_dy), addr, f_addr,
                   fill=WHITE + (text_alpha,), glow=ROYAL_BLUE,
                   glow_radius=4, glow_alpha=int(140 * intro_e))
    draw_text_glow(canvas, (text_left, addr_y + 22 + text_dy), handle, f_addr,
                   fill=ORANGE + (text_alpha,), glow=ORANGE,
                   glow_radius=4, glow_alpha=int(160 * intro_e))

    # --- QR animation (scale-in then breathe) ---
    qr_in = clamp01((t - 0.85) / 0.55)
    qr_e = ease_out_back(qr_in)
    breathe = 1.0 + 0.025 * math.sin((t - 1.4) * 2 * math.pi / 1.6)
    if qr_in < 1.0:
        scale = max(0.05, qr_e)
    else:
        scale = breathe
    sized = max(1, int(qr_size * scale))
    qr_scaled = qr_img.resize((sized, sized), Image.LANCZOS)
    qx = qr_x + (qr_size - sized) // 2
    qy = qr_y + (qr_size - sized) // 2

    # soft halo behind QR
    halo = Image.new("RGBA", (qr_size + 80, qr_size + 80), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse([0, 0, qr_size + 80, qr_size + 80],
               fill=GOLD + (int(60 * qr_in),))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=24))
    canvas.alpha_composite(halo, (qr_x - 40, qr_y - 40))

    canvas.paste(qr_scaled, (qx, qy))

    # SCAN caption under QR
    scan = "SCAN  TO  VISIT"
    f_scan = font(FONT_BOLD, 20)
    sw_ = text_w(draw, scan, f_scan)
    sx = qr_x + (qr_size - sw_) // 2
    sy = qr_y + qr_size + 14
    cap_alpha = int(255 * clamp01((t - 1.4) / 0.6))
    draw_text_glow(canvas, (sx, sy), scan, f_scan,
                   fill=GOLD_LIGHT + (cap_alpha,), glow=GOLD,
                   glow_radius=4, glow_alpha=int(160 * (cap_alpha / 255)))


def render_rear_panel(canvas: Image.Image, t: float, qr_img: Image.Image):
    """
    Rear panel: centered eyebrow + QR. Everything sits inside the panel
    safe area (90px padding all four edges).
    """
    x0, x1 = PANEL_REAR
    cx = (x0 + x1) // 2

    intro = clamp01((t - 0.45) / 0.6)
    intro_e = ease_out_cubic(intro)
    alpha = int(255 * intro_e)

    draw = ImageDraw.Draw(canvas)

    # QR is the main element — center it vertically in the safe area.
    qr_size = qr_img.size[0]
    qr_in = clamp01((t - 1.0) / 0.6)
    qr_e = ease_out_back(qr_in)
    breathe = 1.0 + 0.03 * math.sin((t - 1.6) * 2 * math.pi / 1.8)
    scale = max(0.05, qr_e) if qr_in < 1.0 else breathe
    sized = max(1, int(qr_size * scale))
    qr_scaled = qr_img.resize((sized, sized), Image.LANCZOS)

    qy = (H - qr_size) // 2  # vertically centered in full panel height
    qx = cx - sized // 2
    qy_draw = qy + (qr_size - sized) // 2

    halo = Image.new("RGBA", (qr_size + 80, qr_size + 80), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse([0, 0, qr_size + 80, qr_size + 80],
               fill=ORANGE + (int(70 * qr_in),))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=26))
    canvas.alpha_composite(halo, (cx - (qr_size + 80) // 2, qy - 40))

    canvas.paste(qr_scaled, (qx, qy_draw))

    # Eyebrow header sits inside the top safe band (above QR).
    f_eye = font(FONT_BLACK, 22)
    eye = "MOSES  ×  KNICKS"
    ew = text_w(draw, eye, f_eye)
    ex = cx - ew // 2
    ey = max(PAD, qy - 38) - int((1 - intro_e) * 16)
    draw_text_glow(canvas, (ex, ey), eye, f_eye,
                   fill=WHITE + (alpha,), glow=ROYAL_BLUE,
                   glow_radius=8, glow_alpha=int(220 * intro_e))

    # SCAN caption under QR, still inside the bottom safe band.
    f_scan = font(FONT_BOLD, 14)
    scan = "SCAN"
    sw_ = text_w(draw, scan, f_scan)
    sx = cx - sw_ // 2
    sy = qy + qr_size + 10
    if sy + 18 <= H - PAD:
        draw_text_glow(canvas, (sx, sy), scan, f_scan,
                       fill=GOLD_LIGHT + (alpha,), glow=GOLD,
                       glow_radius=3, glow_alpha=int(150 * intro_e))


# ---------------------------------------------------------------------------
# Frame composition
# ---------------------------------------------------------------------------

def compose_frame(t: float, qr_side: Image.Image, qr_rear: Image.Image) -> Image.Image:
    bg = gradient_bg(t).convert("RGBA")
    canvas = bg

    render_side_panel(canvas, *PANEL_LEFT, t=t, qr_img=qr_side)
    render_rear_panel(canvas, t=t, qr_img=qr_rear)
    render_side_panel(canvas, *PANEL_RIGHT, t=t, qr_img=qr_side)

    # global flash-in over the first ~0.3s
    flash = clamp01(1.0 - t / 0.30)
    if flash > 0:
        overlay = Image.new("RGBA", canvas.size, WHITE + (int(255 * flash),))
        canvas.alpha_composite(overlay)

    # fade-out at the very end so the loop bridge stays clean
    fade_start = DURATION - 0.4
    if t > fade_start:
        f = clamp01((t - fade_start) / 0.4)
        overlay = Image.new("RGBA", canvas.size, BLACK + (int(255 * f * 0.85),))
        canvas.alpha_composite(overlay)

    out = canvas.convert("RGB")
    out = add_grain(out, t)
    return out


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main():
    # QR sizing — keep both side and rear QRs fully inside their safe zones.
    # Side panel: 800w, 90 pad each side → 620 usable; ~244 card leaves 348 for text.
    # Rear panel: 500w, 90 pad each side → 320 usable; 244 card fits centered.
    qr_raw_side = make_qr(QR_URL, 220)
    qr_raw_rear = make_qr(QR_URL, 220)
    qr_side_card = qr_card(qr_raw_side, pad=12)
    qr_rear_card = qr_card(qr_raw_rear, pad=12)

    # Save the standalone QR for verification
    qr_raw_side.save(QR_PNG)

    # JPEG snapshot at ~4.5s
    snap = compose_frame(4.5, qr_side_card, qr_rear_card)
    snap.save(OUT_JPG, "JPEG", quality=92, optimize=True)
    print(f"wrote {OUT_JPG} ({snap.size})")

    # MP4 via piped ffmpeg
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-", "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart",
        str(OUT_MP4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(N_FRAMES):
            t = i / FPS
            frame = compose_frame(t, qr_side_card, qr_rear_card)
            proc.stdin.write(frame.tobytes())
            if i % 30 == 0:
                print(f"frame {i}/{N_FRAMES}  t={t:.2f}s")
        proc.stdin.close()
    except Exception:
        proc.kill()
        raise
    rc = proc.wait()
    if rc != 0:
        err = proc.stderr.read().decode("utf-8", "ignore")
        raise SystemExit(f"ffmpeg failed: {err[-2000:]}")
    print(f"wrote {OUT_MP4}")


if __name__ == "__main__":
    main()
