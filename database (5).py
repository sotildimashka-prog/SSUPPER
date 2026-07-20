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
