"""
WheatPost - Build Annotation Database
======================================
Run this script ONCE to build the annotation SQLite database
from IWGSC RefSeq v1.0 and v2.1 GFF3 files.

Usage:
    python scripts/build_annotation_db.py

Output:
    database/annotation.db
"""

import sqlite3
import os
import re

# ── File paths ────────────────────────────────────────────────
GFF3_FILES = {
    "v1.0": r"data\iwgsc_refseqv1.0_HighConf_2017Mar13.gff3\iwgsc_refseqv1.0_HighConf_2017Mar13.gff3",
    "v2.1": r"data\iwgsc_refseqv2.1_gene_annotation_200916\iwgsc_refseqv2.1_gene_annotation_200916\iwgsc_refseqv2.1_annotation_200916_HC.gff3"
}

DB_PATH = os.path.join("database", "annotation.db")

# ── Helper: parse GFF3 attributes column ─────────────────────
def parse_attributes(attr_string):
    """Extract gene_id, description, gene_symbol from GFF3 attributes."""
    gene_id = ""
    description = ""
    gene_symbol = ""

    # Extract ID
    id_match = re.search(r'ID=([^;]+)', attr_string)
    if id_match:
        gene_id = id_match.group(1).strip()

    # Extract functional description
    desc_match = re.search(r'Note=([^;]+)', attr_string)
    if desc_match:
        description = desc_match.group(1).strip()

    # Extract gene symbol if present
    sym_match = re.search(r'gene_symbol=([^;]+)', attr_string)
    if sym_match:
        gene_symbol = sym_match.group(1).strip()

    return gene_id, description, gene_symbol

# ── Create database and table ─────────────────────────────────
def create_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id     TEXT,
            chrom       TEXT,
            start       INTEGER,
            end         INTEGER,
            strand      TEXT,
            version     TEXT,
            description TEXT,
            gene_symbol TEXT
        )
    """)
    # Index for fast range queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chrom_start_end ON genes (chrom, start, end)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_version ON genes (version)")
    conn.commit()
    print("✅ Database and table created.")

# ── Parse GFF3 and insert genes ───────────────────────────────
def parse_gff3(filepath, version, conn):
    cursor = conn.cursor()
    count = 0
    batch = []
    batch_size = 1000

    print(f"\nProcessing {version} — {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            # Skip comment lines
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue

            chrom, source, feature, start, end, score, strand, phase, attributes = parts

            # Only process gene features
            if feature != "gene":
                continue

            gene_id, description, gene_symbol = parse_attributes(attributes)

            batch.append((
                gene_id,
                chrom,
                int(start),
                int(end),
                strand,
                version,
                description,
                gene_symbol
            ))

            count += 1

            # Insert in batches for speed
            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT INTO genes
                    (gene_id, chrom, start, end, strand, version, description, gene_symbol)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch = []
                print(f"  {count} genes processed...", end="\r")

    # Insert remaining
    if batch:
        cursor.executemany("""
            INSERT INTO genes
            (gene_id, chrom, start, end, strand, version, description, gene_symbol)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    print(f"  ✅ {version} complete — {count} genes inserted.")
    return count

# ── Main ──────────────────────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("WheatPost — Building Annotation Database")
    print("="*55)

    # Check input files exist
    for version, path in GFF3_FILES.items():
        if not os.path.exists(path):
            print(f"❌ File not found for {version}: {path}")
            print("   Please check your data folder.")
            return

    # Remove old database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old database: {DB_PATH}")

    # Connect and build
    conn = sqlite3.connect(DB_PATH)
    create_database(conn)

    total = 0
    for version, path in GFF3_FILES.items():
        total += parse_gff3(path, version, conn)

    conn.close()

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n{'='*55}")
    print(f"✅ Done! Total genes: {total:,}")
    print(f"📦 Database size: {size_mb:.1f} MB")
    print(f"📁 Saved to: {DB_PATH}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()