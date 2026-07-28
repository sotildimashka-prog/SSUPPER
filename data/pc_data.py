# -*- coding: utf-8 -*-
"""
💻 PC (kompyuter) uchun Free Fire nastroykalari (emulyator orqali o'ynash).

20 ta mashhur kompyuter konfiguratsiyasi, quvvat darajasiga (tier) qarab
guruhlangan. Har bir konfiguratsiya uchun sichqoncha (mouse) sezgirligi,
emulyator FPS/grafik sozlamalari va tavsiyalar beriladi.
"""

# 20 ta mashhur PC konfiguratsiyasi -> [(nomi, tier), ...]
PC_MODELS = [
    ("Intel Celeron G5905 + Intel UHD 610 (Ofis PC)", "budget"),
    ("AMD Athlon 3000G + Radeon Vega 3", "budget"),
    ("Intel Core i3-10100 + Intel UHD 630", "budget"),
    ("AMD Ryzen 3 3200G + Radeon Vega 8", "budget"),
    ("Intel Core i3-12100F + GTX 1650", "budget"),
    ("Intel Core i5-9400F + GTX 1650 Super", "mid"),
    ("AMD Ryzen 5 3500 + GTX 1660 Super", "mid"),
    ("Intel Core i5-11400F + RTX 2060", "mid"),
    ("AMD Ryzen 5 5600G + Radeon Vega 7", "mid"),
    ("AMD Ryzen 5 5600 + RTX 3050", "mid"),
    ("Intel Core i5-12400F + RTX 3060", "flagship"),
    ("AMD Ryzen 7 5700X + RTX 3060 Ti", "flagship"),
    ("Intel Core i7-11700F + RTX 3070", "flagship"),
    ("AMD Ryzen 7 5800X + RTX 3070 Ti", "flagship"),
    ("Intel Core i7-13700K + RTX 4070", "flagship"),
    ("AMD Ryzen 9 5900X + RTX 3080", "flagship_pro"),
    ("Intel Core i9-12900K + RTX 3080 Ti", "flagship_pro"),
    ("AMD Ryzen 9 5950X + RTX 3090", "flagship_pro"),
    ("Intel Core i9-14900K + RTX 4080 Super", "flagship_pro"),
    ("AMD Ryzen 9 7950X3D + RTX 4090", "flagship_pro"),
]

# Tier bo'yicha bazaviy diapazonlar (PC/emulyator uchun moslashtirilgan)
TIER_RANGES_PC = {
    "budget": {
        "general": (88, 94), "red_dot": (85, 92), "x2": (78, 85),
        "x4": (62, 70), "sniper": (38, 45), "freelook": (88, 94),
        "mouse_dpi": (800, 1200), "resolution": "720p (Smooth)",
        "fps": "60 FPS", "graphics": "Smooth / Balanced",
    },
    "mid": {
        "general": (92, 97), "red_dot": (90, 96), "x2": (84, 90),
        "x4": (72, 80), "sniper": (46, 54), "freelook": (93, 98),
        "mouse_dpi": (1200, 1600), "resolution": "900p-1080p (HD)",
        "fps": "60-90 FPS", "graphics": "HD / Ultra HD",
    },
    "flagship": {
        "general": (96, 100), "red_dot": (95, 99), "x2": (89, 95),
        "x4": (78, 86), "sniper": (50, 58), "freelook": (96, 100),
        "mouse_dpi": (1600, 2400), "resolution": "1080p (Ultra HD)",
        "fps": "90-120 FPS", "graphics": "Ultra HD",
    },
    "flagship_pro": {
        "general": (99, 100), "red_dot": (98, 100), "x2": (93, 98),
        "x4": (83, 90), "sniper": (55, 62), "freelook": (99, 100),
        "mouse_dpi": (2400, 3200), "resolution": "1080p+ (Maksimal)",
        "fps": "120-144 FPS", "graphics": "Ultra HD (Max)",
    },
}

TIPS_PC = {
    "budget": "Emulyatorda (LDPlayer/GameLoop/BlueStacks) grafikani \"Smooth\" rejimida "
              "saqlang, RAM va CPU ajratmasini oshiring. Sichqoncha sezgirligini past "
              "DPI'da barqaror ushlang, aim tugmalarini klaviaturaga qulay joylashtiring.",
    "mid": "Grafik va FPS o'rtasida muvozanat saqlang - HD rejimda barqaror ishlaydi. "
           "Sniper va 4x scope uchun sichqoncha sezgirligini biroz pasaytiring, bu "
           "aniqlikni oshiradi. Emulyatorda \"Advanced graphics engine\"ni yoqing.",
    "flagship": "Ultra HD grafika va yuqori FPS'da barqaror o'ynash mumkin. Sichqoncha "
                "DPI'sini oshirib, aim sensitivity'ni moslang - tez burilish va aniq "
                "otish uchun qulay. Turnir formatidagi o'yinlarga mos konfiguratsiya.",
    "flagship_pro": "Maksimal sozlamalarda (Ultra HD, 120-144 FPS) barqaror ishlaydi. "
                    "Pro/Turnir o'yinchilar uchun eng yuqori sichqoncha DPI va "
                    "sezgirlik tavsiya etiladi. Klaviatura+sichqoncha keybindlarini "
                    "o'zingizga moslab sozlang.",
}


def _pick(rng, seed, spread=5):
    """Tier diapazoni ichida seed asosida deterministik qiymat tanlaydi."""
    lo, hi = rng
    if hi <= lo:
        return lo
    step = ((seed * 7) + 3) % (hi - lo + 1)
    return lo + step


def build_pc_settings():
    """Har bir PC konfiguratsiyasi uchun to'liq nastroykalar lug'atini yaratadi."""
    result = {}
    seed_counter = 0
    for model_name, tier in PC_MODELS:
        seed_counter += 1
        r = TIER_RANGES_PC[tier]
        settings = {
            "tier": tier,
            "general": f"{_pick(r['general'], seed_counter)}%",
            "red_dot": f"{_pick(r['red_dot'], seed_counter + 1)}%",
            "x2": f"{_pick(r['x2'], seed_counter + 2)}%",
            "x4": f"{_pick(r['x4'], seed_counter + 3)}%",
            "sniper": f"{_pick(r['sniper'], seed_counter + 4)}%",
            "freelook": f"{_pick(r['freelook'], seed_counter + 5)}%",
            "mouse_dpi": f"{_pick(r['mouse_dpi'], seed_counter + 6)}",
            "resolution": r["resolution"],
            "graphics": r["graphics"],
            "fps": r["fps"],
            "tips": TIPS_PC[tier],
        }
        result[model_name] = settings
    return result


PC_SETTINGS = build_pc_settings()


def format_pc_settings_text(model_name: str) -> str:
    s = PC_SETTINGS.get(model_name)
    if not s:
        return "Ma'lumot topilmadi."
    return (
        f"💻 <b>{model_name}</b>\nuchun tavsiya etilgan Free Fire (emulyator) nastroykalari:\n\n"
        f"🎯 General Sensitivity: <b>{s['general']}</b>\n"
        f"🔴 Red Dot: <b>{s['red_dot']}</b>\n"
        f"🔭 2x Scope: <b>{s['x2']}</b>\n"
        f"🔭 4x Scope: <b>{s['x4']}</b>\n"
        f"🎯 Sniper Scope: <b>{s['sniper']}</b>\n"
        f"👁 Free Look: <b>{s['freelook']}</b>\n"
        f"🖱 Sichqoncha DPI: <b>{s['mouse_dpi']}</b>\n"
        f"🖥 Ekran o'lchami: <b>{s['resolution']}</b>\n"
        f"🎨 Grafik sifati: <b>{s['graphics']}</b>\n"
        f"⚡ FPS: <b>{s['fps']}</b>\n\n"
        f"💡 <b>Tavsiya:</b>\n{s['tips']}"
    )
