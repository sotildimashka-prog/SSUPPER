# -*- coding: utf-8 -*-
"""🖼️ Rasm Yasash - "Oddiy Rasm" bo'limi uchun 10 ta tayyor uslub (stil).

Har bir uslub uchun:
- id: ichki identifikator (callback_data ichida ishlatiladi)
- title: foydalanuvchiga ko'rsatiladigan nom
- preview: uslub namunasi rasm fayli (assets papkasida)
- bg_from / bg_to: yakuniy rasm foni uchun gradient ranglar (RGB)
- accent: asosiy urg'u rang (matn porlashi / chiziqlar uchun)
- text_color: matn rangi
"""

import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

STYLES = [
    {
        "id": "1",
        "title": "🔴 Qizil Olov",
        "preview": os.path.join(ASSETS_DIR, "uslub_01.jpg"),
        "bg_from": (40, 0, 0),
        "bg_to": (0, 0, 0),
        "accent": (255, 59, 31),
        "text_color": (255, 255, 255),
    },
    {
        "id": "2",
        "title": "🟠 Olovli Portlash",
        "preview": os.path.join(ASSETS_DIR, "uslub_02.jpg"),
        "bg_from": (43, 20, 0),
        "bg_to": (0, 0, 0),
        "accent": (255, 140, 0),
        "text_color": (255, 255, 255),
    },
    {
        "id": "3",
        "title": "🔵 Ko'k Neon",
        "preview": os.path.join(ASSETS_DIR, "uslub_03.jpg"),
        "bg_from": (0, 26, 43),
        "bg_to": (0, 0, 0),
        "accent": (0, 212, 255),
        "text_color": (255, 255, 255),
    },
    {
        "id": "4",
        "title": "🟣 Binafsha Neon",
        "preview": os.path.join(ASSETS_DIR, "uslub_04.jpg"),
        "bg_from": (26, 0, 51),
        "bg_to": (0, 0, 0),
        "accent": (185, 103, 255),
        "text_color": (255, 255, 255),
    },
    {
        "id": "5",
        "title": "🟢 Zahar Yashil",
        "preview": os.path.join(ASSETS_DIR, "uslub_05.jpg"),
        "bg_from": (0, 26, 0),
        "bg_to": (0, 0, 0),
        "accent": (57, 255, 20),
        "text_color": (255, 255, 255),
    },
    {
        "id": "6",
        "title": "🟡 Oltin Hashamat",
        "preview": os.path.join(ASSETS_DIR, "uslub_06.jpg"),
        "bg_from": (26, 20, 0),
        "bg_to": (0, 0, 0),
        "accent": (255, 215, 0),
        "text_color": (255, 255, 255),
    },
    {
        "id": "7",
        "title": "🧡 Quyosh Botishi",
        "preview": os.path.join(ASSETS_DIR, "uslub_07.jpg"),
        "bg_from": (46, 12, 0),
        "bg_to": (10, 0, 20),
        "accent": (255, 94, 0),
        "text_color": (255, 255, 255),
    },
    {
        "id": "8",
        "title": "⚪ Kumush Minimal",
        "preview": os.path.join(ASSETS_DIR, "uslub_08.jpg"),
        "bg_from": (25, 25, 25),
        "bg_to": (0, 0, 0),
        "accent": (224, 224, 224),
        "text_color": (255, 255, 255),
    },
    {
        "id": "9",
        "title": "🌊 Feruza Kibernetika",
        "preview": os.path.join(ASSETS_DIR, "uslub_09.jpg"),
        "bg_from": (0, 26, 26),
        "bg_to": (0, 0, 0),
        "accent": (0, 255, 204),
        "text_color": (255, 255, 255),
    },
    {
        "id": "10",
        "title": "🌹 Pushti Neon",
        "preview": None,  # namunasi yo'q, faqat generatsiya
        "bg_from": (26, 0, 17),
        "bg_to": (0, 0, 0),
        "accent": (255, 45, 149),
        "text_color": (255, 255, 255),
    },
]


def get_style(style_id: str) -> dict | None:
    for s in STYLES:
        if s["id"] == style_id:
            return s
    return None
