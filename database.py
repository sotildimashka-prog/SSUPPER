"""
SQLite ma'lumotlar bazasi bilan ishlash moduli.
GitHub'da qayta deploy qilinganda ma'lumotlar o'chib ketmasligi uchun
DB fayli persistent volume (Railway Volume) ga ulanishi tavsiya etiladi -
buni README.md faylida batafsil tushuntirilgan.
"""

import sqlite3
import json
from datetime import date, datetime, timedelta
from contextlib import contextmanager

from config import DB_PATH, REQUIRED_CHANNELS as _DEFAULT_REQUIRED_CHANNELS


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        _init_turnirlar_table(conn)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                joined_at TEXT,
                last_active TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_starts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS message_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS apples (
                user_id INTEGER PRIMARY KEY,
                apples INTEGER DEFAULT 0,
                penalties INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS referrals (
                referred_id INTEGER PRIMARY KEY,
                referrer_id INTEGER,
                credited INTEGER DEFAULT 0,
                created_at TEXT,
                credited_at TEXT,
                penalty_applied INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS topup_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                photo_file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hspro_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                method TEXT,
                amount INTEGER,
                file_id TEXT,
                file_type TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diamond_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                package_label TEXT,
                price INTEGER,
                ff_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bonus_claims (
                user_id INTEGER PRIMARY KEY,
                last_claim_date TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_progress (
                user_id INTEGER PRIMARY KEY,
                day TEXT,
                answered_count INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_diamonds (
                user_id INTEGER PRIMARY KEY,
                diamonds INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_asked_questions (
                user_id INTEGER,
                question_index INTEGER,
                PRIMARY KEY (user_id, question_index)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diamonds_earned_daily (
                user_id INTEGER,
                day TEXT,
                earned INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, day)
            )
            """
        )
        # ---------- 💰 To'lov usullari: yangi bonus jadvallari ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_money_bonus (
                user_id INTEGER PRIMARY KEY,
                last_claim_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diamond_bonus_claims (
                user_id INTEGER PRIMARY KEY,
                last_claim_date TEXT
            )
            """
        )
        # ---------- 🌐 Til tanlash (uz / ru) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_language (
                user_id INTEGER PRIMARY KEY,
                language TEXT
            )
            """
        )
        # ---------- 🎮 Mini O'yinlar (24 soatlik limit, mukofotli rejim) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS game_cooldowns (
                user_id INTEGER,
                game_key TEXT,
                last_played_at TEXT,
                PRIMARY KEY (user_id, game_key)
            )
            """
        )
        # Raqam topish o'yini uchun vaqtinchalik holat (ketma-ket taxminlar)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS number_game_state (
                user_id INTEGER PRIMARY KEY,
                target INTEGER,
                tries_left INTEGER,
                mode TEXT
            )
            """
        )
        # ---------- 🔥 Qiyin O'yinlar (Free Fire mavzusidagi 10 ta o'yin) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diamonds_lost_daily (
                user_id INTEGER,
                day TEXT,
                lost INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, day)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hard_games_cooldown (
                user_id INTEGER,
                game_key TEXT,
                next_allowed_at TEXT,
                PRIMARY KEY (user_id, game_key)
            )
            """
        )
        # Migratsiya: eski versiyada bu jadval faqat user_id bo'yicha edi
        # (barcha 10 ta o'yinga UMUMIY kutish vaqti). Endi har bir o'yin
        # (game_key) uchun ALOHIDA kutish vaqti saqlanadi - bitta o'yinni
        # o'ynash faqat o'sha o'yinni bloklaydi, qolganlari band bo'lib
        # qolmaydi. Eski formatdagi jadval topilsa, yangi formatga
        # o'tkaziladi (eski umumiy kutish vaqti shu jarayonda tozalanadi -
        # bu vaqtinchalik holat, foydalanuvchiga zarar keltirmaydi).
        cur.execute("PRAGMA table_info(hard_games_cooldown)")
        _hgc_cols = {row[1] for row in cur.fetchall()}
        if "game_key" not in _hgc_cols:
            cur.execute("DROP TABLE hard_games_cooldown")
            cur.execute(
                """
                CREATE TABLE hard_games_cooldown (
                    user_id INTEGER,
                    game_key TEXT,
                    next_allowed_at TEXT,
                    PRIMARY KEY (user_id, game_key)
                )
                """
            )
        # ---------- 💣 Portlovchi almaz (tavakkal o'yinlari) ----------
        # Har bir raund alohida yoziladi: bir marta bosilgan tugma ikkinchi
        # marta hisobga ta'sir qila olmaydi (state: open -> won/lost/...).
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_key TEXT NOT NULL,
                stake INTEGER NOT NULL,
                state TEXT NOT NULL DEFAULT 'open',
                choice INTEGER,
                created_at TEXT,
                settled_at TEXT
            )
            """
        )
        # ---------- 🔄 Avtomatik menyu yangilanishi ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_menu_version (
                user_id INTEGER PRIMARY KEY,
                version INTEGER DEFAULT 0
            )
            """
        )
        # ---------- 🏆 Yutiqni chiqarish (pul yechish so'rovlari) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cash_withdraw_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
            """
        )
        # ---------- 🎵 Musiqa yaratish (kunlik limit) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS music_generations (
                user_id INTEGER PRIMARY KEY,
                day TEXT,
                count INTEGER DEFAULT 0
            )
            """
        )
        # ---------- 👑 Pro obuna (admin tomonidan qo'lda beriladi) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pro_users (
                user_id INTEGER PRIMARY KEY,
                granted_at TEXT
            )
            """
        )
        # ---------- 🚫 Bloklangan foydalanuvchilar (admin tomonidan) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                blocked_at TEXT
            )
            """
        )
        # ---------- 💘 Headshot Pro - "Nastroykani olish" (telefon modeli) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS hspro_settings_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                user_id INTEGER,
                phone_model TEXT,
                created_at TEXT
            )
            """
        )
        # ---------- 🏆 Top foydalanuvchilar reytingi (har kuni yangilanadigan keshi) ----------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT,
                updated_at TEXT
            )
            """
        )

        # ---------- 🍎➡️💎 / ⚠️ Eski bazalarni yangi ustunlar bilan ----------
        # to'ldirish (jarima tizimi uchun). CREATE TABLE IF NOT EXISTS eski
        # (allaqachon yaratilgan) jadvalga yangi ustun qo'shmaydi, shu sabab
        # bu yerda alohida ALTER TABLE bilan qo'shib qo'yamiz - agar ustun
        # allaqachon mavjud bo'lsa xato e'tiborsiz qoldiriladi.
        for alter_sql in (
            "ALTER TABLE apples ADD COLUMN penalties INTEGER DEFAULT 0",
            "ALTER TABLE referrals ADD COLUMN credited_at TEXT",
            "ALTER TABLE referrals ADD COLUMN penalty_applied INTEGER DEFAULT 0",
            # 🚫 Bloklanganlar: blokdan chiqarilgan foydalanuvchi ro'yxatdan
            # o'chib ketmasligi uchun (admin uni qayta bloklay olsin).
            "ALTER TABLE blocked_users ADD COLUMN is_active INTEGER DEFAULT 1",
            "ALTER TABLE blocked_users ADD COLUMN unblocked_at TEXT",
        ):
            try:
                cur.execute(alter_sql)
            except sqlite3.OperationalError:
                pass


def set_user_language(user_id: int, language: str):
    """Foydalanuvchi tanlagan tilni saqlaydi ('uz' yoki 'ru')."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_language (user_id, language) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET language = excluded.language",
            (user_id, language),
        )


def get_user_language(user_id: int) -> str | None:
    """Foydalanuvchining saqlangan tilini qaytaradi, tanlanmagan bo'lsa None."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT language FROM user_language WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row["language"] if row else None


def add_user_if_new(user_id: int, first_name: str, username: str) -> bool:
    """Foydalanuvchini bazaga qo'shadi. Yangi bo'lsa True qaytaradi."""
    now = datetime.utcnow().isoformat()
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing = cur.fetchone()
        is_new = existing is None
        if is_new:
            cur.execute(
                "INSERT INTO users (user_id, first_name, username, joined_at, last_active) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, first_name, username, now, now),
            )
        else:
            cur.execute(
                "UPDATE users SET first_name = ?, username = ?, last_active = ? WHERE user_id = ?",
                (first_name, username, now, user_id),
            )
        cur.execute(
            "INSERT INTO daily_starts (user_id, day) VALUES (?, ?)", (user_id, today)
        )
    return is_new


def touch_user_activity(user_id: int):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))


def log_message(user_id: int):
    today = date.today().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO message_log (user_id, day) VALUES (?, ?)", (user_id, today)
        )


def get_all_user_ids():
    with get_conn() as conn:
        cur = conn.execute("SELECT user_id FROM users")
        return [row["user_id"] for row in cur.fetchall()]


def get_stats():
    today = date.today().isoformat()
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        today_users = conn.execute(
            "SELECT COUNT(*) c FROM users WHERE substr(joined_at, 1, 10) = ?", (today,)
        ).fetchone()["c"]
        today_starts = conn.execute(
            "SELECT COUNT(*) c FROM daily_starts WHERE day = ?", (today,)
        ).fetchone()["c"]
        total_messages = conn.execute("SELECT COUNT(*) c FROM message_log").fetchone()["c"]
    return {
        "total_users": total_users,
        "today_users": today_users,
        "today_starts": today_starts,
        "total_messages": total_messages,
    }


def get_user(user_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()


def get_user_by_username(username: str):
    """Telegram username (@ belgisiz yoki bilan) bo'yicha foydalanuvchini topadi.
    Katta-kichik harflarga sezgir emas (case-insensitive)."""
    clean = username.strip().lstrip("@")
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (clean,)
        )
        return cur.fetchone()


# ---------------- Tahrirlanadigan matnlar (app_settings) ----------------

def get_setting(key: str, default: str = "") -> str:
    with get_conn() as conn:
        cur = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


# ---------------- 📢 Majburiy obuna kanallari (admin panel orqali boshqariladi) ----------------

_REQUIRED_CHANNELS_KEY = "required_channels"


def get_required_channels() -> list:
    """Majburiy obuna kanallari ro'yxatini qaytaradi. Birinchi chaqiruvda
    (hali app_settings'da saqlanmagan bo'lsa) config.py dagi standart
    ro'yxat bilan boshlang'ich holatga keltiriladi (seed), shundan keyin
    hammasi bazadan (admin panel orqali) boshqariladi."""
    raw = get_setting(_REQUIRED_CHANNELS_KEY, "")
    if not raw:
        set_setting(_REQUIRED_CHANNELS_KEY, json.dumps(_DEFAULT_REQUIRED_CHANNELS))
        return [dict(ch) for ch in _DEFAULT_REQUIRED_CHANNELS]
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except (ValueError, TypeError):
        pass
    return [dict(ch) for ch in _DEFAULT_REQUIRED_CHANNELS]


def add_required_channel(name: str, username: str, emoji: str = "📡") -> None:
    username = (username or "").strip().lstrip("@")
    channels = get_required_channels()
    for ch in channels:
        if ch.get("username", "").lower() == username.lower():
            ch["name"] = name
            ch["emoji"] = emoji
            set_setting(_REQUIRED_CHANNELS_KEY, json.dumps(channels))
            return
    channels.append({"name": name, "username": username, "emoji": emoji})
    set_setting(_REQUIRED_CHANNELS_KEY, json.dumps(channels))


def remove_required_channel(username: str) -> None:
    username = (username or "").strip().lstrip("@")
    channels = get_required_channels()
    channels = [ch for ch in channels if ch.get("username", "").lower() != username.lower()]
    set_setting(_REQUIRED_CHANNELS_KEY, json.dumps(channels))


# ---------------- 💎 Almaz yechish so'rovi uchun minimal miqdor ----------------

_MIN_WITHDRAW_KEY = "min_withdraw"
_DEFAULT_MIN_WITHDRAW = 350


def get_min_withdraw() -> int:
    raw = get_setting(_MIN_WITHDRAW_KEY, "")
    if raw and raw.isdigit():
        return int(raw)
    return _DEFAULT_MIN_WITHDRAW


def set_min_withdraw(value: int) -> None:
    set_setting(_MIN_WITHDRAW_KEY, str(int(value)))


def get_content(key: str, default_text: str) -> dict:
    """Matn yoki media (rasm/video/fayl) saqlangan sozlamani JSON sifatida qaytaradi."""
    import json

    raw = get_setting(key, "")
    if not raw:
        return {"type": "text", "text": default_text, "caption": ""}
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {"type": "text", "text": raw, "caption": ""}


def set_content(key: str, content_type: str, text: str = "", file_id: str = "", caption: str = ""):
    import json

    set_setting(
        key,
        json.dumps(
            {"type": content_type, "text": text, "file_id": file_id, "caption": caption}
        ),
    )


# ---------------- ⚙️ Nastroykalar: telefon modeli bo'yicha kontent ----------------
# Har bir telefon modeli uchun admin panel orqali qo'shilgan kontent (matn /
# rasm / video / rasm+matn / video+matn). app_settings jadvalida
# "nastroyka:<model nomi>" kaliti ostida JSON sifatida saqlanadi.

def get_nastroyka_content(model_name: str) -> dict | None:
    """Model uchun saqlangan kontentni qaytaradi, hali qo'shilmagan bo'lsa None."""
    raw = get_setting(f"nastroyka:{model_name}", "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def set_nastroyka_content(
    model_name: str, content_type: str, text: str = "", file_id: str = "", caption: str = ""
):
    set_setting(
        f"nastroyka:{model_name}",
        json.dumps(
            {"type": content_type, "text": text, "file_id": file_id, "caption": caption}
        ),
    )


def delete_nastroyka_content(model_name: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM app_settings WHERE key = ?", (f"nastroyka:{model_name}",))


# ---------------- 🏆 Free Fire turnirlar / 🎮 Free Fire akkauntlar ----------------
# "Nima gap?" bo'limi uchun: admin panel orqali qo'shiladigan, oddiy JSON
# (app_settings jadvali) sifatida saqlanadigan kontent. Alohida jadval
# yaratilmadi - loyihada allaqachon mavjud bo'lgan get_setting/set_setting
# patterni ishlatildi.

TOURNAMENT_SLOTS = ("today", "tomorrow", "2days", "3days", "1week")

_TOURNAMENT_KEY_PREFIX = "fftournament_"
_FF_ACCOUNT_KEY = "ffaccount"


def get_tournament(slot: str) -> dict | None:
    """Berilgan kun (slot) uchun saqlangan turnir ma'lumotini qaytaradi.
    Agar admin hali qo'shmagan bo'lsa - None qaytadi."""
    raw = get_setting(f"{_TOURNAMENT_KEY_PREFIX}{slot}", "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def set_tournament(
    slot: str,
    content_type: str,
    file_id: str = "",
    caption: str = "",
    channel_url: str = "",
):
    set_setting(
        f"{_TOURNAMENT_KEY_PREFIX}{slot}",
        json.dumps(
            {
                "type": content_type,
                "file_id": file_id,
                "caption": caption,
                "channel_url": channel_url,
            }
        ),
    )


def delete_tournament(slot: str):
    set_setting(f"{_TOURNAMENT_KEY_PREFIX}{slot}", "")


# ---------------- 🏆 Free Fire Turnirlar (ochiq ro'yxat, cheksiz son) ----------------
# "🏆 Free Fire Turnirlar" (asosiy pastki tugma) bo'limi uchun: admin
# xohlagancha turnir qo'shishi mumkin (bir kunda 3-4 tasi bo'lsa ham),
# har biri o'z kuni, formati (3/3, 1/1 va h.k.) va vaqti bilan saqlanadi.

def _init_turnirlar_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ff_turnirlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_label TEXT,
            title TEXT,
            format_text TEXT,
            time_text TEXT,
            note TEXT,
            created_at TEXT
        )
        """
    )


def add_turnir(day_label: str, title: str, format_text: str, time_text: str, note: str = "") -> int:
    with get_conn() as conn:
        _init_turnirlar_table(conn)
        cur = conn.execute(
            "INSERT INTO ff_turnirlar (day_label, title, format_text, time_text, note, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (day_label, title, format_text, time_text, note, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_turnirlar_list() -> list:
    """Barcha qo'shilgan turnirlarni (eskisidan yangisiga) ro'yxat qilib qaytaradi."""
    with get_conn() as conn:
        _init_turnirlar_table(conn)
        rows = conn.execute(
            "SELECT id, day_label, title, format_text, time_text, note FROM ff_turnirlar ORDER BY id ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_turnir_by_id(turnir_id: int) -> dict | None:
    with get_conn() as conn:
        _init_turnirlar_table(conn)
        row = conn.execute(
            "SELECT id, day_label, title, format_text, time_text, note FROM ff_turnirlar WHERE id = ?",
            (turnir_id,),
        ).fetchone()
        return dict(row) if row else None


def delete_turnir_by_id(turnir_id: int):
    with get_conn() as conn:
        _init_turnirlar_table(conn)
        conn.execute("DELETE FROM ff_turnirlar WHERE id = ?", (turnir_id,))


def get_all_tournament_status() -> dict:
    """Har bir kun (slot) uchun turnir qo'shilgan-qo'shilmaganini (True/False)
    qaytaradi - admin panelida ✅/❌ belgisi uchun ishlatiladi."""
    return {slot: get_tournament(slot) is not None for slot in TOURNAMENT_SLOTS}


def get_ff_account() -> dict | None:
    """Sotuvdagi Free Fire akkaunt ma'lumotini qaytaradi. Admin hali
    qo'shmagan bo'lsa - None qaytadi."""
    raw = get_setting(_FF_ACCOUNT_KEY, "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def set_ff_account(content_type: str, file_id: str = "", caption: str = "", buy_url: str = ""):
    set_setting(
        _FF_ACCOUNT_KEY,
        json.dumps(
            {
                "type": content_type,
                "file_id": file_id,
                "caption": caption,
                "buy_url": buy_url,
            }
        ),
    )


def delete_ff_account():
    set_setting(_FF_ACCOUNT_KEY, "")


# ---------------- Savol va Javob (Quiz) ----------------

def get_quiz_answered_today(user_id: int) -> int:
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT day, answered_count FROM quiz_progress WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if not row or row["day"] != today:
            return 0
        return row["answered_count"]


def increment_quiz_answered(user_id: int):
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT day, answered_count FROM quiz_progress WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if not row or row["day"] != today:
            conn.execute(
                "INSERT INTO quiz_progress (user_id, day, answered_count) VALUES (?, ?, 1) "
                "ON CONFLICT(user_id) DO UPDATE SET day = excluded.day, answered_count = 1",
                (user_id, today),
            )
        else:
            conn.execute(
                "UPDATE quiz_progress SET answered_count = answered_count + 1 WHERE user_id = ?",
                (user_id,),
            )


def _record_diamonds_earned(conn, user_id: int, amount: int):
    """Foydalanuvchi 💎 almaz ishlab olganda (yutuq, mukofot, bonus va h.k.)
    "Bugun ishlagan almazim" statistikasi uchun kunlik yig'indiga qo'shadi.
    Faqat musbat miqdorlar hisoblanadi (ayirishlar bu yerga kirmaydi)."""
    if amount <= 0:
        return
    today = date.today().isoformat()
    conn.execute(
        "INSERT INTO diamonds_earned_daily (user_id, day, earned) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, day) DO UPDATE SET earned = earned + excluded.earned",
        (user_id, today, amount),
    )


def get_diamonds_earned_today(user_id: int) -> int:
    """Foydalanuvchi bugun jami necha dona 💎 almaz ishlaganini qaytaradi
    (referal, o'yinlar, viktorina, bonuslar - barchasi hisobga olinadi)."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT earned FROM diamonds_earned_daily WHERE user_id = ? AND day = ?",
            (user_id, today),
        )
        row = cur.fetchone()
        return row["earned"] if row else 0


def add_quiz_diamonds(user_id: int, amount: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET diamonds = diamonds + excluded.diamonds",
            (user_id, amount),
        )
        _record_diamonds_earned(conn, user_id, amount)


def get_quiz_diamonds(user_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT diamonds FROM quiz_diamonds WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row["diamonds"] if row else 0


def deduct_quiz_diamonds(user_id: int, amount: int) -> int:
    """Foydalanuvchining almaz hisobidan 'amount' dona ayiradi (manfiy bo'lib
    ketmasligi uchun 0 dan pastga tushmaydi). Haqiqatda necha dona ayirilganini
    qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute("SELECT diamonds FROM quiz_diamonds WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        current = row["diamonds"] if row else 0
        actually_deducted = min(current, amount)
        new_value = current - actually_deducted
        conn.execute(
            "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET diamonds = excluded.diamonds",
            (user_id, new_value),
        )
        return actually_deducted


def deduct_diamonds_all_users() -> int:
    """Barcha foydalanuvchilarning 💎 almaz hisobini nolga tushiradi
    (ommaviy yechish - foydalanuvchilarga xabar yubormaydi, buni chaqiruvchi
    handler o'zi hal qiladi). Balansi 0 dan katta bo'lgan nechta
    foydalanuvchidan almaz olib tashlanganini qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) AS c FROM quiz_diamonds WHERE diamonds > 0"
        )
        affected = cur.fetchone()["c"]
        conn.execute("UPDATE quiz_diamonds SET diamonds = 0")
        return affected


def reset_quiz_diamonds(user_id: int):
    """Foydalanuvchi 'Tekin almaz'dan yig'gan almazlarini yechib olgach, 0 ga tushiradi."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, 0) "
            "ON CONFLICT(user_id) DO UPDATE SET diamonds = 0",
            (user_id,),
        )


def has_promo_credit(user_id: int) -> bool:
    """Foydalanuvchiga promo-almaz allaqachon berilganmi, tekshiradi."""
    with get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS promo_credits (user_id INTEGER PRIMARY KEY)"
        )
        cur = conn.execute("SELECT 1 FROM promo_credits WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None


def mark_promo_credited(user_id: int):
    """Foydalanuvchiga promo-almaz berilganini belgilaydi (qayta berilmasligi uchun)."""
    with get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS promo_credits (user_id INTEGER PRIMARY KEY)"
        )
        conn.execute(
            "INSERT OR IGNORE INTO promo_credits (user_id) VALUES (?)", (user_id,)
        )


def get_asked_question_indices(user_id: int) -> set:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT question_index FROM quiz_asked_questions WHERE user_id = ?", (user_id,)
        )
        return {row["question_index"] for row in cur.fetchall()}


def mark_question_asked(user_id: int, question_index: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO quiz_asked_questions (user_id, question_index) VALUES (?, ?)",
            (user_id, question_index),
        )


def reset_asked_questions(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM quiz_asked_questions WHERE user_id = ?", (user_id,))


# ---------------- Kunlik bonus ----------------

def claim_daily_bonus(user_id: int, amount: int) -> bool:
    """Agar bugun hali bonus olinmagan bo'lsa, hisobga qo'shadi va True qaytaradi."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT last_claim_date FROM bonus_claims WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if row and row["last_claim_date"] == today:
            return False
        conn.execute(
            "INSERT INTO bonus_claims (user_id, last_claim_date) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_claim_date = excluded.last_claim_date",
            (user_id, today),
        )
        _ensure_balance_row(conn, user_id)
        conn.execute(
            "UPDATE balances SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        return True


# ---------------- Hisob balansi ----------------

def get_balance(user_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row["balance"] if row else 0


def _ensure_balance_row(conn, user_id: int):
    conn.execute(
        "INSERT OR IGNORE INTO balances (user_id, balance) VALUES (?, 0)", (user_id,)
    )


def add_balance(user_id: int, amount: int):
    with get_conn() as conn:
        _ensure_balance_row(conn, user_id)
        conn.execute(
            "UPDATE balances SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )


# ==================== 💎 Referal orqali to'g'ridan-to'g'ri almaz ====================

# Har bir tasdiqlangan referal uchun ikkala tomonga ham beriladigan almaz.
REFERRAL_DIAMOND_REWARD = 5

# ⚠️ Jarima: do'st referal orqali qo'shilib, mukofot berilgach, agar
# quyidagi soat ichida (taxminan 1-2 kun) majburiy kanallardan chiqib
# ketsa - ikkalasining hisobidan ham shuncha 💎 ayiriladi.
REFERRAL_PENALTY_DIAMONDS = 2
REFERRAL_PENALTY_CHECK_HOURS = 36


def register_referral(referred_id: int, referrer_id: int) -> bool:
    """Yangi referal munosabatini ro'yxatga oladi (hali mukofot berilmagan
    holatda). O'z-o'ziga taklif yoki allaqachon ro'yxatga olingan bo'lsa
    False qaytaradi."""
    if referred_id == referrer_id:
        return False
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT referred_id FROM referrals WHERE referred_id = ?", (referred_id,)
        )
        if cur.fetchone():
            return False
        conn.execute(
            "INSERT INTO referrals (referred_id, referrer_id, credited, created_at) "
            "VALUES (?, ?, 0, ?)",
            (referred_id, referrer_id, datetime.utcnow().isoformat()),
        )
        return True


def credit_referral_if_pending(referred_id: int) -> int | None:
    """Foydalanuvchi majburiy obunani bajarganda chaqiriladi: agar u
    kimningdir referal havolasi orqali kirgan va hali mukofot berilmagan
    bo'lsa - ikkalasiga ham REFERRAL_DIAMOND_REWARD dona 💎 almaz beradi
    (faqat bir marta, to'g'ridan-to'g'ri, hech qanday oraliq birliksiz).
    Mukofot berilgan bo'lsa taklif qiluvchining user_id sini, aks holda
    None qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT referrer_id FROM referrals WHERE referred_id = ? AND credited = 0",
            (referred_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        referrer_id = row["referrer_id"]
        updated = conn.execute(
            "UPDATE referrals SET credited = 1, credited_at = ? "
            "WHERE referred_id = ? AND credited = 0",
            (datetime.utcnow().isoformat(), referred_id),
        )
        if updated.rowcount == 0:
            return None
        for uid in (referrer_id, referred_id):
            conn.execute(
                "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET diamonds = diamonds + excluded.diamonds",
                (uid, REFERRAL_DIAMOND_REWARD),
            )
            _record_diamonds_earned(conn, uid, REFERRAL_DIAMOND_REWARD)
        return referrer_id


def count_referrals(user_id: int) -> int:
    """Shu foydalanuvchi taklif qilgan va mukofot berilgan (obunasi
    tasdiqlangan) do'stlar sonini qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ? AND credited = 1",
            (user_id,),
        )
        row = cur.fetchone()
        return row["c"] if row else 0


def count_referral_links(user_id: int) -> int:
    """Shu foydalanuvchining referal havolasi orqali /start bosgan barcha
    foydalanuvchilar sonini (hali obunasi tasdiqlanmaganlar ham) qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        return row["c"] if row else 0


def get_penalties(user_id: int) -> int:
    """Foydalanuvchiga qo'llangan jarimalar sonini qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT penalties FROM apples WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row["penalties"] if row else 0


# ==================== ⚠️ Referal jarima tizimi ====================


def get_referral_admin_stats():
    """Admin uchun 💎 Almaz ishlash / Referal tizimi bo'yicha umumiy
    statistika: jami havola bosishlar, tasdiqlangan (mukofotli)
    referallar, hali jarima tekshiruvini kutayotganlar, barcha
    foydalanuvchilarning joriy jami 💎 almaz hisobi va jami qo'llangan
    jarima hodisalari (taxminan)."""
    with get_conn() as conn:
        total_links = conn.execute("SELECT COUNT(*) c FROM referrals").fetchone()["c"]
        total_credited = conn.execute(
            "SELECT COUNT(*) c FROM referrals WHERE credited = 1"
        ).fetchone()["c"]
        pending_check = conn.execute(
            "SELECT COUNT(*) c FROM referrals WHERE credited = 1 AND penalty_applied = 0"
        ).fetchone()["c"]
        total_diamonds = conn.execute(
            "SELECT COALESCE(SUM(diamonds), 0) s FROM quiz_diamonds"
        ).fetchone()["s"]
        # Har bir jarima hodisasi ikkala tomonga ham +1 penalties qo'shadi,
        # shu sabab yig'indini 2 ga bo'lib taxminiy hodisalar sonini olamiz.
        total_penalty_points = conn.execute(
            "SELECT COALESCE(SUM(penalties), 0) s FROM apples"
        ).fetchone()["s"]
    return {
        "total_links": total_links,
        "total_credited": total_credited,
        "pending_check": pending_check,
        "total_diamonds": total_diamonds,
        "total_penalty_events": total_penalty_points // 2,
    }


def get_pending_penalty_checks(older_than_hours: int = REFERRAL_PENALTY_CHECK_HOURS):
    """Mukofot berilgan (credited=1), hali jarima tekshiruvidan
    o'tmagan (penalty_applied=0) va mukofot berilganiga kamida
    `older_than_hours` soat bo'lgan referallar ro'yxatini qaytaradi:
    [(referred_id, referrer_id), ...]."""
    cutoff = (datetime.utcnow() - timedelta(hours=older_than_hours)).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT referred_id, referrer_id FROM referrals "
            "WHERE credited = 1 AND penalty_applied = 0 "
            "AND credited_at IS NOT NULL AND credited_at <= ?",
            (cutoff,),
        )
        return [(r["referred_id"], r["referrer_id"]) for r in cur.fetchall()]


def mark_penalty_checked(referred_id: int):
    """Referalni jarima tekshiruvidan o'tgan deb belgilaydi (jarima
    qo'llanganmi yoki yo'qmi - farqi yo'q, qayta tekshirilmasligi uchun)."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE referrals SET penalty_applied = 1 WHERE referred_id = ?",
            (referred_id,),
        )


def apply_referral_penalty(
    referred_id: int, referrer_id: int, amount: int = REFERRAL_PENALTY_DIAMONDS
):
    """Do'st majburiy kanaldan chiqib ketgani uchun ikkala tomondan ham
    `amount` dona 💎 almaz ayiradi (0 dan pastga tushmaydi) va jarima
    hisoblagichini oshiradi, so'ng referalni tekshirilgan deb belgilaydi."""
    with get_conn() as conn:
        for uid in (referred_id, referrer_id):
            cur = conn.execute(
                "SELECT diamonds FROM quiz_diamonds WHERE user_id = ?", (uid,)
            )
            row = cur.fetchone()
            current = row["diamonds"] if row else 0
            new_diamonds = max(0, current - amount)
            conn.execute(
                "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET diamonds = excluded.diamonds",
                (uid, new_diamonds),
            )
            conn.execute(
                "INSERT INTO apples (user_id, penalties) VALUES (?, 1) "
                "ON CONFLICT(user_id) DO UPDATE SET penalties = penalties + 1",
                (uid,),
            )
        conn.execute(
            "UPDATE referrals SET penalty_applied = 1 WHERE referred_id = ?",
            (referred_id,),
        )


def deduct_balance(user_id: int, amount: int) -> bool:
    """Agar mablag' yetarli bo'lsa yechib oladi va True qaytaradi."""
    with get_conn() as conn:
        _ensure_balance_row(conn, user_id)
        cur = conn.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        current = cur.fetchone()["balance"]
        if current < amount:
            return False
        conn.execute(
            "UPDATE balances SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id),
        )
        return True


# ---------------- To'lov cheklari (Hisobim to'ldirish) ----------------

def create_topup_request(user_id: int, amount: int, photo_file_id: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO topup_requests (user_id, amount, photo_file_id, status, created_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (user_id, amount, photo_file_id, now),
        )
        return cur.lastrowid


def get_topup_request(request_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM topup_requests WHERE id = ?", (request_id,))
        return cur.fetchone()


def update_topup_status(request_id: int, status: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE topup_requests SET status = ? WHERE id = ?", (status, request_id)
        )


# ---------------- 💘 Headshot Pro (pullik nastroyka) buyurtmalari ----------------

def create_hspro_order(user_id: int, method: str, amount: int, file_id: str, file_type: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO hspro_orders (user_id, method, amount, file_id, file_type, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (user_id, method, amount, file_id, file_type, now),
        )
        return cur.lastrowid


def get_hspro_order(order_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM hspro_orders WHERE id = ?", (order_id,))
        return cur.fetchone()


def update_hspro_order_status(order_id: int, status: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE hspro_orders SET status = ? WHERE id = ?", (status, order_id)
        )


def save_hspro_phone_model(order_id: int, user_id: int, phone_model: str):
    """'🔧 Nastroykani olish' bosilib, foydalanuvchi telefon modelini
    yozganda shu yerda saqlanadi (admin uchun tarix/hisobot sifatida)."""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO hspro_settings_requests (order_id, user_id, phone_model, created_at) "
            "VALUES (?, ?, ?, ?)",
            (order_id, user_id, phone_model, now),
        )


# ---------------- 🚫 Bloklangan foydalanuvchilar ----------------
# Blokdan chiqarilgan foydalanuvchi jadvaldan O'CHIRILMAYDI, faqat
# is_active = 0 qilib belgilanadi. Shunda admin panelidagi "Bloklanganlar"
# ro'yxatida u qoladi va admin uni qayta bloklay oladi.

def block_user(user_id: int):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO blocked_users (user_id, blocked_at, is_active, unblocked_at) "
            "VALUES (?, ?, 1, NULL) "
            "ON CONFLICT(user_id) DO UPDATE SET "
            "blocked_at = excluded.blocked_at, is_active = 1, unblocked_at = NULL",
            (user_id, now),
        )


def unblock_user(user_id: int):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE blocked_users SET is_active = 0, unblocked_at = ? "
            "WHERE user_id = ?",
            (now, user_id),
        )


def is_user_blocked(user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM blocked_users WHERE user_id = ? AND is_active = 1",
            (user_id,),
        )
        return cur.fetchone() is not None


def count_blocked_users() -> tuple[int, int]:
    """(hozir bloklangan, ro'yxatdagi jami) sonini qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active, "
            "COUNT(*) AS total FROM blocked_users"
        )
        row = cur.fetchone()
        return int(row["active"]), int(row["total"])


def get_blocked_users(limit: int = 10, offset: int = 0) -> list:
    """Bloklanganlar ro'yxati (avval hozir bloklanganlar, keyin blokdan
    chiqarilganlar; ichida eng yangisi birinchi). Har bir qatorda:
    user_id, blocked_at, is_active, unblocked_at, first_name, username."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT b.user_id, b.blocked_at, b.is_active, b.unblocked_at, "
            "u.first_name, u.username "
            "FROM blocked_users b LEFT JOIN users u ON u.user_id = b.user_id "
            "ORDER BY b.is_active DESC, b.blocked_at DESC "
            "LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cur.fetchall()


def get_blocked_user(user_id: int):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT b.user_id, b.blocked_at, b.is_active, b.unblocked_at, "
            "u.first_name, u.username "
            "FROM blocked_users b LEFT JOIN users u ON u.user_id = b.user_id "
            "WHERE b.user_id = ?",
            (user_id,),
        )
        return cur.fetchone()


# ---------------- Almaz buyurtmalari ----------------

def create_diamond_order(user_id: int, package_label: str, price: int) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO diamond_orders (user_id, package_label, price, status, created_at) "
            "VALUES (?, ?, ?, 'awaiting_id', ?)",
            (user_id, package_label, price, now),
        )
        return cur.lastrowid


def get_diamond_order(order_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM diamond_orders WHERE id = ?", (order_id,))
        return cur.fetchone()


def set_diamond_order_ff_id(order_id: int, ff_id: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE diamond_orders SET ff_id = ?, status = 'awaiting_delivery' WHERE id = ?",
            (ff_id, order_id),
        )


def update_diamond_order_status(order_id: int, status: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE diamond_orders SET status = ? WHERE id = ?", (status, order_id)
        )


# ---------------- 🌙 Bonus Almaz (kunlik almaz bonusi) ----------------

DIAMOND_BONUS_AMOUNT = 3


def claim_diamond_bonus(user_id: int, amount: int = DIAMOND_BONUS_AMOUNT) -> bool:
    """Agar bugun hali 'Bonus Almaz' olinmagan bo'lsa, almaz qo'shadi va True qaytaradi."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT last_claim_date FROM diamond_bonus_claims WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if row and row["last_claim_date"] == today:
            return False
        conn.execute(
            "INSERT INTO diamond_bonus_claims (user_id, last_claim_date) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_claim_date = excluded.last_claim_date",
            (user_id, today),
        )
        conn.execute(
            "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET diamonds = diamonds + excluded.diamonds",
            (user_id, amount),
        )
        _record_diamonds_earned(conn, user_id, amount)
        return True


# ---------------- 💵 Kunlik Bonus (har 24 soatda avtomatik 20 so'm) ----------------

DAILY_MONEY_BONUS_AMOUNT = 20
DAILY_MONEY_BONUS_SECONDS = 24 * 60 * 60


def try_give_daily_money_bonus(user_id: int, amount: int = DAILY_MONEY_BONUS_AMOUNT):
    """Agar oxirgi berilgan vaqtdan beri 24 soat o'tgan bo'lsa (yoki umuman berilmagan
    bo'lsa), foydalanuvchi balansiga avtomatik ravishda `amount` qo'shadi.
    Qaytaradi: (berildimi: bool, keyingi bonusgacha qolgan soniya: int)."""
    now = datetime.utcnow()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT last_claim_at FROM daily_money_bonus WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if row and row["last_claim_at"]:
            last = datetime.fromisoformat(row["last_claim_at"])
            elapsed = (now - last).total_seconds()
            if elapsed < DAILY_MONEY_BONUS_SECONDS:
                return False, int(DAILY_MONEY_BONUS_SECONDS - elapsed)

        conn.execute(
            "INSERT INTO daily_money_bonus (user_id, last_claim_at) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_claim_at = excluded.last_claim_at",
            (user_id, now.isoformat()),
        )
        _ensure_balance_row(conn, user_id)
        conn.execute(
            "UPDATE balances SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        return True, DAILY_MONEY_BONUS_SECONDS


# ==================== 🎮 Mini O'yinlar ====================

GAME_COOLDOWN_SECONDS = 24 * 60 * 60  # 24 soat


def check_game_cooldown(user_id: int, game_key: str):
    """Mukofotli rejimda o'yin 24 soatda 1 marta o'ynaladi.
    Qaytaradi: (ruxsat_bormi: bool, qolgan_soniya: int)"""
    now = datetime.utcnow()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT last_played_at FROM game_cooldowns WHERE user_id = ? AND game_key = ?",
            (user_id, game_key),
        )
        row = cur.fetchone()
        if row and row["last_played_at"]:
            last = datetime.fromisoformat(row["last_played_at"])
            elapsed = (now - last).total_seconds()
            if elapsed < GAME_COOLDOWN_SECONDS:
                return False, int(GAME_COOLDOWN_SECONDS - elapsed)
        return True, 0


def set_game_cooldown(user_id: int, game_key: str):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO game_cooldowns (user_id, game_key, last_played_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, game_key) DO UPDATE SET last_played_at = excluded.last_played_at",
            (user_id, game_key, now),
        )


def give_game_reward(user_id: int, amount: int = 10):
    """Mukofotli o'yinda g'alaba qozonilganda Almaz balansiga qo'shadi
    (Tekin almaz bilan bir xil hisobdan foydalaniladi)."""
    add_quiz_diamonds(user_id, amount)


# ==================== 🔥 Qiyin O'yinlar (10 ta FF mavzusidagi o'yin) ====================

def _record_diamonds_lost(conn, user_id: int, amount: int):
    """Foydalanuvchi o'yinda yutqazganda (jarima) \"Bugun minus bo'lgan\"
    statistikasi uchun kunlik yig'indiga qo'shadi."""
    if amount <= 0:
        return
    today = date.today().isoformat()
    conn.execute(
        "INSERT INTO diamonds_lost_daily (user_id, day, lost) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, day) DO UPDATE SET lost = lost + excluded.lost",
        (user_id, today, amount),
    )


def get_diamonds_lost_today(user_id: int) -> int:
    """Foydalanuvchi bugun jami necha dona 💎 almazni o'yinlarda yutqazganini
    qaytaradi."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT lost FROM diamonds_lost_daily WHERE user_id = ? AND day = ?",
            (user_id, today),
        )
        row = cur.fetchone()
        return row["lost"] if row else 0


def apply_hard_game_penalty(user_id: int, amount: int) -> int:
    """Qiyin o'yinda yutqazganda hisobdan `amount` dona Almaz yechadi va buni
    kunlik \"minus\" statistikasiga yozadi. Haqiqatda necha dona yechilganini
    qaytaradi (balans yetarli bo'lmasa, borini yechadi)."""
    deducted = deduct_quiz_diamonds(user_id, amount)
    if deducted > 0:
        with get_conn() as conn:
            _record_diamonds_lost(conn, user_id, deducted)
    return deducted


def check_hard_game_cooldown(user_id: int, game_key: str):
    """Har bir o'yin (game_key) uchun ALOHIDA kutish vaqtini tekshiradi -
    bitta o'yinni o'ynash faqat o'sha o'yinni bloklaydi, qolgan 9 ta o'yin
    band bo'lib qolmaydi. Qaytaradi: (ruxsat_bormi: bool, qolgan_soniya: int)."""
    now = datetime.utcnow()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT next_allowed_at FROM hard_games_cooldown WHERE user_id = ? AND game_key = ?",
            (user_id, game_key),
        )
        row = cur.fetchone()
        if row and row["next_allowed_at"]:
            next_allowed = datetime.fromisoformat(row["next_allowed_at"])
            remaining = (next_allowed - now).total_seconds()
            if remaining > 0:
                return False, int(remaining)
        return True, 0


def set_hard_game_cooldown(user_id: int, game_key: str, hours: float):
    """Berilgan o'yin (game_key) uchun keyingi o'ynash vaqtini `hours`
    soatdan keyinga o'rnatadi - faqat shu o'yinga tegishli, qolgan
    o'yinlarga ta'sir qilmaydi (o'yin ochilgan payt darhol chaqiriladi)."""
    next_allowed_at = (datetime.utcnow() + timedelta(hours=hours)).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO hard_games_cooldown (user_id, game_key, next_allowed_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, game_key) DO UPDATE SET next_allowed_at = excluded.next_allowed_at",
            (user_id, game_key, next_allowed_at),
        )


# ==================== 💣 Portlovchi almaz (tavakkal o'yinlari) ====================

RISK_ROUND_TTL_SECONDS = 120  # Raund ochilgach tanlov qilish uchun berilgan vaqt


def risk_create_round(user_id: int, game_key: str, stake: int) -> int:
    """Yangi raund ochadi (almaz HALI yechilmaydi). Foydalanuvchining eski
    ochiq raundlari bekor qilinadi - bir vaqtda faqat bitta faol raund."""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE risk_rounds SET state = 'expired', settled_at = ? "
            "WHERE user_id = ? AND state = 'open'",
            (now, user_id),
        )
        cur = conn.execute(
            "INSERT INTO risk_rounds (user_id, game_key, stake, state, created_at) "
            "VALUES (?, ?, ?, 'open', ?)",
            (user_id, game_key, stake, now),
        )
        return cur.lastrowid


def risk_get_round(round_id: int, user_id: int):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM risk_rounds WHERE id = ? AND user_id = ?", (round_id, user_id)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def risk_cancel_round(round_id: int, user_id: int) -> bool:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE risk_rounds SET state = 'cancelled', settled_at = ? "
            "WHERE id = ? AND user_id = ? AND state = 'open'",
            (now, round_id, user_id),
        )
        return cur.rowcount == 1


def risk_settle_round(round_id: int, user_id: int, choice: int, won: bool,
                      prize: int | None = None) -> dict:
    """Raundni ATOMAR tarzda yakunlaydi: raund faqat bir marta 'open' holatdan
    chiqadi, shu tranzaksiya ichida almaz qo'shiladi yoki ayriladi.
    Yutsa `prize` dona (berilmasa - stavka miqdorida) qo'shiladi, yutqazsa
    raund stavkasi (stake) ayriladi.

    Qaytaradi: {"status": ..., ...}
      status = "won" | "lost"  -> {"stake", "prize", "balance"}
      status = "closed"        -> raund allaqachon yakunlangan (qayta bosish)
      status = "expired"       -> tanlov vaqti o'tib ketgan (almaz o'zgarmadi)
      status = "insufficient"  -> balans yetarli emas (almaz o'zgarmadi)
      status = "missing"       -> raund topilmadi
    """
    now_dt = datetime.utcnow()
    now = now_dt.isoformat()
    with get_conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM risk_rounds WHERE id = ? AND user_id = ?", (round_id, user_id)
        ).fetchone()
        if not row:
            return {"status": "missing"}
        if row["state"] != "open":
            return {"status": "closed"}

        created = datetime.fromisoformat(row["created_at"])
        if (now_dt - created).total_seconds() > RISK_ROUND_TTL_SECONDS:
            conn.execute(
                "UPDATE risk_rounds SET state = 'expired', settled_at = ? WHERE id = ?",
                (now, round_id),
            )
            return {"status": "expired"}

        stake = int(row["stake"])
        bal_row = conn.execute(
            "SELECT diamonds FROM quiz_diamonds WHERE user_id = ?", (user_id,)
        ).fetchone()
        balance = bal_row["diamonds"] if bal_row else 0
        if balance < stake:
            conn.execute(
                "UPDATE risk_rounds SET state = 'void', settled_at = ? WHERE id = ?",
                (now, round_id),
            )
            return {"status": "insufficient", "balance": balance, "stake": stake}

        win_amount = int(prize) if prize is not None else stake
        if won:
            new_balance = balance + win_amount
            _record_diamonds_earned(conn, user_id, win_amount)
        else:
            new_balance = balance - stake
            _record_diamonds_lost(conn, user_id, stake)

        conn.execute(
            "INSERT INTO quiz_diamonds (user_id, diamonds) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET diamonds = excluded.diamonds",
            (user_id, new_balance),
        )
        conn.execute(
            "UPDATE risk_rounds SET state = ?, choice = ?, settled_at = ? WHERE id = ?",
            ("won" if won else "lost", choice, now, round_id),
        )
        return {
            "status": "won" if won else "lost",
            "stake": stake,
            "prize": win_amount,
            "balance": new_balance,
        }


# ---- Raqamni top o'yini uchun holat ----

def start_number_game(user_id: int, target: int, tries: int, mode: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO number_game_state (user_id, target, tries_left, mode) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET target = excluded.target, "
            "tries_left = excluded.tries_left, mode = excluded.mode",
            (user_id, target, tries, mode),
        )


def get_number_game(user_id: int):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT target, tries_left, mode FROM number_game_state WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"target": row["target"], "tries_left": row["tries_left"], "mode": row["mode"]}


def decrement_number_game_try(user_id: int) -> int:
    with get_conn() as conn:
        conn.execute(
            "UPDATE number_game_state SET tries_left = tries_left - 1 WHERE user_id = ?",
            (user_id,),
        )
        cur = conn.execute(
            "SELECT tries_left FROM number_game_state WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row["tries_left"] if row else 0


def clear_number_game(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM number_game_state WHERE user_id = ?", (user_id,))


# ==================== 🔄 Avtomatik menyu yangilanishi ====================

def get_menu_version(user_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT version FROM user_menu_version WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row["version"] if row else 0


def set_menu_version(user_id: int, version: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_menu_version (user_id, version) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET version = excluded.version",
            (user_id, version),
        )


# ==================== 🏆 Yutiqni chiqarish (Pul) ====================

def create_cash_withdraw_request(user_id: int, amount: int) -> int:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO cash_withdraw_requests (user_id, amount, status, created_at) "
            "VALUES (?, ?, 'pending', ?)",
            (user_id, amount, now),
        )
        return cur.lastrowid


# ==================== 🎵 Musiqa yaratish (kunlik limit) ====================

def get_music_generated_today(user_id: int) -> int:
    """Foydalanuvchi BUGUN nechta musiqa so'rovi yuborganini qaytaradi."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT day, count FROM music_generations WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if not row or row["day"] != today:
            return 0
        return row["count"]


def increment_music_generated(user_id: int):
    """Foydalanuvchining bugungi musiqa so'rovlar sonini +1 oshiradi."""
    today = date.today().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT day, count FROM music_generations WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if not row or row["day"] != today:
            conn.execute(
                "INSERT INTO music_generations (user_id, day, count) VALUES (?, ?, 1) "
                "ON CONFLICT(user_id) DO UPDATE SET day = excluded.day, count = 1",
                (user_id, today),
            )
        else:
            conn.execute(
                "UPDATE music_generations SET count = count + 1 WHERE user_id = ?",
                (user_id,),
            )


# ==================== 📢 Bajarilgan buyurtmalar raqamlash (kanal uchun) ====================

def get_next_order_number() -> int:
    """@buyurtmalar_ff kanaliga yuboriladigan har bir 'N# buyurtma bajarildi'
    xabari uchun ketma-ket raqam beradi (app_settings jadvalida saqlanadi,
    shuning uchun bot qayta ishga tushirilsa ham hisob yo'qolmaydi)."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT value FROM app_settings WHERE key = 'order_counter'"
        )
        row = cur.fetchone()
        try:
            current = int(row["value"]) if row and row["value"] else 0
        except (TypeError, ValueError):
            current = 0
        new_value = current + 1
        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES ('order_counter', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(new_value),),
        )
        return new_value


# ==================== 👑 Pro obuna (musiqa limiti uchun) ====================

def is_pro_user(user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM pro_users WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None


def set_pro_user(user_id: int, is_pro: bool = True):
    with get_conn() as conn:
        if is_pro:
            now = datetime.utcnow().isoformat()
            conn.execute(
                "INSERT INTO pro_users (user_id, granted_at) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET granted_at = excluded.granted_at",
                (user_id, now),
            )
        else:
            conn.execute("DELETE FROM pro_users WHERE user_id = ?", (user_id,))


# ==================== 🏆 Top foydalanuvchilar reytingi ====================
# Ikkita reyting yuritiladi: eng ko'p referal olib kelganlar va eng ko'p
# 💎 almaz yig'ganlar. Natija leaderboard_cache jadvalida saqlanadi va
# bot.py dagi kunlik JobQueue vazifasi orqali har kuni avtomatik
# yangilanadi (foydalanuvchi tugmani bosganda esa faqat shu keshdan
# o'qiladi - tezkor javob uchun).

LEADERBOARD_TOP_LIMIT = 10


def _display_name(first_name: str | None, username: str | None) -> str:
    name = (first_name or "").strip() or "Foydalanuvchi"
    if username:
        return f"{name} (@{username})"
    return name


def get_top_referrers(limit: int = LEADERBOARD_TOP_LIMIT) -> list[dict]:
    """Eng ko'p referal olib kelgan (mukofoti tasdiqlangan do'stlar soni
    bo'yicha) foydalanuvchilarni qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT r.referrer_id AS user_id,
                   COUNT(*) AS cnt,
                   u.first_name AS first_name,
                   u.username AS username
            FROM referrals r
            LEFT JOIN users u ON u.user_id = r.referrer_id
            WHERE r.credited = 1
            GROUP BY r.referrer_id
            ORDER BY cnt DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {
                "user_id": row["user_id"],
                "name": _display_name(row["first_name"], row["username"]),
                "value": row["cnt"],
            }
            for row in rows
        ]


def get_top_diamond_holders(limit: int = LEADERBOARD_TOP_LIMIT) -> list[dict]:
    """Hisobida eng ko'p 💎 almazi bor foydalanuvchilarni qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT q.user_id AS user_id,
                   q.diamonds AS diamonds,
                   u.first_name AS first_name,
                   u.username AS username
            FROM quiz_diamonds q
            LEFT JOIN users u ON u.user_id = q.user_id
            WHERE q.diamonds > 0
            ORDER BY q.diamonds DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {
                "user_id": row["user_id"],
                "name": _display_name(row["first_name"], row["username"]),
                "value": row["diamonds"],
            }
            for row in rows
        ]


def get_top_money_holders(limit: int = LEADERBOARD_TOP_LIMIT) -> list[dict]:
    """Hisobida eng ko'p 💰 puli (so'm) bor foydalanuvchilarni qaytaradi."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT b.user_id AS user_id,
                   b.balance AS balance,
                   u.first_name AS first_name,
                   u.username AS username
            FROM balances b
            LEFT JOIN users u ON u.user_id = b.user_id
            WHERE b.balance > 0
            ORDER BY b.balance DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {
                "user_id": row["user_id"],
                "name": _display_name(row["first_name"], row["username"]),
                "value": row["balance"],
            }
            for row in rows
        ]


def refresh_leaderboard_cache():
    """Uchala reytingni (referal, almaz va pul) qayta hisoblab, keshga
    yozadi. Bot ishga tushganda, har kuni (JobQueue orqali, bot.py) va
    admin "🔄 Top yangilash" tugmasini bosganda chaqiriladi."""
    now = datetime.utcnow().isoformat()
    top_referrers = get_top_referrers()
    top_diamonds = get_top_diamond_holders()
    top_money = get_top_money_holders()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO leaderboard_cache (cache_key, data, updated_at) "
            "VALUES ('top_money', ?, ?) "
            "ON CONFLICT(cache_key) DO UPDATE SET data = excluded.data, "
            "updated_at = excluded.updated_at",
            (json.dumps(top_money), now),
        )
        conn.execute(
            "INSERT INTO leaderboard_cache (cache_key, data, updated_at) "
            "VALUES ('top_referrers', ?, ?) "
            "ON CONFLICT(cache_key) DO UPDATE SET data = excluded.data, "
            "updated_at = excluded.updated_at",
            (json.dumps(top_referrers), now),
        )
        conn.execute(
            "INSERT INTO leaderboard_cache (cache_key, data, updated_at) "
            "VALUES ('top_diamonds', ?, ?) "
            "ON CONFLICT(cache_key) DO UPDATE SET data = excluded.data, "
            "updated_at = excluded.updated_at",
            (json.dumps(top_diamonds), now),
        )
    return top_referrers, top_diamonds, top_money


def resolve_user(raw: str):
    """Admin kiritgan matn bo'yicha foydalanuvchini topadi.

    Qabul qilinadi:
      - Telegram ID (faqat raqam):  123456789
      - username:                   @ali_ff  yoki  ali_ff
      - havola:                     https://t.me/ali_ff  yoki  t.me/ali_ff

    Topilsa users jadvalidagi qator (row), topilmasa None qaytaradi.
    ID bo'yicha qidirilganda foydalanuvchi bazada bo'lmasa ham ishlash
    imkoni bo'lishi uchun chaqiruvchi tomonda alohida tekshiriladi."""
    clean = (raw or "").strip()
    if not clean:
        return None
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):]
            break
    clean = clean.lstrip("@").strip()
    if not clean:
        return None
    if clean.isdigit():
        return get_user(int(clean))
    return get_user_by_username(clean)


def parse_user_id(raw: str) -> int | None:
    """Matn faqat raqamlardan iborat bo'lsa, uni Telegram ID sifatida
    qaytaradi. Aks holda None. (Bazada hali yo'q foydalanuvchiga ham
    almaz/pul berish yoki bloklash uchun kerak.)"""
    clean = (raw or "").strip().replace(" ", "")
    return int(clean) if clean.isdigit() else None


def get_cached_leaderboard(cache_key: str) -> tuple[list, str | None]:
    """cache_key: 'top_referrers', 'top_diamonds' yoki 'top_money'. Keshda mavjud bo'lsa
    (ro'yxat, oxirgi_yangilanish_vaqti) qaytaradi, aks holda ([], None)."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT data, updated_at FROM leaderboard_cache WHERE cache_key = ?",
            (cache_key,),
        )
        row = cur.fetchone()
        if not row or not row["data"]:
            return [], None
        try:
            data = json.loads(row["data"])
        except (TypeError, ValueError):
            data = []
        return data, row["updated_at"]
