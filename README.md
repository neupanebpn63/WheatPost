# 🌾 WheatPost

**A post-GWAS analysis toolkit for wheat (*Triticum aestivum*)**

WheatPost is an open-source Python web application designed for wheat geneticists and breeders who need fast, reproducible, reference-aware tools for interpreting GWAS and QTL mapping results. Instead of manually searching genome browsers, cross-referencing annotation files, or digging through literature, WheatPost provides a clean browser-based interface that runs locally on your machine.

Built exclusively for *Triticum aestivum* using IWGSC RefSeq v1.0 and v2.1 reference assemblies.

---

## Why WheatPost?

After running a GWAS, researchers typically spend hours manually:
- Looking up what genes are near their significant markers
- Checking whether their QTL overlaps with previously published loci
- Converting gene IDs between reference genome versions

WheatPost automates all three of these tasks in one place, with version-aware handling to prevent coordinate mixing errors between IWGSC RefSeq v1.0 and v2.1.

---

## Features

### 🧬 Tab 1 — QTL Overlap Checker *(coming soon)*
Check whether your significant GWAS markers overlap with previously published wheat QTL from WheatQTLdb (27,000+ curated QTL). Results are kept strictly separated by reference version to prevent coordinate errors.

### 🔍 Tab 2 — Gene Proximity Search
Find all annotated genes within a user-defined window (100 kb, 200 kb, or custom) around your significant marker. Supports both single marker input and batch CSV upload for multiple markers simultaneously.

- Powered by IWGSC RefSeq v1.0 and v2.1 High Confidence gene annotation
- Highlights markers that fall directly inside a gene
- Clickable gene IDs link directly to Ensembl Gramene
- Downloadable CSV output

### 🔄 Tab 3 — Gene ID Liftover
Convert wheat gene IDs across IWGSC RefSeq versions (v1.0 ↔ v1.1 ↔ v2.1). Supports single gene lookup and batch conversion from a text file or pasted list.

- Based on the official IWGSC all correspondences file
- Clickable v2.1 IDs link to Ensembl Gramene
- Downloadable CSV output

---

## Installation

### Requirements
- Python 3.10 or higher
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/neupanebpn/WheatPost.git
cd WheatPost
```

**2. Create and activate a virtual environment**
```bash
# Windows
py -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Verify setup**
```bash
python setup_data.py
```

**5. Run the app**
```bash
streamlit run app.py
```

The app will open automatically in your browser.

---

## Data Sources

| Data | Source | Version |
|---|---|---|
| Gene annotation | IWGSC RefSeq via URGI | v1.0 (2017), v2.1 (2020) |
| Gene ID correspondence | IWGSC all correspondences via URGI | v1.0, v1.1, v2.1 |
| QTL database | WheatQTLdb | V2.0 (2022) |

---

## Credits

### IWGSC RefSeq v1.0 Gene Annotation
Generated as a collaborative effort between:
- INRA-GDEC Clermont Ferrand, France (Frederic Choulet, Philippe Leroy, Helene Rimbert)
- Plant Genome and Systems Biology, Helmholtz Zentrum, Munich, Germany (Klaus Mayer, Manuel Spannagl, Sven Twardziok, Heidrun Gundlach)
- Earlham Institute, Norwich, UK (David Swarbreck, Luca Venturini, Gemy Kaithakottil)

Under the coordination of IWGSC (Kellye Eversole, Jane Rogers).

### IWGSC RefSeq v2.1 Gene Annotation
Authors: Helene Rimbert, Frédéric Choulet
Date: September 2020

### WheatQTLdb
Singh K, Saini DK, Saripalli G, Batra R, Gautam T, Singh R, Pal S, Kumar M, Jan I, Singh S, Kumar A, Sharma H, Chaudhary J, Kumar K, Kumar S, Singh VK, Singh VP, Kumar D, Sharma S, Kumar S, Kumar R, Sharma S, Gaurav SS, Sharma PK, Balyan HS, Gupta PK. WheatQTLdb V2.0: a supplement to the database for wheat QTL. Mol Breed. 2022 Sep 16;42(10):56. doi: 10.1007/s11032-022-01329-1. PMID: 37313017; PMCID: PMC10248696.

---

## How to Cite

If you use WheatPost in your research, please cite:

> Neupane, B. (2026). WheatPost: A post-GWAS analysis toolkit for wheat (*Triticum aestivum*). GitHub. https://github.com/neupanebpn63/WheatPost

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

## Contact

Developed by **Bipin Neupane**
Wheat genomics and plant breeding researcher

For questions, suggestions, or bug reports, please open an issue on GitHub.
