# 🌾 WheatPost

**A post-GWAS analysis toolkit for wheat (*Triticum aestivum*)**

WheatPost is an open-source Python web application designed for wheat geneticists and breeders who need fast, reproducible, reference-aware tools for interpreting GWAS and QTL mapping results. Instead of manually searching genome browsers, cross-referencing annotation files, or digging through literature, WheatPost provides a clean browser-based interface that runs locally on your machine.

Built exclusively for *Triticum aestivum* using IWGSC RefSeq v1.0 and v2.1 reference assemblies.

---

## Why WheatPost?

After running a GWAS, researchers typically spend hours manually:

- Checking whether their significant markers fall within previously published QTL
- Looking up what genes are near their significant markers
- Converting gene IDs between reference genome versions

WheatPost automates all three tasks in one place, with version-aware handling to prevent coordinate-mixing errors between IWGSC RefSeq v1.0 and v2.1.

---

## Features

### 🔍 Tab 1 — QTL Overlap Checker
Check whether your significant GWAS markers appear in any previously reported wheat QTL. Supports single marker lookup and batch search from a pasted list or uploaded text file. Returns QTL name, species, trait, chromosome, position, and a direct link to the source paper.

- Powered by WheatQTLdb v3.0 (pre-release) — curated QTL records across multiple traits
- Covers quality traits, selenium content, phosphorous deficiency, phosphorous use efficiency, and fungal resistance
- More trait data being added as WheatQTLdb v3.0 is finalized

### 🧬 Tab 2 — Gene Proximity Search
Find all annotated genes within a user-defined window (100 kb, 200 kb, or custom) around your significant marker. Supports both single marker input and batch CSV upload for multiple markers simultaneously.

- Powered by IWGSC RefSeq v1.0 and v2.1 High Confidence gene annotation (217,704 genes)
- Highlights markers that fall directly inside a gene
- Clickable gene IDs link directly to Ensembl Gramene (v2.1)
- Downloadable CSV output

### 🔄 Tab 3 — Gene ID Liftover
Convert wheat gene IDs across IWGSC RefSeq versions (v1.0 ↔ v1.1 ↔ v2.1). Supports single gene lookup and batch conversion from a text file or pasted list.

- Based on the official IWGSC all correspondences file (368,659 entries)
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

## Example Input Files

Example input files for Tab 2 and Tab 3 are provided in the `examples/` folder:

- `examples/example_markers.csv` — for batch marker input in Tab 2
- `examples/example_genes.txt` — for batch gene ID input in Tab 3

---

## Database Summary

| Database | Source | Size | Records |
|---|---|---|---|
| `annotation.db` | IWGSC RefSeq v1.0 + v2.1 via URGI | 22.5 MB | 217,704 genes |
| `wheat_qtl.db` | WheatQTLdb v3.0 (pre-release) | 0.3 MB | 700+ QTL |
| `liftover.db` | IWGSC all correspondences via URGI | 57.7 MB | 368,659 entries |

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
Data kindly shared by:
- Gautam Saripalli, Clemson University
- Dinesh Saini, Texas A&M University
- Prof. P.K. Gupta, Emeritus Professor & INSA Honorary Scientist

WheatQTLdb v3.0 manuscript in preparation. Please credit WheatQTLdb when using this data.

Singh K, Saini DK, Saripalli G, Batra R, Gautam T, Singh R, Pal S, Kumar M, Jan I, Singh S, Kumar A, Sharma H, Chaudhary J, Kumar K, Kumar S, Singh VK, Singh VP, Kumar D, Sharma S, Kumar S, Kumar R, Sharma S, Gaurav SS, Sharma PK, Balyan HS, Gupta PK. WheatQTLdb V2.0: a supplement to the database for wheat QTL. Mol Breed. 2022 Sep 16;42(10):56. doi: 10.1007/s11032-022-01329-1. PMID: 37313017; PMCID: PMC10248696.

---

## How to Cite

If you use WheatPost in your research, please cite:

> Neupane, B. (2026). WheatPost: A post-GWAS analysis toolkit for wheat (*Triticum aestivum*). GitHub. https://github.com/neupanebpn/WheatPost

And please credit WheatQTLdb for QTL data used in Tab 1.

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

## Contact

Developed by **Bipin Neupane**
Wheat genomics and plant breeding researcher

For questions, suggestions, or bug reports, please open an issue on GitHub.