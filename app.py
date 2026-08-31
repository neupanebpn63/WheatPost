import streamlit as st
from tabs import tab1_qtl, tab2_genes, tab3_liftover

st.set_page_config(
    page_title="WheatPost",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 WheatPost")
st.markdown("**Post-GWAS Analysis Toolkit for Wheat (*Triticum aestivum*)**")

# Reference version selector
st.sidebar.title("Settings")
version = st.sidebar.radio(
    "Select Reference Version",
    ["v1.0", "v2.1"],
    index=1
)
st.sidebar.info(f"Active: IWGSC RefSeq {version}")

# Three tabs
tab1, tab2, tab3 = st.tabs([
    "🔍 QTL Overlap",
    "🧬 Gene Proximity",
    "🔄 Gene ID Liftover"
])

with tab1:
    tab1_qtl.show()

with tab2:
    tab2_genes.show(version)

with tab3:
    tab3_liftover.show()