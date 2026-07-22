# -*- coding: utf-8 -*-
"""Almaz (Diamond) sotib olish paketlari."""

# Asosiy paketlar: ID orqali beriladigan miqdor va sovg'a (gift/redeem) orqali
# beriladigan miqdor har xil bo'ladi - shuning uchun ikkalasi ham ko'rsatiladi.
PACKAGES = [
    {"key": "p1", "diamonds": 105, "gift_diamonds": 180, "price_som": 13000, "price_rub": 92},
    {"key": "p2", "diamonds": 326, "gift_diamonds": 559, "price_som": 35000, "price_rub": 260},
    {"key": "p3", "diamonds": 431, "gift_diamonds": 664, "price_som": 48000, "price_rub": 360},
    {"key": "p4", "diamonds": 546, "gift_diamonds": 936, "price_som": 60000, "price_rub": 450},
    {"key": "p5", "diamonds": 651, "gift_diamonds": 1041, "price_som": 70000, "price_rub": 550},
    {"key": "p6", "diamonds": 872, "gift_diamonds": 1262, "price_som": 92000, "price_rub": 710},
]

# Obuna turidagi paketlar (Kunlik/Haftalik/Oylik)
SUBSCRIPTIONS = [
    {"key": "s1", "label": "Kunlik", "diamonds": 90, "price_som": 11000, "price_rub": 75},
    {"key": "s2", "label": "Haftalik", "diamonds": 450, "price_som": 18000, "price_rub": 180},
    {"key": "s3", "label": "Oylik", "diamonds": 2600, "price_som": 123000, "price_rub": 1150},
]


def find_package(key: str):
    for p in PACKAGES:
        if p["key"] == key:
            return {**p, "type": "package"}
    for s in SUBSCRIPTIONS:
        if s["key"] == key:
            return {**s, "type": "subscription"}
    return None


def button_label(item: dict) -> str:
    if item.get("type") == "subscription" or "label" in item:
        return f"{item['label']} 💎{item['diamonds']}"
    return f"💎{item['diamonds']} / 🎁{item['gift_diamonds']}"


def detail_text(item: dict) -> str:
    if "label" in item:
        return (
            f"💎 <b>{item['label']} paket</b>\n\n"
            f"Miqdor: <b>{item['diamonds']} 💎</b>\n"
            f"Narxi: <b>{item['price_som']:,} so'm</b> | {item['price_rub']}₽".replace(",", ".")
        )
    return (
        "✔️ <b>ID ORQALI QILIB BERAMIZ</b> ✅\n\n"
        f"💎 <b>{item['diamonds']}</b> (yoki sovg'a/redeem orqali 🎁 <b>{item['gift_diamonds']}</b>)\n\n"
        f"Narxi: <b>{item['price_som']:,} so'm</b> | {item['price_rub']}₽".replace(",", ".")
    )
