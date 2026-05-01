"""
LED billboard wraparound ad: MOSES tablet logo morphs from b&w to the
NY Knicks orange/blue colorway over 10s.

Output: 2100x420 MP4 (10s, 30fps, loops) + JPEG snapshot at ~4.5s.

Panels:
  Left  : 0    - 800
  Rear  : 800  - 1300
  Right : 1300 - 2100

90px safe padding on every panel edge. Side panels: morphing MOSES tablet
logo (left zone), tagline + QR stacked (right zone). Side panels are
mirrored. Rear panel: morphing "MAZAL" header centered + large QR centered.

Animation timeline (continuous, loops cleanly):
  0.0 - 1.0s  white background + pure black logo, gentle entrance
  1.0 - 2.5s  background fades white → dark navy w/ Knicks glow
  2.5 - 5.0s  logo body fills black → Knicks orange (top-down sweep)
  5.0 - 6.5s  blue rim glow emerges + 3D vertical gradient settles
  6.5 - 8.0s  glossy highlight sweeps across the logo
  8.0 - 9.6s  hold full color, breathing pulse
  9.6 - 10.0s soft fade to bridge the loop
"""

from __future__ import annotations

import math
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
N_FRAMES = int(FPS * DURATION)

PANEL_LEFT = (0, 800)
PANEL_REAR = (800, 1300)
PANEL_RIGHT = (1300, 2100)
PAD = 90

QR_URL = "https://mosesnyc.com"

# Palette
WHITE_BG = (250, 250, 250)
BLACK = (8, 8, 10)
DARK_NAVY = (10, 14, 28)
NAVY = (0, 33, 71)              # Knicks navy
ROYAL = (0, 107, 182)            # Knicks royal
BLUE_RIM = (60, 150, 240)
ORANGE = (245, 132, 38)
ORANGE_HOT = (255, 170, 70)
ORANGE_DEEP = (190, 78, 14)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
GOLD_LIGHT = (245, 217, 152)

ROOT = Path(__file__).parent
OUT_MP4 = ROOT / "moses_knicks_billboard.mp4"
OUT_JPG = ROOT / "moses_knicks_billboard.jpg"
QR_PNG = ROOT / "qr_mosesnyc.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_BLACK = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Easing + color helpers
# ---------------------------------------------------------------------------

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def ease_out_cubic(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, t: float):
    t = clamp01(t)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------------------
# QR
# ---------------------------------------------------------------------------

def make_qr(url: str, size_px: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size_px, size_px), Image.NEAREST)


def qr_card(qr: Image.Image, pad: int = 12, trim_color=GOLD) -> Image.Image:
    side = qr.size[0] + pad * 2
    card = Image.new("RGB", (side, side), WHITE)
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, side - 1, side - 1], outline=trim_color, width=3)
    card.paste(qr, (pad, pad))
    return card


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

def gradient_bg(t: float) -> Image.Image:
    """Background morphs from clean white to Knicks-blue-and-orange glow."""
    bg_p = ease_in_out(clamp01((t - 1.0) / 1.8))

    sw, sh = W // 6, H // 6

    # base color: white → near-black navy
    base = lerp(WHITE_BG, DARK_NAVY, bg_p)
    arr = np.full((sh, sw, 3), base, dtype=np.float32)

    if bg_p > 0:
        pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.5)
        pulse2 = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.7 + 1.2)

        xs = np.linspace(0, W, sw)
        ys = np.linspace(0, H, sh)
        xg, yg = np.meshgrid(xs, ys)

        # blue glow on left, orange glow on right, gold center
        for cx, cy, sigma, color, weight in [
            (380, H / 2, 380, ROYAL, 0.55 * (0.55 + 0.45 * pulse)),
            (1720, H / 2, 380, ORANGE, 0.55 * (0.55 + 0.45 * pulse2)),
            (1050, H / 2, 280, ORANGE, 0.35 * (0.6 + 0.4 * (1 - pulse))),
        ]:
            d = np.sqrt((xg - cx) ** 2 + (yg - cy) ** 2)
            g = np.exp(-(d ** 2) / (2 * sigma ** 2)) * weight * bg_p
            arr[..., 0] += color[0] * g
            arr[..., 1] += color[1] * g
            arr[..., 2] += color[2] * g

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr).resize((W, H), Image.BILINEAR)
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    return img.convert("RGBA")


def add_grain(img: Image.Image, t: float, strength: int = 5) -> Image.Image:
    rng = np.random.default_rng(int(t * 1000) & 0xFFFF)
    noise = rng.integers(-strength, strength + 1, size=(H, W, 1), dtype=np.int16)
    arr = np.array(img, dtype=np.int16) + noise
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------------------
# MOSES tablet logo
# ---------------------------------------------------------------------------

def vertical_gradient(width: int, height: int, top_color, bottom_color) -> Image.Image:
    """Solid vertical gradient (RGBA)."""
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    arr[..., 3] = 255
    for r in range(height):
        f = r / max(1, height - 1)
        c = lerp(top_color, bottom_color, f)
        arr[r, :, 0] = c[0]
        arr[r, :, 1] = c[1]
        arr[r, :, 2] = c[2]
    return Image.fromarray(arr)


def draw_moses_logo(canvas: Image.Image, x0: int, y0: int, h: int, t: float,
                    intro_alpha: int = 255):
    """
    Draw the MOSES tablet logo with the b&w → Knicks-color morph.

    Layout (proportions of total height h):
      top bar   : 13%  (with letter-spaced "MOSES" text)
      gap       : 2.5%
      bottom    : 84.5% (square, with two arched "tablet" cutouts)

    Returns the rendered logo width (= bottom-block width).
    """
    bar_h = max(1, int(h * 0.13))
    gap_h = max(1, int(h * 0.025))
    block_h = h - bar_h - gap_h
    block_w = block_h  # square
    bar_w = block_w

    # animation timing
    color_p = ease_out_cubic(clamp01((t - 2.5) / 2.5))   # 2.5 → 5.0s
    rim_p = ease_in_out(clamp01((t - 5.0) / 1.5))        # 5.0 → 6.5s
    gloss_p = clamp01((t - 6.5) / 1.5)                   # 6.5 → 8.0s
    breathe = 1.0 + 0.012 * math.sin((t - 8.0) * 2 * math.pi / 1.6)

    # working layer with margin for rim glow + gloss
    margin = 28
    layer = Image.new("RGBA", (block_w + 2 * margin, h + 2 * margin), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    lx, ly = margin, margin

    # Body colors
    body_top = lerp(BLACK, ORANGE_HOT, color_p)
    body_bot = lerp(BLACK, ORANGE_DEEP, color_p)

    by0 = ly + bar_h + gap_h
    by1 = ly + h

    # Top bar
    bar_grad = vertical_gradient(bar_w, bar_h,
                                 lerp(BLACK, ORANGE, color_p),
                                 lerp(BLACK, ORANGE_DEEP, color_p))
    layer.paste(bar_grad, (lx, ly))

    # Bottom block
    block_grad = vertical_gradient(block_w, block_h, body_top, body_bot)
    layer.paste(block_grad, (lx, by0))

    # MOSES text in top bar
    bar_font_size = max(6, int(bar_h * 0.5))
    f_bar = font(FONT_BOLD, bar_font_size)
    text_str = "M  O  S  E  S"
    bb = ld.textbbox((0, 0), text_str, font=f_bar)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    tx = lx + (bar_w - tw) // 2
    ty = ly + (bar_h - th) // 2 - bb[1]
    text_color = lerp(WHITE, NAVY, color_p)
    ld.text((tx, ty), text_str, font=f_bar, fill=text_color)

    # Two arched "tablet" cutouts (white, always)
    margin_x = int(block_w * 0.13)
    inner_gap = int(block_w * 0.07)
    arch_w = (block_w - 2 * margin_x - inner_gap) // 2
    arch_top_y = by0 + int(block_h * 0.13)

    arch_color = lerp(WHITE, (235, 240, 255), color_p)
    for i in range(2):
        ax = lx + margin_x + i * (arch_w + inner_gap)
        # tombstone shape: top half-circle + rectangle below
        ld.ellipse([ax, arch_top_y, ax + arch_w, arch_top_y + arch_w],
                   fill=arch_color)
        ld.rectangle([ax, arch_top_y + arch_w // 2, ax + arch_w, by1],
                     fill=arch_color)

    # White highlight along the very top edge (subtle 3D)
    if color_p > 0.4:
        hl_alpha = int(180 * (color_p - 0.4) / 0.6)
        hl = Image.new("RGBA", (bar_w, 4), (0, 0, 0, 0))
        ImageDraw.Draw(hl).rectangle([0, 0, bar_w, 4],
                                      fill=WHITE + (hl_alpha,))
        layer.alpha_composite(hl, (lx, ly))

    # Blue rim glow once colored
    if rim_p > 0:
        rim_alpha = int(255 * rim_p)
        rim = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim)
        rd.rectangle([lx, ly, lx + bar_w, ly + bar_h],
                     outline=BLUE_RIM + (rim_alpha,), width=3)
        rd.rectangle([lx, by0, lx + block_w, by1],
                     outline=BLUE_RIM + (rim_alpha,), width=3)
        # outer glow
        glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rectangle([lx - 4, ly - 4, lx + bar_w + 4, ly + bar_h + 4],
                     outline=BLUE_RIM + (rim_alpha // 2,), width=6)
        gd.rectangle([lx - 4, by0 - 4, lx + block_w + 4, by1 + 4],
                     outline=BLUE_RIM + (rim_alpha // 2,), width=6)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=6))
        layer.alpha_composite(glow)
        layer.alpha_composite(rim)

    # Glossy diagonal sweep across the body
    if gloss_p > 0:
        gloss = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gloss)
        sweep_x = lx + int((bar_w + 200) * (gloss_p - 0.2)) - 100
        for offset in range(-40, 41):
            falloff = 1 - abs(offset) / 40
            a = int(160 * falloff * (0.5 + 0.5 * gloss_p))
            gd.line([(sweep_x + offset, ly - 10),
                     (sweep_x + offset + 60, ly + h + 10)],
                    fill=WHITE + (a,), width=2)
        gloss = gloss.filter(ImageFilter.GaussianBlur(radius=2))
        # mask to logo silhouette only
        mask = Image.new("L", layer.size, 0)
        md = ImageDraw.Draw(mask)
        md.rectangle([lx, ly, lx + bar_w, ly + bar_h], fill=255)
        md.rectangle([lx, by0, lx + block_w, by1], fill=255)
        gloss.putalpha(Image.eval(mask, lambda v: v).point(
            lambda v, alpha=gloss.split()[3]: 0))
        # easier: just compose then mask via alpha
        gloss_arr = np.array(gloss)
        mask_arr = np.array(mask)
        gloss_arr[..., 3] = np.minimum(gloss_arr[..., 3], mask_arr)
        gloss = Image.fromarray(gloss_arr)
        layer.alpha_composite(gloss)

    # Apply intro alpha + breathe scale
    if intro_alpha < 255:
        a = layer.split()[3].point(lambda v: int(v * intro_alpha / 255))
        layer.putalpha(a)
    if abs(breathe - 1.0) > 0.001:
        new_w = int(layer.size[0] * breathe)
        new_h = int(layer.size[1] * breathe)
        layer = layer.resize((new_w, new_h), Image.LANCZOS)

    cx = x0 - margin + (block_w + 2 * margin - layer.size[0]) // 2
    cy = y0 - margin + (h + 2 * margin - layer.size[1]) // 2
    canvas.alpha_composite(layer, (cx, cy))
    return block_w


# ---------------------------------------------------------------------------
# Side panel
# ---------------------------------------------------------------------------

def render_side_panel(canvas: Image.Image, x0: int, x1: int, t: float,
                      qr_img: Image.Image):
    """
    Side panel layout (everything inside x0+PAD .. x1-PAD):
      left   : MOSES tablet logo (the b&w → color hero)
      middle : tagline column
      right  : QR card

    Hard rule: text NEVER crosses into the QR card.
    """
    text_left = x0 + PAD

    # Right zone: QR card vertically centered.
    qr_size = qr_img.size[0]
    qr_x = x1 - PAD - qr_size
    qr_y = (H - qr_size) // 2

    GUTTER = 24

    # Left zone: morphing logo, vertically centered.
    logo_h = 200
    logo_y = (H - logo_h) // 2
    logo_w = int(logo_h * (1 - 0.13 - 0.025))  # ≈169
    logo_x = text_left

    intro = ease_out_cubic(clamp01(t / 0.8))
    intro_alpha = int(255 * intro)
    draw_moses_logo(canvas, logo_x, logo_y, logo_h, t, intro_alpha=intro_alpha)

    # Middle zone: tagline column between logo and QR.
    tag_left = logo_x + logo_w + GUTTER
    tag_right = qr_x - GUTTER
    tag_w = tag_right - tag_left  # ≈ 800-90-186-24-24-200 = 276 (when QR=200)

    color_p = ease_out_cubic(clamp01((t - 2.5) / 2.5))
    intro_t = ease_out_cubic(clamp01((t - 0.2) / 0.8))
    text_alpha = int(255 * intro_t)
    text_dy = int((1 - intro_t) * 18)

    body_color = lerp(BLACK, WHITE, color_p)
    accent = lerp(BLACK, ORANGE, color_p)
    sub_color = lerp(BLACK, GOLD_LIGHT, color_p)

    draw = ImageDraw.Draw(canvas)

    f_head = font(FONT_BLACK, 34)
    f_sub = font(FONT_BOLD, 20)
    f_addr = font(FONT_BOLD, 14)

    # Vertical stack inside [PAD .. H-PAD] = [90 .. 330]:
    draw.text((tag_left, 110 + text_dy), "BRINGING", font=f_head,
              fill=body_color + (text_alpha,))
    chunk_x = tag_left
    draw.text((chunk_x, 148 + text_dy), "THE ", font=f_head,
              fill=body_color + (text_alpha,))
    chunk_x += draw.textlength("THE ", font=f_head)
    draw.text((chunk_x, 148 + text_dy), "MAZAL", font=f_head,
              fill=accent + (text_alpha,))

    draw.text((tag_left, 196 + text_dy), "×  KNICKS",
              font=f_sub, fill=sub_color + (text_alpha,))

    draw.text((tag_left, 232 + text_dy), "@MOSESJEWELRY", font=f_addr,
              fill=accent + (text_alpha,))
    draw.text((tag_left, 254 + text_dy), "22A  W  47TH  ST  ·  NYC",
              font=f_addr, fill=body_color + (text_alpha,))

    # Halo behind QR that emerges as the bg darkens.
    bg_p = ease_in_out(clamp01((t - 1.0) / 1.8))
    if bg_p > 0:
        halo = Image.new("RGBA", (qr_size + 80, qr_size + 80), (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse(
            [0, 0, qr_size + 80, qr_size + 80],
            fill=ORANGE + (int(50 * bg_p),))
        halo = halo.filter(ImageFilter.GaussianBlur(radius=24))
        canvas.alpha_composite(halo, (qr_x - 40, qr_y - 40))

    # QR scale-in fast (visible by t≈0.5s) then breathe.
    qr_in = ease_out_cubic(clamp01(t / 0.6))
    breathe = 1.0 + 0.02 * math.sin((t - 1.5) * 2 * math.pi / 1.8)
    scale = max(0.05, qr_in) if qr_in < 1.0 else breathe
    sized = max(1, int(qr_size * scale))
    qr_scaled = qr_img.resize((sized, sized), Image.LANCZOS)
    qx = qr_x + (qr_size - sized) // 2
    qy = qr_y + (qr_size - sized) // 2
    canvas.paste(qr_scaled, (qx, qy))


# ---------------------------------------------------------------------------
# Rear panel
# ---------------------------------------------------------------------------

def render_rear_panel(canvas: Image.Image, t: float, qr_img: Image.Image):
    x0, x1 = PANEL_REAR
    cx = (x0 + x1) // 2
    draw = ImageDraw.Draw(canvas)

    color_p = ease_out_cubic(clamp01((t - 2.5) / 2.5))
    intro_t = ease_out_cubic(clamp01((t - 0.2) / 0.8))
    text_alpha = int(255 * intro_t)
    text_dy = int((1 - intro_t) * 16)

    # Top: morphing "MAZAL" word
    f_head = font(FONT_BLACK, 56)
    head = "MAZAL"
    head_color = lerp(BLACK, ORANGE, color_p)
    hw = draw.textlength(head, font=f_head)
    hx = cx - hw / 2
    hy = 92

    # subtle glow that emerges with color
    if color_p > 0.05:
        glow = Image.new("RGBA", (int(hw) + 80, 80), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((40, 0), head, font=f_head, fill=ORANGE + (int(180 * color_p),))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=12))
        canvas.alpha_composite(glow, (int(hx) - 40, int(hy) - 8 + text_dy))

    draw.text((hx, hy + text_dy), head, font=f_head,
              fill=head_color + (text_alpha,))

    # tiny eyebrow above MAZAL
    f_eye = font(FONT_BOLD, 14)
    eye = "MOSES  ×  KNICKS"
    eye_color = lerp(BLACK, GOLD_LIGHT, color_p)
    ew = draw.textlength(eye, font=f_eye)
    ex = cx - ew / 2
    ey = hy - 22
    draw.text((ex, ey + text_dy), eye, font=f_eye,
              fill=eye_color + (text_alpha,))

    # Centered QR — visible immediately, scales in fast.
    qr_size = qr_img.size[0]
    qr_in = ease_out_cubic(clamp01(t / 0.6))
    breathe = 1.0 + 0.025 * math.sin((t - 1.6) * 2 * math.pi / 1.8)
    scale = max(0.05, qr_in) if qr_in < 1.0 else breathe
    sized = max(1, int(qr_size * scale))
    qr_scaled = qr_img.resize((sized, sized), Image.LANCZOS)

    qy = hy + 70
    qx = cx - sized // 2

    # halo behind QR that emerges with color
    bg_p = ease_in_out(clamp01((t - 1.0) / 1.8))
    if bg_p > 0:
        halo = Image.new("RGBA", (qr_size + 80, qr_size + 80), (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse(
            [0, 0, qr_size + 80, qr_size + 80],
            fill=ORANGE + (int(70 * bg_p),))
        halo = halo.filter(ImageFilter.GaussianBlur(radius=26))
        canvas.alpha_composite(halo, (cx - (qr_size + 80) // 2,
                                      qy + (qr_size - sized) // 2 - 40))

    canvas.paste(qr_scaled, (qx, qy + (qr_size - sized) // 2))


# ---------------------------------------------------------------------------
# Frame composition
# ---------------------------------------------------------------------------

def compose_frame(t: float, qr_side: Image.Image, qr_rear: Image.Image) -> Image.Image:
    canvas = gradient_bg(t)

    render_side_panel(canvas, *PANEL_LEFT, t=t, qr_img=qr_side)
    render_rear_panel(canvas, t=t, qr_img=qr_rear)
    render_side_panel(canvas, *PANEL_RIGHT, t=t, qr_img=qr_side)

    # gentle flash-in over first ~0.25s (white veil that fades)
    flash = clamp01(1.0 - t / 0.25)
    if flash > 0:
        overlay = Image.new("RGBA", canvas.size, WHITE + (int(255 * flash),))
        canvas.alpha_composite(overlay)

    # fade-out at the very end so loop bridge stays clean
    fade_start = DURATION - 0.4
    if t > fade_start:
        f = clamp01((t - fade_start) / 0.4)
        # fade target = the early-state white so the loop joins naturally
        overlay = Image.new("RGBA", canvas.size,
                            WHITE_BG + (int(255 * f * 0.85),))
        canvas.alpha_composite(overlay)

    out = canvas.convert("RGB")
    out = add_grain(out, t, strength=4)
    return out


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main():
    # QR cards: 200 (side) and 200 (rear). Card = raw + 2*pad. ECC=H, version
    # auto. Side card 200x200 fits comfortably inside the side safe zone with
    # text + logo; rear card 200x200 fits the centered rear safe zone.
    qr_raw_side = make_qr(QR_URL, 176)  # card = 200
    qr_raw_rear = make_qr(QR_URL, 200)
    qr_side_card = qr_card(qr_raw_side, pad=12)
    qr_rear_card = qr_card(qr_raw_rear, pad=12)

    qr_raw_side.save(QR_PNG)

    # JPEG snapshot at ~4.5s — mid-morph (orange filling in, rim emerging)
    snap = compose_frame(4.5, qr_side_card, qr_rear_card)
    snap.save(OUT_JPG, "JPEG", quality=92, optimize=True)
    print(f"wrote {OUT_JPG} ({snap.size})")

    # MP4
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-", "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "20",
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
