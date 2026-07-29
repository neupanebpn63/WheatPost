"""
WheatPost - Tab 1: QTL Overlap Checker
========================================
Search whether a marker appears in any known wheat QTL.
Uses WheatQTLdb v2.0 data via qtl_service.py
"""

import streamlit as st
import pandas as pd
from services.qtl_service import search_marker, batch_search


def show():
    st.header("🔍 QTL Overlap Checker")
    st.markdown(
        "Check whether your significant GWAS markers appear in any "
        "previously reported wheat QTL. Data sourced from "
        "[WheatQTLdb](http://wheatqtldb.net) v2.0."
    )
    st.info(
        "💡 Marker search is flexible — `wPt-4669`, `WPT4669`, and `wpt_4669` "
        "all return the same results."
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
            placeholder="e.g. IWB53606 or wPt-4669",
            help="Case insensitive. Hyphens and underscores are ignored."
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
                            f"**{marker}** was not found in any QTL record. "
                            "This may mean:\n"
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
            placeholder="IWB53606\nwPt-4669\nBS00084995_51",
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
                            "None of the markers were found in any QTL record."
                        )
                    else:
                        found_markers = df["Input Marker"].nunique()
                        st.success(
                            f"**{found_markers}** of **{len(markers)}** markers "
                            f"found in **{len(df)}** QTL record(s)"
                        )
                        _display_results(df, "batch")

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
        "QTL data from WheatQTLdb v2.0. "
        "Singh et al. Mol Breed. 2022. doi:10.1007/s11032-022-01329-1. "
        "Credits: Saripalli G., Saini D.K., Gupta P.K. et al."
    )


def _display_results(df: pd.DataFrame, marker: str):
    """Display QTL results as HTML table with clickable links."""

    display_df = df.copy()

    display_df["Link"] = display_df["Link"].apply(
        lambda url: (
            f'<a href="{url}" target="_blank">🔗 View paper</a>'
            if url and url != "nan" and str(url).startswith("http")
            else ""
        )
    )

    headers = "".join(
        f'<th style="padding:6px 10px; background-color:#f0f2f6; '
        f'text-align:left; border-bottom:2px solid #ccc;">{col}</th>'
        for col in display_df.columns
    )

    rows_html = ""
    for _, row in display_df.iterrows():
        cells = "".join(
            f'<td style="padding:6px 10px; border-bottom:1px solid #eee;">{val}</td>'
            for val in row.values
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

    if marker != "batch":
        st.divider()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Results as CSV",
            data=csv,
            file_name=f"WheatPost_QTL_{marker}.csv",
            mime="text/csv"
        )