import streamlit as st
from tabs import tab2_genes

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
    ["v1.0", "v2.1"]
)
st.sidebar.info(f"Active: IWGSC RefSeq {version}")

# Three tabs
tab1, tab2, tab3 = st.tabs([
    "🔍 QTL Overlap",
    "🧬 Gene Proximity",
    "🔄 Coordinate Liftover"
])

with tab1:
    st.header("QTL Overlap Checker")
    st.info("Coming soon — Milestone 2")

with tab2:
    tab2_genes.show(version)

with tab3:
    st.header("Coordinate Liftover")
    st.info("Coming soon — Milestone 3")