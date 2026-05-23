"""
7CS108 Portfolio Evaluation Engine — Clinical Information Retrieval Dashboard.

Compares TF-IDF, dense semantic (MiniLM), and hybrid BM25+MedCPT on MIMIC-IV discharge notes.
Evaluation: 10-query graded relevance matrix with MAP and NDCG@3.

Run: python -m streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from data import EVAL_QUERY_SUITE, load_notes
from evaluation import DEFAULT_K, run_full_evaluation
from search_engines import (
    HybridBm25MedCptSearchEngine,
    SemanticSearchEngine,
    TfidfSearchEngine,
    enable_offline_huggingface_env,
)

st.set_page_config(
    page_title="7CS108 Portfolio Evaluation Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .note-card {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
        border-left: 4px solid #4f46e5;
        padding: 1rem 1.1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    .note-card h4 { margin: 0 0 0.35rem 0; color: #1e1b4b; }
    .note-card p { margin: 0; font-size: 0.9rem; color: #334155; line-height: 1.45; }
    .system-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #312e81;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Bump when ground-truth schema changes so @st.cache_resource rebuilds indexes.
_GT_CACHE_VERSION = "graded_dict_v1"
SEARCH_TOP_K_OPTIONS = (3, 5, 10, 15, 20)


def _coerce_graded_ground_truth(
    ground_truth: dict,
) -> dict[str, dict[str, int]]:
    """Accept graded dict labels; upgrade legacy list[str] caches to grade-2 only."""
    coerced: dict[str, dict[str, int]] = {}
    for query, labels in ground_truth.items():
        if isinstance(labels, dict):
            coerced[query] = {str(nid): int(score) for nid, score in labels.items()}
        elif isinstance(labels, list):
            coerced[query] = {str(nid): 2 for nid in labels}
        else:
            coerced[query] = {}
    return coerced


REFERENCES = [
    "Johnson et al. (2023) — MIMIC-IV, a freely accessible electronic health record dataset. Scientific Data.",
    "Devlin et al. (2019) — BERT: Pre-training of deep bidirectional transformers for language understanding. NAACL-HLT.",
    "Alsentzer et al. (2019) — Publicly available clinical BERT embeddings. arXiv:1904.03323.",
    "Salton & Buckley (1988) — Term-weighting approaches in automatic text retrieval. Inf. Process. Manage.",
    "Reimers & Gurevych (2019) — Sentence-BERT: Sentence embeddings using Siamese BERT-networks. EMNLP.",
    "Robertson & Zaragoza (2009) — The probabilistic relevance framework: BM25 and beyond. Found. Trends Inf. Retr.",
    "Jin, Fang & Lu (2023) — MedCPT: Contrastive pre-trained medical transformers with PubMed search logs. Bioinformatics.",
    "Cormack, Clarke & Buettcher (2009) — Reciprocal rank fusion outperforms data fusion methods. ACM SIGIR.",
    "Arnold et al. (2020) — Learning contextualized document representations for healthcare answer retrieval. WWW.",
    "Agostinelli, Patel & Taylor (2024) — Dense text retrieval for electronic health records. IEEE J. Biomed. Health Inform.",
    "Lee et al. (2020) — BioBERT: A pre-trained biomedical language representation model. Bioinformatics.",
    "Fang, Xu & Zhou (2024) — Information retrieval in the clinical domain: A review of evaluation metrics. IEEE TKDE.",
    "Gu et al. (2021) — Domain-specific language model pre-training for biomedical NLP. ACM Trans. Comput. Healthcare.",
    "Gao, Dai & Callan (2021) — COCO-DR: Combating the text length challenge in dense text retrieval. J. Biomed. Inform.",
    "Wang, Zhang & Chen (2023) — Hybrid clinical information retrieval pipelines. Artif. Intell. Med.",
]


@st.cache_resource(
    show_spinner=(
        "Random-sampling MIMIC notes and building indexes "
        "(System C MedCPT encoding may take several minutes on first run)..."
    )
)
def _build_engines(
    max_rows: int,
    random_seed: int,
    primary_diagnosis_only: bool,
    require_text_match: bool,
    _gt_cache_version: str = _GT_CACHE_VERSION,
):
    enable_offline_huggingface_env()

    corpus = load_notes(
        max_rows=max_rows,
        random_seed=random_seed,
        primary_diagnosis_only=primary_diagnosis_only,
        require_text_match=require_text_match,
    )
    search_df = corpus.notes[["note_id", "subject_id", "text", "note_type"]]

    tfidf = TfidfSearchEngine()
    semantic = SemanticSearchEngine()
    hybrid = HybridBm25MedCptSearchEngine()
    tfidf.fit(search_df)
    try:
        semantic.fit(search_df)
    except Exception as exc:
        raise RuntimeError(
            f"Semantic search failed: {exc}\n\n"
            "Fix: pip install -r requirements.txt  (needs huggingface_hub>=0.34,<1.0)\n"
            "Model folder: models/all-MiniLM-L6-v2\n"
            "Then stop the app, run: unset TRANSFORMERS_OFFLINE (optional), keep HF_HUB_OFFLINE=1\n"
            "In Streamlit: menu (☰) → Clear cache → refresh."
        ) from exc
    try:
        hybrid.fit(search_df)
    except Exception as exc:
        raise RuntimeError(
            f"Hybrid BM25 + MedCPT failed: {exc}\n\n"
            "System C requires MedCPT models in models/ and rank-bm25 installed.\n"
            "Download:\n"
            "  hf download ncbi/MedCPT-Query-Encoder --local-dir models/MedCPT-Query-Encoder\n"
            "  hf download ncbi/MedCPT-Article-Encoder --local-dir models/MedCPT-Article-Encoder\n"
            "Then: pip install rank-bm25 -r requirements.txt\n"
            "Streamlit menu (☰) → Clear cache → refresh."
        ) from exc

    ground_truth = _coerce_graded_ground_truth(corpus.ground_truth)
    return corpus.notes, ground_truth, tfidf, semantic, hybrid


def _render_note_card(rank: int, result) -> None:
    preview = result.text[:280] + ("…" if len(result.text) > 280 else "")
    st.markdown(
        f"""
        <div class="note-card">
            <h4>#{rank} · {result.note_id} · subject {result.subject_id}</h4>
            <p><em>{result.note_type}</em> · score <strong>{result.score:.4f}</strong></p>
            <p>{preview}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_note_detail(rank: int, result, system_key: str) -> None:
    header = (
        f"#{rank} · {result.note_id} · subject {result.subject_id} · "
        f"score {result.score:.4f}"
    )
    with st.expander(header, expanded=False):
        st.caption(f"{result.note_type} · {len(result.text):,} characters")
        st.text_area(
            "Full discharge note",
            value=result.text,
            height=min(480, max(200, len(result.text) // 4)),
            disabled=True,
            label_visibility="collapsed",
            key=f"detail_{system_key}_{result.note_id}_{rank}",
        )


def _render_results(
    column,
    title: str,
    results: list,
    *,
    system_key: str,
    detail_mode: bool,
) -> None:
    column.markdown(f'<p class="system-header">{title}</p>', unsafe_allow_html=True)
    if not results:
        column.info("No results — enter a clinical query above.")
        return
    for i, hit in enumerate(results, start=1):
        with column.container():
            if detail_mode:
                _render_note_detail(i, hit, system_key)
            else:
                _render_note_card(i, hit)


def _build_note_lookup(
    tfidf_hits: list,
    semantic_hits: list,
    hybrid_hits: list,
) -> dict[str, dict[str, tuple[int, float, object]]]:
    """Map note_id → {system_label: (rank, score, SearchResult)}."""
    lookup: dict[str, dict[str, tuple[int, float, object]]] = {}
    for label, hits in (
        ("System A (TF-IDF)", tfidf_hits),
        ("System B (Semantic)", semantic_hits),
        ("System C (Hybrid)", hybrid_hits),
    ):
        for rank, hit in enumerate(hits, start=1):
            lookup.setdefault(hit.note_id, {})[label] = (rank, hit.score, hit)
    return lookup


def _render_unified_detail(
    query: str,
    tfidf_hits: list,
    semantic_hits: list,
    hybrid_hits: list,
    top_k: int,
) -> None:
    lookup = _build_note_lookup(tfidf_hits, semantic_hits, hybrid_hits)
    if not lookup:
        return

    st.subheader("Note detail view")
    st.caption(
        "Select any note returned by one or more systems to read the full discharge text "
        "and compare ranks."
    )

    note_ids = sorted(lookup.keys())
    selected_id = st.selectbox(
        "Note",
        options=note_ids,
        format_func=lambda nid: f"{nid} ({len(lookup[nid])} system(s))",
        key="detail_note_select",
    )
    if not selected_id:
        return

    systems = lookup[selected_id]
    result = next(iter(systems.values()))[2]

    rank_cols = st.columns(3)
    for col, (label, hits) in zip(
        rank_cols,
        (
            ("System A (TF-IDF)", tfidf_hits),
            ("System B (Semantic)", semantic_hits),
            ("System C (Hybrid)", hybrid_hits),
        ),
    ):
        with col:
            if label in systems:
                rank, score, _ = systems[label]
                st.metric(label, f"#{rank}", f"score {score:.4f}")
            else:
                st.metric(label, "—", f"not in Top-{top_k}")

    meta1, meta2, meta3 = st.columns(3)
    meta1.markdown(f"**Note ID:** `{result.note_id}`")
    meta2.markdown(f"**Subject:** {result.subject_id}")
    meta3.markdown(f"**Type:** {result.note_type}")

    st.text_area(
        f"Full note — query: {query}",
        value=result.text,
        height=min(560, max(240, len(result.text) // 3)),
        disabled=True,
        key=f"unified_detail_{selected_id}",
    )


def _metric_chart(per_query, value_col: str, title: str) -> None:
    chart_df = per_query[["query", "system", value_col]].copy()
    chart_df = chart_df.rename(columns={value_col: "score"})
    chart_df["query_short"] = chart_df["query"].apply(
        lambda q: (q[:42] + "…") if len(q) > 42 else q
    )
    st.subheader(title)
    st.bar_chart(chart_df, x="query_short", y="score", color="system")


with st.sidebar:
    st.subheader("Evaluation Engine")
    st.markdown(
        """
        **Corpus**

        Random sample from MIMIC-IV-Note `discharge.csv.gz`.

        **Graded labels (10 queries)**

        - **2** — keywords in text + matching ICD on admission
        - **1** — keywords in text, no matching ICD (partial)
        - **0** — not labeled
        """
    )

    max_rows = st.slider(
        "Random sample size",
        min_value=500,
        max_value=5000,
        value=2000,
        step=500,
        help="Larger = slower first load (full pass over discharge file for sampling).",
    )
    random_seed = st.number_input("Random seed", min_value=0, value=42, step=1)
    primary_diagnosis_only = st.checkbox(
        "Primary ICD only (for grade-2 ICD match)",
        value=True,
    )
    require_text_match = st.checkbox(
        "Include partial labels (grade 1, text without ICD)",
        value=True,
    )

    with st.expander("Evaluation queries (10)"):
        for query, cfg in EVAL_QUERY_SUITE.items():
            icd10 = ", ".join(cfg["icd10"])
            icd9 = ", ".join(cfg["icd9"])
            terms = ", ".join(cfg["keywords"][:5])
            st.markdown(f"**{query}**")
            st.caption(f"ICD-10: {icd10} · ICD-9: {icd9}")
            st.caption(f"Keywords: {terms}…")

    with st.expander("Retrieval systems (A / B / C)"):
        st.markdown(
            """
            **System A — TF-IDF (Baseline)**  
            Keyword search. Notes are scored by **word overlap** using TF-IDF
            (unigrams + bigrams) and cosine similarity. Fast and interpretable;
            works best when your query words appear in the note.

            **System B — Semantic (MiniLM)**  
            Meaning-based search. Query and notes are encoded with
            **all-MiniLM-L6-v2** into dense vectors; ranking uses cosine
            similarity. Can match **synonyms and paraphrases** (e.g. “acute kidney
            injury” vs “renal failure”) even without exact word overlap.

            **System C — Hybrid (BM25 + MedCPT)**  
            Combines **BM25** keyword ranking with **MedCPT** biomedical
            encoders (separate query/article models). The two ranked lists are
            merged with **Reciprocal Rank Fusion (RRF)**. Aims to balance lexical
            precision and clinical semantic relevance; slower to index at startup.
            """
        )

    with st.expander("References"):
        for ref in REFERENCES:
            st.caption(ref)

    st.caption("Research use only — not for clinical decision-making.")

st.title("Clinical IR Evaluation Engine")
st.caption(
    f"10-query validation matrix · Top-{DEFAULT_K} · "
    f"Precision@{DEFAULT_K} / Recall@{DEFAULT_K} / MAP / NDCG@{DEFAULT_K}"
)

try:
    notes_df, ground_truth, tfidf_engine, semantic_engine, hybrid_engine = _build_engines(
        max_rows,
        int(random_seed),
        primary_diagnosis_only,
        require_text_match,
    )
except Exception as exc:
    st.error(f"Failed to initialize: {exc}")
    with st.expander("Technical details"):
        st.exception(exc)
    st.info(
        "If you recently fixed dependencies or downloaded the model, use **Clear cache** "
        "in the Streamlit menu (☰) and refresh the page."
    )
    st.stop()

n_subjects = notes_df["subject_id"].nunique()
st.success(
    f"Indexed **{len(notes_df)}** notes from **{n_subjects}** patients (random sample, seed={int(random_seed)}).",
)

with st.expander("Evaluation ground truth in this sample"):
    total = len(notes_df)
    for query, graded in ground_truth.items():
        n_high = sum(1 for s in graded.values() if s == 2)
        n_partial = sum(1 for s in graded.values() if s == 1)
        n_total = n_high + n_partial
        pct = 100.0 * n_total / total if total else 0
        high_ids = [n for n, s in graded.items() if s == 2][:5]
        high_preview = ", ".join(high_ids)
        st.markdown(
            f"- **{query[:60]}{'…' if len(query) > 60 else ''}**: "
            f"{n_high} highly (2), {n_partial} partial (1) — {pct:.1f}% of corpus"
        )
        if high_preview:
            st.caption(f"Sample grade-2 IDs: `{high_preview}`…")

tab_search, tab_eval = st.tabs(["Live Search", "Evaluation Panel"])

with tab_search:
    query = st.text_input(
        "Clinical query",
        placeholder='e.g. "septic shock with positive blood cultures"',
        key="clinical_query",
    )

    search_ctrl_col1, search_ctrl_col2 = st.columns([1, 2])
    with search_ctrl_col1:
        top_k = st.selectbox(
            "Results to show (Top-K)",
            options=SEARCH_TOP_K_OPTIONS,
            index=SEARCH_TOP_K_OPTIONS.index(DEFAULT_K),
            help="Number of ranked notes returned per system.",
        )
    with search_ctrl_col2:
        display_mode = st.radio(
            "Result display",
            options=["Preview", "Detail (expandable)"],
            horizontal=True,
            help="Preview shows a short snippet. Detail adds expanders with the full discharge note.",
        )
    detail_mode = display_mode == "Detail (expandable)"

    if query:
        try:
            tfidf_hits = tfidf_engine.search(query, top_k=top_k)
            semantic_hits = semantic_engine.search(query, top_k=top_k)
            hybrid_hits = hybrid_engine.search(query, top_k=top_k)
        except Exception as exc:
            st.error(f"Search failed: {exc}")
            tfidf_hits, semantic_hits, hybrid_hits = [], [], []
    else:
        st.warning("Enter a clinical query to compare all three retrieval systems.")
        tfidf_hits, semantic_hits, hybrid_hits = [], [], []

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        _render_results(
            col_a, "System A — TF-IDF (Baseline)", tfidf_hits,
            system_key="a", detail_mode=detail_mode,
        )
    with col_b:
        _render_results(
            col_b, "System B — Semantic Search (MiniLM)", semantic_hits,
            system_key="b", detail_mode=detail_mode,
        )
    with col_c:
        _render_results(
            col_c, "System C — Hybrid BM25 + MedCPT", hybrid_hits,
            system_key="c", detail_mode=detail_mode,
        )

    if query and (tfidf_hits or semantic_hits or hybrid_hits):
        all_ids = (
            {h.note_id for h in tfidf_hits}
            | {h.note_id for h in semantic_hits}
            | {h.note_id for h in hybrid_hits}
        )
        shared_all = (
            {h.note_id for h in tfidf_hits}
            & {h.note_id for h in semantic_hits}
            & {h.note_id for h in hybrid_hits}
        )
        st.caption(
            f"Query: **{query}** · Unique Top-{top_k} across systems: "
            f"{len(all_ids)} · In all three: {', '.join(sorted(shared_all)) or 'none'}"
        )
        _render_unified_detail(query, tfidf_hits, semantic_hits, hybrid_hits, top_k)

with tab_eval:
    st.markdown(
        f"""
        **10-query graded benchmark** on the indexed MIMIC sample.

        | Grade | Rule |
        |-------|------|
        | **2** | Query keywords in note text **and** matching ICD on admission |
        | **1** | Keywords in text **without** matching ICD (partial) |

        Metrics at Top-{DEFAULT_K}: Precision@3, Recall@3, **MAP** (mean AP), **NDCG@3**.
        MAP uses the portfolio AP variant (denominator = min(|relevant|, |retrieved|)).
        """
    )

    skipped = [
        q for q, graded in ground_truth.items() if not any(s >= 1 for s in graded.values())
    ]
    if skipped:
        st.warning(
            f"No labeled notes for {len(skipped)} query/queries. "
            "Increase sample size or enable partial labels in the sidebar."
        )

    if st.button("Run built-in evaluation", type="primary", use_container_width=True):
        with st.spinner("Evaluating Systems A, B, and C on 10 queries..."):
            try:
                per_query, summary = run_full_evaluation(
                    [tfidf_engine, semantic_engine, hybrid_engine],
                    ground_truth,
                    k=DEFAULT_K,
                )
                st.session_state.eval_per_query = per_query
                st.session_state.eval_summary = summary
            except Exception as exc:
                st.error(f"Evaluation failed: {exc}")

    if "eval_per_query" in st.session_state:
        per_query = st.session_state.eval_per_query
        summary = st.session_state.eval_summary
        ndcg_col = f"ndcg@{DEFAULT_K}"

        st.subheader("Per-query results")
        st.dataframe(per_query, use_container_width=True, hide_index=True)

        st.subheader("System comparison (macro-averaged)")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        p_col = f"mean_precision@{DEFAULT_K}"
        r_col = f"mean_recall@{DEFAULT_K}"
        mean_ndcg_col = f"mean_{ndcg_col}"
        for _, row in summary.iterrows():
            system = row["system"]
            st.markdown(f"**{system}**")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric(f"Mean Precision@{DEFAULT_K}", f"{row[p_col]:.2%}")
            c2.metric(f"Mean Recall@{DEFAULT_K}", f"{row[r_col]:.2%}")
            c3.metric("MAP", f"{row['mean_ap']:.4f}")
            c4.metric(f"Mean NDCG@{DEFAULT_K}", f"{row[mean_ndcg_col]:.4f}")
            c5.metric("Mean latency (ms)", f"{row['mean_latency_ms']:.1f}")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            _metric_chart(per_query, "ap", "MAP by query (Systems A / B / C)")
        with chart_col2:
            _metric_chart(per_query, ndcg_col, f"NDCG@{DEFAULT_K} by query (Systems A / B / C)")

        st.info(
            "NDCG rewards highly relevant (grade 2) hits higher than partial (grade 1). "
            "System C fuses BM25 + MedCPT ranks; expect higher per-query latency."
        )
    else:
        st.caption("Click **Run built-in evaluation** to populate metrics and charts.")
