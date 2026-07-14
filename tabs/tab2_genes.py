"""
WheatPost - Tab 2: Gene Proximity Search
=========================================
Find all annotated genes within a defined window around a significant marker.
Uses IWGSC RefSeq v1.0 or v2.1 annotation via gene_service.py
"""

import streamlit as st
import pandas as pd
from services.gene_service import get_nearby_genes, get_chromosome_list


def show(version: str):
    st.header("🧬 Gene Proximity Search")
    st.markdown(
        "Find all annotated wheat genes within a defined window around your significant marker. "
        "Results are based on **" + version + "** annotation."
    )

    st.divider()

    # ── Input Section ────────────────────────────────────────
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

    st.caption(
        f"Searching ± {window_bp:,} bp around position {position:,} on {chrom} ({version})"
    )

    st.divider()

    # ── Search Button ────────────────────────────────────────
    if st.button("🔍 Search Nearby Genes", type="primary"):
        with st.spinner("Querying annotation database..."):
            try:
                df = get_nearby_genes(chrom, position, window_bp, version)

                if df.empty:
                    st.warning(
                        f"No genes found within ± {window_bp:,} bp of "
                        f"{chrom}:{position:,} in {version}. "
                        "Try increasing your window size."
                    )
                else:
                    st.success(
                        f"Found **{len(df)} genes** within ± {window_bp:,} bp "
                        f"of {chrom}:{position:,} ({version})"
                    )

                    # ── Results Table ────────────────────────
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # ── Download Button ──────────────────────
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Download Results as CSV",
                        data=csv,
                        file_name=f"WheatPost_{chrom}_{position}_{window_option.replace(' ', '')}_{version}.csv",
                        mime="text/csv"
                    )

                    # ── Summary Stats ────────────────────────
                    st.divider()
                    st.markdown("**Summary**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Genes", len(df))
                    c2.metric("Closest Gene", df["Gene ID"].iloc[0])
                    c3.metric(
                        "Closest Distance",
                        f"{df['Distance from Marker (bp)'].iloc[0]:,} bp"
                    )

            except FileNotFoundError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {e}")