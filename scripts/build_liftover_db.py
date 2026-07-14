"""
WheatPost - Build Liftover Database
=====================================
Run this script ONCE to build the gene ID correspondence SQLite database
from the IWGSC all correspondences file.

Usage:
    python scripts/build_liftover_db.py

Output:
    database/liftover.db
"""

import sqlite3
import pandas as pd
import os

# ── File paths ────────────────────────────────────────────────
INPUT_FILE = r"data\liftover\iwgsc_refseq_all_correspondances\iwgsc_refseq_all_correspondances.csv"
DB_PATH = os.path.join("database", "liftover.db")

def main():
    print("\n" + "="*55)
    print("WheatPost — Building Liftover Database")
    print("="*55)

    if not os.path.exists(INPUT_FILE):
        print(f"❌ File not found: {INPUT_FILE}")
        return

    print(f"Reading correspondence file...")
    df = pd.read_csv(INPUT_FILE, sep=" ")

    # Rename columns to clean names
    df.columns = ["v1_0", "v1_1", "v2_1", "css2014"]

    # Replace "-" with empty string for missing entries
    df = df.replace("-", "")

    # Remove old database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old database: {DB_PATH}")

    # Write to SQLite
    conn = sqlite3.connect(DB_PATH)

    df.to_sql("liftover", conn, index=False, if_exists="replace")

    # Create indexes for fast lookup on each version column
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_v1_0 ON liftover (v1_0)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_v1_1 ON liftover (v1_1)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_v2_1 ON liftover (v2_1)")
    conn.commit()
    conn.close()

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"✅ Done! Total entries: {len(df):,}")
    print(f"📦 Database size: {size_mb:.1f} MB")
    print(f"📁 Saved to: {DB_PATH}")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()