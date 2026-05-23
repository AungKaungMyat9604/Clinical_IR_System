# Clinical IR System

A Streamlit evaluation dashboard for clinical information retrieval on MIMIC-IV discharge notes. Compares three retrieval systems on the same random note sample:

| System | Method |
|--------|--------|
| **A** | TF-IDF + cosine similarity (sparse lexical baseline) |
| **B** | Dense semantic search with `all-MiniLM-L6-v2` |
| **C** | Hybrid BM25 + MedCPT dual encoders, fused with Reciprocal Rank Fusion (RRF) |

The app supports **live search**, **note detail view**, and a **10-query graded evaluation panel** (Precision@3, Recall@3, MAP, NDCG@3).

> **Research use only** — not for clinical decision-making.

---

## Project structure

```
Clinical_IR_System/
├── clinical_ir_app/
│   ├── streamlit_app.py      # Streamlit dashboard (entry point)
│   ├── data.py               # MIMIC sampling + graded ground truth
│   ├── search_engines.py     # Systems A, B, C
│   ├── evaluation.py         # IR metrics
│   ├── requirements.txt
│   └── models/               # Download models here (not in git)
├── datasets/
│   └── physionet.org/files/  # MIMIC data (not in git — download locally)
├── Report/
│   └── report.tex            # IEEE-format portfolio report
└── README.md
```

---

## Prerequisites

- **Python 3.9+**
- **Git** (to clone the repo)
- **PhysioNet credentialed access** to [MIMIC-IV](https://physionet.org/content/mimiciv/3.1/) and [MIMIC-IV-Note](https://physionet.org/content/mimic-iv-note/2.2/)
- **Hugging Face CLI** (`pip install huggingface_hub`) for downloading embedding models
- ~**16 GB free disk space** for MIMIC files + models (datasets are **not** included in this repo)

---

## 1. Clone the repository

```bash
git clone git@github.com:AungKaungMyat9604/Clinical_IR_System.git
cd Clinical_IR_System
```

---

## 2. Download MIMIC data

After completing PhysioNet credentialing, download and place files so the paths match what `data.py` expects:

```
datasets/physionet.org/files/mimiciv/3.1/hosp/admissions.csv.gz
datasets/physionet.org/files/mimiciv/3.1/hosp/diagnoses_icd.csv.gz
datasets/physionet.org/files/mimic-iv-note/2.2/note/discharge.csv.gz
```

You can use the PhysioNet download tools or `wget` with your credentialed session. The app reads a **random sample** from `discharge.csv.gz` (default 2000 notes) — it does not load the full 300k+ file into memory.

---

## 3. Download embedding models

From the repo root:

```bash
cd clinical_ir_app

# System B — MiniLM (~90 MB)
hf download sentence-transformers/all-MiniLM-L6-v2 \
  --local-dir models/all-MiniLM-L6-v2

# System C — MedCPT (~2 GB total)
hf download ncbi/MedCPT-Query-Encoder \
  --local-dir models/MedCPT-Query-Encoder

hf download ncbi/MedCPT-Article-Encoder \
  --local-dir models/MedCPT-Article-Encoder
```

Each model folder must contain at least:

- MiniLM: `config.json`, `model.safetensors`, `tokenizer.json`, `modules.json`
- MedCPT: `config.json`, `model.safetensors`, `tokenizer.json`

---

## 4. Install Python dependencies

```bash
cd clinical_ir_app
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Important:** keep `huggingface_hub>=0.34,<1.0` as pinned in `requirements.txt`. Upgrading past 1.0 can break `transformers`.

---

## 5. Run the app

```bash
cd clinical_ir_app
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

### First run

The first startup builds all three indexes and can take **several minutes** (MedCPT Article encoding is the slowest step). Later runs are faster because Streamlit caches the indexes in memory.

Change **sample size**, **random seed**, or sidebar filters → cache rebuilds.

To force a rebuild: Streamlit menu (☰) → **Clear cache** → refresh.

---

## Using the dashboard

### Sidebar

- **Random sample size** — number of discharge notes indexed (500–5000)
- **Random seed** — reproducible random subset
- **Primary ICD only** / **Include partial labels** — ground-truth strictness
- **Retrieval systems (A / B / C)** — brief explanation of each system
- **References** — bibliography aligned with `Report/report.tex`

### Live Search tab

1. Enter a clinical query (e.g. `septic shock with positive blood cultures`)
2. Choose **Results to show (Top-K)**: 3, 5, 10, 15, or 20
3. Choose **Preview** or **Detail (expandable)** for result cards
4. Use **Note detail view** at the bottom to read full discharge text and compare ranks across systems

### Evaluation Panel tab

1. Click **Run built-in evaluation**
2. Review per-query metrics and macro-averaged system comparison
3. Metrics: Precision@3, Recall@3, MAP, NDCG@3, latency

**Ground truth grades:**

| Grade | Rule |
|-------|------|
| **2** | Query keywords in note text **and** matching ICD on admission |
| **1** | Keywords in text **without** matching ICD |
| **0** | Not labeled |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Discharge notes not found` | Check MIMIC paths under `datasets/physionet.org/files/` |
| Semantic search / MiniLM failed | Re-download MiniLM; run `pip install -r requirements.txt`; Clear cache |
| Hybrid BM25 + MedCPT failed | Download both MedCPT models; ensure `rank-bm25` is installed |
| `huggingface_hub` version conflict | `pip install 'huggingface_hub>=0.34.0,<1.0'` then restart Streamlit |
| Slow every refresh | Avoid changing sidebar settings unnecessarily; first load always scans the full discharge file once |
| No labeled notes for evaluation | Increase sample size or enable partial labels in sidebar |

---

## What is not included in git

These are excluded via `.gitignore` and must be set up locally:

- `datasets/` — MIMIC-IV and MIMIC-IV-Note files (licensed, large)
- `clinical_ir_app/.venv/` — Python virtual environment
- `clinical_ir_app/models/*` — downloaded model weights

---

## Export presentation to PowerPoint

`Presentation.html` can be exported as `presentation.pptx` (one PNG image per slide via html2canvas + pptxgenjs):

```bash
npm install
npm run export:pptx
```

Requires Node.js 18+. The script uses headless Chrome (Puppeteer) to render each slide, then writes `presentation.pptx` in the project root (~22 MB for 24 slides).

---

## Report

The IEEE-format write-up is in `Report/report.tex` (compiled PDF: `Report/report.pdf`).

---

## License and data use

MIMIC data use requires PhysioNet credentialing and adherence to the [PhysioNet Credentialed Health Data License](https://physionet.org/content/mimiciv/view-license/3.1/). Do not commit MIMIC files to public repositories.
