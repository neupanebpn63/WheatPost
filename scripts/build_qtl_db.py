"""
WheatPost - Build QTL Database
================================
Run this script ONCE to build the QTL SQLite database
from the standardized WheatQTLdb master file.

Usage:
    python scripts/build_qtl_db.py

Input:
    data/qtl/wheatqtl_master.xlsx

Output:
    database/wheat_qtl.db
"""

import sqlite3
import pandas as pd
import os
import re

# ── File paths ────────────────────────────────────────────────
INPUT_FILE = os.path.join("data", "qtl", "wheatqtl_master.xlsx")
DB_PATH = os.path.join("database", "wheat_qtl.db")

# ── Expected columns ──────────────────────────────────────────
REQUIRED_COLS = [
    "species", "trait", "parameter", "qtl_name",
    "chromosome", "position", "markers", "link", "reference"
]


def normalize_markers(marker_string: str) -> list:
    """Split comma-separated marker string into individual markers."""
    if not marker_string or pd.isna(marker_string):
        return []
    marker_string = str(marker_string)
    markers = [m.strip() for m in marker_string.split(",")]
    return [m for m in markers if m and m != "-"]


def main():
    print("\n" + "="*55)
    print("WheatPost — Building QTL Database")
    print("="*55)

    # ── Check input file ──────────────────────────────────────
    if not os.path.exists(INPUT_FILE):
        print(f"❌ File not found: {INPUT_FILE}")
        print("   Please place wheatqtl_master.xlsx in data/qtl/")
        return

    print(f"Reading: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)

    # ── Validate columns ──────────────────────────────────────
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        print(f"❌ Missing columns: {missing}")
        print(f"   Found columns: {df.columns.tolist()}")
        return

    # ── Clean data ────────────────────────────────────────────
    df = df.dropna(how="all")
    df = df.fillna("")
    df["qtl_name"] = df["qtl_name"].astype(str).str.strip()
    df = df[df["qtl_name"].str.len() > 0]
    df = df[df["qtl_name"] != "nan"]

    print(f"✅ Loaded {len(df):,} QTL records")

    # ── Remove old database ───────────────────────────────────
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old database")

    # ── Create database ───────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qtl (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            species     TEXT,
            trait       TEXT,
            parameter   TEXT,
            qtl_name    TEXT,
            chromosome  TEXT,
            position    TEXT,
            markers     TEXT,
            link        TEXT,
            reference   TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marker_qtl (
            marker      TEXT,
            qtl_id      INTEGER,
            FOREIGN KEY (qtl_id) REFERENCES qtl(id)
        )
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_marker ON marker_qtl (marker)"
    )
    conn.commit()

    # ── Insert records ────────────────────────────────────────
    marker_count = 0

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO qtl
            (species, trait, parameter, qtl_name, chromosome, position, markers, link, reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row["species"]).strip(),
            str(row["trait"]).strip(),
            str(row["parameter"]).strip(),
            str(row["qtl_name"]).strip(),
            str(row["chromosome"]).strip(),
            str(row["position"]).strip(),
            str(row["markers"]).strip(),
            str(row["link"]).strip(),
            str(row["reference"]).strip()
        ))

        qtl_id = cursor.lastrowid

        for marker in normalize_markers(str(row["markers"])):
            cursor.execute(
                "INSERT INTO marker_qtl (marker, qtl_id) VALUES (?, ?)",
                (marker, qtl_id)
            )
            marker_count += 1

    conn.commit()
    conn.close()

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"✅ {len(df):,} QTL records inserted")
    print(f"✅ {marker_count:,} marker index entries created")
    print(f"📦 Database size: {size_mb:.1f} MB")
    print(f"📁 Saved to: {DB_PATH}")
    print("="*55 + "\n")


if __name__ == "__main__":
    main()