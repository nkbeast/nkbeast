#!/usr/bin/env python3
"""Generate featured tool cards (ghost-recover, reconk-cli) for the nkbeast profile."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 420
BOLD = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"
REG = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"

BG_TOP = (6, 13, 10)
BG_BOT = (10, 20, 15)
GREEN = (0, 255, 156)
GREEN_DIM = (0, 179, 104)
PALE = (214, 255, 234)
SUB = (140, 224, 180)
FEAT = (108, 189, 149)
PATHC = (86, 148, 118)
LINE = (24, 66, 48)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        g.putpixel((0, y), lerp(top, bottom, y / max(h - 1, 1)))
    return g.resize((w, h))


def base_card():
    img = vertical_gradient((W, H), BG_TOP, BG_BOT).convert("RGB")
    glow = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(glow)
    dg.ellipse([W / 2 - 560, -260, W / 2 + 560, 300], fill=40)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(vertical_gradient((W, H), (12, 32, 23), BG_TOP), img, glow)
    d = ImageDraw.Draw(img)
    d.line([(60, 26), (W - 60, 26)], fill=LINE, width=2)
    d.line([(60, H - 26), (W - 60, H - 26)], fill=LINE, width=2)
    for cx in (60, W - 60):
        d.line([(cx, 26), (cx, 54)], fill=LINE, width=2)
        d.line([(cx, H - 26), (cx, H - 54)], fill=LINE, width=2)
    return img


def finish(img, path):
    scan = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 3):
        sd.line([(0, y), (W, y)], fill=14)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(black, img, scan)
    vig = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.rectangle([0, 0, W, H], fill=70)
    dv.ellipse([-160, -140, W + 160, H + 140], fill=0)
    vig = vig.filter(ImageFilter.GaussianBlur(80))
    img = Image.composite(black, img, vig)
    img.save(path, "PNG")
    print(f"saved {path}")


def tracked_text(draw, x, y, text, font, tracking, fill):
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + tracking
    return x


def gradient_title(img, x, y, text, font, tracking):
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    xx = x
    for c in text:
        md.text((xx, y), c, font=font, fill=255)
        xx += md.textlength(c, font=font) + tracking
    grad = vertical_gradient((W, H), PALE, GREEN_DIM)
    return Image.composite(grad, img, mask)


def draw_ghost_icon(img, cx, cy, r):
    # glow
    gl = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(gl)
    _ghost(gd, cx, cy, r, GREEN)
    gl = gl.filter(ImageFilter.GaussianBlur(18))
    img = Image.blend(img, Image.blend(img, gl, 0.6), 0.85)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r * 1.35, cy - r * 1.35, cx + r * 1.35, cy + r * 1.35],
              outline=LINE, width=2)
    _ghost(d, cx, cy, r, GREEN)
    return img


def _ghost(d, cx, cy, r, fill):
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=fill)
    d.rectangle([cx - r, cy, cx + r, cy + r * 0.78], fill=fill)
    br = r * 0.30
    for i in range(4):
        bx = cx - r + br + i * (2 * r - 2 * br) / 3
        d.ellipse([bx - br, cy + r * 0.78 - br, bx + br, cy + r * 0.78 + br], fill=fill)
    er = r * 0.13
    for ex in (cx - r * 0.38, cx + r * 0.38):
        d.ellipse([ex - er, cy - r * 0.28 - er * 1.7, ex + er, cy - r * 0.28 + er * 1.7],
                  fill=BG_TOP)


def draw_radar_icon(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r * 1.35, cy - r * 1.35, cx + r * 1.35, cy + r * 1.35],
              outline=LINE, width=2)
    for rr, wd in ((r, 4), (r * 0.62, 3), (r * 0.30, 3)):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=GREEN_DIM, width=wd)
    d.line([(cx - r, cy), (cx + r, cy)], fill=GREEN_DIM, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=GREEN_DIM, width=2)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.pieslice([cx - r, cy - r, cx + r, cy + r], 300, 360, fill=(0, 255, 156, 66))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    for bx, by in ((cx + r * 0.45, cy - r * 0.38), (cx - r * 0.40, cy + r * 0.42)):
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=GREEN)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=GREEN)
    # sweep leading edge
    import math
    ex = cx + r * math.cos(math.radians(-60))
    ey = cy + r * math.sin(math.radians(-60))
    d.line([(cx, cy), (ex, ey)], fill=GREEN, width=3)
    return img


def make_card(path, repo, name, tagline, features, icon):
    img = base_card()
    d = ImageDraw.Draw(img)

    f_path = ImageFont.truetype(REG, 26)
    tracked_text(d, 100, 62, f"~/arsenal/{repo}", f_path, 3, PATHC)

    f_name = ImageFont.truetype(BOLD, 104)
    tracking = 8
    img = gradient_title(img, 100, 100, name, f_name, tracking)
    d = ImageDraw.Draw(img)

    f_tag = ImageFont.truetype(REG, 33)
    tracked_text(d, 100, 240, tagline, f_tag, 10, SUB)

    f_feat = ImageFont.truetype(REG, 25)
    tracked_text(d, 100, 312, features, f_feat, 2, FEAT)

    if icon == "ghost":
        img = draw_ghost_icon(img, 1290, 210, 92)
    else:
        img = draw_radar_icon(img, 1290, 210, 100)

    finish(img, path)


if __name__ == "__main__":
    make_card(
        "/home/nk/Documents/project/websites/nkbeast/assets/ghost-recover-card.png",
        "ghost-recover",
        "GHOST-RECOVER",
        "LINUX DATA RECOVERY ENGINE",
        "44 FILESYSTEMS · 315 FILE SIGNATURES · RAID · DRIVE IMAGING",
        "ghost",
    )
    make_card(
        "/home/nk/Documents/project/websites/nkbeast/assets/reconk-card.png",
        "reconk-cli",
        "RECONK-CLI",
        "BUG BOUNTY RECON ORCHESTRATOR",
        "SUBDOMAINS · DNS · LIVE HOSTS · URLS · JS ANALYSIS · TAKEOVERS",
        "radar",
    )
