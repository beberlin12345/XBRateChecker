"""
Run this on a schedule (GitHub Actions cron, etc) to pull a fresh snapshot
of quotes across all configured corridors and amount tiers.

    python collect.py
"""

import time

from config import AMOUNT_TIERS, CORRIDORS
from db import get_conn, insert_snapshot
from providers import remitly

# seconds to wait between requests, be polite to avoid rate limiting / bot detection
REQUEST_DELAY = 8

# add: from providers import wise, western_union   once those are implemented


def collect_remitly(conn):
    for corridor_label, cfg in CORRIDORS.items():
        conduit = cfg.get("remitly_conduit")
        if not conduit:
            print(f"[skip] no remitly conduit configured for {corridor_label}")
            continue

        for amount in AMOUNT_TIERS:
            row = remitly.get_quote(conduit, amount)
            if row is None:
                time.sleep(REQUEST_DELAY)
                continue
            row["corridor"] = corridor_label  # use our own label, not the raw conduit string
            insert_snapshot(conn, row)
            print(
                f"[remitly] {corridor_label} @ ${amount}: "
                f"effective_rate={row['effective_rate']:.4f} "
                f"fee=${row['fee']} promo={row['promo_code']}"
            )
            time.sleep(REQUEST_DELAY)


def main():
    conn = get_conn()
    try:
        collect_remitly(conn)
        # collect_wise(conn)
        # collect_western_union(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
