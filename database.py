"""
SQLite ma'lumotlar bazasi bilan ishlash moduli.
GitHub'da qayta deploy qilinganda ma'lumotlar o'chib ketmasligi uchun
DB fayli persistent volume (Railway Volume) ga ulanishi tavsiya etiladi -
buni README.md faylida batafsil tushuntirilgan.
"""

import sqlite3
from datetime import date, datetime
from contextlib import contextmanager

from config import DB_PATH


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
            CREATE TABLE IF NOT EXISTS daily_bonus (
                user_id INTEGER PRIMARY KEY,
                last_claim TEXT
            )
            """
        )


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


# ---------------- Kunlik bonus (Hisobim -> Bonus) ----------------

def get_last_bonus_claim(user_id: int):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT last_claim FROM daily_bonus WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row["last_claim"] if row else None


def set_bonus_claim(user_id: int, day: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO daily_bonus (user_id, last_claim) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_claim = excluded.last_claim",
            (user_id, day),
        )
