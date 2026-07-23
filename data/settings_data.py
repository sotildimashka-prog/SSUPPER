# -*- coding: utf-8 -*-
"""
Har bir telefon modeli uchun Free Fire nastroykalari.

Telefonlar quvvat darajasiga (tier) qarab guruhlangan, va har bir
model uchun qiymatlar shu model indeksiga qarab tier ichida biroz
farqlantiriladi - shu sababli hech qanday ikkita telefon bir xil
qiymatlarga ega bo'lmaydi.
"""

# Brend -> [(model nomi, tier), ...]
PHONES = {
    "📱 Samsung": [
        ("Samsung Galaxy A06", "budget"),
        ("Samsung Galaxy A30", "budget"),
        ("Samsung Galaxy A31", "mid"),
        ("Samsung Galaxy S21", "flagship"),
        ("Samsung Galaxy S25 Ultra", "flagship_pro"),
        ("Samsung Galaxy A03", "budget"),
        ("Samsung Galaxy A04", "budget"),
        ("Samsung Galaxy A05", "budget"),
        ("Samsung Galaxy A13", "budget"),
        ("Samsung Galaxy A14", "budget"),
        ("Samsung Galaxy A23", "mid"),
        ("Samsung Galaxy A24", "mid"),
        ("Samsung Galaxy A34", "mid"),
        ("Samsung Galaxy A54", "flagship"),
        ("Samsung Galaxy M14", "mid"),
    ],
    "📱 Redmi": [
        ("Redmi 9A", "budget"),
        ("Redmi 12", "mid"),
        ("Redmi 13", "mid"),
        ("Redmi 14C", "mid"),
        ("Redmi 15C", "mid"),
        ("Redmi 9C", "budget"),
        ("Redmi 10", "budget"),
        ("Redmi 10C", "budget"),
        ("Redmi 12C", "budget"),
        ("Redmi 13C", "mid"),
        ("Redmi Note 13", "mid"),
    ],
    "📱 Poco": [
        ("Poco C71", "budget"),
        ("Poco C75", "budget"),
        ("Poco X7 Pro", "mid"),
        ("Poco F7", "flagship"),
        ("Poco F7 Pro", "flagship_pro"),
    ],
    "📱 Infinix": [
        ("Infinix Smart 9", "budget"),
        ("Infinix Note 40", "mid"),
        ("Infinix GT 20 Pro", "flagship"),
        ("Infinix GT 30 Pro", "flagship"),
        ("Infinix Hot 50 Pro+", "mid"),
        ("Infinix Hot 10", "budget"),
        ("Infinix Hot 11", "budget"),
        ("Infinix Hot 12", "budget"),
        ("Infinix Hot 20", "mid"),
        ("Infinix Hot 30", "mid"),
        ("Infinix Hot 40", "mid"),
        ("Infinix Note 12", "mid"),
        ("Infinix Note 30", "mid"),
        ("Infinix Smart 7", "budget"),
        ("Infinix Smart 8", "budget"),
    ],
    "📱 Honor": [
        ("Honor X5b", "budget"),
        ("Honor X6b", "budget"),
        ("Honor X7c", "mid"),
        ("Honor 200 Lite", "mid"),
        ("Honor 400 Lite", "flagship"),
    ],
    "📱 iPhone": [
        ("iPhone 11", "mid"),
        ("iPhone 12", "mid"),
        ("iPhone 13", "flagship"),
        ("iPhone 14 Pro Max", "flagship_pro"),
        ("iPhone 16 Pro Max", "flagship_pro"),
    ],
    "📱 ASUS": [
        ("ASUS ROG Phone 6", "flagship"),
        ("ASUS ROG Phone 7", "flagship_pro"),
        ("ASUS ROG Phone 8", "flagship_pro"),
        ("ASUS ROG Phone 8 Pro", "flagship_pro"),
        ("ASUS ROG Phone 9 Pro", "flagship_pro"),
    ],
    "📱 Oppo": [
        ("Oppo A5s", "budget"),
        ("Oppo A12", "budget"),
        ("Oppo A16", "budget"),
        ("Oppo A17", "budget"),
        ("Oppo A38", "mid"),
        ("Oppo A58", "mid"),
        ("Oppo A78", "mid"),
        ("Oppo Reno 8", "flagship"),
        ("Oppo Reno 10", "flagship"),
        ("Oppo A98", "flagship"),
    ],
    "📱 Tecno": [
        ("Tecno Spark 8", "budget"),
        ("Tecno Spark 9", "budget"),
        ("Tecno Spark 10", "budget"),
        ("Tecno Spark 20", "mid"),
        ("Tecno Camon 18", "mid"),
        ("Tecno Camon 19", "mid"),
        ("Tecno Camon 20", "mid"),
        ("Tecno Pova 5", "flagship"),
        ("Tecno Pop 7", "budget"),
        ("Tecno Pop 8", "budget"),
    ],
    "📱 Vivo": [
        ("Vivo Y02", "budget"),
        ("Vivo Y12", "budget"),
        ("Vivo Y15", "budget"),
        ("Vivo Y17", "budget"),
        ("Vivo Y20", "budget"),
        ("Vivo Y21", "budget"),
        ("Vivo Y33s", "mid"),
        ("Vivo Y36", "mid"),
        ("Vivo V27", "flagship"),
        ("Vivo V29", "flagship"),
    ],
}

# Tier bo'yicha bazaviy diapazonlar
TIER_RANGES = {
    "budget": {
        "general": (85, 92), "red_dot": (82, 90), "x2": (75, 82),
        "x4": (60, 68), "sniper": (35, 42), "freelook": (85, 92),
        "dpi": (300, 350), "fire_btn": (110, 125),
        "hud": "Kichik (kam RAM tejaydi)", "graphics": "Smooth",
        "fps": "60 FPS",
    },
    "mid": {
        "general": (90, 96), "red_dot": (88, 94), "x2": (80, 88),
        "x4": (68, 76), "sniper": (42, 50), "freelook": (90, 97),
        "dpi": (350, 420), "fire_btn": (125, 140),
        "hud": "O'rtacha", "graphics": "Balanced / HD",
        "fps": "60-90 FPS",
    },
    "flagship": {
        "general": (95, 100), "red_dot": (93, 99), "x2": (86, 93),
        "x4": (75, 83), "sniper": (48, 56), "freelook": (95, 100),
        "dpi": (420, 480), "fire_btn": (140, 155),
        "hud": "Katta (aniqlik uchun)", "graphics": "HD / Ultra HD",
        "fps": "90 FPS",
    },
    "flagship_pro": {
        "general": (98, 100), "red_dot": (96, 100), "x2": (90, 97),
        "x4": (80, 88), "sniper": (52, 60), "freelook": (97, 100),
        "dpi": (450, 520), "fire_btn": (145, 160),
        "hud": "Katta (Pro darajali sezgirlik)", "graphics": "Ultra HD",
        "fps": "90-120 FPS",
    },
}

TIPS = {
    "budget": "Qurilma quvvati cheklangan, shuning uchun grafikani past darajada saqlang, "
              "fon ilovalarini yoping va Bluetooth/Wi-Fi optimallashtirishdan foydalaning. "
              "Rush o'ynashda soddaroq HUD tavsiya etiladi.",
    "mid": "Grafik va FPS o'rtasidagi muvozanatni saqlang. Balanced rejimda barqaror "
           "ishlaydi. Uzoq o'yin seanslarida telefon qizib ketmasligi uchun quvvatlash "
           "rejimini yoqing.",
    "flagship": "Qurilma yuqori FPS'ni qo'llab-quvvatlaydi - HD/Ultra HD grafikada "
                "o'ynash tavsiya etiladi. Sniper janglarida sezgirlikni pasaytirib, "
                "aniqlikni oshiring.",
    "flagship_pro": "Eng yuqori sozlamalarda (Ultra HD, 90-120 FPS) barqaror ishlaydi. "
                     "Pro o'yinchilar uchun maksimal sezgirlik va tezkor fire button "
                     "hajmi tavsiya etiladi. Turnir formatidagi o'yinlarga mos.",
}


def _pick(rng, seed, spread=5):
    """Tier diapazoni ichida seed asosida deterministik qiymat tanlaydi."""
    lo, hi = rng
    if hi <= lo:
        return lo
    step = ((seed * 7) + 3) % (hi - lo + 1)
    return lo + step


def build_settings():
    """Har bir telefon uchun to'liq nastroykalar lug'atini yaratadi."""
    result = {}
    seed_counter = 0
    for brand, models in PHONES.items():
        for model_name, tier in models:
            seed_counter += 1
            r = TIER_RANGES[tier]
            settings = {
                "brand": brand,
                "tier": tier,
                "general": f"{_pick(r['general'], seed_counter)}%",
                "red_dot": f"{_pick(r['red_dot'], seed_counter + 1)}%",
                "x2": f"{_pick(r['x2'], seed_counter + 2)}%",
                "x4": f"{_pick(r['x4'], seed_counter + 3)}%",
                "sniper": f"{_pick(r['sniper'], seed_counter + 4)}%",
                "freelook": f"{_pick(r['freelook'], seed_counter + 5)}%",
                "dpi": f"{_pick(r['dpi'], seed_counter + 6)}",
                "fire_btn": f"{_pick(r['fire_btn'], seed_counter + 7)}%",
                "hud": r["hud"],
                "graphics": r["graphics"],
                "fps": r["fps"],
                "tips": TIPS[tier],
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
        f"🎯 General Sensitivity: <b>{s['general']}</b>\n"
        f"🔴 Red Dot: <b>{s['red_dot']}</b>\n"
        f"🔭 2x Scope: <b>{s['x2']}</b>\n"
        f"🔭 4x Scope: <b>{s['x4']}</b>\n"
        f"🎯 Sniper Scope: <b>{s['sniper']}</b>\n"
        f"👁 Free Look: <b>{s['freelook']}</b>\n"
        f"🖱 DPI: <b>{s['dpi']}</b>\n"
        f"🔥 Fire Button Size: <b>{s['fire_btn']}</b>\n"
        f"🎛 HUD: <b>{s['hud']}</b>\n"
        f"🎨 Grafik sifati: <b>{s['graphics']}</b>\n"
        f"⚡ FPS: <b>{s['fps']}</b>\n\n"
        f"💡 <b>Tavsiya:</b>\n{s['tips']}"
    )
