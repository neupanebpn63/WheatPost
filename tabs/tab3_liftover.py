"""
WheatPost - Tab 3: Gene ID Liftover
=====================================
Convert gene IDs across IWGSC RefSeq versions:
v1.0 ↔ v1.1 ↔ v2.1
Uses the IWGSC all correspondences file via liftover_service.py
"""

import streamlit as st
import pandas as pd
from services.liftover_service import lookup_gene, batch_lookup


def show():
    st.header("🔄 Gene ID Liftover")
    st.markdown(
        "Convert wheat gene IDs across IWGSC RefSeq versions. "
        "Supports v1.0, v1.1, and v2.1 in any direction."
    )
    st.divider()

    # ── Input version selector ───────────────────────────────
    input_version = st.selectbox(
        "Version of your input gene ID",
        options=["v1.0", "v1.1", "v2.1"],
        help="Select which reference version your gene ID comes from"
    )

    st.divider()

    # ── Mode selector ────────────────────────────────────────
    mode = st.radio(
        "Input mode",
        ["Single gene ID", "Batch lookup"],
        horizontal=True
    )

    st.divider()

    # ── Single gene ID mode ──────────────────────────────────
    if mode == "Single gene ID":
        gene_id = st.text_input(
            "Enter gene ID",
            placeholder=f"e.g. TraesCS1A01G000100",
            help="Enter a single wheat gene ID"
        )

        if st.button("🔄 Convert", type="primary"):
            if not gene_id.strip():
                st.warning("Please enter a gene ID.")
                return

            with st.spinner("Looking up gene ID..."):
                try:
                    result = lookup_gene(gene_id.strip(), input_version)

                    if result is None:
                        st.error(
                            f"Gene ID `{gene_id}` not found in {input_version} "
                            f"of the IWGSC correspondence table. "
                            f"Please check the ID and version."
                        )
                    else:
                        st.success(f"Gene ID found — showing all version equivalents")

                        # Display as a clean card
                        c1, c2, c3 = st.columns(3)

                        with c1:
                            st.metric(
                                label="IWGSC RefSeq v1.0",
                                value=result["v1.0"]
                            )

                        with c2:
                            st.metric(
                                label="IWGSC RefSeq v1.1",
                                value=result["v1.1"]
                            )

                        with c3:
                            st.metric(
                                label="IWGSC RefSeq v2.1",
                                value=result["v2.1"]
                            )
                            if result["v2.1"] not in ("Not available", "Not found"):
                                st.markdown(
                                    f'<a href="https://ensembl.gramene.org/Triticum_aestivum_refseqv2/Gene/Summary?g={result["v2.1"]}" target="_blank">🔗 View in Gramene (v2.1)</a>',
                                    unsafe_allow_html=True
                                )

                        # Download single result
                        st.divider()
                        df_single = pd.DataFrame([{
                            "Input Gene ID": gene_id,
                            "Input Version": input_version,
                            "v1.0 ID": result["v1.0"],
                            "v1.1 ID": result["v1.1"],
                            "v2.1 ID": result["v2.1"]
                        }])
                        csv = df_single.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇️ Download Result as CSV",
                            data=csv,
                            file_name=f"WheatPost_liftover_{gene_id}.csv",
                            mime="text/csv"
                        )

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    # ── Batch lookup mode ────────────────────────────────────
    else:
        st.markdown("**Option A — Paste gene IDs**")
        pasted = st.text_area(
            "Paste gene IDs (one per line)",
            placeholder="TraesCS1A01G000100\nTraesCS1A01G000200\nTraesCS1A01G000300",
            height=150
        )

        st.markdown("**Option B — Upload a text file**")
        uploaded = st.file_uploader(
            "Upload a .txt file with one gene ID per line",
            type=["txt"]
        )

        gene_ids = []

        if pasted.strip():
            gene_ids = [g.strip() for g in pasted.strip().split("\n") if g.strip()]
        elif uploaded is not None:
            content = uploaded.read().decode("utf-8")
            gene_ids = [g.strip() for g in content.split("\n") if g.strip()]

        if gene_ids:
            st.caption(f"{len(gene_ids)} gene ID(s) ready for lookup")

        if st.button("🔄 Convert All", type="primary"):
            if not gene_ids:
                st.warning("Please paste or upload gene IDs.")
                return

            with st.spinner(f"Looking up {len(gene_ids)} gene ID(s)..."):
                try:
                    df = batch_lookup(gene_ids, input_version)

                    found = len(df[df["v1.0 ID"] != "Not found"])
                    not_found = len(df[df["v1.0 ID"] == "Not found"])

                    st.success(
                        f"**{found}** gene(s) found — "
                        f"**{not_found}** not found in correspondence table"
                    )

                    # Add Gramene links to v2.1 column
                    display_df = df.copy()
                    display_df["v2.1 ID"] = display_df["v2.1 ID"].apply(
                        lambda gid: (
                            f'<a href="https://ensembl.gramene.org/Triticum_aestivum_refseqv2/Gene/Summary?g={gid}" target="_blank">{gid}</a>'
                            if gid not in ("Not available", "Not found", "")
                            else gid
                        )
                    )

                    # Build HTML table
                    headers = "".join(
                        f'<th style="padding:6px 10px; background-color:#f0f2f6; text-align:left; border-bottom:2px solid #ccc;">{col}</th>'
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

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Results as CSV",
                        data=csv,
                        file_name=f"WheatPost_liftover_batch_{input_version}.csv",
                        mime="text/csv"
                    )

                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    st.divider()
    st.caption(
        "Gene ID correspondence data from IWGSC RefSeq all correspondences file. "
        "Credits: URGI — https://urgi.versailles.inrae.fr"
    )