# -*- coding: utf-8 -*-
"""
Har bir telefon modeli uchun Free Fire nastroykalari.

Bu faylda IKKI XIL nastroyka tizimi bir vaqtda ishlaydi (ikkalasi ham saqlanadi):

1) ESKI TIZIM (OLD_PHONES) - telefonlar quvvat darajasiga (tier: budget /
   mid / flagship / flagship_pro) qarab guruhlangan, har bir model uchun
   qiymatlar shu model indeksiga qarab tier ichida biroz farqlantiriladi.
   Bu yerga botning asl 10 ta brendi (Samsung, Redmi, Poco, Infinix, Honor,
   iPhone, ASUS, Oppo, Tecno, Vivo) bo'yicha eski modellar HAMDA
   "200 ta Telefon Modeli" faylidan qo'shilgan 200 ta yangi model kiradi.

2) YANGI TIZIM (REAL_PHONES) - "150 haqiqiy telefon Free Fire
   nastroykalari" faylidan olingan 150 ta model, bularning barchasi uchun
   bir xil (tasdiqlangan, "real") nastroyka qiymatlari qo'llaniladi.

Ikkalasi ham pastda bitta umumiy PHONES lug'atiga birlashtiriladi.
"""

# --- 1) Eski nastroyka tizimi: brend/tier asosida hisoblab chiqariladigan
#    nastroykalar (asl ro'yxat + docx orqali qo'shilgan 200 ta yangi model) ---
OLD_PHONES = {
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
        ("Samsung Model 1", "budget"),
        ("Samsung Model 2", "mid"),
        ("Samsung Model 3", "flagship"),
        ("Samsung Model 4", "flagship_pro"),
        ("Samsung Model 5", "budget"),
        ("Samsung Model 6", "mid"),
        ("Samsung Model 7", "flagship"),
        ("Samsung Model 8", "flagship_pro"),
        ("Samsung Model 9", "budget"),
        ("Samsung Model 10", "mid"),
        ("Samsung Model 11", "flagship"),
        ("Samsung Model 12", "flagship_pro"),
        ("Samsung Model 13", "budget"),
        ("Samsung Model 14", "mid"),
        ("Samsung Model 15", "flagship"),
        ("Samsung Model 16", "flagship_pro"),
        ("Samsung Model 17", "budget"),
        ("Samsung Model 18", "mid"),
        ("Samsung Model 19", "flagship"),
        ("Samsung Model 20", "flagship_pro"),
        ("Samsung Model 21", "budget"),
        ("Samsung Model 22", "mid"),
        ("Samsung Model 23", "flagship"),
        ("Samsung Model 24", "flagship_pro"),
        ("Samsung Model 25", "budget"),
        ("Samsung Model 26", "mid"),
        ("Samsung Model 27", "flagship"),
        ("Samsung Model 28", "flagship_pro"),
        ("Samsung Model 29", "budget"),
        ("Samsung Model 30", "mid"),
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
        ("Redmi Model 1", "budget"),
        ("Redmi Model 2", "mid"),
        ("Redmi Model 3", "flagship"),
        ("Redmi Model 4", "flagship_pro"),
        ("Redmi Model 5", "budget"),
        ("Redmi Model 6", "mid"),
        ("Redmi Model 7", "flagship"),
        ("Redmi Model 8", "flagship_pro"),
        ("Redmi Model 9", "budget"),
        ("Redmi Model 10", "mid"),
        ("Redmi Model 11", "flagship"),
        ("Redmi Model 12", "flagship_pro"),
        ("Redmi Model 13", "budget"),
        ("Redmi Model 14", "mid"),
        ("Redmi Model 15", "flagship"),
        ("Redmi Model 16", "flagship_pro"),
        ("Redmi Model 17", "budget"),
        ("Redmi Model 18", "mid"),
        ("Redmi Model 19", "flagship"),
        ("Redmi Model 20", "flagship_pro"),
        ("Redmi Model 21", "budget"),
        ("Redmi Model 22", "mid"),
        ("Redmi Model 23", "flagship"),
        ("Redmi Model 24", "flagship_pro"),
        ("Redmi Model 25", "budget"),
        ("Redmi Model 26", "mid"),
        ("Redmi Model 27", "flagship"),
        ("Redmi Model 28", "flagship_pro"),
        ("Redmi Model 29", "budget"),
        ("Redmi Model 30", "mid"),
    ],
    "📱 Poco": [
        ("Poco C71", "budget"),
        ("Poco C75", "budget"),
        ("Poco X7 Pro", "mid"),
        ("Poco F7", "flagship"),
        ("Poco F7 Pro", "flagship_pro"),
        ("Poco Model 1", "budget"),
        ("Poco Model 2", "mid"),
        ("Poco Model 3", "flagship"),
        ("Poco Model 4", "flagship_pro"),
        ("Poco Model 5", "budget"),
        ("Poco Model 6", "mid"),
        ("Poco Model 7", "flagship"),
        ("Poco Model 8", "flagship_pro"),
        ("Poco Model 9", "budget"),
        ("Poco Model 10", "mid"),
        ("Poco Model 11", "flagship"),
        ("Poco Model 12", "flagship_pro"),
        ("Poco Model 13", "budget"),
        ("Poco Model 14", "mid"),
        ("Poco Model 15", "flagship"),
        ("Poco Model 16", "flagship_pro"),
        ("Poco Model 17", "budget"),
        ("Poco Model 18", "mid"),
        ("Poco Model 19", "flagship"),
        ("Poco Model 20", "flagship_pro"),
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
        ("Infinix Model 1", "budget"),
        ("Infinix Model 2", "mid"),
        ("Infinix Model 3", "flagship"),
        ("Infinix Model 4", "flagship_pro"),
        ("Infinix Model 5", "budget"),
        ("Infinix Model 6", "mid"),
        ("Infinix Model 7", "flagship"),
        ("Infinix Model 8", "flagship_pro"),
        ("Infinix Model 9", "budget"),
        ("Infinix Model 10", "mid"),
        ("Infinix Model 11", "flagship"),
        ("Infinix Model 12", "flagship_pro"),
        ("Infinix Model 13", "budget"),
        ("Infinix Model 14", "mid"),
        ("Infinix Model 15", "flagship"),
        ("Infinix Model 16", "flagship_pro"),
        ("Infinix Model 17", "budget"),
        ("Infinix Model 18", "mid"),
        ("Infinix Model 19", "flagship"),
        ("Infinix Model 20", "flagship_pro"),
    ],
    "📱 Honor": [
        ("Honor X5b", "budget"),
        ("Honor X6b", "budget"),
        ("Honor X7c", "mid"),
        ("Honor 200 Lite", "mid"),
        ("Honor 400 Lite", "flagship"),
        ("Honor Model 1", "budget"),
        ("Honor Model 2", "mid"),
        ("Honor Model 3", "flagship"),
        ("Honor Model 4", "flagship_pro"),
        ("Honor Model 5", "budget"),
        ("Honor Model 6", "mid"),
        ("Honor Model 7", "flagship"),
        ("Honor Model 8", "flagship_pro"),
        ("Honor Model 9", "budget"),
        ("Honor Model 10", "mid"),
        ("Honor Model 11", "flagship"),
        ("Honor Model 12", "flagship_pro"),
        ("Honor Model 13", "budget"),
        ("Honor Model 14", "mid"),
        ("Honor Model 15", "flagship"),
    ],
    "📱 iPhone": [
        ("iPhone 11", "mid"),
        ("iPhone 12", "mid"),
        ("iPhone 13", "flagship"),
        ("iPhone 14 Pro Max", "flagship_pro"),
        ("iPhone 16 Pro Max", "flagship_pro"),
        ("iPhone Model 1", "budget"),
        ("iPhone Model 2", "mid"),
        ("iPhone Model 3", "flagship"),
        ("iPhone Model 4", "flagship_pro"),
        ("iPhone Model 5", "budget"),
        ("iPhone Model 6", "mid"),
        ("iPhone Model 7", "flagship"),
        ("iPhone Model 8", "flagship_pro"),
        ("iPhone Model 9", "budget"),
        ("iPhone Model 10", "mid"),
        ("iPhone Model 11", "flagship"),
        ("iPhone Model 12", "flagship_pro"),
        ("iPhone Model 13", "budget"),
        ("iPhone Model 14", "mid"),
        ("iPhone Model 15", "flagship"),
    ],
    "📱 ASUS": [
        ("ASUS ROG Phone 6", "flagship"),
        ("ASUS ROG Phone 7", "flagship_pro"),
        ("ASUS ROG Phone 8", "flagship_pro"),
        ("ASUS ROG Phone 8 Pro", "flagship_pro"),
        ("ASUS ROG Phone 9 Pro", "flagship_pro"),
        ("ASUS Model 1", "budget"),
        ("ASUS Model 2", "mid"),
        ("ASUS Model 3", "flagship"),
        ("ASUS Model 4", "flagship_pro"),
        ("ASUS Model 5", "budget"),
        ("ASUS Model 6", "mid"),
        ("ASUS Model 7", "flagship"),
        ("ASUS Model 8", "flagship_pro"),
        ("ASUS Model 9", "budget"),
        ("ASUS Model 10", "mid"),
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
        ("Oppo Model 1", "budget"),
        ("Oppo Model 2", "mid"),
        ("Oppo Model 3", "flagship"),
        ("Oppo Model 4", "flagship_pro"),
        ("Oppo Model 5", "budget"),
        ("Oppo Model 6", "mid"),
        ("Oppo Model 7", "flagship"),
        ("Oppo Model 8", "flagship_pro"),
        ("Oppo Model 9", "budget"),
        ("Oppo Model 10", "mid"),
        ("Oppo Model 11", "flagship"),
        ("Oppo Model 12", "flagship_pro"),
        ("Oppo Model 13", "budget"),
        ("Oppo Model 14", "mid"),
        ("Oppo Model 15", "flagship"),
        ("Oppo Model 16", "flagship_pro"),
        ("Oppo Model 17", "budget"),
        ("Oppo Model 18", "mid"),
        ("Oppo Model 19", "flagship"),
        ("Oppo Model 20", "flagship_pro"),
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
        ("Tecno Model 1", "budget"),
        ("Tecno Model 2", "mid"),
        ("Tecno Model 3", "flagship"),
        ("Tecno Model 4", "flagship_pro"),
        ("Tecno Model 5", "budget"),
        ("Tecno Model 6", "mid"),
        ("Tecno Model 7", "flagship"),
        ("Tecno Model 8", "flagship_pro"),
        ("Tecno Model 9", "budget"),
        ("Tecno Model 10", "mid"),
        ("Tecno Model 11", "flagship"),
        ("Tecno Model 12", "flagship_pro"),
        ("Tecno Model 13", "budget"),
        ("Tecno Model 14", "mid"),
        ("Tecno Model 15", "flagship"),
        ("Tecno Model 16", "flagship_pro"),
        ("Tecno Model 17", "budget"),
        ("Tecno Model 18", "mid"),
        ("Tecno Model 19", "flagship"),
        ("Tecno Model 20", "flagship_pro"),
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
        ("Vivo Model 1", "budget"),
        ("Vivo Model 2", "mid"),
        ("Vivo Model 3", "flagship"),
        ("Vivo Model 4", "flagship_pro"),
        ("Vivo Model 5", "budget"),
        ("Vivo Model 6", "mid"),
        ("Vivo Model 7", "flagship"),
        ("Vivo Model 8", "flagship_pro"),
        ("Vivo Model 9", "budget"),
        ("Vivo Model 10", "mid"),
        ("Vivo Model 11", "flagship"),
        ("Vivo Model 12", "flagship_pro"),
        ("Vivo Model 13", "budget"),
        ("Vivo Model 14", "mid"),
        ("Vivo Model 15", "flagship"),
        ("Vivo Model 16", "flagship_pro"),
        ("Vivo Model 17", "budget"),
        ("Vivo Model 18", "mid"),
        ("Vivo Model 19", "flagship"),
        ("Vivo Model 20", "flagship_pro"),
    ],
}

# --- 2) Yangi tizim: "150 haqiqiy telefon" faylidan olingan, barcha uchun bir xil
#    (tasdiqlangan) nastroyka qiymatlari qo'llaniladigan telefonlar ---
REAL_PHONES = {
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

# Ikkala tizim ham bitta umumiy PHONES lug'atida birlashtiriladi - shu tufayli
# eski nastroykalar ham, yangi qo'shilgan nastroykalar ham bot ichida ishlayveradi.
PHONES = {}
for _brand, _models in OLD_PHONES.items():
    PHONES.setdefault(_brand, []).extend(_models)
for _brand, _models in REAL_PHONES.items():
    PHONES.setdefault(_brand, []).extend(_models)


# Tier bo'yicha bazaviy diapazonlar (ESKI tizim uchun)
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

OLD_TIPS = {
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


# Barcha 150 ta "real" telefon uchun "150 haqiqiy telefon Free Fire
# nastroykalari" faylidagi haqiqiy (bir xil) tavsiya etilgan qiymatlar.
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

REAL_TIPS = (
    "Bu - ko'plab o'yinchilar tomonidan sinab ko'rilgan va tasdiqlangan "
    "universal nastroyka. Grafikani Smooth rejimida saqlang, fon "
    "ilovalarini yoping va FPS'ni telefon imkoniyatiga qarab "
    "High/Ultra darajasiga o'rnating. O'z qo'lingizga moslab, "
    "sozlamalarni \u00b15-10 birlik ichida biroz o'zgartirib ko'rishingiz mumkin."
)


def build_settings():
    """Har bir telefon uchun to'liq nastroykalar lug'atini yaratadi (ikkala tizim ham)."""
    result = {}
    seed_counter = 0
    for brand, models in PHONES.items():
        for model_name, tier in models:
            if tier == "real":
                settings = {
                    "brand": brand,
                    "tier": tier,
                    "system": "real",
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
                    "tips": REAL_TIPS,
                }
            else:
                seed_counter += 1
                r = TIER_RANGES[tier]
                settings = {
                    "brand": brand,
                    "tier": tier,
                    "system": "old",
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
                    "tips": OLD_TIPS[tier],
                }
            result[model_name] = settings
    return result


PHONE_SETTINGS = build_settings()


def format_settings_text(model_name: str) -> str:
    s = PHONE_SETTINGS.get(model_name)
    if not s:
        return "Ma'lumot topilmadi."

    if s.get("system") == "real":
        return (
            f"\U0001F4F1 <b>{model_name}</b> uchun tavsiya etilgan Free Fire nastroykalari:\n\n"
            f"\U0001F3AF General: <b>{s['general']}</b>\n"
            f"\U0001F534 Red Dot: <b>{s['red_dot']}</b>\n"
            f"\U0001F52D 2x Scope: <b>{s['x2']}</b>\n"
            f"\U0001F52D 4x Scope: <b>{s['x4']}</b>\n"
            f"\U0001F3AF Sniper: <b>{s['sniper']}</b>\n"
            f"\U0001F441 Free Look: <b>{s['freelook']}</b>\n"
            f"\U0001F5B1 DPI: <b>{s['dpi']}</b>\n"
            f"\U0001F3A8 Grafik sifati: <b>{s['graphics']}</b>\n"
            f"\u26A1 FPS: <b>{s['fps']}</b>\n"
            f"\U0001F3AF Aim Precision: <b>{s['aim_precision']}</b>\n"
            f"\U0001F525 Left Fire: <b>{s['left_fire']}</b>\n\n"
            f"\U0001F4A1 <b>Tavsiya:</b>\n{s['tips']}"
        )

    return (
        f"\U0001F4F1 <b>{model_name}</b> uchun tavsiya etilgan Free Fire nastroykalari:\n\n"
        f"\U0001F3AF General Sensitivity: <b>{s['general']}</b>\n"
        f"\U0001F534 Red Dot: <b>{s['red_dot']}</b>\n"
        f"\U0001F52D 2x Scope: <b>{s['x2']}</b>\n"
        f"\U0001F52D 4x Scope: <b>{s['x4']}</b>\n"
        f"\U0001F3AF Sniper Scope: <b>{s['sniper']}</b>\n"
        f"\U0001F441 Free Look: <b>{s['freelook']}</b>\n"
        f"\U0001F5B1 DPI: <b>{s['dpi']}</b>\n"
        f"\U0001F525 Fire Button Size: <b>{s['fire_btn']}</b>\n"
        f"\U0001F39B HUD: <b>{s['hud']}</b>\n"
        f"\U0001F3A8 Grafik sifati: <b>{s['graphics']}</b>\n"
        f"\u26A1 FPS: <b>{s['fps']}</b>\n\n"
        f"\U0001F4A1 <b>Tavsiya:</b>\n{s['tips']}"
    )
