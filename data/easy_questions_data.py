# -*- coding: utf-8 -*-
"""🟢 OSON O'YINLAR uchun savollar banki (20 ta o'yin).

Har bir o'yin (kategoriya) uchun alohida, JUDA ODDIY savollar ro'yxati.
Har bir to'g'ri javob uchun +3 💎, noto'g'ri javob yoki vaqt tugasa −3 💎.

Format: {"question": str, "options": [str, str, str, str], "correct": int}
(`correct` - to'g'ri javobning `options` ichidagi indeksi, 0 dan boshlanadi)
"""

EASY_QUESTIONS = {
    # 1) 🎮 Free Fire asoslari
    "ffbasic": [
        {
            "question": "🎮 Free Fire o'yinida bitta klassik o'yinga nechta o'yinchi tushadi?",
            "options": ["50", "100", "30", "20"],
            "correct": 0,
        },
        {
            "question": "🎮 Free Fire qanday janrdagi o'yin?",
            "options": ["Futbol simulyatori", "Battle Royale", "Shaxmat", "Poyga"],
            "correct": 1,
        },
        {
            "question": "🎮 Free Fire'da o'yinchilar maydonga qanday tushadi?",
            "options": ["Parashyut bilan", "Poyezdda", "Yugurib", "Suzib"],
            "correct": 0,
        },
        {
            "question": "🎮 Free Fire'da g'alaba qozonganda ekranda qanday yozuv chiqadi?",
            "options": ["Game Over", "Booyah!", "Win Win", "Finish"],
            "correct": 1,
        },
        {
            "question": "🎮 Free Fire asosan qaysi qurilmalarda o'ynaladi?",
            "options": ["Televizorda", "Mobil telefonda", "Kalkulyatorda", "Soatda"],
            "correct": 1,
        },
    ],
    # 2) 🔫 Qurollar
    "weapons": [
        {
            "question": "🔫 Quyidagilardan qaysi biri Free Fire'dagi snayper miltiq?",
            "options": ["AWM", "MP40", "M1014", "Pan"],
            "correct": 0,
        },
        {
            "question": "🔫 MP40 qanday qurol turiga kiradi?",
            "options": ["Snayper", "Pistolet-pulemyot (SMG)", "Drobovik", "Granata"],
            "correct": 1,
        },
        {
            "question": "🔫 M1014 qanday qurol?",
            "options": ["Drobovik", "Snayper", "Pistolet", "Pichoq"],
            "correct": 0,
        },
        {
            "question": "🔫 Quyidagilardan qaysi biri QUROL EMAS?",
            "options": ["AK47", "M4A1", "Medkit", "SCAR"],
            "correct": 2,
        },
        {
            "question": "🔫 Granata nima uchun ishlatiladi?",
            "options": ["Davolash uchun", "Portlatish uchun", "Yugurish uchun", "Sakrash uchun"],
            "correct": 1,
        },
    ],
    # 3) 🗺 Xaritalar
    "maps": [
        {
            "question": "🗺 Free Fire'dagi eng birinchi va eng mashhur xarita qaysi?",
            "options": ["Bermuda", "Purgatory", "Kalahari", "Alpine"],
            "correct": 0,
        },
        {
            "question": "🗺 Quyidagilardan qaysi biri Free Fire xaritasi?",
            "options": ["Kalahari", "Moskva", "Toshkent", "London"],
            "correct": 0,
        },
        {
            "question": "🗺 O'yinda xavfsiz zona vaqt o'tishi bilan qanday o'zgaradi?",
            "options": ["Kattalashadi", "Kichrayadi", "O'zgarmaydi", "Yo'qoladi"],
            "correct": 1,
        },
        {
            "question": "🗺 Xavfsiz zonadan tashqarida turgan o'yinchiga nima bo'ladi?",
            "options": ["Jon yo'qotadi", "Jon qo'shiladi", "Tez yuguradi", "Hech narsa"],
            "correct": 0,
        },
        {
            "question": "🗺 Xaritada o'z jamoadoshingiz qanday belgilanadi?",
            "options": ["Qizil rangda", "Ko'k/yashil belgi bilan", "Ko'rinmaydi", "Qora nuqta bilan"],
            "correct": 1,
        },
    ],
    # 4) 🦸 Personajlar
    "characters": [
        {
            "question": "🦸 Quyidagilardan qaysi biri Free Fire personaji?",
            "options": ["Alok", "Mario", "Sonic", "Pikachu"],
            "correct": 0,
        },
        {
            "question": "🦸 Chrono personaji kimning obrazida yaratilgan?",
            "options": ["Cristiano Ronaldo", "Lionel Messi", "Neymar", "Mbappe"],
            "correct": 0,
        },
        {
            "question": "🦸 Free Fire'da personajlar nima beradi?",
            "options": ["Maxsus qobiliyat", "Pul", "Internet", "Batareya"],
            "correct": 0,
        },
        {
            "question": "🦸 Quyidagilardan qaysi biri Free Fire personaji EMAS?",
            "options": ["Kelly", "Hayato", "Batman", "Andrew"],
            "correct": 2,
        },
        {
            "question": "🦸 Kelly personaji nimasi bilan mashhur?",
            "options": ["Tez yugurishi", "Uchishi", "Suzishi", "Ko'rinmasligi"],
            "correct": 0,
        },
    ],
    # 5) 🐾 Pitomeslar
    "pets": [
        {
            "question": "🐾 Free Fire'da pitomes (pet) nima?",
            "options": ["Hamroh hayvon", "Qurol", "Xarita", "Mashina"],
            "correct": 0,
        },
        {
            "question": "🐾 Quyidagilardan qaysi biri Free Fire pitomesi?",
            "options": ["Ottero", "Tom", "Jerry", "Scooby"],
            "correct": 0,
        },
        {
            "question": "🐾 Pitomes o'yinchiga nima beradi?",
            "options": ["Qo'shimcha foyda (bonus)", "Almaz", "Internet", "Hech narsa"],
            "correct": 0,
        },
        {
            "question": "🐾 Mr. Waggor qanday hayvon?",
            "options": ["Pingvin", "Mushuk", "It", "Ot"],
            "correct": 0,
        },
        {
            "question": "🐾 Bir vaqtning o'zida jangga nechta pitomes olib chiqish mumkin?",
            "options": ["1 ta", "5 ta", "10 ta", "Cheksiz"],
            "correct": 0,
        },
    ],
    # 6) ➕ Oson matematika
    "math": [
        {
            "question": "➕ 7 + 8 = ?",
            "options": ["14", "15", "16", "17"],
            "correct": 1,
        },
        {
            "question": "➕ 12 × 3 = ?",
            "options": ["36", "33", "39", "42"],
            "correct": 0,
        },
        {
            "question": "➕ 100 − 45 = ?",
            "options": ["45", "50", "55", "65"],
            "correct": 2,
        },
        {
            "question": "➕ 81 ÷ 9 = ?",
            "options": ["7", "8", "9", "11"],
            "correct": 2,
        },
        {
            "question": "➕ 25 + 25 + 50 = ?",
            "options": ["90", "100", "110", "75"],
            "correct": 1,
        },
    ],
    # 7) 🎨 Ranglar
    "colors": [
        {
            "question": "🎨 Qizil va sariq rang aralashsa qanday rang hosil bo'ladi?",
            "options": ["Yashil", "To'q sariq", "Binafsha", "Jigarrang"],
            "correct": 1,
        },
        {
            "question": "🎨 Ko'k va sariq aralashsa qanday rang chiqadi?",
            "options": ["Yashil", "Qizil", "Oq", "Qora"],
            "correct": 0,
        },
        {
            "question": "🎨 Osmon odatda qanday rangda ko'rinadi?",
            "options": ["Ko'k", "Qizil", "Yashil", "Sariq"],
            "correct": 0,
        },
        {
            "question": "🎨 Qorning rangi qanday?",
            "options": ["Oq", "Qora", "Ko'k", "Pushti"],
            "correct": 0,
        },
        {
            "question": "🎨 Svetoforning «to'xta» signali qaysi rangda?",
            "options": ["Yashil", "Sariq", "Qizil", "Ko'k"],
            "correct": 2,
        },
    ],
    # 8) 🐘 Hayvonlar
    "animals": [
        {
            "question": "🐘 Quruqlikdagi eng katta hayvon qaysi?",
            "options": ["Fil", "Sher", "Ayiq", "Jirafa"],
            "correct": 0,
        },
        {
            "question": "🐘 Qaysi hayvon «o'rmonlar shohi» deb ataladi?",
            "options": ["Bo'ri", "Sher", "Tulki", "Quyon"],
            "correct": 1,
        },
        {
            "question": "🐘 Eng uzun bo'yinli hayvon qaysi?",
            "options": ["Tuya", "Jirafa", "Ot", "Zebra"],
            "correct": 1,
        },
        {
            "question": "🐘 Qaysi hayvon sut beradi va «mo'» deb ovoz chiqaradi?",
            "options": ["Sigir", "Echki", "Tovuq", "It"],
            "correct": 0,
        },
        {
            "question": "🐘 Baliq nima orqali nafas oladi?",
            "options": ["O'pka", "Jabra", "Teri", "Burun"],
            "correct": 1,
        },
    ],
    # 9) 🍎 Mevalar
    "fruits": [
        {
            "question": "🍎 Qaysi meva sariq va uzun bo'ladi?",
            "options": ["Banan", "Olma", "Uzum", "Anor"],
            "correct": 0,
        },
        {
            "question": "🍎 Tarvuzning ichi odatda qanday rangda?",
            "options": ["Qizil", "Ko'k", "Qora", "Oq"],
            "correct": 0,
        },
        {
            "question": "🍎 Quyidagilardan qaysi biri meva EMAS?",
            "options": ["Olma", "Nok", "Sabzi", "Shaftoli"],
            "correct": 2,
        },
        {
            "question": "🍎 Limon qanday ta'mga ega?",
            "options": ["Nordon", "Shirin", "Achchiq", "Sho'r"],
            "correct": 0,
        },
        {
            "question": "🍎 Uzumdan nima tayyorlanadi?",
            "options": ["Mayiz", "Guruch", "Un", "Tuz"],
            "correct": 0,
        },
    ],
    # 10) 🌍 Davlatlar
    "countries": [
        {
            "question": "🌍 Quyidagilardan qaysi biri davlat?",
            "options": ["Yaponiya", "Samarqand", "Chilonzor", "Sirdaryo"],
            "correct": 0,
        },
        {
            "question": "🌍 Piramidalar qaysi davlatda joylashgan?",
            "options": ["Misr", "Fransiya", "Braziliya", "Kanada"],
            "correct": 0,
        },
        {
            "question": "🌍 Eyfel minorasi qaysi davlatda?",
            "options": ["Italiya", "Fransiya", "Ispaniya", "Germaniya"],
            "correct": 1,
        },
        {
            "question": "🌍 Aholisi eng ko'p bo'lgan qit'a qaysi?",
            "options": ["Afrika", "Yevropa", "Osiyo", "Avstraliya"],
            "correct": 2,
        },
        {
            "question": "🌍 O'zbekiston qaysi qit'ada joylashgan?",
            "options": ["Osiyo", "Yevropa", "Afrika", "Amerika"],
            "correct": 0,
        },
    ],
    # 11) 🏙 Poytaxtlar
    "capitals": [
        {
            "question": "🏙 O'zbekistonning poytaxti qaysi shahar?",
            "options": ["Samarqand", "Toshkent", "Buxoro", "Namangan"],
            "correct": 1,
        },
        {
            "question": "🏙 Fransiyaning poytaxti qaysi shahar?",
            "options": ["Parij", "Lion", "Nitsa", "Marsel"],
            "correct": 0,
        },
        {
            "question": "🏙 Yaponiyaning poytaxti qaysi shahar?",
            "options": ["Osaka", "Kioto", "Tokio", "Nagoya"],
            "correct": 2,
        },
        {
            "question": "🏙 Turkiyaning poytaxti qaysi shahar?",
            "options": ["Istanbul", "Anqara", "Izmir", "Bursa"],
            "correct": 1,
        },
        {
            "question": "🏙 Qozog'istonning poytaxti qaysi shahar?",
            "options": ["Almati", "Astana", "Shimkent", "Taraz"],
            "correct": 1,
        },
    ],
    # 12) ⚽ Sport
    "sport": [
        {
            "question": "⚽ Futbolda bir jamoada maydonda nechta o'yinchi bo'ladi?",
            "options": ["9", "10", "11", "12"],
            "correct": 2,
        },
        {
            "question": "⚽ Basketbolda to'p qayerga tashlanadi?",
            "options": ["Savatga", "Darvozaga", "To'rga", "Chuqurga"],
            "correct": 0,
        },
        {
            "question": "⚽ Olimpiada o'yinlari necha yilda bir marta o'tkaziladi?",
            "options": ["Har yili", "2 yilda", "4 yilda", "10 yilda"],
            "correct": 2,
        },
        {
            "question": "⚽ Lionel Messi qaysi sport turi bilan mashhur?",
            "options": ["Futbol", "Tennis", "Boks", "Suzish"],
            "correct": 0,
        },
        {
            "question": "⚽ Shaxmat taxtasida nechta katakcha bor?",
            "options": ["36", "49", "64", "81"],
            "correct": 2,
        },
    ],
    # 13) 📱 Texnologiya
    "tech": [
        {
            "question": "📱 Telefonga ilova qaysi do'kondan yuklanadi (Android)?",
            "options": ["Play Market", "Telegram", "Youtube", "Word"],
            "correct": 0,
        },
        {
            "question": "📱 Wi-Fi nima uchun kerak?",
            "options": ["Internetga ulanish", "Suratga olish", "Musiqa yozish", "Zaryad berish"],
            "correct": 0,
        },
        {
            "question": "📱 Telegram nima?",
            "options": ["Messenjer (xabar almashish ilovasi)", "O'yin", "Brauzer", "Antivirus"],
            "correct": 0,
        },
        {
            "question": "📱 Kompyuterning «miyasi» deb nima ataladi?",
            "options": ["Monitor", "Protsessor", "Klaviatura", "Sichqoncha"],
            "correct": 1,
        },
        {
            "question": "📱 Quyidagilardan qaysi biri telefon operatsion tizimi?",
            "options": ["Android", "Nokia", "Excel", "Chrome"],
            "correct": 0,
        },
    ],
    # 14) 💡 Oson mantiq
    "logic": [
        {
            "question": "💡 Bir haftada nechta kun bor?",
            "options": ["5", "6", "7", "8"],
            "correct": 2,
        },
        {
            "question": "💡 Yilning eng qisqa oyi qaysi?",
            "options": ["Yanvar", "Fevral", "Aprel", "Dekabr"],
            "correct": 1,
        },
        {
            "question": "💡 Agar sizda 5 ta olma bo'lsa va 2 tasini bersangiz, nechta qoladi?",
            "options": ["2", "3", "4", "5"],
            "correct": 1,
        },
        {
            "question": "💡 Bir sutkada necha soat bor?",
            "options": ["12", "24", "36", "48"],
            "correct": 1,
        },
        {
            "question": "💡 Quyoshning chiqishi qaysi tomondan bo'ladi?",
            "options": ["Sharq", "G'arb", "Shimol", "Janub"],
            "correct": 0,
        },
    ],
    # 15) 🔤 So'zlar
    "words": [
        {
            "question": "🔤 O'zbek alifbosida «Kitob» so'zi nechta harfdan iborat?",
            "options": ["4", "5", "6", "7"],
            "correct": 1,
        },
        {
            "question": "🔤 «Katta» so'zining ma'nodoshi (antonimi) qaysi?",
            "options": ["Kichik", "Baland", "Uzun", "Keng"],
            "correct": 0,
        },
        {
            "question": "🔤 «Issiq» so'zining teskarisi qaysi?",
            "options": ["Iliq", "Sovuq", "Quruq", "Yumshoq"],
            "correct": 1,
        },
        {
            "question": "🔤 Quyidagilardan qaysi biri hayvon nomi?",
            "options": ["Stol", "Quyon", "Daftar", "Eshik"],
            "correct": 1,
        },
        {
            "question": "🔤 «Salom» so'zi nima uchun ishlatiladi?",
            "options": ["Salomlashish", "Xayrlashish", "So'rash", "Rahmat aytish"],
            "correct": 0,
        },
    ],
    # 16) 🔢 Sonlar
    "numbers": [
        {
            "question": "🔢 Qaysi son eng katta?",
            "options": ["19", "91", "29", "88"],
            "correct": 1,
        },
        {
            "question": "🔢 2, 4, 6, 8, ... — keyingi son qaysi?",
            "options": ["9", "10", "11", "12"],
            "correct": 1,
        },
        {
            "question": "🔢 5, 10, 15, 20, ... — keyingi son qaysi?",
            "options": ["22", "24", "25", "30"],
            "correct": 2,
        },
        {
            "question": "🔢 Quyidagilardan qaysi biri juft son?",
            "options": ["7", "13", "18", "21"],
            "correct": 2,
        },
        {
            "question": "🔢 10 ning yarmi qancha?",
            "options": ["2", "4", "5", "6"],
            "correct": 2,
        },
    ],
    # 17) 🌳 Tabiat
    "nature": [
        {
            "question": "🌳 Daraxtlar havoga qaysi gazni chiqaradi?",
            "options": ["Kislorod", "Azot", "Vodorod", "Geliy"],
            "correct": 0,
        },
        {
            "question": "🌳 Yilda nechta fasl bor?",
            "options": ["2", "3", "4", "5"],
            "correct": 2,
        },
        {
            "question": "🌳 Suv necha darajada muzlaydi?",
            "options": ["0°C", "10°C", "50°C", "100°C"],
            "correct": 0,
        },
        {
            "question": "🌳 Eng katta okean qaysi?",
            "options": ["Atlantika", "Tinch okeani", "Hind okeani", "Shimoliy Muz okeani"],
            "correct": 1,
        },
        {
            "question": "🌳 Yomg'ir qayerdan yog'adi?",
            "options": ["Bulutlardan", "Tog'lardan", "Daryodan", "Yerdan"],
            "correct": 0,
        },
    ],
    # 18) 🚀 Kosmos
    "space": [
        {
            "question": "🚀 Quyosh tizimidagi eng katta sayyora qaysi?",
            "options": ["Yer", "Mars", "Yupiter", "Venera"],
            "correct": 2,
        },
        {
            "question": "🚀 Yerning tabiiy yo'ldoshi nima deb ataladi?",
            "options": ["Oy", "Quyosh", "Mars", "Yulduz"],
            "correct": 0,
        },
        {
            "question": "🚀 «Qizil sayyora» deb qaysi sayyora ataladi?",
            "options": ["Mars", "Venera", "Saturn", "Neptun"],
            "correct": 0,
        },
        {
            "question": "🚀 Quyosh nima?",
            "options": ["Yulduz", "Sayyora", "Kometa", "Yo'ldosh"],
            "correct": 0,
        },
        {
            "question": "🚀 Kosmosga uchadigan odam qanday ataladi?",
            "options": ["Kosmonavt", "Haydovchi", "Uchuvchi", "Dengizchi"],
            "correct": 0,
        },
    ],
    # 19) 😀 Emoji topishmoq
    "emoji": [
        {
            "question": "😀 Bu emoji nimani anglatadi: 🔥",
            "options": ["Olov", "Suv", "Muz", "Shamol"],
            "correct": 0,
        },
        {
            "question": "😀 Bu emoji nimani anglatadi: 💎",
            "options": ["Almaz", "Tosh", "Qalam", "Kalit"],
            "correct": 0,
        },
        {
            "question": "😀 Bu emoji nimani anglatadi: ⚽",
            "options": ["Futbol to'pi", "Olma", "Soat", "Doira"],
            "correct": 0,
        },
        {
            "question": "😀 Bu emoji nimani anglatadi: 🚗",
            "options": ["Mashina", "Velosiped", "Samolyot", "Kema"],
            "correct": 0,
        },
        {
            "question": "😀 Bu emoji nimani anglatadi: 🍎",
            "options": ["Olma", "Anor", "Pomidor", "Gilos"],
            "correct": 0,
        },
    ],
    # 20) 🇺🇿 O'zbekiston
    "uz": [
        {
            "question": "🇺🇿 O'zbekiston bayrog'ida nechta rang bor?",
            "options": ["2", "3", "4", "5"],
            "correct": 1,
        },
        {
            "question": "🇺🇿 Registon maydoni qaysi shaharda joylashgan?",
            "options": ["Toshkent", "Samarqand", "Xiva", "Buxoro"],
            "correct": 1,
        },
        {
            "question": "🇺🇿 O'zbekiston pul birligi nima deb ataladi?",
            "options": ["So'm", "Tanga", "Dollar", "Tenge"],
            "correct": 0,
        },
        {
            "question": "🇺🇿 O'zbekiston Mustaqillik kuni qachon nishonlanadi?",
            "options": ["1-sentabr", "9-may", "1-yanvar", "8-mart"],
            "correct": 0,
        },
        {
            "question": "🇺🇿 Alisher Navoiy kim bo'lgan?",
            "options": ["Shoir", "Sportchi", "Qo'shiqchi", "Uchuvchi"],
            "correct": 0,
        },
    ],
}
