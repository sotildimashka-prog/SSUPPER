# -*- coding: utf-8 -*-
"""Planshetlar uchun Free Fire sensitivity nastroykalari."""

TABLETS = {
    "📲 Samsung Galaxy Tab": [
        ("Galaxy Tab A8", "budget"),
        ("Galaxy Tab A9+", "mid"),
        ("Galaxy Tab S6 Lite", "mid"),
        ("Galaxy Tab S8", "upper"),
        ("Galaxy Tab S9", "flagship"),
    ],
    "📲 Apple iPad": [
        ("iPad 9-gen", "mid"),
        ("iPad 10-gen", "upper"),
        ("iPad Air 5", "upper"),
        ("iPad Pro 11", "flagship"),
        ("iPad Pro 12.9", "flagship"),
    ],
    "📲 Xiaomi Pad": [
        ("Redmi Pad SE", "budget"),
        ("Redmi Pad", "mid"),
        ("Xiaomi Pad 5", "upper"),
        ("Xiaomi Pad 6", "upper"),
        ("Xiaomi Pad 6 Pro", "flagship"),
    ],
    "📲 Huawei MatePad": [
        ("MatePad T10", "budget"),
        ("MatePad SE", "budget"),
        ("MatePad T10s", "mid"),
        ("MatePad 11", "upper"),
        ("MatePad Pro 11", "flagship"),
    ],
    "📲 Lenovo Tab": [
        ("Lenovo Tab M10", "budget"),
        ("Lenovo Tab M11", "mid"),
        ("Lenovo Tab P11", "upper"),
        ("Lenovo Tab P12", "flagship"),
        ("Lenovo Legion Y700", "flagship"),
    ],
    "📲 Honor Pad": [
        ("Honor Pad X8", "budget"),
        ("Honor Pad 8", "mid"),
        ("Honor Pad X9", "mid"),
        ("Honor Pad 9", "upper"),
        ("Honor Pad V8 Pro", "flagship"),
    ],
}

TIER_RANGES = {
    "budget": {
        "general": (84, 90), "red_dot": (80, 88), "x2": (72, 80),
        "x4": (55, 63), "sniper": (30, 37), "freelook": (82, 90),
        "dpi": (280, 330), "fire_btn": (105, 120),
        "hud": "Kichik", "graphics": "Smooth", "fps": "60 FPS",
    },
    "mid": {
        "general": (89, 95), "red_dot": (87, 93), "x2": (79, 87),
        "x4": (63, 71), "sniper": (37, 44), "freelook": (88, 95),
        "dpi": (330, 390), "fire_btn": (120, 135),
        "hud": "O'rtacha", "graphics": "Balanced / HD", "fps": "60-90 FPS",
    },
    "upper": {
        "general": (94, 99), "red_dot": (92, 98), "x2": (85, 92),
        "x4": (72, 80), "sniper": (44, 52), "freelook": (94, 99),
        "dpi": (390, 450), "fire_btn": (135, 150),
        "hud": "Katta (planshet ekrani uchun qulay)", "graphics": "HD / Ultra HD", "fps": "90 FPS",
    },
    "flagship": {
        "general": (97, 100), "red_dot": (96, 100), "x2": (90, 97),
        "x4": (79, 88), "sniper": (50, 60), "freelook": (97, 100),
        "dpi": (440, 500), "fire_btn": (145, 160),
        "hud": "Katta (Pro darajali)", "graphics": "Ultra HD", "fps": "90-120 FPS",
    },
}

TIPS = {
    "budget": "Planshet katta ekranli bo'lgani uchun HUD kichikroq qilinsa, ko'rish maydoni "
              "kengayadi. Grafikani Smooth'da saqlang, fon ilovalarini yoping.",
    "mid": "Katta ekran aniqroq nishonga olishga yordam beradi - Red Dot va 2x sensitivligini "
           "biroz oshirib mashq qiling.",
    "upper": "Planshetning katta ekrani sniper janglarida katta afzallik beradi - 4x/Sniper "
             "Scope sensitivligini aniq nishonga olish uchun sozlang.",
    "flagship": "Yuqori yangilanish chastotali (90-120Hz) ekranlar tezkor harakatlarni silliq "
                "ko'rsatadi - flick-headshot mashqlari uchun ideal.",
}


def _pick(rng, seed):
    lo, hi = rng
    if hi <= lo:
        return lo
    step = ((seed * 7) + 3) % (hi - lo + 1)
    return lo + step


def build_settings():
    result = {}
    seed_counter = 0
    for brand, models in TABLETS.items():
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


TABLET_SETTINGS = build_settings()


def format_tablet_settings_text(model_name: str) -> str:
    s = TABLET_SETTINGS.get(model_name)
    if not s:
        return "Ma'lumot topilmadi."
    return (
        f"📲 <b>{model_name}</b> uchun tavsiya etilgan Free Fire nastroykalari:\n\n"
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
