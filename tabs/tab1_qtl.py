"""
WheatPost - Tab 1: QTL Overlap Checker
========================================
Search whether a marker appears in any known wheat QTL.
Uses WheatQTLdb data via qtl_service.py
"""

import streamlit as st
import pandas as pd
from services.qtl_service import search_marker, batch_search


def show():
    st.header("🔍 QTL Overlap Checker")
    st.markdown(
        "Check whether your significant GWAS markers appear in any "
        "previously reported wheat QTL. Data sourced from "
        "[WheatQTLdb](http://wheatqtldb.net) v3.0 (pre-release)."
    )
    st.divider()

    # ── Mode selector ────────────────────────────────────────
    mode = st.radio(
        "Input mode",
        ["Single marker", "Batch search"],
        horizontal=True
    )

    st.divider()

    # ── Single marker mode ───────────────────────────────────
    if mode == "Single marker":
        marker = st.text_input(
            "Enter marker name",
            placeholder="e.g. IWB53606",
            help="Enter the exact marker name as it appears in your GWAS output"
        )

        if st.button("🔍 Search", type="primary"):
            if not marker.strip():
                st.warning("Please enter a marker name.")
                return

            with st.spinner("Searching QTL database..."):
                try:
                    df = search_marker(marker.strip())

                    if df.empty:
                        st.info(
                            f"**{marker}** was not found in any QTL record "
                            "in the current database. This may mean:\n"
                            "- The marker has not been reported in a QTL study yet\n"
                            "- The marker name format differs from what is stored\n"
                            "- More trait data is being added to the database"
                        )
                    else:
                        st.success(
                            f"**{marker}** appears in **{len(df)} QTL record(s)**"
                        )
                        _display_results(df, marker)

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # ── Batch search mode ────────────────────────────────────
    else:
        st.markdown("**Option A — Paste marker names**")
        pasted = st.text_area(
            "Paste marker names (one per line)",
            placeholder="IWB53606\nIWB48157\nwPt741599",
            height=150
        )

        st.markdown("**Option B — Upload a text file**")
        uploaded = st.file_uploader(
            "Upload a .txt file with one marker name per line",
            type=["txt"]
        )

        markers = []
        if pasted.strip():
            markers = [m.strip() for m in pasted.strip().split("\n") if m.strip()]
        elif uploaded is not None:
            content = uploaded.read().decode("utf-8")
            markers = [m.strip() for m in content.split("\n") if m.strip()]

        if markers:
            st.caption(f"{len(markers)} marker(s) ready for search")

        if st.button("🔍 Search All Markers", type="primary"):
            if not markers:
                st.warning("Please paste or upload marker names.")
                return

            with st.spinner(f"Searching {len(markers)} marker(s)..."):
                try:
                    df = batch_search(markers)

                    if df.empty:
                        st.info(
                            "None of the markers were found in any QTL record. "
                            "Try checking marker name formats."
                        )
                    else:
                        found_markers = df["Input Marker"].nunique()
                        st.success(
                            f"**{found_markers}** of **{len(markers)}** markers "
                            f"found in **{len(df)}** QTL record(s)"
                        )
                        _display_results(df, "batch")

                        # CSV download
                        st.divider()
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Download Results as CSV",
                            data=csv,
                            file_name="WheatPost_QTL_batch_results.csv",
                            mime="text/csv"
                        )

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    st.divider()
    st.caption(
        "QTL data from WheatQTLdb v3.0 (pre-release). "
        "Credits: Saripalli G., Saini D.K., Gupta P.K. et al. "
        "Data shared for academic use."
    )


def _display_results(df: pd.DataFrame, marker: str):
    """Display QTL results as HTML table with clickable links."""

    display_df = df.copy()

    # Make link column clickable
    display_df["Link"] = display_df["Link"].apply(
        lambda url: (
            f'<a href="{url}" target="_blank">🔗 View paper</a>'
            if url and url != "nan" and url.startswith("http")
            else ""
        )
    )

    # Build HTML table
    headers = "".join(
        f'<th style="padding:6px 10px; background-color:#f0f2f6; '
        f'text-align:left; border-bottom:2px solid #ccc;">{col}</th>'
        for col in display_df.columns
        if col != "Reference"
    )

    rows_html = ""
    for _, row in display_df.iterrows():
        cells = "".join(
            f'<td style="padding:6px 10px; border-bottom:1px solid #eee;">{val}</td>'
            for col, val in row.items()
            if col != "Reference"
        )
        rows_html += f"<tr>{cells}</tr>"

    table_html = f"""
    <div style="overflow-x: auto;">
    <table style="width:100%; border-collapse: collapse; font-size: 14px;">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    # Reference section below table
    if "Reference" in df.columns:
        st.divider()
        st.markdown("**References**")
        refs = df["Reference"].dropna().unique()
        for i, ref in enumerate(refs, 1):
            if ref and ref != "nan":
                st.markdown(f"{i}. {ref}")

    # CSV download for single marker
    if marker != "batch":
        st.divider()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Results as CSV",
            data=csv,
            file_name=f"WheatPost_QTL_{marker}.csv",
            mime="text/csv"
        )