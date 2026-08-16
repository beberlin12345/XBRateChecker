import sqlite3
from datetime import datetime, timezone

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    hour_of_day INTEGER NOT NULL,
    provider TEXT NOT NULL,
    corridor TEXT NOT NULL,
    send_amount REAL NOT NULL,
    receive_amount REAL,
    standard_rate REAL,
    welcome_rate REAL,
    welcome_cap_usd REAL,
    effective_rate REAL,
    fee REAL,
    fee_discount REAL,
    net_fee REAL,
    total_charge REAL,
    pay_out_method TEXT,
    promo_code TEXT,
    promo_bps REAL,
    raw_response TEXT
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def insert_snapshot(conn, row: dict):
    """
    row must contain keys matching the snapshots columns (timestamp/day_of_week/
    hour_of_day are filled in automatically if missing).
    """
    now = datetime.now(timezone.utc)
    row.setdefault("timestamp", now.isoformat())
    row.setdefault("day_of_week", now.strftime("%A"))
    row.setdefault("hour_of_day", now.hour)

    columns = [
        "timestamp", "day_of_week", "hour_of_day", "provider", "corridor",
        "send_amount", "receive_amount", "standard_rate", "welcome_rate",
        "welcome_cap_usd", "effective_rate", "fee", "fee_discount", "net_fee",
        "total_charge", "pay_out_method", "promo_code", "promo_bps", "raw_response",
    ]
    values = [row.get(col) for col in columns]
    placeholders = ", ".join(["?"] * len(columns))
    conn.execute(
        f"INSERT INTO snapshots ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
