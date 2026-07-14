"""
WheatPost - Tab 2: Gene Proximity Search
=========================================
Find all annotated genes within a defined window around a significant marker.
Uses IWGSC RefSeq v1.0 or v2.1 annotation via gene_service.py
"""

import streamlit as st
import pandas as pd
from services.gene_service import get_nearby_genes, get_chromosome_list


def build_ensembl_link(gene_id: str, version: str) -> str:
    """Generate Ensembl Plants URL for a given gene ID."""
    if version == "v2.1":
        base = "https://plants.ensembl.org/Triticum_aestivum/Gene/Summary?g="
    else:
        base = "https://plants.ensembl.org/Triticum_aestivum/Gene/Summary?g="
    return f"{base}{gene_id}"


def add_hyperlinks(df: pd.DataFrame, version: str) -> pd.DataFrame:
    """Add clickable Ensembl links to Gene ID column."""
    df["Gene ID"] = df["Gene ID"].apply(
        lambda gid: f'<a href="{build_ensembl_link(gid, version)}" target="_blank">{gid}</a>'
    )
    return df


def highlight_inside_gene(row):
    """Highlight rows where marker falls inside a gene."""
    if row["Location"] == "Overlaps marker":
        return ["background-color: #d4edda; font-weight: bold"] * len(row)
    return [""] * len(row)


def show(version: str):
    st.header("🧬 Gene Proximity Search")
    st.markdown(
        "Find all annotated wheat genes within a defined window around your "
        "significant marker. Results are based on **" + version + "** annotation."
    )
    st.divider()

    # ── Mode selector ────────────────────────────────────────
    mode = st.radio(
        "Input mode",
        ["Single marker", "Batch upload (CSV)"],
        horizontal=True
    )

    st.divider()

    # ── Window Size ──────────────────────────────────────────
    st.markdown("**Window Size**")
    window_option = st.radio(
        "Select window size around marker",
        options=["100 kb", "200 kb", "Custom"],
        horizontal=True
    )

    if window_option == "100 kb":
        window_bp = 100000
    elif window_option == "200 kb":
        window_bp = 200000
    else:
        custom_kb = st.number_input(
            "Enter custom window size (kb)",
            min_value=1,
            max_value=10000,
            value=500,
            step=50
        )
        window_bp = custom_kb * 1000

    st.divider()

    # ── Single Marker Mode ───────────────────────────────────
    if mode == "Single marker":
        col1, col2 = st.columns(2)

        with col1:
            chrom_list = get_chromosome_list(version)
            chrom = st.selectbox(
                "Chromosome",
                options=chrom_list,
                help="Select the chromosome your marker is on"
            )

        with col2:
            position = st.number_input(
                "Marker Position (bp)",
                min_value=1,
                value=45320000,
                step=1000,
                help="Physical position of your significant marker in base pairs"
            )

        st.caption(
            f"Searching ± {window_bp:,} bp around {chrom}:{position:,} ({version})"
        )

        if st.button("🔍 Search Nearby Genes", type="primary"):
            _run_search([(chrom, position, f"{chrom}:{position:,}")], window_bp, version)

    # ── Batch Upload Mode ────────────────────────────────────
    else:
        st.markdown("**Upload a CSV file with your significant markers**")
        st.caption(
            "Required columns: `Marker`, `Chr`, `Position` — "
            "Example: AX-123, 2B, 45320000"
        )

        # Download example CSV
        example = "Marker,Chr,Position\nAX-123,2B,45320000\nAX-456,3A,71234566\nAX-789,7D,651234321"
        st.download_button(
            "⬇️ Download Example CSV",
            data=example,
            file_name="example_markers.csv",
            mime="text/csv"
        )

        uploaded = st.file_uploader("Upload your marker CSV", type=["csv"])

        if uploaded is not None:
            try:
                markers_df = pd.read_csv(uploaded)

                # Validate columns
                required = {"Marker", "Chr", "Position"}
                if not required.issubset(markers_df.columns):
                    st.error(
                        f"CSV must contain columns: {required}. "
                        f"Found: {set(markers_df.columns)}"
                    )
                    return

                st.success(f"Loaded {len(markers_df)} markers.")
                st.dataframe(markers_df, use_container_width=True, hide_index=True)

                markers = [
                    (row["Chr"], int(row["Position"]), row["Marker"])
                    for _, row in markers_df.iterrows()
                ]

                if st.button("🔍 Search All Markers", type="primary"):
                    _run_search(markers, window_bp, version)

            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def _run_search(markers: list, window_bp: int, version: str):
    """Run gene proximity search for one or more markers."""

    all_results = []

    with st.spinner(f"Searching {len(markers)} marker(s)..."):
        for chrom, position, marker_name in markers:
            try:
                df = get_nearby_genes(chrom, position, window_bp, version)
                if not df.empty:
                    df.insert(0, "Marker", marker_name)
                    df.insert(1, "Query Position (bp)", position)
                    all_results.append(df)
            except Exception as e:
                st.warning(f"Error processing {marker_name}: {e}")

    if not all_results:
        st.warning(
            "No genes found for any marker. Try increasing your window size."
        )
        return

    combined = pd.concat(all_results, ignore_index=True)
    # Drop Gene Symbol column if entirely empty
    if combined["Gene Symbol"].eq("").all():
        combined = combined.drop(columns=["Gene Symbol"])

    st.success(
        f"Found **{len(combined)} gene matches** across "
        f"**{len(markers)} marker(s)**"
    )

    # ── Display with highlighting and hyperlinks ─────────────
    display_df = combined.copy()

    # Add Ensembl Gramene hyperlinks
    display_df["Gene ID"] = display_df["Gene ID"].apply(
        lambda gid: f'<a href="https://ensembl.gramene.org/Triticum_aestivum_refseqv2/Gene/Summary?g={gid}" target="_blank">{gid}</a>'
    )

    # Build styled HTML table
    rows_html = ""
    for _, row in display_df.iterrows():
        if row["Location"] == "Overlaps marker":
            row_style = "background-color: #d4edda; font-weight: bold;"
        else:
            row_style = ""

        cells = "".join(
            f'<td style="padding:6px 10px; border-bottom:1px solid #eee;">{val}</td>'
            for val in row.values
        )
        rows_html += f'<tr style="{row_style}">{cells}</tr>'

    headers = "".join(
        f'<th style="padding:6px 10px; background-color:#f0f2f6; text-align:left; border-bottom:2px solid #ccc;">{col}</th>'
        for col in display_df.columns
    )

    table_html = f"""
    <div style="overflow-x: auto;">
    <table style="width:100%; border-collapse: collapse; font-size: 14px;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown(
        "🟢 **Green rows** = marker **overlaps** the gene | "
        "White rows = near marker genes"
    )

    # ── Download ─────────────────────────────────────────────
    st.divider()
    csv = combined.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name=f"WheatPost_gene_proximity_{version}.csv",
        mime="text/csv"
    )

    # ── Summary ──────────────────────────────────────────────
    st.divider()
    st.markdown("**Summary**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Gene Matches", len(combined))
    c2.metric(
        "Markers with genes found",
        combined["Marker"].nunique()
    )
    inside = len(combined[combined["Location"] == "Inside gene"])
    c3.metric("Markers inside a gene", inside)