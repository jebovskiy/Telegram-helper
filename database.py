import sqlite3
from datetime import date, datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            contacts INTEGER DEFAULT 0,
            messages_sent INTEGER DEFAULT 0,
            responses INTEGER DEFAULT 0,
            calls INTEGER DEFAULT 0,
            money_earned REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            adj_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            focus_area TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_daily_log(user_id: int, log_date: date, contacts: int,
                   messages_sent: int, responses: int, calls: int,
                   money_earned: float, notes: str = ""):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO daily_log (user_id, log_date, contacts, messages_sent,
                               responses, calls, money_earned, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, log_date.isoformat(), contacts, messages_sent,
          responses, calls, money_earned, notes))

    conn.commit()
    conn.close()


def get_daily_log(user_id: int, log_date: date):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM daily_log
        WHERE user_id = ? AND log_date = ?
    """, (user_id, log_date.isoformat()))

    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_logs(user_id: int):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM daily_log
        WHERE user_id = ?
        ORDER BY log_date DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_earned(user_id: int):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT COALESCE(SUM(money_earned), 0) as total
        FROM daily_log
        WHERE user_id = ?
    """, (user_id,))

    row = c.fetchone()
    conn.close()
    return row["total"] if row else 0.0


def get_total_stats(user_id: int):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT
            COALESCE(SUM(contacts), 0) as total_contacts,
            COALESCE(SUM(messages_sent), 0) as total_messages,
            COALESCE(SUM(responses), 0) as total_responses,
            COALESCE(SUM(calls), 0) as total_calls,
            COALESCE(SUM(money_earned), 0) as total_money,
            COUNT(*) as days_logged
        FROM daily_log
        WHERE user_id = ?
    """, (user_id,))

    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def save_adjustment(user_id: int, adj_date: date, reason: str, focus_area: str):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO adjustments (user_id, adj_date, reason, focus_area)
        VALUES (?, ?, ?, ?)
    """, (user_id, adj_date.isoformat(), reason, focus_area))

    conn.commit()
    conn.close()


def get_adjustment(user_id: int, adj_date: date):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM adjustments
        WHERE user_id = ? AND adj_date = ?
    """, (user_id, adj_date.isoformat()))

    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_user(user_id: int, username: str = "", first_name: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
    """, (user_id, username or "", first_name or ""))
    conn.commit()
    conn.close()


def get_registered_user():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users ORDER BY registered_at DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row["user_id"] if row else None
