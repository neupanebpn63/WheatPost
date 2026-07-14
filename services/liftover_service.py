"""
WheatPost - Liftover Service
=============================
Handles gene ID correspondence lookups across IWGSC reference versions.
Called by Tab 3 — Coordinate Liftover.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join("database", "liftover.db")

# Map user-friendly version names to column names
VERSION_TO_COL = {
    "v1.0": "v1_0",
    "v1.1": "v1_1",
    "v2.1": "v2_1"
}


def lookup_gene(gene_id: str, input_version: str) -> dict:
    """
    Look up a gene ID and return its equivalents in all other versions.

    Parameters:
        gene_id      : Gene ID to look up
        input_version: Version of the input gene ID (v1.0, v1.1, or v2.1)

    Returns:
        dict with keys v1.0, v1.1, v2.1 and their corresponding gene IDs
        Returns None if gene ID not found
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"liftover.db not found at {DB_PATH}. "
            "Please run: python scripts/build_liftover_db.py"
        )

    col = VERSION_TO_COL.get(input_version)
    if not col:
        raise ValueError(f"Unknown version: {input_version}. Use v1.0, v1.1, or v2.1")

    gene_id = gene_id.strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT v1_0, v1_1, v2_1 FROM liftover WHERE {col} = ?",
        (gene_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "v1.0": row[0] if row[0] else "Not available",
        "v1.1": row[1] if row[1] else "Not available",
        "v2.1": row[2] if row[2] else "Not available"
    }


def batch_lookup(gene_ids: list, input_version: str) -> pd.DataFrame:
    """
    Look up multiple gene IDs at once.

    Parameters:
        gene_ids     : List of gene IDs
        input_version: Version of the input gene IDs

    Returns:
        pandas DataFrame with input ID and all version equivalents
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"liftover.db not found at {DB_PATH}. "
            "Please run: python scripts/build_liftover_db.py"
        )

    col = VERSION_TO_COL.get(input_version)
    if not col:
        raise ValueError(f"Unknown version: {input_version}")

    results = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for gene_id in gene_ids:
        gene_id = gene_id.strip()
        if not gene_id:
            continue
        cursor.execute(
            f"SELECT v1_0, v1_1, v2_1 FROM liftover WHERE {col} = ?",
            (gene_id,)
        )
        row = cursor.fetchone()
        if row:
            results.append({
                "Input Gene ID": gene_id,
                "Input Version": input_version,
                "v1.0 ID": row[0] if row[0] else "Not available",
                "v1.1 ID": row[1] if row[1] else "Not available",
                "v2.1 ID": row[2] if row[2] else "Not available"
            })
        else:
            results.append({
                "Input Gene ID": gene_id,
                "Input Version": input_version,
                "v1.0 ID": "Not found",
                "v1.1 ID": "Not found",
                "v2.1 ID": "Not found"
            })

    conn.close()
    return pd.DataFrame(results)