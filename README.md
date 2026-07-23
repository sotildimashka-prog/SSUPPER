# 🎮 O'yin Sirlari — Free Fire Telegram Bot

Free Fire o'yinchilari uchun sensitivity nastroykalari, premium nicknamelar,
qo'llanmalar va foydalanuvchi statistikasini taqdim etuvchi professional
Telegram bot.

## 📋 Imkoniyatlar

- Majburiy kanal obunasi (5 ta kanal)
- `/start`, `/haqida`, `/menu`, `/profil`, `/yordam`, `/yangiliklar` buyruqlari
- Pastki ReplyKeyboard menyu (2 tugma bir qatorda)
- ⚙️ Nastroykalar — 7 brend, har birida 5 tadan (jami 35) telefon modeli,
  har biriga alohida sensitivity/DPI/HUD/FPS tavsiyalari
- 🆔 Niklar — Erkaklar va Qizlar uchun 20 tadan premium nickname (nusxalash uchun `code` formatda)
- 📚 Qo'llanmalar — Headshot, Gloo Wall, Rush, Rank strategiyalari va boshqalar
- 💎 Premium bo'lim — narxlar va aloqa
- 🎮 Mening FF ID'im — UID orqali profil ma'lumotlarini olish (API ulash kerak)
- 📊 Statistika va 📢 Xabar yuborish — faqat admin uchun
- Har bir yangi foydalanuvchi haqida adminga avtomatik xabar
- SQLite bazasi orqali foydalanuvchilarni saqlash

## 🗂 Loyiha tuzilishi

```
ffbot/
├── bot.py                  # Asosiy ishga tushirish fayli
├── config.py                # Sozlamalar (token, admin, kanallar)
├── database.py               # SQLite bilan ishlash
├── keyboards.py               # Reply/Inline klaviaturalar
├── data/
│   ├── nicknames_data.py       # Nicknamelar ro'yxati
│   ├── settings_data.py        # Telefon nastroykalari
│   └── guides_data.py          # Qo'llanmalar matnlari
├── handlers/
│   ├── start.py                # /start va obuna tekshiruvi
│   ├── menu.py                  # Menyu buyruqlari va tugmalar
│   ├── settings.py               # Nastroykalar callback'lari
│   ├── nicknames.py               # Niklar callback'lari
│   ├── guides.py                   # Qo'llanmalar callback'lari
│   ├── ffid.py                      # Free Fire ID qidiruv
│   ├── admin.py                      # Statistika va xabar yuborish
│   └── subscription.py                # Obuna tekshiruv yordamchisi
├── requirements.txt
├── Procfile                 # Railway uchun
└── .env.example
```

## ⚙️ O'rnatish (lokal test uchun)

```bash
git clone <repo-url>
cd ffbot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # so'ng .env faylini tahrirlang
python bot.py
```

## 🚀 Railway'ga deploy qilish

1. Ushbu papkani GitHub repositoriyasiga yuklang.
2. [Railway](https://railway.app) da **New Project → Deploy from GitHub repo**
   ni tanlang va repositoriyani ulang.
3. **Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN` — bot tokeningiz
   - `ADMIN_ID` — sizning Telegram ID'ingiz
   - (ixtiyoriy) `FF_API_URL`, `FF_API_KEY`
4. **Ma'lumotlar yo'qolmasligi uchun MUHIM:** Railway loyihasiga
   **Volume** qo'shing (Settings → Volumes) va uni masalan `/data` yo'liga
   ulang, so'ng `DB_PATH` o'zgaruvchisini `/data/database.db` qilib
   sozlang. Aks holda har safar qayta deploy qilinganda konteyner fayl
   tizimi tozalanadi va SQLite bazasi o'chib ketadi.
5. Railway `Procfile` orqali avtomatik `worker: python bot.py` jarayonini
   ishga tushiradi (Start Command sifatida `python bot.py` ni ham qo'lda
   ko'rsatishingiz mumkin).
6. Deploy tugagach, botga Telegram'da `/start` yuboring.

## 📢 Majburiy obuna qanday ishlaydi

`get_chat_member` API'si orqali foydalanuvchining kanal a'zoligi
tekshiriladi. **Buning ishlashi uchun bot har bir majburiy kanalda
ADMIN sifatida qo'shilgan bo'lishi shart.** Aks holda Telegram bot uchun
a'zolik holatini bermaydi va foydalanuvchi "obuna bo'lmagan" deb
hisoblanadi.

Kanallar ro'yxatini `config.py` dagi `REQUIRED_CHANNELS` orqali
o'zgartirishingiz mumkin.

## 🎮 Free Fire ID xizmatini ulash

Bot hozircha `FF_API_URL` sozlanmagan bo'lsa, foydalanuvchiga xizmat
hali ulanmaganini bildiradi (Free Fire uchun rasmiy ochiq API mavjud
emas). Agar ishonchli uchinchi tomon API xizmatidan foydalanish
niyatingiz bo'lsa:

1. `FF_API_URL` — API manzilini (masalan `https://.../info`) kiriting.
2. `FF_API_KEY` — agar API token talab qilsa, shuni kiriting.
3. `handlers/ffid.py` faylidagi `receive_ff_id` funksiyasida API
   javobidagi maydon nomlarini (`nickname`, `uid`, `region` va h.k.)
   xizmatingiz formatiga moslab o'zgartiring.

## 🛠 Texnologiyalar

- Python 3.11+
- [python-telegram-bot](https://docs.python-telegram-bot.org/) 21.x (async)
- SQLite3 (standart kutubxona)
- httpx (Free Fire API so'rovlari uchun)

## 🔐 Xavfsizlik bo'yicha eslatma

Bot tokenini ochiq GitHub repositoriyasida saqlamang. `config.py`
ichida standart qiymat sifatida ko'rsatilgan token faqat qulaylik
uchun; production muhitda albatta `BOT_TOKEN` environment
o'zgaruvchisidan foydalaning va tokenni GitHub'ga push qilishdan oldin
[@BotFather](https://t.me/BotFather) orqali yangilang (agar u allaqachon
ochiq joyda ulashilgan bo'lsa).

## 🆕 Yangi qo'shilgan imkoniyatlar (v2 yangilanish)

- **Tugma nomlari aniqlashtirildi**: "📱⚙️ Telefon uchun nastroyka" va "📲⚙️ Planshet uchun nastroyka" endi bir-biriga o'xshamaydi.
- **💣🔥 Free Fire Hack**: Proxy server, Cheat va panellar, Mening FF ID'im — bittasi ostida, inline tugmalar va "⬅️ Orqaga" bilan.
- **✏️ Tugmalarni tahrirlash** endi rasm/video/fayl ham qabul qiladi (avval faqat matn edi). Admin istalgan matnni tahrirlashda, matn o'rniga rasm/video yuborsa, shu media keyingi safar ko'rsatiladi.
- **🎛️✨ Alohida nastroyka**: foydalanuvchi telefon modelini batafsil yozadi → admin ID bilan birga xabar oladi → admin "✍️ Nastroyka yuborish" tugmasini bosib, javobni (matn/rasm/video) to'g'ridan-to'g'ri o'sha foydalanuvchiga yuboradi.
- **💰 Hisobim → 🎁 Kunlik bonus**: har kuni bosilganda 10 so'm hisobga qo'shiladi (kuniga 1 marta).
- **🌐✨ Foydali web sayt**: bosilganda https://freefireuz.netlify.app saytiga olib boradigan tugma chiqadi.

Barcha yangi bo'limlarda "⬅️ Orqaga" tugmasi mavjud.
