#!/usr/bin/env python3
"""Generate a clean phosphor-terminal banner for the nkbeast profile."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

W, H = 1600, 420
BOLD = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"
REG = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"

# palette
BG_TOP = (6, 13, 10)
BG_BOT = (10, 20, 15)
GREEN = (0, 255, 156)
GREEN_DIM = (0, 179, 104)
PALE = (214, 255, 234)
SUB = (140, 224, 180)
LINE = (24, 66, 48)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        g.putpixel((0, y), lerp(top, bottom, y / max(h - 1, 1)))
    return g.resize((w, h))


def draw_tracked(draw, xy_center, text, font, tracking, fill):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy_center[0] - total / 2
    for c, w in zip(text, widths):
        draw.text((x, xy_center[1]), c, font=font, fill=fill)
        x += w + tracking
    return total


def make(path):
    img = vertical_gradient((W, H), BG_TOP, BG_BOT).convert("RGB")

    # soft center glow
    glow = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(glow)
    dg.ellipse([W / 2 - 560, -260, W / 2 + 560, 300], fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(
        vertical_gradient((W, H), (14, 36, 26), BG_TOP), img, glow
    )

    d = ImageDraw.Draw(img)

    # hairline frame
    d.line([(60, 26), (W - 60, 26)], fill=LINE, width=2)
    d.line([(60, H - 26), (W - 60, H - 26)], fill=LINE, width=2)
    for cx in (60, W - 60):  # corner ticks
        d.line([(cx, 26), (cx, 54)], fill=LINE, width=2)
        d.line([(cx, H - 26), (cx, H - 54)], fill=LINE, width=2)

    # ---- title ----
    title_font = ImageFont.truetype(BOLD, 168)
    title = "NKBEAST"
    # measure with tracking
    tw = sum(d.textlength(c, font=title_font) for c in title) + 26 * (len(title) - 1)
    tx, ty = W / 2 - tw / 2, 74

    # glow layer
    glow_layer = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    x = tx
    for c in title:
        gd.text((x, ty), c, font=title_font, fill=GREEN)
        x += d.textlength(c, font=title_font) + 26
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(22))
    img = Image.blend(img, Image.blend(img, glow_layer, 0.55), 0.9)
    d = ImageDraw.Draw(img)

    # gradient-filled title via mask
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    x = tx
    for c in title:
        md.text((x, ty), c, font=title_font, fill=255)
        x += d.textlength(c, font=title_font) + 26
    grad = vertical_gradient((W, H), PALE, GREEN_DIM)
    band = vertical_gradient((W, 200), (0, 0, 0), (0, 0, 0))
    img = Image.composite(grad, img, mask)
    d = ImageDraw.Draw(img)

    # gradient rule under title
    rule_y = 308
    for rx in range(500, W - 500):
        t = 1 - abs((rx - 500) / (W - 1000) - 0.5) * 2
        col = lerp((8, 48, 32), GREEN, t)
        d.line([(rx, rule_y), (rx, rule_y + 2)], fill=col)

    # subtitle
    sub_font = ImageFont.truetype(REG, 30)
    draw_tracked(d, (W / 2, 330), "OFFENSIVE SECURITY RESEARCHER", sub_font, 18, SUB)

    # scanlines (subtle)
    scan = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 3):
        sd.line([(0, y), (W, y)], fill=14)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(black, img, scan)

    # vignette
    vig = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.rectangle([0, 0, W, H], fill=70)
    dv.ellipse([-160, -140, W + 160, H + 140], fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(80))
    img = Image.composite(black, img, vig)

    img.save(path, "PNG")
    print(f"saved {path} ({W}x{H})")


if __name__ == "__main__":
    make("/home/nk/Documents/project/websites/nkbeast/assets/crt-banner.png")
