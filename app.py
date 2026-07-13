import streamlit as st

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
    ["IWGSC RefSeq v1.0", "IWGSC RefSeq v2.1"]
)
st.sidebar.info(f"Active: {version}")

# Three tabs
tab1, tab2, tab3 = st.tabs([
    "🔍 QTL Overlap",
    "🧬 Gene Proximity",
    "🔄 Coordinate Liftover"
])

with tab1:
    st.header("QTL Overlap Checker")
    st.write("Check if your significant markers overlap with published wheat QTL.")
    st.info("Coming soon — Milestone 2")

with tab2:
    st.header("Gene Proximity Search")
    st.write("Find all annotated genes within a defined window around your marker.")
    st.info("Coming soon — Milestone 3")

with tab3:
    st.header("Coordinate Liftover")
    st.write("Convert marker positions between IWGSC RefSeq v1.0 and v2.1.")
    st.info("Coming soon — Milestone 4")