"""
Data layer — local MIMIC-IV + MIMIC-IV-Note discharge corpus only.

Loads a random sample of discharge notes and builds graded evaluation ground truth:
  Grade 2 — query keywords in note text AND matching ICD on admission
  Grade 1 — query keywords in note text BUT no matching ICD on admission
  Grade 0 — otherwise (omitted from labels)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MIMIC_CORE = PROJECT_ROOT / "datasets/physionet.org/files/mimiciv/3.1"
MIMIC_NOTE_DIR = PROJECT_ROOT / "datasets/physionet.org/files/mimic-iv-note/2.2/note"

# 10-query validation matrix: ICD prefixes + clinical keywords per query
EVAL_QUERY_SUITE: dict[str, dict[str, list[str]]] = {
    "acute kidney injury secondary to dehydration": {
        "icd10": ["N17", "E86"],
        "icd9": ["584", "2765"],
        "keywords": [
            "acute kidney injury",
            "aki",
            "dehydration",
            "volume depletion",
            "prerenal",
            "creatinine",
        ],
    },
    "end-stage renal disease / ESRD": {
        "icd10": ["N18"],
        "icd9": ["585"],
        "keywords": [
            "end-stage renal",
            "end stage renal",
            "esrd",
            "esrd patient",
            "dialysis",
            "kidney failure",
        ],
    },
    "septic shock with positive blood cultures": {
        "icd10": ["R6521", "A41"],
        "icd9": ["99592", "038"],
        "keywords": [
            "septic shock",
            "blood culture",
            "bacteremia",
            "sepsis",
            "positive culture",
        ],
    },
    "bacteremia and systemic inflammatory response": {
        "icd10": ["A41", "R651"],
        "icd9": ["038", "99591"],
        "keywords": [
            "bacteremia",
            "sirs",
            "systemic inflammatory",
            "sepsis",
            "septicemia",
        ],
    },
    "congestive heart failure exacerbation": {
        "icd10": ["I50"],
        "icd9": ["428"],
        "keywords": [
            "congestive heart failure",
            "heart failure exacerbation",
            "chf exacerbation",
            "acute decompensated heart failure",
            "adhf",
        ],
    },
    "CHF with reduced ejection fraction": {
        "icd10": ["I502", "I509"],
        "icd9": ["4282", "4284"],
        "keywords": [
            "chf",
            "reduced ejection fraction",
            "hfref",
            "systolic dysfunction",
            "ejection fraction",
        ],
    },
    "altered mental status due to metabolic encephalopathy": {
        "icd10": ["G9341", "R4182"],
        "icd9": ["3483", "78009"],
        "keywords": [
            "altered mental status",
            "encephalopathy",
            "metabolic encephalopathy",
            "confusion",
            "delirium",
        ],
    },
    "type 2 diabetes mellitus with peripheral neuropathy": {
        "icd10": ["E11", "G632"],
        "icd9": ["250", "3371"],
        "keywords": [
            "type 2 diabetes",
            "diabetes mellitus",
            "peripheral neuropathy",
            "diabetic neuropathy",
            "neuropathy",
        ],
    },
    "hospital-acquired pneumonia / HAP": {
        "icd10": ["J152", "J189"],
        "icd9": ["482", "486"],
        "keywords": [
            "hospital-acquired pneumonia",
            "hospital acquired pneumonia",
            "hap",
            "nosocomial pneumonia",
            "ventilator-associated",
        ],
    },
    "gastrointestinal bleeding secondary to peptic ulcer": {
        "icd10": ["K922", "K27"],
        "icd9": ["578", "531"],
        "keywords": [
            "gastrointestinal bleeding",
            "gi bleed",
            "peptic ulcer",
            "upper gi bleed",
            "melena",
            "hematemesis",
        ],
    },
}

DISCHARGE_USECOLS = ["note_id", "subject_id", "hadm_id", "note_type", "text"]
CHUNK_SIZE = 10_000


@dataclass
class MimicCorpus:
    """Indexed notes plus graded evaluation labels for the same sample."""

    notes: pd.DataFrame
    ground_truth: dict[str, dict[str, int]]


def _icd_matches(code: str, version: int, patterns: dict[str, list[str]]) -> bool:
    code = str(code).upper().replace(".", "")
    if version == 10:
        return any(code.startswith(p.upper()) for p in patterns["icd10"])
    if version == 9:
        return any(code.startswith(p) for p in patterns["icd9"])
    return False


def _text_matches_keywords(text: str, keywords: list[str]) -> bool:
    lowered = str(text).lower()
    return any(kw.lower() in lowered for kw in keywords)


def _reservoir_sample_discharge(
    discharge_path: Path,
    max_rows: int,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Random sample of discharge notes without loading the full 300k+ file into memory.

    Uses reservoir sampling in a single pass over chunked reads.
    """
    if max_rows <= 0:
        raise ValueError("max_rows must be positive.")

    rng = random.Random(seed)
    reservoir: list[pd.Series] = []
    n_seen = 0

    reader = pd.read_csv(
        discharge_path,
        compression="gzip",
        usecols=DISCHARGE_USECOLS,
        chunksize=CHUNK_SIZE,
        dtype={"note_id": str},
    )

    for chunk in reader:
        for i in range(len(chunk)):
            row = chunk.iloc[i]
            n_seen += 1
            if len(reservoir) < max_rows:
                reservoir.append(row)
            else:
                j = rng.randint(0, n_seen - 1)
                if j < max_rows:
                    reservoir[j] = row

    if not reservoir:
        raise ValueError(f"No rows read from {discharge_path}.")

    return pd.DataFrame(reservoir).reset_index(drop=True)


def _hadm_ids_with_icd_match(
    diagnoses: pd.DataFrame,
    icd_patterns: dict[str, list[str]],
) -> set:
    mask = diagnoses.apply(
        lambda row: _icd_matches(row["icd_code"], int(row["icd_version"]), icd_patterns),
        axis=1,
    )
    return set(diagnoses.loc[mask, "hadm_id"].unique())


def build_graded_ground_truth(
    notes: pd.DataFrame,
    diagnoses: pd.DataFrame,
    suite: dict[str, dict[str, list[str]]] | None = None,
    primary_diagnosis_only: bool = True,
    include_partial_labels: bool = True,
) -> dict[str, dict[str, int]]:
    """
    Build graded relevance per query: note_id -> 2 (highly) or 1 (partial).

    Grade 2: keywords in note text AND admission has matching ICD code.
    Grade 1: keywords in note text BUT admission has no matching ICD (if include_partial_labels).
    Grade 0: omitted from the returned dict.
    """
    queries = suite or EVAL_QUERY_SUITE
    dx = diagnoses
    if primary_diagnosis_only and "seq_num" in dx.columns:
        dx = dx[dx["seq_num"] == 1]

    ground_truth: dict[str, dict[str, int]] = {}

    for query, config in queries.items():
        icd_patterns = {"icd10": config["icd10"], "icd9": config["icd9"]}
        keywords = config["keywords"]
        hadm_with_icd = _hadm_ids_with_icd_match(dx, icd_patterns)

        labels: dict[str, int] = {}
        for _, row in notes.iterrows():
            text = str(row["text"])
            if not _text_matches_keywords(text, keywords):
                continue

            hadm_id = row["hadm_id"]
            note_id = str(row["note_id"])
            if hadm_id in hadm_with_icd:
                labels[note_id] = 2
            elif include_partial_labels:
                labels[note_id] = 1

        ground_truth[query] = dict(sorted(labels.items()))

    return ground_truth


def load_mimic_notes(
    max_rows: int = 2000,
    random_seed: int = 42,
    primary_diagnosis_only: bool = True,
    require_text_match: bool = True,
) -> MimicCorpus:
    """
    Load a random sample of MIMIC-IV discharge notes with hosp joins.

    First full pass over discharge.csv.gz uses reservoir sampling (can take 1–3 minutes).
    Subsequent Streamlit runs use the cache and are much faster.
    """
    discharge_path = MIMIC_NOTE_DIR / "discharge.csv.gz"
    admissions_path = MIMIC_CORE / "hosp/admissions.csv.gz"
    diagnoses_path = MIMIC_CORE / "hosp/diagnoses_icd.csv.gz"

    if not discharge_path.exists():
        raise FileNotFoundError(
            f"Discharge notes not found at {discharge_path}. "
            "Download MIMIC-IV-Note from PhysioNet."
        )
    if not admissions_path.exists():
        raise FileNotFoundError(f"MIMIC admissions not found at {admissions_path}.")
    if not diagnoses_path.exists():
        raise FileNotFoundError(f"MIMIC diagnoses not found at {diagnoses_path}.")

    discharge = _reservoir_sample_discharge(discharge_path, max_rows=max_rows, seed=random_seed)

    admissions = pd.read_csv(
        admissions_path,
        compression="gzip",
        usecols=["subject_id", "hadm_id"],
    )

    merged = discharge.merge(admissions, on=["subject_id", "hadm_id"], how="inner")
    merged = merged.dropna(subset=["text"])
    merged = merged[merged["text"].str.strip().astype(bool)]
    merged["note_id"] = merged["note_id"].astype(str)
    merged["note_type"] = merged["note_type"].fillna("DS").astype(str)

    if merged.empty:
        raise ValueError("No discharge notes loaded after merge with admissions.")

    hadm_ids = merged["hadm_id"].unique()
    diagnoses = pd.read_csv(
        diagnoses_path,
        compression="gzip",
        usecols=["subject_id", "hadm_id", "seq_num", "icd_code", "icd_version"],
    )
    diagnoses = diagnoses[diagnoses["hadm_id"].isin(hadm_ids)]

    ground_truth = build_graded_ground_truth(
        merged,
        diagnoses,
        primary_diagnosis_only=primary_diagnosis_only,
        include_partial_labels=require_text_match,
    )

    notes = merged[["note_id", "subject_id", "hadm_id", "text", "note_type"]].reset_index(drop=True)
    return MimicCorpus(notes=notes, ground_truth=ground_truth)


def load_notes(
    max_rows: int = 2000,
    random_seed: int = 42,
    primary_diagnosis_only: bool = True,
    require_text_match: bool = True,
) -> MimicCorpus:
    """Entry point used by the Streamlit app."""
    return load_mimic_notes(
        max_rows=max_rows,
        random_seed=random_seed,
        primary_diagnosis_only=primary_diagnosis_only,
        require_text_match=require_text_match,
    )
