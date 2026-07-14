"""
WheatPost - Gene Service
=========================
Handles all gene proximity queries against annotation.db.
Called by Tab 2 — Gene Proximity Search.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join("database", "annotation.db")


def normalize_chrom(chrom: str) -> str:
    """Normalize chromosome input to match database format (e.g. Chr2B)."""
    chrom = chrom.strip()
    if not chrom.lower().startswith("chr"):
        return "Chr" + chrom.upper()
    else:
        return "Chr" + chrom[3:].upper()


def get_nearby_genes(chrom: str, position: int, window_bp: int, version: str) -> pd.DataFrame:
    """
    Find all genes within a window around a marker position.

    Parameters:
        chrom    : Chromosome name e.g. '2B' or 'Chr2B'
        position : Marker position in base pairs
        window_bp: Window size in base pairs (e.g. 100000 for 100kb)
        version  : 'v1.0' or 'v2.1'

    Returns:
        pandas DataFrame with nearby genes sorted by distance from marker
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"annotation.db not found at {DB_PATH}. "
            "Please run: python scripts/build_annotation_db.py"
        )

    chrom = normalize_chrom(chrom)
    start = max(0, position - window_bp)
    end = position + window_bp

    query = """
        SELECT
            gene_id,
            chrom,
            start,
            end,
            strand,
            description,
            gene_symbol,
            version
        FROM genes
        WHERE version = ?
          AND chrom = ?
          AND start <= ?
          AND end >= ?
        ORDER BY start
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=(version, chrom, end, start))
    conn.close()

    if df.empty:
        return df

    # Calculate distance from marker to nearest gene edge
    df["distance_bp"] = df.apply(
        lambda row: 0 if row["start"] <= position <= row["end"]
        else min(abs(position - row["start"]), abs(position - row["end"])),
        axis=1
    )

    df = df.sort_values("distance_bp").reset_index(drop=True)

    df = df.rename(columns={
        "gene_id":     "Gene ID",
        "chrom":       "Chromosome",
        "start":       "Start (bp)",
        "end":         "End (bp)",
        "strand":      "Strand",
        "description": "Description",
        "gene_symbol": "Gene Symbol",
        "version":     "Reference Version",
        "distance_bp": "Distance from Marker (bp)"
    })

    return df


def get_chromosome_list(version: str) -> list:
    """Return list of chromosomes available for a given version."""

    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT chrom FROM genes WHERE version = ? ORDER BY chrom",
        (version,)
    )
    chroms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return chroms