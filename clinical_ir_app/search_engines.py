"""
Retrieval engines for clinical note search.

System A: lexical TF-IDF + cosine similarity (Robertson & Zaragoza, 2009).
System B: dense sentence embeddings + cosine similarity (Agostinelli et al., 2024).
System C: BM25Okapi + MedCPT dual encoders fused with RRF (Robertson & Zaragoza, 2009).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Offline copy: place files here after `hf download` (see requirements.txt)
_DEFAULT_LOCAL_MODEL_DIR = Path(__file__).resolve().parent / "models" / "all-MiniLM-L6-v2"
_HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
_REQUIRED_MODEL_FILES = ("config.json", "model.safetensors", "tokenizer.json", "modules.json")
_MEDCPT_QUERY_DIR = Path(__file__).resolve().parent / "models" / "MedCPT-Query-Encoder"
_MEDCPT_ARTICLE_DIR = Path(__file__).resolve().parent / "models" / "MedCPT-Article-Encoder"
_MEDCPT_QUERY_HF = "ncbi/MedCPT-Query-Encoder"
_MEDCPT_ARTICLE_HF = "ncbi/MedCPT-Article-Encoder"
_MEDCPT_REQUIRED_FILES = ("config.json", "model.safetensors", "tokenizer.json")
RRF_K_DEFAULT = 60
RRF_CANDIDATE_POOL = 50


def _local_model_ready(path: Path) -> bool:
    return path.is_dir() and all((path / name).is_file() for name in _REQUIRED_MODEL_FILES)


def resolve_embedding_model_path(model_name: str | None = None) -> str:
    """
    Prefer a fully downloaded local folder for offline use.

    Order: EMBEDDING_MODEL_PATH env → clinical_ir_app/models/all-MiniLM-L6-v2 → Hugging Face id.
    """
    if model_name and Path(model_name).is_dir():
        return str(Path(model_name).resolve())

    env_path = os.environ.get("EMBEDDING_MODEL_PATH", "").strip()
    if env_path and Path(env_path).is_dir():
        return str(Path(env_path).resolve())

    if _local_model_ready(_DEFAULT_LOCAL_MODEL_DIR):
        return str(_DEFAULT_LOCAL_MODEL_DIR)

    return model_name or _HF_MODEL_ID


def _local_medcpt_ready(path: Path) -> bool:
    return path.is_dir() and all((path / name).is_file() for name in _MEDCPT_REQUIRED_FILES)


def _medcpt_missing_files_message(query_path: Path, article_path: Path) -> str | None:
    """Return an error message if either local MedCPT folder is incomplete."""
    problems: list[str] = []
    for label, path in (("Query", query_path), ("Article", article_path)):
        if not path.is_dir():
            problems.append(f"  {label}: folder missing ({path})")
            continue
        missing = [f for f in _MEDCPT_REQUIRED_FILES if not (path / f).is_file()]
        if missing:
            problems.append(f"  {label} ({path}): missing {', '.join(missing)}")
    if not problems:
        return None
    return (
        "MedCPT local model folders are incomplete.\n"
        + "\n".join(problems)
        + "\n\nRequired per folder: config.json, model.safetensors, tokenizer.json\n"
        "If hf download fails, use curl (see sidebar) for each missing file."
    )


def resolve_medcpt_query_path() -> str:
    env = os.environ.get("MEDCPT_QUERY_PATH", "").strip()
    if env and Path(env).is_dir():
        return str(Path(env).resolve())
    if _local_medcpt_ready(_MEDCPT_QUERY_DIR):
        return str(_MEDCPT_QUERY_DIR)
    return _MEDCPT_QUERY_HF


def resolve_medcpt_article_path() -> str:
    env = os.environ.get("MEDCPT_ARTICLE_PATH", "").strip()
    if env and Path(env).is_dir():
        return str(Path(env).resolve())
    if _local_medcpt_ready(_MEDCPT_ARTICLE_DIR):
        return str(_MEDCPT_ARTICLE_DIR)
    return _MEDCPT_ARTICLE_HF


def _tokenize_for_bm25(text: str) -> list[str]:
    return str(text).lower().split()


def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = RRF_K_DEFAULT,
) -> list[tuple[str, float]]:
    """
    Fuse multiple ranked lists with Reciprocal Rank Fusion.

    score(doc) = sum_r 1 / (k + rank_r(doc))  over retrievers r (1-based ranks).
    """
    scores: dict[str, float] = {}
    for ranked_ids in rankings:
        for rank, note_id in enumerate(ranked_ids, start=1):
            scores[note_id] = scores.get(note_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


@dataclass(frozen=True)
class SearchResult:
    """One ranked retrieval hit."""

    note_id: str
    subject_id: int
    text: str
    note_type: str
    score: float


class SearchEngine(Protocol):
    """Common interface for System A and System B."""

    name: str

    def fit(self, df: pd.DataFrame) -> None: ...

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]: ...


class TfidfSearchEngine:
    """
    System A — keyword-based TF-IDF retrieval.

    Uses unigrams and bigrams to capture short clinical phrases (e.g. "renal failure").
    """

    name = "System A (TF-IDF)"

    def __init__(self) -> None:
        self._vectorizer: TfidfVectorizer | None = None
        self._doc_matrix = None
        self._df: pd.DataFrame | None = None

    def fit(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Cannot fit TF-IDF engine on an empty DataFrame.")
        self._df = df.reset_index(drop=True)
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1,
        )
        self._doc_matrix = self._vectorizer.fit_transform(self._df["text"].astype(str))

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if not query or not str(query).strip():
            return []
        if self._vectorizer is None or self._doc_matrix is None or self._df is None:
            raise RuntimeError("TfidfSearchEngine.fit() must be called before search().")

        q_vec = self._vectorizer.transform([str(query).strip()])
        scores = cosine_similarity(q_vec, self._doc_matrix).flatten()
        return _rank_results(self._df, scores, top_k)


class SemanticSearchEngine:
    """
    System B — dense vector semantic search.

    Default model: sentence-transformers/all-MiniLM-L6-v2 (384-dim, fast CPU inference).

    Clinical upgrade options (slower, higher quality on biomedical text):
      - "emilyalsentzer/Bio_ClinicalBERT"  (Alsentzer et al., 2019)
      - "dmis-lab/biobert-v1.1"            (Lee et al., 2020; BioBERT)

    Swap model_name in __init__ and use SentenceTransformer-compatible wrappers or
    a mean-pooled transformers pipeline for BERT-family checkpoints.
    """

    name = "System B (Semantic)"

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = resolve_embedding_model_path(model_name)
        self._model = None
        self._doc_embeddings: np.ndarray | None = None
        self._df: pd.DataFrame | None = None

    def fit(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Cannot fit semantic engine on an empty DataFrame.")
        self._df = df.reset_index(drop=True)
        texts = self._df["text"].astype(str).tolist()

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            msg = str(exc)
            if "huggingface-hub" in msg or "huggingface_hub" in msg:
                raise ImportError(
                    "Dependency conflict: transformers needs huggingface_hub>=0.34,<1.0. "
                    "Run: pip install 'huggingface_hub>=0.34.0,<1.0' -r requirements.txt"
                ) from exc
            raise ImportError(
                "sentence-transformers is required for System B. "
                "Install with: pip install -r requirements.txt"
            ) from exc

        model_path = Path(self._model_name)
        use_local_files = model_path.is_dir()

        if use_local_files and not _local_model_ready(model_path):
            missing = [f for f in _REQUIRED_MODEL_FILES if not (model_path / f).is_file()]
            raise RuntimeError(
                f"Local model at {model_path} is incomplete. Missing: {', '.join(missing)}. "
                "Re-download with:\n"
                f"  hf download {_HF_MODEL_ID} --local-dir {_DEFAULT_LOCAL_MODEL_DIR}"
            )

        try:
            self._model = SentenceTransformer(
                self._model_name,
                local_files_only=use_local_files,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model '{self._model_name}'.\n"
                f"Cause: {type(exc).__name__}: {exc}\n"
                "If the model is already downloaded, run: pip install 'huggingface_hub>=0.34.0,<1.0'\n"
                "Then restart Streamlit and use menu → Clear cache."
            ) from exc

        self._doc_embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if not query or not str(query).strip():
            return []
        if self._model is None or self._doc_embeddings is None or self._df is None:
            raise RuntimeError("SemanticSearchEngine.fit() must be called before search().")

        q_emb = self._model.encode(
            [str(query).strip()],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        # L2-normalized vectors: dot product equals cosine similarity
        scores = np.dot(self._doc_embeddings, q_emb.T).flatten()
        return _rank_results(self._df, scores, top_k)


class HybridBm25MedCptSearchEngine:
    """
    System C — hybrid retrieval: BM25Okapi + MedCPT (Query/Article encoders) + RRF.

    Robertson & Zaragoza (2009) for BM25; MedCPT (NCBI) for clinical dense retrieval.
    """

    name = "System C (Hybrid BM25 + MedCPT)"

    def __init__(self, rrf_k: int = RRF_K_DEFAULT) -> None:
        self._rrf_k = rrf_k
        self._bm25 = None
        self._query_model = None
        self._query_tokenizer = None
        self._article_model = None
        self._article_tokenizer = None
        self._article_embeddings: np.ndarray | None = None
        self._df: pd.DataFrame | None = None
        self._query_path = resolve_medcpt_query_path()
        self._article_path = resolve_medcpt_article_path()

    def fit(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Cannot fit hybrid engine on an empty DataFrame.")

        self._df = df.reset_index(drop=True)
        texts = self._df["text"].astype(str).tolist()
        note_types = self._df["note_type"].astype(str).tolist()

        try:
            from rank_bm25 import BM25Okapi
        except ImportError as exc:
            raise ImportError(
                "rank-bm25 is required for System C. Install with: pip install rank-bm25"
            ) from exc

        corpus_tokens = [_tokenize_for_bm25(t) for t in texts]
        self._bm25 = BM25Okapi(corpus_tokens)

        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError as exc:
            raise ImportError(
                "transformers and torch are required for System C. "
                "Install with: pip install -r requirements.txt"
            ) from exc

        query_path = Path(self._query_path)
        article_path = Path(self._article_path)
        use_local = query_path.is_dir() and article_path.is_dir()

        if use_local:
            missing_msg = _medcpt_missing_files_message(query_path, article_path)
            if missing_msg:
                raise RuntimeError(missing_msg)

        try:
            self._query_tokenizer = AutoTokenizer.from_pretrained(
                self._query_path, local_files_only=use_local
            )
            self._query_model = AutoModel.from_pretrained(
                self._query_path, local_files_only=use_local
            )
            self._article_tokenizer = AutoTokenizer.from_pretrained(
                self._article_path, local_files_only=use_local
            )
            self._article_model = AutoModel.from_pretrained(
                self._article_path, local_files_only=use_local
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load MedCPT models.\n"
                f"Query path: {self._query_path}\n"
                f"Article path: {self._article_path}\n"
                f"Cause: {type(exc).__name__}: {exc}"
            ) from exc

        self._query_model.eval()
        self._article_model.eval()

        self._article_embeddings = self._encode_medcpt_articles(
            note_types, texts, batch_size=16
        )

    def _encode_medcpt_articles(
        self,
        note_types: list[str],
        texts: list[str],
        batch_size: int = 16,
    ) -> np.ndarray:
        import torch

        pairs = [[nt or "DS", txt] for nt, txt in zip(note_types, texts)]
        all_embeddings: list[np.ndarray] = []

        with torch.no_grad():
            for start in range(0, len(pairs), batch_size):
                batch = pairs[start : start + batch_size]
                encoded = self._article_tokenizer(
                    batch,
                    truncation=True,
                    padding=True,
                    return_tensors="pt",
                    max_length=512,
                )
                out = self._article_model(**encoded)
                emb = out.last_hidden_state[:, 0, :].cpu().numpy()
                norms = np.linalg.norm(emb, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1, norms)
                all_embeddings.append(emb / norms)

        return np.vstack(all_embeddings).astype(np.float32)

    def _encode_medcpt_query(self, query: str) -> np.ndarray:
        import torch

        with torch.no_grad():
            encoded = self._query_tokenizer(
                [query],
                truncation=True,
                padding=True,
                return_tensors="pt",
                max_length=64,
            )
            out = self._query_model(**encoded)
            emb = out.last_hidden_state[:, 0, :].cpu().numpy()
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        return emb.astype(np.float32)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if not query or not str(query).strip():
            return []
        if (
            self._bm25 is None
            or self._article_embeddings is None
            or self._df is None
        ):
            raise RuntimeError("HybridBm25MedCptSearchEngine.fit() must be called before search().")

        n_docs = len(self._df)
        pool_k = min(RRF_CANDIDATE_POOL, n_docs)

        query_tokens = _tokenize_for_bm25(query)
        bm25_scores = self._bm25.get_scores(query_tokens)
        bm25_top = np.argsort(bm25_scores)[::-1][:pool_k]
        bm25_ids = [str(self._df.iloc[int(i)]["note_id"]) for i in bm25_top]

        q_emb = self._encode_medcpt_query(str(query).strip())
        medcpt_scores = np.dot(self._article_embeddings, q_emb.T).flatten()
        medcpt_top = np.argsort(medcpt_scores)[::-1][:pool_k]
        medcpt_ids = [str(self._df.iloc[int(i)]["note_id"]) for i in medcpt_top]

        fused = reciprocal_rank_fusion([bm25_ids, medcpt_ids], k=self._rrf_k)
        id_to_row = {str(row["note_id"]): row for _, row in self._df.iterrows()}

        results: list[SearchResult] = []
        for note_id, rrf_score in fused[:top_k]:
            if note_id not in id_to_row:
                continue
            row = id_to_row[note_id]
            results.append(
                SearchResult(
                    note_id=note_id,
                    subject_id=int(row["subject_id"]),
                    text=str(row["text"]),
                    note_type=str(row["note_type"]),
                    score=float(rrf_score),
                )
            )
        return results


def _rank_results(df: pd.DataFrame, scores: np.ndarray, top_k: int) -> list[SearchResult]:
    """Return top_k hits sorted by descending similarity score."""
    k = min(top_k, len(df))
    if k == 0:
        return []

    top_indices = np.argsort(scores)[::-1][:k]
    results: list[SearchResult] = []
    for idx in top_indices:
        row = df.iloc[int(idx)]
        results.append(
            SearchResult(
                note_id=str(row["note_id"]),
                subject_id=int(row["subject_id"]),
                text=str(row["text"]),
                note_type=str(row["note_type"]),
                score=float(scores[int(idx)]),
            )
        )
    return results
