# -*- coding: utf-8 -*-
"""
Har bir telefon modeli uchun Free Fire nastroykalari.

Bu yerdagi 150 ta telefon modeli va ularning nastroyka qiymatlari
"150 haqiqiy telefon Free Fire nastroykalari" faylidan olingan haqiqiy
(tasdiqlangan) nastroykalar bo'lib, barcha modellar uchun bir xil
tavsiya etilgan qiymatlar qo'llaniladi.
"""

# Brend -> [(model nomi, tier), ...]
PHONES = {
    "📱 Xiaomi": [
        ("Xiaomi Redmi Note 10", "real"),
        ("Xiaomi Redmi Note 11", "real"),
        ("Xiaomi Redmi Note 12", "real"),
        ("Xiaomi Redmi Note 13", "real"),
        ("Xiaomi Redmi 13C", "real"),
    ],
    "📱 Realme": [
        ("Realme C33", "real"),
        ("Realme C51", "real"),
        ("Realme C55", "real"),
        ("Realme Note 50", "real"),
        ("Realme 12", "real"),
    ],
    "📱 Huawei": [
        ("Huawei Nova 9", "real"),
        ("Huawei Nova 10", "real"),
        ("Huawei Nova 11", "real"),
        ("Huawei Nova 12", "real"),
        ("Huawei Y9a", "real"),
    ],
    "📱 OnePlus": [
        ("OnePlus Nord CE 3", "real"),
        ("OnePlus Nord 3", "real"),
        ("OnePlus 11R", "real"),
        ("OnePlus 12R", "real"),
        ("OnePlus 12", "real"),
    ],
    "📱 Motorola": [
        ("Motorola G24", "real"),
        ("Motorola G34", "real"),
        ("Motorola G54", "real"),
        ("Motorola Edge 40", "real"),
        ("Motorola Edge 50", "real"),
    ],
    "📱 Nokia": [
        ("Nokia G21", "real"),
        ("Nokia G42", "real"),
        ("Nokia G60", "real"),
        ("Nokia X20", "real"),
        ("Nokia XR21", "real"),
    ],
    "📱 Google Pixel": [
        ("Google Pixel Pixel 6", "real"),
        ("Google Pixel Pixel 6a", "real"),
        ("Google Pixel Pixel 7", "real"),
        ("Google Pixel Pixel 7a", "real"),
        ("Google Pixel Pixel 8", "real"),
    ],
    "📱 Sony Xperia": [
        ("Sony Xperia 10 IV", "real"),
        ("Sony Xperia 10 V", "real"),
        ("Sony Xperia 5 IV", "real"),
        ("Sony Xperia 5 V", "real"),
        ("Sony Xperia 1 V", "real"),
    ],
    "📱 ZTE": [
        ("ZTE Blade A52", "real"),
        ("ZTE Blade A72", "real"),
        ("ZTE Blade V40", "real"),
        ("ZTE Nubia Neo", "real"),
        ("ZTE Blade V50", "real"),
    ],
    "📱 Lenovo": [
        ("Lenovo K14", "real"),
        ("Lenovo K15", "real"),
        ("Lenovo K13", "real"),
        ("Lenovo Legion Y70", "real"),
        ("Lenovo Legion Y90", "real"),
    ],
    "📱 Nothing Phone": [
        ("Nothing Phone (1)", "real"),
        ("Nothing Phone (2)", "real"),
        ("Nothing Phone (2a)", "real"),
        ("Nothing Phone (3a)", "real"),
        ("Nothing Phone CMF Phone 1", "real"),
    ],
    "📱 Meizu": [
        ("Meizu M10", "real"),
        ("Meizu M20", "real"),
        ("Meizu Note 21", "real"),
        ("Meizu 20 Pro", "real"),
        ("Meizu 21", "real"),
    ],
    "📱 iQOO": [
        ("iQOO Z7", "real"),
        ("iQOO Z9", "real"),
        ("iQOO Neo 9", "real"),
        ("iQOO 12", "real"),
        ("iQOO 13", "real"),
    ],
    "📱 Nubia": [
        ("Nubia Neo 2", "real"),
        ("Nubia Z50", "real"),
        ("Nubia Z60", "real"),
        ("Nubia Flip", "real"),
        ("Nubia Focus", "real"),
    ],
    "📱 Black Shark": [
        ("Black Shark 4", "real"),
        ("Black Shark 4 Pro", "real"),
        ("Black Shark 5", "real"),
        ("Black Shark 5 Pro", "real"),
        ("Black Shark 5 RS", "real"),
    ],
    "📱 RedMagic": [
        ("RedMagic 7", "real"),
        ("RedMagic 8 Pro", "real"),
        ("RedMagic 9 Pro", "real"),
        ("RedMagic 10 Pro", "real"),
        ("RedMagic 10 Air", "real"),
    ],
    "📱 ROG Phone": [
        ("ROG Phone 5", "real"),
        ("ROG Phone 6", "real"),
        ("ROG Phone 7", "real"),
        ("ROG Phone 8", "real"),
        ("ROG Phone 9", "real"),
    ],
    "📱 Lava": [
        ("Lava Blaze", "real"),
        ("Lava Blaze 2", "real"),
        ("Lava Blaze 5G", "real"),
        ("Lava Yuva 3", "real"),
        ("Lava Storm 5G", "real"),
    ],
    "📱 Itel": [
        ("Itel A49", "real"),
        ("Itel A60", "real"),
        ("Itel A70", "real"),
        ("Itel S23", "real"),
        ("Itel P55", "real"),
    ],
    "📱 Coolpad": [
        ("Coolpad Cool 20", "real"),
        ("Coolpad Cool 30", "real"),
        ("Coolpad CP12", "real"),
        ("Coolpad X100", "real"),
        ("Coolpad Legacy 5G", "real"),
    ],
    "📱 Doogee": [
        ("Doogee N50", "real"),
        ("Doogee V20", "real"),
        ("Doogee S41", "real"),
        ("Doogee Blade10", "real"),
        ("Doogee Note59", "real"),
    ],
    "📱 Ulefone": [
        ("Ulefone Note 16", "real"),
        ("Ulefone Note 18", "real"),
        ("Ulefone Armor X10", "real"),
        ("Ulefone Armor 21", "real"),
        ("Ulefone Armor 26", "real"),
    ],
    "📱 Oukitel": [
        ("Oukitel C36", "real"),
        ("Oukitel WP23", "real"),
        ("Oukitel WP35", "real"),
        ("Oukitel C51", "real"),
        ("Oukitel WP39", "real"),
    ],
    "📱 Sharp": [
        ("Sharp Aquos Wish", "real"),
        ("Sharp Wish2", "real"),
        ("Sharp Sense4", "real"),
        ("Sharp Sense8", "real"),
        ("Sharp R8", "real"),
    ],
    "📱 LG": [
        ("LG Velvet 5G", "real"),
        ("LG Wing", "real"),
        ("LG V60", "real"),
        ("LG G8X", "real"),
        ("LG K92", "real"),
    ],
    "📱 HTC": [
        ("HTC U20", "real"),
        ("HTC Desire20+", "real"),
        ("HTC Wildfire E3", "real"),
        ("HTC U23", "real"),
        ("HTC U24", "real"),
    ],
    "📱 Acer": [
        ("Acer Liquid Z6", "real"),
        ("Acer Liquid Z630", "real"),
        ("Acer Liquid Jade", "real"),
        ("Acer one10", "real"),
        ("Acer Super ZX", "real"),
    ],
    "📱 Micromax": [
        ("Micromax IN 2C", "real"),
        ("Micromax IN Note 2", "real"),
        ("Micromax IN 1", "real"),
        ("Micromax IN 2B", "real"),
        ("Micromax Canvas 2", "real"),
    ],
    "📱 Blackview": [
        ("Blackview A52", "real"),
        ("Blackview A96", "real"),
        ("Blackview BV5300", "real"),
        ("Blackview Shark8", "real"),
        ("Blackview Oscal C80", "real"),
    ],
    "📱 Cat Phone": [
        ("Cat Phone S42", "real"),
        ("Cat Phone S52", "real"),
        ("Cat Phone S62", "real"),
        ("Cat Phone S62 Pro", "real"),
        ("Cat Phone S75", "real"),
    ],
}

# Barcha 150 ta telefon uchun "150 haqiqiy telefon Free Fire nastroykalari"
# faylidagi haqiqiy (bir xil) tavsiya etilgan nastroyka qiymatlari.
REAL_SETTINGS = {
    "general": "200",
    "red_dot": "195",
    "x2": "188",
    "x4": "178",
    "sniper": "30",
    "freelook": "100",
    "dpi": "580",
    "graphics": "Smooth",
    "fps": "High/Ultra (mavjud bo'lsa)",
    "aim_precision": "Default",
    "left_fire": "Always",
}

TIPS = {
    "real": "Bu - ko'plab o'yinchilar tomonidan sinab ko'rilgan va tasdiqlangan "
            "universal nastroyka. Grafikani Smooth rejimida saqlang, fon "
            "ilovalarini yoping va FPS'ni telefon imkoniyatiga qarab "
            "High/Ultra darajasiga o'rnating. O'z qo'lingizga moslab, "
            "sozlamalarni ±5-10 birlik ichida biroz o'zgartirib ko'rishingiz mumkin.",
}


def build_settings():
    """Har bir telefon uchun to'liq nastroykalar lug'atini yaratadi."""
    result = {}
    for brand, models in PHONES.items():
        for model_name, tier in models:
            settings = {
                "brand": brand,
                "tier": tier,
                "general": REAL_SETTINGS["general"],
                "red_dot": REAL_SETTINGS["red_dot"],
                "x2": REAL_SETTINGS["x2"],
                "x4": REAL_SETTINGS["x4"],
                "sniper": REAL_SETTINGS["sniper"],
                "freelook": REAL_SETTINGS["freelook"],
                "dpi": REAL_SETTINGS["dpi"],
                "graphics": REAL_SETTINGS["graphics"],
                "fps": REAL_SETTINGS["fps"],
                "aim_precision": REAL_SETTINGS["aim_precision"],
                "left_fire": REAL_SETTINGS["left_fire"],
                "tips": TIPS.get(tier, TIPS["real"]),
            }
            result[model_name] = settings
    return result


PHONE_SETTINGS = build_settings()


def format_settings_text(model_name: str) -> str:
    s = PHONE_SETTINGS.get(model_name)
    if not s:
        return "Ma'lumot topilmadi."
    return (
        f"📱 <b>{model_name}</b> uchun tavsiya etilgan Free Fire nastroykalari:\n\n"
        f"🎯 General: <b>{s['general']}</b>\n"
        f"🔴 Red Dot: <b>{s['red_dot']}</b>\n"
        f"🔭 2x Scope: <b>{s['x2']}</b>\n"
        f"🔭 4x Scope: <b>{s['x4']}</b>\n"
        f"🎯 Sniper: <b>{s['sniper']}</b>\n"
        f"👁 Free Look: <b>{s['freelook']}</b>\n"
        f"🖱 DPI: <b>{s['dpi']}</b>\n"
        f"🎨 Grafik sifati: <b>{s['graphics']}</b>\n"
        f"⚡ FPS: <b>{s['fps']}</b>\n"
        f"🎯 Aim Precision: <b>{s['aim_precision']}</b>\n"
        f"🔥 Left Fire: <b>{s['left_fire']}</b>\n\n"
        f"💡 <b>Tavsiya:</b>\n{s['tips']}"
    )
