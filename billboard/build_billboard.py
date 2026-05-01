"""
LED billboard wraparound ad — Moses the Jeweler × NY Knicks Playoffs hype.

The MOSES tablet logo (top bar + two white arched tablet cutouts in a
black square) starts in pure black-and-white on a clean white field and
morphs across 10s into the glossy Knicks orange/blue colorway.

No QR codes. Pure brand promo: logo morph + headline + Knicks Playoffs
call-out.

Output: 2100x420 MP4 (10s, 30fps, loops) + JPEG snapshot at ~4.5s.

Panels:
  Left  : 0    - 800   morphing logo + headline (mirrored)
  Rear  : 800  - 1300  centered "MAZAL" hero with playoffs sub
  Right : 1300 - 2100  morphing logo + headline (mirrored)

90px safe padding on every panel edge.

Animation timeline (loops cleanly):
  0.0 - 1.0s  pure b&w, gentle entrance
  1.0 - 2.5s  background fades white → dark navy w/ Knicks glow
  2.5 - 5.0s  logo + headline fill black → Knicks orange (3D gradient)
  5.0 - 6.5s  blue rim glow emerges
  6.5 - 8.0s  glossy diagonal highlight sweeps across logo + MAZAL
  8.0 - 9.6s  hold full color, breathing pulse
  9.6 - 10.0s soft fade for clean loop bridge
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

def render_side_panel(canvas: Image.Image, x0: int, x1: int, t: float):
    """
    Side panel layout (everything inside x0+PAD .. x1-PAD):
      left  : morphing MOSES tablet logo (hero)
      right : stacked headline + playoffs call-out
    """
    text_left = x0 + PAD
    panel_right = x1 - PAD
    GUTTER = 32

    # Logo fills the safe-zone height, vertically centered.
    logo_h = H - 2 * PAD                     # 240
    logo_y = PAD                              # 90
    logo_w = int(logo_h * (1 - 0.13 - 0.025))  # ≈ 203
    logo_x = text_left

    intro = ease_out_cubic(clamp01(t / 0.8))
    intro_alpha = int(255 * intro)
    draw_moses_logo(canvas, logo_x, logo_y, logo_h, t, intro_alpha=intro_alpha)

    # Headline column to the right of the logo.
    head_left = logo_x + logo_w + GUTTER
    head_right = panel_right
    head_w = head_right - head_left  # ≈ 800-90-203-32-90 = 385

    color_p = ease_out_cubic(clamp01((t - 2.5) / 2.5))
    intro_t = ease_out_cubic(clamp01((t - 0.2) / 0.8))
    text_alpha = int(255 * intro_t)
    text_dy = int((1 - intro_t) * 22)

    body_color = lerp(BLACK, WHITE, color_p)
    accent = lerp(BLACK, ORANGE, color_p)
    gold_color = lerp(BLACK, GOLD_LIGHT, color_p)

    draw = ImageDraw.Draw(canvas)

    f_eyebrow = font(FONT_BOLD, 18)
    f_head = font(FONT_BLACK, 56)
    f_sub = font(FONT_BLACK, 28)
    f_addr = font(FONT_BOLD, 16)

    # Eyebrow
    draw.text((head_left, 96 + text_dy), "MOSES  THE  JEWELER",
              font=f_eyebrow, fill=gold_color + (text_alpha,))

    # "BRINGING" / "THE MAZAL"
    draw.text((head_left, 124 + text_dy), "BRINGING", font=f_head,
              fill=body_color + (text_alpha,))
    chunk_x = head_left
    draw.text((chunk_x, 184 + text_dy), "THE ", font=f_head,
              fill=body_color + (text_alpha,))
    chunk_x += draw.textlength("THE ", font=f_head)
    draw.text((chunk_x, 184 + text_dy), "MAZAL", font=f_head,
              fill=accent + (text_alpha,))

    # Playoffs call-out
    draw.text((head_left, 250 + text_dy), "×  KNICKS  PLAYOFFS",
              font=f_sub, fill=accent + (text_alpha,))

    # Footer line
    draw.text((head_left, 290 + text_dy),
              "@MOSESJEWELRY  ·  22A  W  47TH  ST  ·  NYC",
              font=f_addr, fill=body_color + (text_alpha,))


# ---------------------------------------------------------------------------
# Rear panel
# ---------------------------------------------------------------------------

def render_rear_panel(canvas: Image.Image, t: float):
    """
    Rear panel — centered playoffs hero text. Stacked:
        eyebrow:  MOSES  ×  KNICKS
        hero   :  MAZAL    (huge, morphs black → orange)
        sub    :  PLAYOFFS  2026
    Everything stays inside the 90px safe zone.
    """
    x0, x1 = PANEL_REAR
    cx = (x0 + x1) // 2
    draw = ImageDraw.Draw(canvas)

    color_p = ease_out_cubic(clamp01((t - 2.5) / 2.5))
    rim_p = ease_in_out(clamp01((t - 5.0) / 1.5))
    gloss_p = clamp01((t - 6.5) / 1.5)
    intro_t = ease_out_cubic(clamp01((t - 0.2) / 0.8))
    text_alpha = int(255 * intro_t)
    text_dy = int((1 - intro_t) * 22)

    f_eyebrow = font(FONT_BOLD, 18)
    f_hero = font(FONT_BLACK, 110)
    f_sub = font(FONT_BLACK, 28)

    # Eyebrow at top of safe zone
    eyebrow = "MOSES   ×   KNICKS"
    eyebrow_color = lerp(BLACK, GOLD_LIGHT, color_p)
    ew = draw.textlength(eyebrow, font=f_eyebrow)
    draw.text((cx - ew / 2, 100 + text_dy), eyebrow,
              font=f_eyebrow, fill=eyebrow_color + (text_alpha,))

    # Hero "MAZAL" - largest text on the billboard
    hero = "MAZAL"
    hero_top = lerp(BLACK, ORANGE_HOT, color_p)
    hero_bot = lerp(BLACK, ORANGE_DEEP, color_p)
    hw = draw.textlength(hero, font=f_hero)
    hx = cx - hw / 2
    hy = 138

    # Soft outer glow that emerges with color
    if color_p > 0.05:
        glow = Image.new("RGBA", (int(hw) + 120, 160), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((60, 10), hero, font=f_hero,
                fill=ORANGE + (int(200 * color_p),))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
        canvas.alpha_composite(glow, (int(hx) - 60, int(hy) - 10 + text_dy))

    # Render MAZAL with vertical 3D gradient by drawing letterform mask
    bb = draw.textbbox((0, 0), hero, font=f_hero)
    text_w_px = bb[2] - bb[0]
    text_h_px = bb[3] - bb[1]
    pad_w = 12
    layer = Image.new("RGBA", (text_w_px + 2 * pad_w, text_h_px + 2 * pad_w),
                      (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad_w - bb[0], pad_w - bb[1]), hero, font=f_hero,
            fill=(255, 255, 255, 255))
    mask = layer.split()[3]

    grad = vertical_gradient(layer.size[0], layer.size[1], hero_top, hero_bot)
    grad.putalpha(mask)

    # Blue rim glow (mirrors the logo treatment)
    if rim_p > 0:
        rim_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim_layer)
        rd.text((pad_w - bb[0], pad_w - bb[1]), hero, font=f_hero,
                fill=BLUE_RIM + (int(220 * rim_p),))
        # outline only — subtract original from blurred copy via masks
        rim_blur = rim_layer.filter(ImageFilter.GaussianBlur(radius=6))
        # mask out the inner area
        inner = Image.new("L", layer.size, 0)
        ImageDraw.Draw(inner).text((pad_w - bb[0], pad_w - bb[1]), hero,
                                   font=f_hero, fill=255)
        rim_arr = np.array(rim_blur)
        inner_arr = np.array(inner)
        rim_arr[..., 3] = np.clip(
            rim_arr[..., 3].astype(np.int16) - inner_arr.astype(np.int16),
            0, 255
        ).astype(np.uint8)
        rim_blur = Image.fromarray(rim_arr)
        canvas.alpha_composite(rim_blur,
                               (int(hx) - pad_w + bb[0],
                                int(hy) - pad_w + bb[1] + text_dy))

    canvas.alpha_composite(grad,
                           (int(hx) - pad_w + bb[0],
                            int(hy) - pad_w + bb[1] + text_dy))

    # Glossy sweep across MAZAL
    if gloss_p > 0:
        gloss = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gloss)
        sweep_x = int((layer.size[0] + 120) * (gloss_p - 0.1)) - 60
        for offset in range(-30, 31):
            falloff = 1 - abs(offset) / 30
            a = int(180 * falloff * (0.6 + 0.4 * gloss_p))
            gd.line([(sweep_x + offset, -20),
                     (sweep_x + offset + 40, layer.size[1] + 20)],
                    fill=WHITE + (a,), width=2)
        gloss = gloss.filter(ImageFilter.GaussianBlur(radius=2))
        gloss_arr = np.array(gloss)
        mask_arr = np.array(mask)
        gloss_arr[..., 3] = np.minimum(gloss_arr[..., 3], mask_arr)
        gloss = Image.fromarray(gloss_arr)
        canvas.alpha_composite(gloss,
                               (int(hx) - pad_w + bb[0],
                                int(hy) - pad_w + bb[1] + text_dy))

    # Bottom call-out: PLAYOFFS  '26
    sub = "PLAYOFFS   '26"
    sub_color = lerp(BLACK, WHITE, color_p)
    sw = draw.textlength(sub, font=f_sub)
    sy = 280
    draw.text((cx - sw / 2, sy + text_dy), sub, font=f_sub,
              fill=sub_color + (text_alpha,))


# ---------------------------------------------------------------------------
# Frame composition
# ---------------------------------------------------------------------------

def compose_frame(t: float) -> Image.Image:
    canvas = gradient_bg(t)

    render_side_panel(canvas, *PANEL_LEFT, t=t)
    render_rear_panel(canvas, t=t)
    render_side_panel(canvas, *PANEL_RIGHT, t=t)

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
    # JPEG snapshot at ~4.5s — mid-morph (orange filling in, rim emerging)
    snap = compose_frame(4.5)
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
            frame = compose_frame(t)
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
