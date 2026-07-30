# -*- coding: utf-8 -*-
"""🖼️ "Oddiy Rasm" bo'limi uchun yakuniy rasm generatsiya qiluvchi modul.

Foydalanuvchi yozgan nom/matn va tanlagan uslubi asosida PIL yordamida
tayyor rasm (PNG) yaratadi va vaqtincha faylga saqlaydi.
"""

import os
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from data.rasm_uslublari_data import STYLES

CANVAS_SIZE = (1080, 1080)

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_BUNDLED_BOLD = os.path.join(_PROJECT_ROOT, "assets", "fonts", "Poppins-Bold.ttf")
_BUNDLED_REGULAR = os.path.join(_PROJECT_ROOT, "assets", "fonts", "Poppins-Regular.ttf")

_SYSTEM_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_SYSTEM_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _first_existing(paths, fallback):
    for p in paths:
        if os.path.exists(p):
            return p
    return fallback


FONT_PATH_BOLD = _first_existing(
    [_BUNDLED_BOLD] + _SYSTEM_BOLD_CANDIDATES, _BUNDLED_BOLD
)
FONT_PATH_REGULAR = _first_existing(
    [_BUNDLED_REGULAR] + _SYSTEM_REGULAR_CANDIDATES, _BUNDLED_REGULAR
)


def _vertical_gradient(size, color_from, color_to):
    w, h = size
    base = Image.new("RGB", (1, h), color_from)
    top = Image.new("RGB", (1, h), color_to)
    mask = Image.linear_gradient("L").resize((1, h))
    grad = Image.composite(top, base, mask)
    return grad.resize((w, h))


def _fit_font(draw, text, max_width, start_size=170, min_size=40):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(FONT_PATH_BOLD, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            return font, bbox
        size -= 4
    font = ImageFont.truetype(FONT_PATH_BOLD, min_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    return font, bbox


def generate_oddiy_rasm(text: str, style_id: str) -> str:
    """Berilgan matn va uslub bo'yicha yakuniy rasmni yaratadi.

    Qaytaradi: vaqtinchalik PNG fayl yo'li.
    """
    style = None
    for s in STYLES:
        if s["id"] == style_id:
            style = s
            break
    if style is None:
        style = STYLES[0]

    text = (text or "").strip().upper()[:28] or "XONFIRE"

    w, h = CANVAS_SIZE
    img = _vertical_gradient((w, h), style["bg_from"], style["bg_to"]).convert("RGB")

    # Yengil "vinyet" effekti - chetlarni qorong'ilashtirish
    vignette = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-w * 0.3, -h * 0.3, w * 1.3, h * 1.3), fill=180)
    vignette = vignette.filter(ImageFilter.GaussianBlur(180))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    img = Image.composite(img, dark, vignette)

    draw = ImageDraw.Draw(img)

    accent = style["accent"]

    # Fon bezaklari: ikki nozik gorizontal chiziq
    draw.line([(w * 0.15, h * 0.34), (w * 0.85, h * 0.34)], fill=accent, width=4)
    draw.line([(w * 0.15, h * 0.66), (w * 0.85, h * 0.66)], fill=accent, width=4)

    # Asosiy matn (glow effekti bilan)
    max_text_width = int(w * 0.82)
    font, bbox = _fit_font(draw, text, max_text_width)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (w - tw) / 2 - bbox[0]
    ty = (h - th) / 2 - bbox[1]

    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text((tx, ty), text, font=font, fill=accent + (255,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer)

    draw = ImageDraw.Draw(img)
    draw.text(
        (tx, ty),
        text,
        font=font,
        fill=style["text_color"],
        stroke_width=3,
        stroke_fill=accent,
    )

    # Pastki kichik yorliq
    tag = "XONFIRE BOT"
    small_font = ImageFont.truetype(FONT_PATH_REGULAR, 30)
    tag_bbox = draw.textbbox((0, 0), tag, font=small_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    draw.text(((w - tag_w) / 2, h * 0.88), tag, font=small_font, fill=accent)

    out_dir = tempfile.mkdtemp(prefix="oddiy_rasm_")
    out_path = os.path.join(out_dir, "natija.png")
    img.convert("RGB").save(out_path, "PNG")
    return out_path


def generate_style_grid() -> str:
    """10 ta uslubni 2 ustun x 5 qatorli jadval (kollaj) ko'rinishida birlashtiradi,
    har bir katakka raqam va nom yozadi. Foydalanuvchi shu rasmga qarab uslub
    tanlaydi."""
    cols, rows = 2, 5
    cell_w, cell_h = 480, 300
    pad = 14
    grid_w = cols * cell_w + pad * (cols + 1)
    grid_h = rows * cell_h + pad * (rows + 1)

    canvas = Image.new("RGB", (grid_w, grid_h), (10, 10, 12))
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.truetype(FONT_PATH_BOLD, 28)

    for idx, style in enumerate(STYLES):
        col = idx % cols
        row = idx // cols
        x0 = pad + col * (cell_w + pad)
        y0 = pad + row * (cell_h + pad)

        if style["preview"] and os.path.exists(style["preview"]):
            thumb = Image.open(style["preview"]).convert("RGB")
            # markazdan kesib, katakka moslashtirish (cover)
            tw, th = thumb.size
            target_ratio = cell_w / cell_h
            src_ratio = tw / th
            if src_ratio > target_ratio:
                new_w = int(th * target_ratio)
                left = (tw - new_w) // 2
                thumb = thumb.crop((left, 0, left + new_w, th))
            else:
                new_h = int(tw / target_ratio)
                top = (th - new_h) // 2
                thumb = thumb.crop((0, top, tw, top + new_h))
            thumb = thumb.resize((cell_w, cell_h))
        else:
            thumb = _vertical_gradient((cell_w, cell_h), style["bg_from"], style["bg_to"])

        canvas.paste(thumb, (x0, y0))

        # Raqam belgisi (chapdan yuqori burchakda)
        badge_r = 26
        bx, by = x0 + 18, y0 + 18
        draw.ellipse((bx, by, bx + badge_r * 2, by + badge_r * 2), fill=(0, 0, 0, 200))
        num = style["id"]
        num_bbox = draw.textbbox((0, 0), num, font=label_font)
        nw = num_bbox[2] - num_bbox[0]
        nh = num_bbox[3] - num_bbox[1]
        draw.text(
            (bx + badge_r - nw / 2 - num_bbox[0], by + badge_r - nh / 2 - num_bbox[1]),
            num,
            font=label_font,
            fill=(255, 255, 255),
        )

    out_dir = tempfile.mkdtemp(prefix="uslub_grid_")
    out_path = os.path.join(out_dir, "uslublar.jpg")
    canvas.save(out_path, "JPEG", quality=90)
    return out_path
