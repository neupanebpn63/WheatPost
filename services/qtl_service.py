"""
WheatPost - QTL Service
========================
Handles marker-to-QTL lookups against wheat_qtl.db.
Called by Tab 1 — QTL Overlap Checker.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join("database", "wheat_qtl.db")


def search_marker(marker: str) -> pd.DataFrame:
    """
    Search for a single marker name across all QTL records.

    Parameters:
        marker: Marker name e.g. 'IWB53606'

    Returns:
        pandas DataFrame with matching QTL records
        Empty DataFrame if not found
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"wheat_qtl.db not found at {DB_PATH}. "
            "Please run: python scripts/build_qtl_db.py"
        )

    marker = marker.strip()

    query = """
        SELECT
            q.qtl_name      AS "QTL Name",
            q.species       AS "Species",
            q.trait         AS "Trait",
            q.parameter     AS "Parameter",
            q.chromosome    AS "Chromosome",
            q.position      AS "Position",
            q.markers       AS "Associated Markers",
            q.link          AS "Link",
            q.reference     AS "Reference"
        FROM qtl q
        JOIN marker_qtl m ON q.id = m.qtl_id
        WHERE m.marker = ?
        ORDER BY q.trait, q.chromosome
    """

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=(marker,))
    conn.close()

    return df


def batch_search(markers: list) -> pd.DataFrame:
    """
    Search multiple markers at once.

    Parameters:
        markers: List of marker names

    Returns:
        pandas DataFrame with all matches, including input marker column
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"wheat_qtl.db not found at {DB_PATH}. "
            "Please run: python scripts/build_qtl_db.py"
        )

    all_results = []

    conn = sqlite3.connect(DB_PATH)

    for marker in markers:
        marker = marker.strip()
        if not marker:
            continue

        query = """
            SELECT
                ? AS "Input Marker",
                q.qtl_name      AS "QTL Name",
                q.species       AS "Species",
                q.trait         AS "Trait",
                q.parameter     AS "Parameter",
                q.chromosome    AS "Chromosome",
                q.position      AS "Position",
                q.markers       AS "Associated Markers",
                q.link          AS "Link",
                q.reference     AS "Reference"
            FROM qtl q
            JOIN marker_qtl m ON q.id = m.qtl_id
            WHERE m.marker = ?
            ORDER BY q.trait, q.chromosome
        """

        df = pd.read_sql_query(query, conn, params=(marker, marker))
        if not df.empty:
            all_results.append(df)

    conn.close()

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)