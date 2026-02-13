"""
Ripple (XRP Ledger) snapshot extraction.
This module fetches monthly account state snapshots from xrplcluster.com,
stores them in SQLite, and exports CSVs. Balances are stored in drops (int).
"""

import requests
import sqlite3
import csv
import os
import logging
import time
from datetime import datetime, timezone, timedelta

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
RPC_URL = "https://xrplcluster.com"
OUTPUT_DIR = "/mnt/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DB_FILE = os.path.join(OUTPUT_DIR, "balances.db")

logging.basicConfig(
    filename=os.path.join(OUTPUT_DIR, "xrpl_cluster.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

session = requests.Session()
# ----------------------------------------------------------------------
# RPC utilities
# ----------------------------------------------------------------------


def rpc_call(payload, retries: int = 3, delay: float = 0.4) -> dict:
    """Perform an RPC call with retries."""
    for attempt in range(retries):
        try:
            resp = session.post(RPC_URL, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            time.sleep(delay)
            return result
        except Exception as e:
            logging.warning(f"RPC call failed (attempt {attempt+1}): {e}")
            time.sleep(1)
    raise RuntimeError("RPC call failed after retries")


def get_complete_ledger_range() -> tuple[int, int]:
    """
    Returns (min_index, max_index) from server_info.complete_ledgers.
    """
    result = rpc_call({"method": "server_info", "params": [{}]})
    complete = result["result"]["info"]["complete_ledgers"]
    # Parse ranges and take overall min/max
    min_idx, max_idx = None, None
    for part in complete.split(","):
        start_idx, end_idx = map(int, part.split("-"))
        min_idx = start_idx if min_idx is None else min(min_idx, start_idx)
        max_idx = end_idx if max_idx is None else max(max_idx, end_idx)
    return min_idx, max_idx


def get_ledger_close_time(ledger_index: int) -> datetime:
    """Return the UTC close time of a given ledger index."""
    result = rpc_call(
        {
            "method": "ledger",
            "params": [
                {
                    "ledger_index": ledger_index,
                    "transactions": False,
                    "accounts": False,
                    "full": False,
                    "expand": False,
                }
            ],
        }
    )
    ledger = result["result"]["ledger"]

    ct_human = ledger.get("close_time_human")
    if ct_human and ct_human.endswith(" UTC"):
        clean = ct_human.replace(" UTC", "")
        # If fractional seconds are present, strip them off
        if "." in clean:
            clean = clean.split(".")[0]
        return datetime.strptime(clean, "%Y-%b-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )

    # Fallback: use ripple epoch seconds
    ct_ripple = ledger.get("close_time")
    if isinstance(ct_ripple, int):
        ripple_epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
        return ripple_epoch + timedelta(seconds=ct_ripple)

    raise ValueError("close_time not available in ledger response")


# ----------------------------------------------------------------------
# Database utilities
# ----------------------------------------------------------------------


def init_db(year, month):
    """Initialize SQLite tables for a given snapshot month."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    table_name = f"accounts_{year}_{month:02d}"
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            account TEXT PRIMARY KEY,
            balance TEXT
        )
    """
    )
    # Progress table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            year INTEGER,
            month INTEGER,
            ledger_index INTEGER,
            last_marker TEXT,
            PRIMARY KEY (year, month)
        )
    """
    )
    conn.commit()
    return conn, table_name


def get_exact_snapshot_ledger_index(year: int, month: int) -> int:
    """
    Find the first validated ledger whose close_time >= first day of next month (UTC).
    This is the canonical anchor for the prior month's end-of-month snapshot.
    """
    # Target: first day of next month at 00:00:00 UTC
    next_month_dt = datetime(year, month, 1, tzinfo=timezone.utc) + timedelta(days=32)
    target = datetime(next_month_dt.year, next_month_dt.month, 1, tzinfo=timezone.utc)

    lo, hi = get_complete_ledger_range()

    ans = None
    while lo <= hi:
        mid = (lo + hi) // 2
        ct = get_ledger_close_time(mid)
        if ct >= target:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1

    if ans is None:
        raise RuntimeError(
            "No ledger found at or after the target time within complete range"
        )
    return ans


def save_progress(conn, year, month, ledger_index, marker):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO progress (year, month, ledger_index, last_marker)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE
        SET ledger_index=excluded.ledger_index,
            last_marker=excluded.last_marker
    """,
        (year, month, ledger_index, marker),
    )
    conn.commit()


def load_progress(conn, year, month):
    cur = conn.cursor()
    cur.execute(
        "SELECT ledger_index, last_marker FROM progress WHERE year=? AND month=?",
        (year, month),
    )
    row = cur.fetchone()
    return row if row else (None, None)


def upsert_balance(conn, table_name, account, balance):
    """Insert or update account balance in the month’s table."""
    cur = conn.cursor()
    cur.execute(
        f"""
        INSERT INTO {table_name} (account, balance)
        VALUES (?, ?)
        ON CONFLICT(account) DO UPDATE SET balance=excluded.balance
    """,
        (account, balance),
    )


# ----------------------------------------------------------------------
# Snapshots
# ----------------------------------------------------------------------


def fetch_snapshot(ledger_index, conn, table_name, year, month):
    payload = {
        "method": "ledger_data",
        "params": [{"ledger_index": ledger_index, "type": "account", "limit": 1000}],
    }

    # Resume from last marker if available
    last_ledger, last_marker = load_progress(conn, year, month)
    if last_marker:
        payload["params"][0]["marker"] = last_marker
        logging.info(f"Resuming from marker {last_marker}")

    total_accounts = 0

    while True:
        result = rpc_call(payload)
        state = result.get("result", {}).get("state", [])
        for entry in state:
            if entry["LedgerEntryType"] == "AccountRoot":
                account = entry["Account"]
                balance_drops = int(entry["Balance"])
                # balance_xrp = f"{balance_drops / 1_000_000:.6f}"
                # upsert_balance(conn, table_name, account, balance_xrp)
                upsert_balance(conn, table_name, account, balance_drops)
                total_accounts += 1
                if total_accounts % 1000 == 0:
                    logging.info(
                        f"{year} - {month} Total accounts saved: {total_accounts}"
                    )

        # Commit after each page
        conn.commit()

        marker = result.get("result", {}).get("marker")
        save_progress(conn, year, month, ledger_index, marker)

        if not marker:
            break
        payload["params"][0]["marker"] = marker

    logging.info(f"Snapshot complete. Final total accounts saved: {total_accounts}")


def export_month(year: int, month: int):

    # Resolve exact anchor: first validated ledger of the next month (UTC)
    ledger_index = get_exact_snapshot_ledger_index(year, month)
    close_time = get_ledger_close_time(ledger_index)

    logging.info(
        f"Fetching snapshot for {year}-{month:02d} at ledger {ledger_index} (close_time {close_time.isoformat()})"
    )

    # Compute the first day of the next month
    snapshot_date = datetime(year, month, 1)
    next_month_date = snapshot_date.replace(day=28) + timedelta(days=4)
    next_month_date = next_month_date.replace(day=1)

    filename = os.path.join(
        OUTPUT_DIR, f"xrpl_{next_month_date.strftime('%Y-%m-%d')}_raw_data.csv"
    )
    conn, table_name = init_db(year, month)
    ensure_metadata_table(conn)
    record_snapshot_metadata(conn, year, month, ledger_index, close_time)

    try:
        fetch_snapshot(ledger_index, conn, table_name, year, month)
    except Exception as e:
        logging.error(f"Error fetching ledger {ledger_index}: {e}")
        conn.close()
        return

    # Export final balances to CSV
    cur = conn.cursor()
    cur.execute(f"SELECT account, balance FROM {table_name}")
    rows = cur.fetchall()
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

    logging.info(f"Finished. Saved {len(rows)} accounts to {filename}")
    conn.close()


def export_range(start_year: int, start_month: int, end_year: int, end_month: int):
    """
    Export multiple months in sequence, from (start_year, start_month)
    through (end_year, end_month), inclusive.
    """
    year, month = start_year, start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        logging.info(f"Starting export for {year}-{month:02d}")
        export_month(year, month)
        # increment month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def export_csv_from_sqlite(year: int, month: int):
    """
    Export account balances for a given year and month from SQLite to CSV.
    Reads from table accounts_YYYY_MM and writes to /mnt/output/xrp_MM_YYYY.csv
    """
    table_name = f"accounts_{year}_{month:02d}"
    csv_filename = f"xrpl_{month:02d}_{year}.csv"
    csv_path = os.path.join(OUTPUT_DIR, csv_filename)

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Check if table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cur.fetchone():
            logging.error(f"Table {table_name} does not exist in {DB_FILE}")
            conn.close()
            return

        # Query all rows
        cur.execute(f"SELECT account, balance FROM {table_name}")
        rows = cur.fetchall()

        # Write to CSV
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account", "balance"])
            writer.writerows(rows)

        logging.info(f"Successfully exported {len(rows)} rows to {csv_path}")
        conn.close()
    except Exception as e:
        logging.error(f"Failed to export CSV for {year}-{month:02d}: {e}")


def ensure_metadata_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS snapshot_metadata (
            year INTEGER,
            month INTEGER,
            ledger_index INTEGER,
            close_time TEXT,
            PRIMARY KEY (year, month)
        )
    """
    )
    conn.commit()


def record_snapshot_metadata(
    conn, year: int, month: int, ledger_index: int, close_time: datetime
):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO snapshot_metadata (year, month, ledger_index, close_time)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(year, month) DO UPDATE
        SET ledger_index = excluded.ledger_index,
            close_time = excluded.close_time
    """,
        (year, month, ledger_index, close_time.isoformat()),
    )
    conn.commit()
    logging.info(
        f"Recorded metadata: {year}-{month:02d} → ledger {ledger_index}, close_time {close_time.isoformat()}"
    )


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    export_month(2025, 10)  # Export October 2025 snapshot
