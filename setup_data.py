"""
WheatPost Setup Checker
=======================
Run this before starting the app to verify all databases are present.
    python setup_data.py
"""

import os

DATABASES = {
    "Wheat annotation (v1.0 + v2.1)": "database/annotation.db",
    "WheatQTLdb":                      "database/wheat_qtl.db",
    "Liftover table":                  "database/liftover.db"
}

def check():
    print("\n" + "="*50)
    print("WheatPost - Setup Check")
    print("="*50)

    all_ok = True
    for name, path in DATABASES.items():
        if os.path.exists(path):
            print(f"✅ {name}")
        else:
            print(f"❌ {name} — not found at {path}")
            all_ok = False

    print("="*50)
    if all_ok:
        print("✅ All good. Run: streamlit run app.py")
    else:
        print("⚠️  Missing databases. See README for setup instructions.")
    print("="*50 + "\n")

if __name__ == "__main__":
    check()