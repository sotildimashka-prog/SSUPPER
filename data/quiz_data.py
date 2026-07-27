# -*- coding: utf-8 -*-
"""Free Fire savol-javob (viktorina) uchun savollar bazasi."""

# Har bir savol: matn, variantlar ro'yxati, to'g'ri variant indeksi (0 dan boshlanadi)
QUESTIONS = [
    {
        "question": "Free Fire'da himoya devori yaratish uchun nima ishlatiladi?",
        "options": ['Gloo Wall', 'Smoke Grenade', 'Flashbang', 'Med Kit'],
        "correct": 0,
    },
    {
        "question": "Free Fire o'yinini ishlab chiqargan kompaniya qaysi?",
        "options": ['Tencent', 'Garena', 'EA Sports', 'Ubisoft'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da xarita chetidan kelib, maydonni kichraytiradigan zona qanday ataladi?",
        "options": ['Safe Zone', 'Danger Zone', 'Gloo Zone', 'Battle Zone'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da eng yuqori Rank darajasi qanday ataladi?",
        "options": ['Master', 'Grandmaster', 'Heroic', 'Legend'],
        "correct": 2,
    },
    {
        "question": "Free Fire'da yiqilgan sherigingizni tiklash uchun nima qilish kerak?",
        "options": ['Uni tiklash (revive) qilish', 'Uni otish', 'Yangi qurol berish', 'Chat yozish'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da qaysi qurol turi uzoq masofada eng samarali?",
        "options": ['Shotgun', 'Sniper', 'Pistol', 'SMG'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da o'yin oxirida g'olib bo'lgan jamoa/o'yinchi qanday deb ataladi?",
        "options": ['Champion (Booyah)', 'Winner Cup', 'Top Fragger', 'MVP'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da o'yinchi maksimal nechta qurol olib yura oladi (odatiy holatda)?",
        "options": ['2 ta', '3 ta', '4 ta', '5 ta'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da 'Airdrop' nima uchun ishlatiladi?",
        "options": ['Kuchli qurol-jihoz olish uchun', "Dushmanni ko'rish uchun", 'Tezlashish uchun', "Sog'liqni tiklash uchun"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xarakterlarning maxsus qobiliyati qanday ataladi?",
        "options": ['Skill', 'Perk', 'Power', 'Ability'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da eng ko'p tarqalgan o'yin rejimi qaysi?",
        "options": ['Clash Squad', 'Battle Royale', 'Lone Wolf', 'Rush Hour'],
        "correct": 1,
    },
    {
        "question": "Clash Squad rejimida bitta raundda g'alaba qozonish uchun nima qilish kerak?",
        "options": ["Barcha dushmanlarni yo'q qilish", 'Bombani portlatish', 'Vaqtda omon qolish', "Eng ko'p ochko to'plash"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Med Kit' nima uchun ishlatiladi?",
        "options": ["Sog'liqni tiklash", 'Qurol tuzatish', 'Tezlik oshirish', "Ko'rish maydonini kengaytirish"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da parashyut bilan tushish qaysi bosqichda sodir bo'ladi?",
        "options": ["O'yin boshida", "O'yin oxirida", 'Zona kichraygandan keyin', "Faqat Clash Squad'da"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da transport vositalaridan qaysi biri suvda yura oladi?",
        "options": ['Motorsikl', 'Qayiq', 'Avtomobil', 'Skeytbord'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da 'Booyah' so'zi nimani anglatadi?",
        "options": ["G'alaba", "Mag'lubiyat", 'Yangi daraja', 'Yangi qurol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da eng tez otish tezligiga ega qurol turi qaysi?",
        "options": ['SMG', 'Sniper', 'Shotgun', 'Pistol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Gloo Wall'ni qayta tiklash uchun nima kerak?",
        "options": ['Vaqt kutish', 'Yangi Gloo Wall sotib olish/topish', 'Level oshirish', 'Boshqa qurol ishlatish'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da jamoa necha kishidan iborat bo'lishi mumkin (standart Squad rejimida)?",
        "options": ['2 kishi', '3 kishi', '4 kishi', '5 kishi'],
        "correct": 2,
    },
    {
        "question": "Free Fire'da 'Ranked' o'yinda yutqazsangiz nima bo'ladi?",
        "options": ["Ball qo'shiladi", 'Ball kamayadi', "Hech narsa o'zgarmaydi", 'Level oshadi'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da 'Clan' nima?",
        "options": ["O'yinchilar guruhi/jamoasi", 'Xarita nomi', 'Qurol turi', 'Transport turi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xaritadagi eng katta tahdid hisoblanadigan narsa nima?",
        "options": ['Zona (xavfsiz maydon torayishi)', "Yomg'ir", 'Tungi vaqt', 'Shamol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da eng ko'p ishlatiladigan snayper miltig'i qaysi?",
        "options": ['AWM', 'M1887', 'MP40', 'Desert Eagle'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Flashbang' granatasi nima qiladi?",
        "options": ["Dushmanni ko'r qiladi", "Dushmanni o'ldiradi", 'Devor yaratadi', "Sog'liqni tiklaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Smoke Grenade' nima uchun ishlatiladi?",
        "options": ["Tutun to'sig'i yaratish", "Dushmanni ko'r qilish", 'Portlatish', "Sog'liq tiklash"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da qaysi rejimda respawn (qayta tirilish) mavjud?",
        "options": ['Battle Royale', "Clash Squad (ba'zi holatlarda)", 'Lone Wolf', 'Hech qaysi birida'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da 'Karambit' nima?",
        "options": ['Pichoq turi (yaqin jang quroli)', 'Miltiq turi', 'Transport', 'Xarita'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'M4A1' qaysi qurol toifasiga kiradi?",
        "options": ['Assault Rifle', 'Sniper', 'Shotgun', 'Pistol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da o'yinchi qancha vaqt davomida nafas ushlab tura oladi (suv ostida)?",
        "options": ['Cheklangan vaqt bor', 'Cheksiz', 'Umuman suzolmaydi', 'Faqat 1 soniya'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Rank' tizimida eng past daraja qaysi?",
        "options": ['Bronze', 'Silver', 'Gold', 'Iron'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xarita chegarasidan tashqarida qolsangiz nima bo'ladi?",
        "options": ["Sog'liq kamayib boradi", "Hech narsa bo'lmaydi", "Avtomatik o'lasiz", "Kuchli bo'lasiz"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Desert Eagle' qaysi turdagi qurol?",
        "options": ['Pistol', 'Snayper', 'Shotgun', 'SMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da eng ko'p o'yinchi tomonidan sevilgan rejim qaysi (mashhurligi bilan)?",
        "options": ['Battle Royale', 'Domination', 'Deathmatch', 'Capture the Flag'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Diamond Royale' nima?",
        "options": ["Maxsus buyumlar to'plami (do'kon aksiyasi)", 'Xarita nomi', 'Qurol turi', 'Rank darajasi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da yutuqni nishonlash uchun ekranga qanday yozuv chiqadi?",
        "options": ['Booyah!', 'Victory!', 'Winner!', 'Champion!'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Alok' xarakterining maxsus qobiliyati nima deb ataladi?",
        "options": ['Drop the Beat', 'Camouflage', 'Riptide Rhythm', 'Hat Trick'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Chrono' xarakteri qanday qobiliyatga ega?",
        "options": ["Vaqtinchalik himoya to'sig'i yaratadi", "Ko'rinmas bo'ladi", "Sog'liqni tiklaydi", 'Tezlikni oshiradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Kelly' xarakteri nimasi bilan mashhur?",
        "options": ['Yugurish tezligi yuqori', 'Snayper aniqligi yuqori', "Ko'p HP'ga ega", "Ko'rinmas bo'la oladi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Wukong' xarakteri qaysi qobiliyatga ega?",
        "options": ['Bambukka aylanib, kamuflyaj qiladi', "Dushmanlarni ko'radi", 'Uchib yura oladi', "Vaqtni to'xtatadi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Hayato' xarakteri qaysi qurolga bog'liq maxsus qobiliyatga ega?",
        "options": ['Katana (pichoq)', "Snayper miltig'i", 'Pistol', 'Granata'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Moco' xarakterining qobiliyati nima deb ataladi?",
        "options": ["Hacker's Eye", "Sniper's Focus", 'Healing Touch', 'Fast Reload'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Skyler' xarakteri qaysi vaziyatda foydali?",
        "options": ['Zombiylarga qarshi kurashda', "Faqat Clash Squad'da", 'Faqat suvda', 'Faqat tunda'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'K' (Captain Booyah) xarakterining ikkita rejimi qanday nomlanadi?",
        "options": ['Psychology va Jiu-Jitsu', 'Attack va Defense', 'Day va Night', 'Fire va Ice'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Steffie' xarakteri qanday qobiliyatga ega?",
        "options": ['Portlash zararini kamaytiradi', 'Yugurish tezligini oshiradi', "Ko'rinmas bo'ladi", "Qurolni tezroq to'ldiradi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Jai' xarakteri nimasi bilan ajralib turadi?",
        "options": ["Qurolni tez qayta to'ldiradi", "Sog'liqni tiklaydi", "Uzoqni ko'radi", 'Sekin yuguradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Kapella' xarakteri qaysi qobiliyatga ega?",
        "options": ['Jamoadoshlarni davolaydi', 'Dushmanni zaharlaydi', 'Qurolni kuchaytiradi', 'Vaqtni tezlashtiradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da qaysi xarita eng birinchi bo'lib chiqarilgan?",
        "options": ['Bermuda', 'Purgatory', 'Kalahari', 'Alpine'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Purgatory' xaritasining o'ziga xos xususiyati nima?",
        "options": ["O'rta asr uslubidagi qal'alar", "Cho'l relyefi", "Qorli tog'lar", 'Suv osti shaharchasi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Kalahari' xaritasi qanday muhitga ega?",
        "options": ["Afrika savannasi/cho'li", 'Qorli tundralar', 'Tropik orol', 'Sanoat shahri'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Alpine' xaritasi qaysi iqlimga mos?",
        "options": ["Qorli/tog'li iqlim", "Cho'l iqlimi", 'Tropik iqlim', 'Botqoqli iqlim'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'AK47' qurolining asosiy afzalligi nima?",
        "options": ['Yuqori zarar kuchi', 'Eng tez otish tezligi', 'Eng katta magazin', 'Eng yengil vazn'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Groza' qaysi toifadagi qurol?",
        "options": ['Assault Rifle', 'Shotgun', 'Sniper', 'Pistol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'MP40' qurolining toifasi qaysi?",
        "options": ['SMG', 'Assault Rifle', 'Sniper', 'LMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'M1887' qurolining turi qaysi?",
        "options": ['Shotgun', 'SMG', 'Assault Rifle', 'Pistol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Kar98k' qaysi toifaga kiradi?",
        "options": ['Sniper Rifle', 'Assault Rifle', 'SMG', 'Shotgun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'UMP' qurolining toifasi nima?",
        "options": ['SMG', 'Sniper', 'LMG', 'Shotgun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'M60' qurolining toifasi qaysi?",
        "options": ['LMG (Light Machine Gun)', 'Sniper', 'Pistol', 'SMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'SPAS12' qurolining o'ziga xosligi nima?",
        "options": ['Yaqin masofada kuchli shotgun', 'Uzoq masofa snayperi', 'Tez otar pistol', 'Sekin ammo tiklovchi LMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Vector' qurolining toifasi qaysi?",
        "options": ['SMG', 'Assault Rifle', 'Sniper', 'Shotgun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'M82B' qurolining xususiyati nima?",
        "options": ["Kuchli, lekin sekin qayta to'ladigan snayper", 'Tez otadigan pistol', 'Yengil SMG', 'Kichik shotgun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Scar' qurolining toifasi qaysi?",
        "options": ['Assault Rifle', 'Sniper', 'Shotgun', 'Pistol'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da qurolga qo'shiladigan 'Scope' nima uchun ishlatiladi?",
        "options": ['Nishonni yaqinlashtirish uchun', 'Zararni oshirish uchun', 'Ovozni pasaytirish uchun', 'Tezroq otish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Suppressor' (silencer) nima qiladi?",
        "options": ['Otish ovozini pasaytiradi', 'Zararni oshiradi', 'Magazin hajmini oshiradi', 'Otish tezligini oshiradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Extended Magazine' nima uchun ishlatiladi?",
        "options": ["Magazin sig'imini oshirish uchun", 'Zararni oshirish uchun', 'Aniqlikni oshirish uchun', 'Tovushni kamaytirish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da yerga cho'zilib yotish holati qanday deb ataladi?",
        "options": ['Prone', 'Crouch', 'Stand', 'Sprint'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da o'tirib olish (yarim egilish) holati qanday deb ataladi?",
        "options": ['Crouch', 'Prone', 'Jump', 'Sprint'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da boshdan (headshot) urish nima uchun muhim?",
        "options": ["Qo'shimcha zarar beradi", "Hech qanday farqi yo'q", "Faqat ko'rinish uchun", 'Faqat ochko beradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da balandlikdan yiqilib tushish nimaga olib kelishi mumkin?",
        "options": ['Zarar (fall damage) olish', 'Tezlik oshishi', "Ko'rinmas bo'lish", "Hech narsa bo'lmaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'EP' (Energy Point) nima uchun ishlatiladi?",
        "options": ["Ko'p xarakter qobiliyatlarida quvvat sifatida", "Sog'liqni to'liq tiklash uchun", 'Qurol sotib olish uchun', 'Tezlikni cheklash uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'First Aid Kit' bilan 'Med Kit' o'rtasidagi farq nima?",
        "options": ['First Aid Kit tezroq, lekin kamroq HP tiklaydi', 'Ular bir xil narsa', 'Med Kit faqat jamoaga ishlaydi', 'First Aid Kit faqat suvda ishlaydi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Free Fire Max' nima?",
        "options": ['Yaxshilangan grafika bilan alohida ilova', 'Yangi xarita nomi', 'Yangi qurol turi', 'Rank darajasi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Lone Wolf' rejimi qanday o'ynaladi?",
        "options": ['Kichik xaritada, tez, yakka yoki juftlikda', '100 kishi bilan katta xaritada', 'Faqat botlar bilan', 'Faqat mashinada'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Rush Hour' rejimi qanday tavsiflanadi?",
        "options": ['Tez suratdagi jangovar rejim', 'Sekin, strategik rejim', 'Faqat suzish rejimi', 'Faqat piyoda yurish rejimi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Ranked' o'yinlarda qatnashish uchun qaysi daraja talab qilinadi?",
        "options": ["Ma'lum bir hisob darajasi (level)", "Talab yo'q, istalgan vaqt kirish mumkin", "Faqat VIP a'zolar", 'Faqat Clan yetakchilari'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Platinum' darajasi qaysi tartibda joylashadi?",
        "options": ["Gold'dan yuqori, Diamond'dan past", 'Eng yuqori daraja', 'Eng past daraja', 'Bronze bilan bir xil'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Season' (mavsum) tugagach nima sodir bo'ladi?",
        "options": ['Rank qisman pasayadi va yangi mavsum boshlanadi', "Hisob o'chib ketadi", "Barcha buyumlar yo'qoladi", "Hech narsa o'zgarmaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Guild' (Clan) yaratish uchun nima kerak?",
        "options": ["Ma'lum miqdorda tanga yoki daraja", "Hech qanday shart yo'q", 'Faqat administratordan ruxsat', 'Faqat Diamond sotib olish'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Elite Pass' nima?",
        "options": ['Mavsumiy maxsus buyumlar beruvchi tizim', 'Yangi xarita', 'Yangi qurol', 'Ranked liga nomi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Free Fire World Series' nima?",
        "options": ['Xalqaro kiberkurash turniri', "Yangi o'yin rejimi", 'Yangi xarakter', 'Yangi xarita'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da o'yinchilar o'zaro nusxa nikini olishlari uchun qaysi bo'lim ishlatiladi?",
        "options": ['Profil sozlamalari (nickname)', 'Xarita tanlash', 'Qurol ombori', "Klan bo'limi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Pet' (hamroh hayvon) nima uchun kerak?",
        "options": ["Qo'shimcha qobiliyat/bonus berish uchun", 'Faqat bezak uchun', "Dushmanni o'ldirish uchun", "Xaritani ko'rsatish uchun"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da mashhur hamrohlardan (pet) biri qaysi?",
        "options": ['Falco', 'Draco', 'Zumba', 'Rex'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Skin' (ko'rinish) nima uchun sotib olinadi?",
        "options": ["Qurol yoki xarakter tashqi ko'rinishini o'zgartirish uchun", 'Zararni oshirish uchun', 'Tezlikni oshirish uchun', 'HP oshirish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Emote' nima?",
        "options": ["O'yinchining his-tuyg'usini bildiruvchi harakat", 'Yangi qurol turi', 'Yangi xarita nomi', 'Jamoa nomi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Craftland' nima?",
        "options": ["O'yinchilar o'zi xarita yaratadigan bo'lim", 'Yangi qurol', 'Ranked liga', 'Klan turniri'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Training Ground' nima uchun ishlatiladi?",
        "options": ["Ko'nikmalarni mashq qilish uchun", "Real o'yin o'ynash uchun", "Klan yig'ilishi uchun", "Do'kondan xarid qilish uchun"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Sensitivity' sozlamasi nimaga ta'sir qiladi?",
        "options": ['Nishon olish tezligi va aniqligiga', 'Ovoz balandligiga', 'Grafika sifatiga', 'Internet tezligiga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'HUD' nima degani?",
        "options": ['Ekrandagi boshqaruv tugmalari joylashuvi', 'Yangi qurol nomi', 'Xarita nomi', 'Rank nomi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'DPI' nima uchun muhim (ayniqsa telefon sozlamalarida)?",
        "options": ["Ekran sezgirligiga bog'liq", "Internet tezligiga bog'liq", "Batareya sarfiga bog'liq", "Ovoz sifatiga bog'liq"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Peek and fire' texnikasi nima?",
        "options": ["To'siq ortidan chiqib tez otish va yashirinish", 'Uzoq vaqt bir joyda turish', "Faqat yugurib o'tish", 'Faqat granata otish'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Drag headshot' texnikasi nimaga asoslangan?",
        "options": ['Nishonni yuqoriga tortib bosh qismga urish', 'Faqat pastga qarab otish', 'Faqat oyoqqa otish', 'Faqat yon tomonga otish'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Auto headshot' funksiyasi odatda qayerda mavjud emas?",
        "options": ["Rasmiy o'yin sozlamalarida (bu firibgarlik hisoblanadi)", 'Hech qayerda cheklanmagan', 'Faqat Ranked rejimda taqiqlangan', 'Faqat mobil versiyada bor'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Hack' yoki 'Cheat' ishlatish nimaga olib kelishi mumkin?",
        "options": ['Hisobni bloklashga (ban)', "Qo'shimcha mukofotga", 'Yangi qurol berilishiga', 'Hech qanday oqibatga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Report' funksiyasi nima uchun ishlatiladi?",
        "options": ["Firibgar yoki qoidabuzar o'yinchini bildirish uchun", "Do'st qo'shish uchun", 'Xarita tanlash uchun', 'Qurol sotib olish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Voice Chat' nima uchun ishlatiladi?",
        "options": ['Jamoadoshlar bilan ovozli muloqot qilish uchun', 'Dushmanga signal berish uchun', "Xarita ko'rsatish uchun", 'Qurol tanlash uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Spectate' funksiyasi nima qiladi?",
        "options": ["O'lgandan keyin boshqa o'yinchilarni kuzatish imkonini beradi", "O'yinni to'xtatadi", 'Yangi hayot beradi', "Xaritani o'zgartiradi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Custom Room' nima uchun yaratiladi?",
        "options": ["Do'stlar bilan maxsus sozlamali o'yin uyushtirish uchun", "Faqat solo o'ynash uchun", 'Faqat kuzatish uchun', "Faqat do'kon uchun"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Guild Level' nimaga bog'liq holda oshadi?",
        "options": ["A'zolarning faolligi va hissasiga", "Faqat vaqt o'tishiga", 'Faqat pul sarflashga', "Hech nimaga bog'liq emas"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Daily Missions' nima beradi?",
        "options": ['Kunlik topshiriqlar uchun mukofot', 'Faqat ball', 'Faqat vaqtinchalik qurol', 'Hech narsa bermaydi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Gold' (o'yin ichi valyutasi) nima uchun ishlatiladi?",
        "options": ["Do'kondan turli buyum sotib olish uchun", 'Faqat rank oshirish uchun', "Faqat do'st qo'shish uchun", 'Faqat xarita ochish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Diamond' (qimmatbaho valyuta) qanday olinadi?",
        "options": ['Asosan pul evaziga sotib olinadi', "Faqat o'yin ichida g'alaba bilan", 'Faqat kunlik login bilan', "Umuman olib bo'lmaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Top Up' nima degani?",
        "options": ["Hisobga Diamond to'ldirish", 'Yangi xarakter ochish', 'Rank oshirish', 'Klan yaratish'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xavfsizlik uchun ikki bosqichli tasdiqlash (2FA) nimaga yordam beradi?",
        "options": ['Hisobni himoya qilishga', "O'yin tezligini oshirishga", 'Grafikani yaxshilashga', 'Yangi qurol berishga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Facebook' yoki 'Google' orqali kirish nima uchun tavsiya etiladi?",
        "options": ["Hisobni yo'qotib qo'ymaslik uchun", "Tezroq o'ynash uchun", "Ko'proq Diamond olish uchun", 'Yangi xarita ochish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Bermuda Remastered' nima?",
        "options": ['Bermuda xaritasining yangilangan versiyasi', 'Yangi qurol', 'Yangi xarakter', 'Yangi rejim'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'NEXTERRA' xaritasi qanday xususiyatga ega?",
        "options": ['Kelajak/texnologik uslubdagi muhit', "Faqat cho'l relyefi", 'Faqat suv osti dunyosi', "Faqat qor bosgan tog'lar"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Solo vs Squad' rejimida nechta o'yinchi bitta o'zi jamoaga qarshi o'ynaydi?",
        "options": ['1 kishi', '2 kishi', '3 kishi', '4 kishi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Duo' rejimida bir jamoada nechta o'yinchi bo'ladi?",
        "options": ['2 kishi', '3 kishi', '4 kishi', '5 kishi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da qaysi transport vositasi eng tez yuradi (odatda)?",
        "options": ['Sport avtomobil/Motorsikl', 'Qayiq', 'Piyoda yurish', 'Tank'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Monster Truck' qaysi xususiyatga ega?",
        "options": ['Katta va mustahkam transport', 'Eng tez uchuvchi transport', 'Suv osti transporti', 'Faqat parvoz qiladi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da o'yinchi champion bo'lgach ekranda qanday raqam ko'rsatiladi?",
        "options": ["1-o'rin (#1 Booyah)", "0-o'rin", "100-o'rin", 'Hech qanday raqam'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'MVP' unvoni kimga beriladi?",
        "options": ["O'yinda eng ko'p hissa qo'shgan o'yinchiga", "Faqat g'alaba qozongan jamoaning kapitaniga", "Faqat birinchi o'lgan o'yinchiga", "Tasodifiy o'yinchiga"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Kill Count' nimani bildiradi?",
        "options": ["O'ldirilgan dushmanlar sonini", "Yig'ilgan qurollar sonini", "O'tkazilgan o'yinlar sonini", "Klan a'zolari sonini"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Survival Rank' nimaga asoslanadi?",
        "options": ["O'yinlarda qancha tirik qolganingizga", "Faqat o'ldirishlar soniga", 'Faqat vaqtga', 'Faqat Diamond miqdoriga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Ping' nimani anglatadi?",
        "options": ['Internet ulanish tezligi/kechikishi', 'Qurol zarari', 'Xarakter tezligi', "Ekran o'lchami"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da yuqori 'Ping' nimaga olib kelishi mumkin?",
        "options": ["O'yinda kechikish va laglarga", "Ko'proq Diamond olishga", 'Tezroq rank oshishga', 'Yangi qurol ochilishiga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Gyroscope' funksiyasi nima uchun ishlatiladi?",
        "options": ['Telefonni burab nishonni boshqarish uchun', 'Ovozni sozlash uchun', 'Grafikani yaxshilash uchun', 'Internetni tezlashtirish uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Auto Pickup' funksiyasi nima qiladi?",
        "options": ["Yaqin atrofdagi buyumlarni avtomatik yig'adi", 'Dushmanni avtomatik otadi', 'Xaritani avtomatik ochadi', 'Qurolni avtomatik sotadi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Loadout' nimani bildiradi?",
        "options": ["O'yinchining tanlagan qurol va buyumlar to'plami", 'Xarita nomini', 'Klan nomini', 'Rank darajasini'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da yangi yangilanishlar odatda qanday nomlanadi?",
        "options": ['OB (Original Bug) yangilanishlari', 'Faqat raqamli versiyalar', "Faqat 'Update' so'zi bilan", 'Hech qanday nom berilmaydi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Battle Royale' janrining asosiy g'oyasi nima?",
        "options": ["Ko'p o'yinchidan faqat bittasi/bir jamoa omon qolishi", "Faqat ikki kishi o'ynashi", 'Faqat jamoaviy hamkorlik', "G'oliblik bo'lmaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xarakterlarning ba'zilari 'Elite' versiyasiga ega bo'lishi nimani anglatadi?",
        "options": ["Yaxshilangan qobiliyat yoki ko'rinishga ega maxsus versiya", 'Zaifroq versiya', 'Faqat bepul versiya', 'Faqat sinov versiyasi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Global' server nimani anglatadi?",
        "options": ["Butun dunyo o'yinchilari uchun umumiy server", 'Faqat bitta davlat uchun server', 'Faqat sinov serveri', 'Offline rejim'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Advance Server' nima uchun mavjud?",
        "options": ['Yangi funksiyalarni chiqarishdan oldin sinash uchun', "Kundalik o'ynash uchun", "Faqat Ranked o'ynash uchun", 'Faqat Klan urushlari uchun'],
        "correct": 0,
    },
    {
        "question": "Free Fire o'yini qaysi yili chiqarilgan?",
        "options": ['2017-yil', '2010-yil', '2020-yil', '2015-yil'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Andrew' xarakteri nimasi bilan ajralib turadi?",
        "options": ["Qalqon zarari kamayishi yo'q (mustahkam himoya)", 'Eng tez yuguradi', 'Suv ostida nafas oladi', "Ko'rinmas bo'ladi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Laura' xarakteri qaysi qurolda kuchli?",
        "options": ["Snayper miltig'ida (aniqlik oshadi)", 'Shotgunda', 'Pichoqda', 'Granatada'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Dimitri' xarakterining qobiliyati nimaga bog'liq?",
        "options": ['EP (energiya) tiklanishiga', 'Yugurish tezligiga', "Ko'rish maydoniga", 'Qurol zarariga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Notora' xarakterining foydasi nimada?",
        "options": ["Yiqilgan dushmanlardan qurol tezroq yig'iladi", "Ko'rinmas bo'ladi", 'Uchib yuradi', 'Suvda tez suzadi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Shirou' xarakterining qobiliyati nimaga qaratilgan?",
        "options": ["O'ziga qaratilgan zararni ko'rsatish/aniqlashga", "Sog'liq tiklashga", 'Tezlik oshirishga', 'Qurol yashirishga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Ford' xarakterining afzalligi qachon ishga tushadi?",
        "options": ['HP kam qolganda zarar kamayadi', "HP to'liq bo'lganda", 'Faqat suvda', 'Faqat tunda'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Jota' xarakteri qaysi qurol bilan bog'liq maxsus qobiliyatga ega?",
        "options": ["Shotgun (o'ldirishda HP tiklanadi)", 'Sniper', 'Pistol', 'Granata'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Luqueta' xarakteri nima uchun kuchli hisoblanadi?",
        "options": ["Har bir o'ldirish uchun maksimal HP oshadi", 'Tezlik cheksiz oshadi', "Ko'rinmas bo'ladi", 'Qurolsiz kuchli zarar beradi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Maxim' xarakterining qobiliyati nimaga tegishli?",
        "options": ["O'q-dori (ammo) sig'imi oshishiga", 'Yugurish tezligiga', "Ko'rish radiusiga", "Sog'liq tiklashga"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'AUG' qurolining toifasi qaysi?",
        "options": ['Assault Rifle', 'Sniper', 'SMG', 'Shotgun'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'SVD' qurolining toifasi qaysi?",
        "options": ['Sniper Rifle', 'Assault Rifle', 'SMG', 'LMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'MP5' qurolining toifasi qaysi?",
        "options": ['SMG', 'Sniper', 'Shotgun', 'LMG'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Gloo Wall Grenade' oddiy Gloo Wall'dan nimasi bilan farqlanadi?",
        "options": ["Uloqtirilib, uzoqroqqa qo'yiladi", 'Umuman ishlamaydi', 'Faqat suvda ishlaydi', 'Faqat tunda ishlaydi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Clash Squad Ranked' nimasi bilan oddiy Clash Squad'dan farq qiladi?",
        "options": ['Alohida rank tizimiga ega', "Xarita boshqacha bo'ladi", "Faqat botlar bilan o'ynaladi", "Qurol bo'lmaydi"],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Booyah Day' nima?",
        "options": ["O'yinning yillik bayrami/tantanasi", 'Yangi xarita nomi', 'Yangi qurol nomi', 'Rank darajasi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Paloma' xarakterining foydasi nimada?",
        "options": ["Davolanish jarayoni to'xtatilmaydi", 'Tezlik cheksiz oshadi', "Ko'rinmas bo'ladi", 'Zarar ikki barobar oshadi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Advance Server'da xato (bug) topgan o'yinchilarga odatda nima beriladi?",
        "options": ['Diamond mukofoti', 'Yangi xarakter bepul', 'Rank avtomatik oshadi', 'Hech narsa berilmaydi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xarakter qobiliyatlarini birga ishlatish strategiyasi qanday nomlanadi?",
        "options": ['Character combo (kombinatsiya)', 'Solo push', 'Random pick', 'Auto skill'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Xayne' xarakteri qaysi muhitga moslashgan?",
        "options": ["Qorong'i/kechqurun sharoitga", 'Faqat suv ostiga', "Faqat cho'lga", 'Faqat qorli hududga'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da 'Loot Box' nima?",
        "options": ["O'ljalar solingan quti", 'Dushman bazasi', 'Transport turi', 'Xarita nomi'],
        "correct": 0,
    },
    {
        "question": "Free Fire'da xarakter tanlashda nimaga e'tibor berish kerak?",
        "options": ["Faqat tashqi ko'rinishga", 'Uning maxsus qobiliyatiga', 'Faqat narxiga', 'Hech narsaga'],
        "correct": 1,
    },
    {
        "question": "Free Fire'da 'Recall' funksiyasi (ba'zi xarakterlarda) nima qiladi?",
        "options": ['Oldingi joyga qaytaradi', 'Dushmanni chaqiradi', "Qurolni yo'qotadi", "Xaritani o'zgartiradi"],
        "correct": 0,
    },
]
