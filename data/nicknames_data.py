# -*- coding: utf-8 -*-
"""Premium gamerski nickname ro'yxatlari (Telegram code formatida)."""

MALE_NICKNAMES = [

    "VIPER",
    "NO MERCY",
    "RANGER",
    "VENOM",
    "TITAN",
    "RONIN",
    "BLAZE",
    "INFINITY",
    "KING👑",
    "AZRAEL",
    "RAIDEN",
    "NIGHT",
    "INFERNO",
    "VORTEX",
    "STORM",
    "ROGUE",
    "SNIPER",
    "WOLF",
    "FALCON",
    "DRAGON",
    "SAVAGE",
    "GHOST",
    "ZERO",
    "KILLER",
    "FROST",
    "NOVA",
    "CIPHER",
    "ONYX",
]

FEMALE_NICKNAMES = [
    "Dream",
    "Aurora",
    "Nova",
    "Scarlet",
    "Lily",
    "Violet",
    "Flora",
    "Melody",
    "Selena",
    "Stella",
    "Nina",
    "Aria",
    "Sakura",
    "Pearl",
    "Hazel",
    "Ivy",
    "Olivia",
    "Chloe",
    "Ariana",
]


# ---------- 🎮 Foydalanuvchi ismi asosida chiroyli nik generatsiyasi ----------

# {name} o'rniga foydalanuvchi yuborgan ism qo'yiladi. 27 ta shablon - 20+ talabini
# qamrab oladi.
NICK_TEMPLATES = [
    "꧁{name}꧂",
    "☬{name}☬",
    "『{name}』",
    "★彡{name}彡★",
    "≪{name}≫",
    "࿐{name}࿐",
    "☠{name}☠",
    "亗{name}亗",
    "๛{name}๛",
    "❖{name}❖",
    "⚔{name}⚔",
    "『ᴳᵒᵈ』{name}",
    "{name}👑",
    "ᴹᴿ_{name}",
    "Mr.{name}",
    "{name}_YT",
    "《{name}》",
    "†{name}†",
    "☯{name}☯",
    "‡{name}‡",
    "『๖ۣۜ{name}』",
    "ᴸᴼᴿᴰ {name}",
    "{name}_PRO",
    "{name}_TM",
    "『⚡』{name}",
    "{name}ᶠᶠ",
    "০{name}০",
]


def generate_custom_nicknames(name: str) -> list:
    """Foydalanuvchi yuborgan ism asosida 20+ ta chiroyli Free Fire nik yaratadi."""
    clean_name = name.strip()
    if not clean_name:
        return []
    return [tpl.format(name=clean_name) for tpl in NICK_TEMPLATES]
