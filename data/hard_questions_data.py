# -*- coding: utf-8 -*-
"""🔥 Qiyin O'yinlar uchun Free Fire mavzusidagi savollar banki.

Har bir kategoriya (o'yin turi) uchun alohida savollar ro'yxati mavjud.
Barcha savollar FAQAT Free Fire haqida va qiyin darajada tuzilgan.

Format: {"question": str, "options": [str, str, str, str], "correct": int}
"""

HARD_QUESTIONS = {
    # 🧩 Mantiqiy jumboq
    "puzzle": [
        {
            "question": "🧩 Har bir Free Fire jamoasida 4 o'yinchi bor. Reyting xonasida 12 ta jamoa "
                        "ishtirok etsa, jami nechta o'yinchi maydonga tushadi?",
            "options": ["44", "46", "48", "50"],
            "correct": 2,
        },
        {
            "question": "🧩 Bitta granata portlashi 4 metr radiusni qamrab oladi. Agar 2 ta granata "
                        "yonma-yon (radiuslari kesishmasdan) portlasa, umumiy nechta metr diametr "
                        "qamrab olinadi?",
            "options": ["8", "12", "16", "4"],
            "correct": 2,
        },
        {
            "question": "🧩 Xavfsiz zona har bosqichda 2 barobar kichraydi. Boshlang'ich radius 500m "
                        "bo'lsa, 3-bosqichdan keyin radius necha metr bo'ladi?",
            "options": ["250", "125", "62.5", "31.25"],
            "correct": 2,
        },
        {
            "question": "🧩 Bitta o'yinda 50 o'yinchi ishtirok etadi, ular 4 tadan jamoaga bo'lingan "
                        "(oxirgi jamoada kam bo'lishi mumkin). Nechta to'liq 4 kishilik jamoa "
                        "tuzilishi mumkin?",
            "options": ["10", "11", "12", "13"],
            "correct": 2,
        },
        {
            "question": "🧩 Sizda 90 patron bor, har bir to'liq magazin 30 patron sig'diradi. "
                        "Nechta marta to'liq qayta zaryadlash (reload) qilishingiz mumkin?",
            "options": ["2", "3", "4", "9"],
            "correct": 1,
        },
    ],
    # 🧠 Topishmoq
    "riddle": [
        {
            "question": "🧠 Men samolyotdan sakrayman, yerga tushguncha uchaman, lekin qanotim yo'q. "
                        "Kim men?",
            "options": ["Granata", "Parashyut bilan o'yinchi", "Dron", "Gloo Wall"],
            "correct": 1,
        },
        {
            "question": "🧠 Men devorman, lekin g'ishtdan emasman. Bir zumda paydo bo'laman, "
                        "o'q meni teshib o'ta olmaydi, lekin vaqt o'tsa yo'qolaman. Kim men?",
            "options": ["Gloo Wall", "Bermuda tog'i", "Mashina", "Soya"],
            "correct": 0,
        },
        {
            "question": "🧠 Men uy hayvoniman, lekin yemayman, o'ynamayman - faqat egamga foyda beraman "
                        "(tezlik, HP yoki EP). Kim men?",
            "options": ["Bo't", "Falco yoki boshqa Pet", "NPC", "Zombi"],
            "correct": 1,
        },
        {
            "question": "🧠 Men qutiman, osmondan tushaman, ichimda kuchli qurol bor, meni olish uchun "
                        "hamma yugurib keladi. Kim men?",
            "options": ["Airdrop", "Sandiq (Loot box)", "Dorixona", "Gaz baloni"],
            "correct": 0,
        },
        {
            "question": "🧠 Men sonman, har o'yin oxirida ekranda chiqaman va sizning o'rningizni "
                        "bildiraman - 1 bo'lsam eng yaxshisi. Kim men?",
            "options": ["Booyah!", "Reyting ball", "Rank raqami", "K/D"],
            "correct": 0,
        },
    ],
    # 🔢 Sonlar jumbog'i
    "numbers": [
        {
            "question": "🔢 AWM snayper miltig'ining standart magazin sig'imi nechta patron?",
            "options": ["3", "5", "7", "10"],
            "correct": 1,
        },
        {
            "question": "🔢 Bitta reyting (Ranked) faslida eng yuqori daraja - Grandmaster uchun "
                        "minimal necha ball talab qilinishi odatiy holatda qabul qilingan?",
            "options": ["1000", "2100", "4300", "5500"],
            "correct": 2,
        },
        {
            "question": "🔢 M1887 dubulg'ali miltiq (shotgun) nechta o'q otish teshigi (pellet)ga ega?",
            "options": ["4", "6", "8", "10"],
            "correct": 2,
        },
        {
            "question": "🔢 Standart Free Fire mosuvda (match) maksimal nechta o'yinchi ishtirok etadi?",
            "options": ["40", "50", "60", "100"],
            "correct": 1,
        },
        {
            "question": "🔢 Bitta jamoada (Squad) maksimal nechta o'yinchi bo'lishi mumkin?",
            "options": ["2", "3", "4", "5"],
            "correct": 2,
        },
    ],
    # 🕵️ Detektiv savol
    "detective": [
        {
            "question": "🕵️ Qaysi belgi (character) o'zining kuchli maydoni (Force Field) bilan "
                        "tashqi zarardan himoya qila oladi?",
            "options": ["Chrono", "Alok", "Kelly", "Hayato"],
            "correct": 0,
        },
        {
            "question": "🕵️ Qaysi belgi tezlik (Speed) qobiliyati bilan mashhur va suzishda tezroq "
                        "harakatlanadi?",
            "options": ["Moco", "Kelly", "Wukong", "Miso"],
            "correct": 1,
        },
        {
            "question": "🕵️ \"Drop the Beat\" qobiliyati qaysi belgiga tegishli va nima uchun mashhur?",
            "options": [
                "K - qalqon beradi",
                "DJ Alok - jamoa a'zolarini davolaydi",
                "Clu - dushman joylashuvini ko'rsatadi",
                "Jota - HP tiklaydi",
            ],
            "correct": 1,
        },
        {
            "question": "🕵️ Qaysi xarita (map) cho'l (sahro) muhitiga ega va Kalahari nomi bilan tanilgan?",
            "options": ["Bermuda", "Purgatory", "Kalahari", "Alpine"],
            "correct": 2,
        },
        {
            "question": "🕵️ Qaysi belgi qobiliyati dushmanning yashirin joylashuvini (masalan o't-"
                        "o'landa) aniqlashga yordam beradi?",
            "options": ["Clu", "Moco - dushmanni belgilaydi", "Kla", "Steffie"],
            "correct": 1,
        },
    ],
    # 🔥 Free Fire viktorinasi
    "ffquiz": [
        {
            "question": "🔥 Free Fire o'yinini qaysi kompaniya ishlab chiqargan?",
            "options": ["Tencent", "Garena", "Krafton", "Epic Games"],
            "correct": 1,
        },
        {
            "question": "🔥 Free Fire xavfsiz zonadan tashqarida qolgan o'yinchiga nima bo'ladi?",
            "options": [
                "Hech narsa bo'lmaydi",
                "Vaqt o'tishi bilan HP kamayadi",
                "Darhol o'ladi",
                "Tezligi oshadi",
            ],
            "correct": 1,
        },
        {
            "question": "🔥 Free Fire'da eng yuqori sifatli (Legendary darajadagi) qurol skinlari "
                        "odatda qaysi rejim orqali qo'lga kiritiladi?",
            "options": ["Faqat sotib olish", "Luck Royale", "Faqat reyting", "Faqat turnir"],
            "correct": 1,
        },
        {
            "question": "🔥 Clash Squad rejimida bitta raundda g'olib bo'lish uchun necha kill "
                        "yoki vaqt tugashi shart emas - aksincha nima hal qiladi?",
            "options": [
                "Raqib jamoani to'liq yo'q qilish",
                "Ko'proq tanga yig'ish",
                "Tezroq yugurish",
                "Ko'proq granata otish",
            ],
            "correct": 0,
        },
        {
            "question": "🔥 Free Fire'da \"Booyah\" so'zi nimani anglatadi?",
            "options": ["O'yin boshlanishi", "G'alaba qozonish", "Qurol topish", "Jamoaga qo'shilish"],
            "correct": 1,
        },
    ],
    # ⚡ Tezkor savol
    "fast": [
        {
            "question": "⚡ Tezkor javob: Free Fire'da parashyutdan tushish paytida qurol otish "
                        "mumkinmi?",
            "options": ["Ha, har doim", "Yo'q, imkonsiz", "Faqat granata otish mumkin", "Faqat Pro rejimda"],
            "correct": 1,
        },
        {
            "question": "⚡ Tezkor javob: Gloo Wall (Kley devor) nechta zarbadan keyin buziladi "
                        "(taxminan)?",
            "options": ["1-2", "3-4", "Bir necha o'nlab", "Hech qachon buzilmaydi"],
            "correct": 2,
        },
        {
            "question": "⚡ Tezkor javob: Free Fire'da mashina yonilg'isiz ham harakatlana oladimi?",
            "options": ["Ha, yonilg'i shart emas", "Yo'q, faqat elektr mashinalar", "Faqat suvda", "Faqat tunda"],
            "correct": 0,
        },
        {
            "question": "⚡ Tezkor javob: Kar98k miltig'i qanday turdagi qurol?",
            "options": ["Avtomat (AR)", "Snayper miltig'i", "Dubulg'ali (Shotgun)", "Pistolet"],
            "correct": 1,
        },
        {
            "question": "⚡ Tezkor javob: Free Fire'da jarohatlangan (yiqilgan) o'yinchi qayta "
                        "tiklanishi uchun jamoadoshi nima qilishi kerak?",
            "options": ["Uni qutqarish (revive)", "Unga qarab qichqirish", "Chat yozish", "Hech narsa"],
            "correct": 0,
        },
    ],
    # 🎯 Yashirin javob
    "hidden": [
        {
            "question": "🎯 Yashirin javobni toping: Bu qurolning zanjiri yo'q, lekin bitta o'q bilan "
                        "boshga tegsa ko'pincha dushmanni darhol yo'q qiladi. Bu qanday qurol turi?",
            "options": ["Pistolet", "Snayper miltig'i", "Dubulg'ali qurol", "Granata otar"],
            "correct": 1,
        },
        {
            "question": "🎯 Yashirin javobni toping: Bu narsa ko'rinmas, lekin uni ichganingizda "
                        "tezligingiz yoki HP'ingiz tiklanadi. Bu nima?",
            "options": ["Dorixona (Medkit)", "Gaz baloni", "O't-o'lan", "Qum"],
            "correct": 0,
        },
        {
            "question": "🎯 Yashirin javobni toping: Bu qobiliyat egasini vaqtincha ko'rinmas emas, "
                        "balki o'ta tez qiladi va uzoq masofaga sakrashga yordam beradi. Qaysi belgi?",
            "options": ["Kla - Tayg'onib sakrash", "Maro - EP tiklaydi", "Laura - Aniqlik oshadi", "Antonio - HP oshadi"],
            "correct": 0,
        },
        {
            "question": "🎯 Yashirin javobni toping: Xarita chekkasida joylashgan, dengiz va port "
                        "shahri obrazidagi original Free Fire xaritasi qaysi?",
            "options": ["Purgatory", "Bermuda", "Nexterra", "Alpine"],
            "correct": 1,
        },
        {
            "question": "🎯 Yashirin javobni toping: O'yinchi jangda mag'lub bo'lganda, uni yo'q qilgan "
                        "kishi haqida ma'lumot qaysi ekranda ko'rinadi?",
            "options": ["Kill Feed / O'lim xabari", "Chat oynasi", "Inventar", "Xarita"],
            "correct": 0,
        },
    ],
    # 🔐 Kodni top
    "code": [
        {
            "question": "🔐 Kodni toping: Free Fire'da inventardagi qurolni tezda almashtirish uchun "
                        "qaysi tugmalar qatoridan foydalaniladi?",
            "options": ["1, 2, 3, 4 raqamli slotlar", "Faqat sensorli almashtirish", "Chat tugmasi", "Xarita tugmasi"],
            "correct": 0,
        },
        {
            "question": "🔐 Kodni toping: Reyting o'yinida ballarni yo'qotmaslik uchun qaysi "
                        "darajadan past ranklarda \"himoya\" (ball kamaymasligi) mavjud?",
            "options": ["Bronza va Kumush", "Faqat Heroic", "Faqat Grandmaster", "Hech qaysi darajada yo'q"],
            "correct": 0,
        },
        {
            "question": "🔐 Kodni toping: Clash Squad rejimida har bir raundda o'yinchiga qancha "
                        "boshlang'ich tanga (Clash Squad Token) beriladi (standart holat)?",
            "options": ["500", "1000", "2000", "0 - o'zi topishi kerak"],
            "correct": 1,
        },
        {
            "question": "🔐 Kodni toping: Gloo Wall to'liq ochilishi (yig'ilishi) uchun taxminan "
                        "necha soniya kerak?",
            "options": ["1 soniya", "2-3 soniya", "10 soniya", "Zudlik bilan ochiladi"],
            "correct": 1,
        },
        {
            "question": "🔐 Kodni toping: Free Fire ID orqali boshqa o'yinchini profilda qidirish "
                        "uchun nechta xonali raqam kerak (odatda)?",
            "options": ["4-6 xonali", "9-12 xonali", "20 xonali", "Harflardan iborat"],
            "correct": 1,
        },
    ],
    # 🧩 Mantiqiy tuzoq
    "trap": [
        {
            "question": "🧩 Tuzoq savol: AWM bilan dushmanning oyog'iga uzoq masofadan otsangiz, u "
                        "har doim bir zarbada o'ladimi?",
            "options": ["Ha, har doim o'ladi", "Yo'q, HP va qalqonga bog'liq", "Faqat suvda o'ladi", "Faqat tunda o'ladi"],
            "correct": 1,
        },
        {
            "question": "🧩 Tuzoq savol: Xavfsiz zona ichida turgan o'yinchiga gaz (zона tashqarisi) "
                        "zarar beradimi?",
            "options": ["Ha, doim beradi", "Yo'q, zona ichida gaz zarar bermaydi", "Faqat kechqurun", "Faqat suvda"],
            "correct": 1,
        },
        {
            "question": "🧩 Tuzoq savol: Gloo Wall cheksiz marta qo'yilaveradimi, ya'ni sarflanmaydimi?",
            "options": ["Ha, cheksiz", "Yo'q, sonini (miqdorini) sarflaydi", "Faqat Pro versiyada cheksiz", "Faqat kartada bo'lsa cheksiz"],
            "correct": 1,
        },
        {
            "question": "🧩 Tuzoq savol: Mashinada suzib yurganda ham benzin sarflanadimi?",
            "options": ["Ha, xuddi quruqlikdagidek", "Yo'q, suvda benzin sarflanmaydi", "Ikki barobar tez sarflanadi", "Faqat qayiqda sarflanadi"],
            "correct": 1,
        },
        {
            "question": "🧩 Tuzoq savol: Yiqilgan (jarohatlangan) holatda o'yinchi o'zini o'zi "
                        "qutqara (revive qila) oladimi?",
            "options": ["Ha, har doim", "Yo'q, jamoadosh kerak (agar maxsus item bo'lmasa)", "Faqat Rank rejimida", "Faqat soloda"],
            "correct": 1,
        },
    ],
    # 🏆 Free Fire super viktorinasi
    "superquiz": [
        {
            "question": "🏆 Super savol: Free Fire jahon chempionati (World Series) birinchi marta "
                        "qaysi davrda o'tkazila boshlangan?",
            "options": ["2017", "2019", "2021", "2023"],
            "correct": 1,
        },
        {
            "question": "🏆 Super savol: Free Fire'da \"Loadout\" (jihozlanish) tizimi nimani "
                        "anglatadi?",
            "options": [
                "O'yin grafikasi sozlamalari",
                "O'yinchining tayyor qurol/character sozlamalari to'plami",
                "Xarita tanlash",
                "Do'stlar ro'yxati",
            ],
            "correct": 1,
        },
        {
            "question": "🏆 Super savol: Ranked Clash Squad va Battle Royale rejimlarining reyting "
                        "tizimi bir xil hisoblanadimi?",
            "options": ["Ha, bitta umumiy rank", "Yo'q, ikkalasi alohida rank tizimiga ega", "Faqat CS mavjud", "Faqat BR mavjud"],
            "correct": 1,
        },
        {
            "question": "🏆 Super savol: Free Fire'da bitta faslda eng yuqori nishonga (Grandmaster) "
                        "chiqqan o'yinchiga fasl oxirida odatda nima beriladi?",
            "options": ["Hech narsa", "Maxsus rank mukofoti (bonus/skin)", "Faqat tabrik xabari", "O'yin bloklanadi"],
            "correct": 1,
        },
        {
            "question": "🏆 Super savol: Free Fire'da \"MAX\" versiyasining oddiy versiyadan asosiy "
                        "farqi nimada?",
            "options": [
                "Faqat interfeys rangi",
                "Yuqoriroq grafika sifati va qo'shimcha effektlar",
                "Ko'proq o'yinchi soni",
                "Boshqa xarita to'plami",
            ],
            "correct": 1,
        },
    ],
}
