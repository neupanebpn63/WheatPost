"""
WheatPost - Build QTL Database
================================
Run this script ONCE to build the QTL SQLite database
from the WheatQTLdb v2.0 master file.

Usage:
    python scripts/build_qtl_db.py

Input:
    data/qtl/wheatqtl_v2.xlsx

Output:
    database/wheat_qtl.db
"""

import sqlite3
import pandas as pd
import os
import re

# ── File paths ────────────────────────────────────────────────
INPUT_FILE = os.path.join("data", "qtl", "wheatqtl_v2.xlsx")
DB_PATH = os.path.join("database", "wheat_qtl.db")

# ── Expected columns ──────────────────────────────────────────
REQUIRED_COLS = [
    "species", "trait", "parameter", "qtl_name",
    "chromosome", "position", "markers", "link"
]


def normalize_marker(marker: str) -> str:
    """
    Normalize a marker name for consistent searching.
    Removes hyphens, underscores, spaces and lowercases.
    e.g. wPt-4669, wPt_4669, WPT4669 all become wpt4669
    """
    return re.sub(r'[-_\s]', '', marker).lower()


def normalize_markers(marker_string: str) -> list:
    """Split marker string into list of (original, normalized) tuples."""
    if not marker_string or pd.isna(marker_string):
        return []
    marker_string = str(marker_string)
    markers = [m.strip() for m in marker_string.split(",")]
    result = []
    for m in markers:
        if m and m != "-" and m != "nan":
            result.append((m.strip(), normalize_marker(m)))
    return result


def main():
    print("\n" + "="*55)
    print("WheatPost — Building QTL Database")
    print("="*55)

    # ── Check input file ──────────────────────────────────────
    if not os.path.exists(INPUT_FILE):
        print(f"❌ File not found: {INPUT_FILE}")
        print("   Please place wheatqtl_v2.xlsx in data/qtl/")
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
            link        TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marker_qtl (
            marker      TEXT,
            normalized  TEXT,
            qtl_id      INTEGER,
            FOREIGN KEY (qtl_id) REFERENCES qtl(id)
        )
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_normalized ON marker_qtl (normalized)"
    )
    conn.commit()

    # ── Insert records ────────────────────────────────────────
    marker_count = 0

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO qtl
            (species, trait, parameter, qtl_name, chromosome, position, markers, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row["species"]).strip(),
            str(row["trait"]).strip(),
            str(row["parameter"]).strip(),
            str(row["qtl_name"]).strip(),
            str(row["chromosome"]).strip(),
            str(row["position"]).strip(),
            str(row["markers"]).strip(),
            str(row["link"]).strip()
        ))

        qtl_id = cursor.lastrowid

        for original, normalized in normalize_markers(str(row["markers"])):
            cursor.execute(
                "INSERT INTO marker_qtl (marker, normalized, qtl_id) VALUES (?, ?, ?)",
                (original, normalized, qtl_id)
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