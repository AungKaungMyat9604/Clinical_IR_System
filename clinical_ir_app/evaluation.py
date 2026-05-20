"""
Evaluation metrics for the Clinical IR Evaluation Engine.

Precision@K, Recall@K, MAP (AP), and NDCG@K on graded MIMIC labels from data.py.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from data import EVAL_QUERY_SUITE

if TYPE_CHECKING:
    from search_engines import SearchEngine

DEFAULT_K = 3

EVAL_QUERIES: list[str] = list(EVAL_QUERY_SUITE.keys())


def calculate_average_precision(retrieved_ids, ground_truth_relevant_ids):
    """Calculates Average Precision (AP) for a single query."""
    hits = 0
    sum_precisions = 0.0
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in ground_truth_relevant_ids:
            hits += 1
            precision_at_i = hits / (i + 1)
            sum_precisions += precision_at_i
    if len(ground_truth_relevant_ids) == 0:
        return 0.0
    return sum_precisions / min(len(ground_truth_relevant_ids), len(retrieved_ids))


def calculate_ndcg(retrieved_ids, ground_truth_relevance_dict, k=3):
    """
    Calculates Normalized Discounted Cumulative Gain (NDCG) at K.
    ground_truth_relevance_dict maps doc_id to an intensity score (e.g., 2=Highly, 1=Partially)
    """
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k]):
        rel = ground_truth_relevance_dict.get(doc_id, 0)
        dcg += (2**rel - 1) / np.log2(i + 2)

    sorted_rels = sorted(ground_truth_relevance_dict.values(), reverse=True)
    idcg = 0.0
    for i, rel in enumerate(sorted_rels[:k]):
        idcg += (2**rel - 1) / np.log2(i + 2)

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def _preview_ids(
    graded: dict[str, int],
    min_score: int | None = None,
    exact_score: int | None = None,
    limit: int = 15,
) -> str:
    if exact_score is not None:
        ids = [nid for nid, s in graded.items() if s == exact_score]
    elif min_score is not None:
        ids = [nid for nid, s in graded.items() if s >= min_score]
    else:
        ids = list(graded.keys())
    if not ids:
        return "(none)"
    shown = ids[:limit]
    suffix = "…" if len(ids) > limit else ""
    return ", ".join(shown) + suffix


def coerce_graded_ground_truth(
    ground_truth: dict,
) -> dict[str, dict[str, int]]:
    """Normalize graded dict labels; upgrade legacy list[str] entries."""
    coerced: dict[str, dict[str, int]] = {}
    for query, labels in ground_truth.items():
        if isinstance(labels, dict):
            coerced[query] = {str(nid): int(score) for nid, score in labels.items()}
        elif isinstance(labels, list):
            coerced[query] = {str(nid): 2 for nid in labels}
        else:
            coerced[query] = {}
    return coerced


def relevant_ids_binary(graded: dict[str, int], min_score: int = 1) -> list[str]:
    """Note IDs with relevance grade >= min_score."""
    return [nid for nid, score in graded.items() if score >= min_score]


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Precision@K = |relevant ∩ top-K| / K"""
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / k


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Recall@K = |relevant ∩ top-K| / |relevant|"""
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / len(relevant_ids)


def _timed_search(engine: "SearchEngine", query: str, k: int) -> tuple[list[str], float]:
    start = time.perf_counter()
    results = engine.search(query, top_k=k)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return [r.note_id for r in results], elapsed_ms


def evaluate_engine(
    engine: "SearchEngine",
    ground_truth: dict[str, dict[str, int]],
    k: int = DEFAULT_K,
) -> pd.DataFrame:
    """Evaluate one engine on all labeled queries."""
    rows: list[dict] = []
    ndcg_col = f"ndcg@{k}"

    for query, graded in ground_truth.items():
        retrieved_ids, latency_ms = _timed_search(engine, query, k)
        binary_relevant = relevant_ids_binary(graded, min_score=1)
        n_high = sum(1 for s in graded.values() if s == 2)
        n_partial = sum(1 for s in graded.values() if s == 1)
        n_rel = len(binary_relevant)

        rows.append(
            {
                "system": engine.name,
                "query": query,
                f"precision@{k}": precision_at_k(retrieved_ids, binary_relevant, k),
                f"recall@{k}": recall_at_k(retrieved_ids, binary_relevant, k),
                "ap": calculate_average_precision(retrieved_ids, binary_relevant),
                ndcg_col: calculate_ndcg(retrieved_ids, graded, k=k),
                "latency_ms": round(latency_ms, 2),
                "n_highly_relevant": n_high,
                "n_partially_relevant": n_partial,
                "n_relevant_in_corpus": n_rel,
                "retrieved": ", ".join(retrieved_ids) if retrieved_ids else "(none)",
                "relevant_high": _preview_ids(graded, min_score=2),
                "relevant_partial": _preview_ids(graded, exact_score=1),
            }
        )

    return pd.DataFrame(rows)


def summarize_evaluation(per_query_df: pd.DataFrame, k: int = DEFAULT_K) -> pd.DataFrame:
    """Macro-average Precision@K, Recall@K, MAP, NDCG@K, and mean latency per system."""
    p_col = f"precision@{k}"
    r_col = f"recall@{k}"
    ndcg_col = f"ndcg@{k}"

    summary = (
        per_query_df.groupby("system", as_index=False)
        .agg(
            **{
                f"mean_precision@{k}": (p_col, "mean"),
                f"mean_recall@{k}": (r_col, "mean"),
                "mean_ap": ("ap", "mean"),
                f"mean_{ndcg_col}": (ndcg_col, "mean"),
                "mean_latency_ms": ("latency_ms", "mean"),
            }
        )
        .round(4)
    )
    summary["mean_latency_ms"] = summary["mean_latency_ms"].round(2)
    return summary


def run_full_evaluation(
    engines: list["SearchEngine"],
    ground_truth: dict[str, dict[str, int]],
    k: int = DEFAULT_K,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate all engines; skip queries with no graded labels in the indexed sample."""
    if not engines:
        raise ValueError("At least one search engine is required for evaluation.")

    ground_truth = coerce_graded_ground_truth(ground_truth)
    filtered = {
        q: graded for q, graded in ground_truth.items() if any(s >= 1 for s in graded.values())
    }
    if not filtered:
        raise ValueError(
            "No relevant notes in the indexed sample for any evaluation query. "
            "Increase the note sample size in the sidebar or check ICD joins."
        )

    frames = [evaluate_engine(engine, filtered, k=k) for engine in engines]
    per_query = pd.concat(frames, ignore_index=True)
    summary = summarize_evaluation(per_query, k=k)
    return per_query, summary
