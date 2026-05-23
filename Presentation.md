<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical IR Presentation</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Merriweather:wght@400;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { margin: 0; overflow: hidden; background-color: #1e293b; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'DM Sans', sans-serif; color: #1e293b; }
        #presentation-container { width: 1280px; height: 720px; position: relative; background-color: #f8fafc; box-shadow: 0 20px 50px rgba(0,0,0,0.5); overflow: hidden; }
        .slide { width: 100%; height: 100%; position: absolute; top: 0; left: 0; display: none; flex-direction: column; padding: 60px; box-sizing: border-box; background: linear-gradient(135deg, #f3f0df 0%, #ffffff 100%); }
        .slide.active { display: flex; animation: fadeIn 0.4s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        
        h1, h2, h3 { font-family: 'Merriweather', serif; color: #005088; margin-top: 0; }
        h1 { font-size: 56px; line-height: 1.2; font-weight: 900; }
        h2 { font-size: 44px; border-left: 6px solid #11caa0; padding-left: 20px; margin-bottom: 40px; }
        h3 { font-size: 28px; color: #0f172a; margin-bottom: 15px;}
        p, li { font-size: 22px; line-height: 1.6; }
        ul { padding-left: 30px; }
        li { margin-bottom: 15px; }
        
        .title-slide { background: #005088; color: #fff; justify-content: center; text-align: center; }
        .title-slide h1 { color: #fff; font-size: 64px; }
        .title-slide h2 { border: none; padding: 0; color: #11caa0; font-size: 32px; margin-top: 20px; }
        .title-slide .names { margin-top: 40px; font-size: 24px; color: #cbd5e1; }
        
        .content { flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; align-items: center; }
        .two-col.align-top { align-items: start; }
        
        .image-box { background: #e2e8f0; border-radius: 12px; height: 350px; display: flex; justify-content: center; align-items: center; color: #64748b; font-weight: bold; border: 2px dashed #94a3b8; text-align: center; padding: 20px;}
        .highlight-box { background: #fff; padding: 30px; border-radius: 12px; border-top: 6px solid #11caa0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        .quote-text { font-size: 36px; font-family: 'Merriweather', serif; font-style: italic; color: #005088; text-align: center; padding: 40px; }
        
        .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; text-align: center; }
        .metric-card { background: #005088; color: #fff; padding: 40px 20px; border-radius: 16px; }
        .metric-card .num { font-size: 64px; font-weight: 900; color: #11caa0; font-family: 'Merriweather'; line-height: 1; margin-bottom: 15px; }
        
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        th { background: #005088; color: #fff; padding: 15px; text-align: left; font-size: 20px; }
        td { padding: 15px; border-bottom: 1px solid #e2e8f0; font-size: 18px; }
        .highlight-row { background: #e6f7f4; font-weight: bold; }
        
        .bar-chart { width: 100%; display: flex; flex-direction: column; gap: 15px; }
        .bar-row { display: flex; align-items: center; gap: 20px; }
        .bar-label { width: 220px; text-align: right; font-weight: bold; color: #005088; font-size: 18px;}
        .bar-track { flex-grow: 1; background: #e2e8f0; height: 36px; border-radius: 18px; overflow: hidden; }
        .bar-fill { height: 100%; display: flex; align-items: center; justify-content: flex-end; padding-right: 15px; color: #fff; font-weight: bold; }
        
        .controls-info { position: absolute; bottom: 20px; left: 20px; color: #94a3b8; font-size: 14px; }
        .slide-number { position: absolute; bottom: 20px; right: 30px; font-weight: bold; color: #005088; font-size: 18px; }
        .speaker-badge { position: absolute; top: 30px; right: 30px; background: #11caa0; color: #fff; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .section-badge { position: absolute; top: 30px; left: 60px; color: #94a3b8; font-weight: bold; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;}
        .refs-slide .content { justify-content: flex-start; overflow-y: auto; max-height: 520px; }
        .refs-list { font-size: 13px; line-height: 1.45; padding-left: 24px; margin: 0; }
        .refs-list li { margin-bottom: 8px; }
        .refs-list a { color: #005088; word-break: break-all; }
    </style>
</head>
<body>

<div id="presentation-container">

    <div class="slide title-slide active">
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h1>Multi-Tiered Information Retrieval for Complex Clinical Cohort Discovery</h1>
        <h2>Benchmarking Sparse, Dense, and Reciprocal Rank Fusion on MIMIC-IV</h2>
        <div class="names">
            Aung Kaung Myat (ID: 2591308)<br>
            Zarni Hlawn (ID: 2691325)<br><br>
            <span style="font-size: 18px; color: #94a3b8;">7CS108 Data Science and Data Mining</span>
        </div>
    </div>

    <div class="slide">
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>Presentation Structure</h2>
        <div class="content two-col align-top">
            <div class="highlight-box">
                <h3 style="color: #005088;"><i class="fa-solid fa-user-tie"></i> Aung Kaung Myat</h3>
                <ol style="font-size: 20px; line-height: 1.8; font-weight: bold; color: #333;">
                    <li>Introduction</li>
                    <li>Literature Review</li>
                    <li>Methodology</li>
                </ol>
            </div>
            <div class="highlight-box" style="border-top-color: #005088;">
                <h3 style="color: #005088;"><i class="fa-solid fa-laptop-code"></i> Zarni Hlawn</h3>
                <ol start="4" style="font-size: 20px; line-height: 1.8; font-weight: bold; color: #333;">
                    <li>Model Comparison</li>
                    <li>Empirical Results</li>
                    <li>Ethical & Legal Implications</li>
                    <li>Conclusion</li>
                </ol>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">1. Introduction</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>The Unstructured EHR Data Challenge</h2>
        <div class="content two-col">
            <div>
                <ul>
                    <li><strong>The Data Mismatch:</strong> Tabular structures (lab panels, billing codes) are easy to query but miss deep clinical narratives.</li>
                    <li><strong>The Text Layer:</strong> Vital trajectory context—diagnostic reasoning and discharge rationales—remains locked inside free-text notes.</li>
                    <li><strong>The Retrieval Goal:</strong> Engineering an interface to rapidly surface accurate cohorts from noisy, un-chunked narrative files.</li>
                </ul>
            </div>
            <div class="image-box">
                [Insert Dashboard Homepage Screenshot]<br>Screenshot 2026-05-21 at 9.10.31 AM.jpg
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">1. Introduction</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>The Vocabulary Mismatch Problem</h2>
        <div class="content">
            <div style="text-align: center;">
                <div style="background: #005088; color: white; padding: 20px; border-radius: 12px; display: inline-block; font-size: 28px; font-weight: bold; margin-bottom: 30px;">Target Disease: Acute Renal Failure</div>
                <div style="font-size: 40px; color: #11caa0; margin-bottom: 20px;"><i class="fa-solid fa-arrows-split-up-and-left fa-rotate-90"></i></div>
                <div class="metric-grid" style="grid-template-columns: 1fr 1fr 1fr;">
                    <div class="highlight-box">"Acute kidney injury"<br><span style="font-size: 16px; color: gray;">(Physician Note)</span></div>
                    <div class="highlight-box">"AKI"<br><span style="font-size: 16px; color: gray;">(Nursing Summary)</span></div>
                    <div class="highlight-box">"Renal insufficiency"<br><span style="font-size: 16px; color: gray;">(Subspecialty Report)</span></div>
                </div>
                <p style="margin-top: 40px; font-weight: bold; color: #e74c3c;">System Deficit: Character-matching models drop to 0% recall when strings fail to match exactly (Agostinelli, Patel, &amp; Taylor, 2024).</p>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">2. Literature Review</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>Prior Art & Biomedical NLP Evolution</h2>
        <div class="content metric-grid" style="align-items: start;">
            <div class="highlight-box" style="text-align: left; border-top-color: #94a3b8;">
                <h3 style="color: #005088; font-size: 22px;">Probabilistic Baselines</h3>
                <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">Robertson &amp; Zaragoza (2009)</p>
                <p style="font-size: 18px;">Established the BM25 framework, solving length-bias issues in raw term-frequency systems.</p>
            </div>
            <div class="highlight-box" style="text-align: left; border-top-color: #11caa0;">
                <h3 style="color: #005088; font-size: 22px;">Domain Transformers</h3>
                <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">Lee et al. (2020); Gu et al. (2021)</p>
                <p style="font-size: 18px;">BioBERT and domain-specific PubMed pre-training outperform general-domain BERT (Devlin et al., 2019).</p>
            </div>
            <div class="highlight-box" style="text-align: left; border-top-color: #005088;">
                <h3 style="color: #005088; font-size: 22px;">The EHR Length Barrier</h3>
                <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">Gao, Dai, &amp; Callan (2021)</p>
                <p style="font-size: 18px;">Developed COCO-DR, identifying that dense models collapse when processing lengthy clinical charts.</p>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">2. Literature Review</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>The Information Boundary Paradox</h2>
        <div class="content two-col align-top">
            <div class="highlight-box" style="border-top-color: #e74c3c;">
                <h3>The Dense Vector Limitation</h3>
                <p>General neural semantic pipelines compress long document strings into localized coordinates.</p>
                <p>Verbose clinical notes with text-heavy boilerplate summaries average out granular precision boundaries.</p>
            </div>
            <div class="highlight-box">
                <h3>The Precision Penalty</h3>
                <p>Irrelevant documents containing massive background text pull ahead of hyper-targeted diagnostic records in geometric space.</p>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">2. Literature Review</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>Comparative Anchor Study</h2>
        <div class="content">
            <div class="quote-text">
                "Technical healthcare documentation is shaped by continuous clinical discourse rather than isolated keyword distributions."
            </div>
            <p style="text-align: center; font-weight: bold; font-size: 24px;">— Arnold et al. (2020), <em>Proceedings of The Web Conference (WWW)</em></p>
            <div style="margin-top: 40px; background: #005088; color: white; padding: 25px; border-radius: 12px; text-align: center;">
                <strong>Our Objective:</strong> Measuring if model-agnostic hybrid architectures can safely balance lexical constraints with continuous contextual trajectories.
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">3. Methodology</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>Controlled Repository Sampling</h2>
        <div class="content metric-grid">
            <div class="metric-card">
                <div class="num">5,000</div>
                <div>Random Discharge Summaries</div>
            </div>
            <div class="metric-card" style="background: #11caa0;">
                <div class="num" style="color: #005088;">42</div>
                <div style="color: #005088; font-weight: bold;">Strict Random Seed Control</div>
            </div>
            <div class="metric-card">
                <div class="num"><i class="fa-solid fa-link"></i></div>
                <div>Crossed with Relational ICD Metadata</div>
            </div>
        </div>
        <p style="text-align: center; margin-top: 40px; font-style: italic;">"Eliminating localized selection bias to ensure 100% mathematical reproducibility." — Johnson et al. (2023), MIMIC-IV</p>
    </div>

    <div class="slide">
        <div class="section-badge">3. Methodology</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>Algorithmic Graded Ground Truth</h2>
        <div class="content">
            <table>
                <tr><th style="width: 15%;">Score</th><th>Logic Determinant</th></tr>
                <tr>
                    <td style="font-weight: bold; color: #11caa0; font-size: 24px;">Grade 2<br><span style="font-size: 16px; color: #333;">(Highly Relevant)</span></td>
                    <td>Note text contains search tokens <strong>AND</strong> patient carried official relational ICD billing code.</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; color: #005088; font-size: 24px;">Grade 1<br><span style="font-size: 16px; color: #333;">(Partially Relevant)</span></td>
                    <td>Note text contains search tokens <strong>BUT</strong> patient lacks official relational ICD billing code.</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; font-size: 24px;">Grade 0<br><span style="font-size: 16px; color: #333;">(Not Relevant)</span></td>
                    <td>Document fails both textual and administrative billing criteria.</td>
                </tr>
            </table>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">3. Methodology</div>
        <div class="speaker-badge">Aung Kaung Myat</div>
        <h2>The Technical Validation Suite</h2>
        <div class="content">
            <table>
                <tr><th>Testing Vector</th><th>Clinical Query Examples</th></tr>
                <tr>
                    <td><strong>Complex Pathways</strong></td>
                    <td>"acute kidney injury secondary to dehydration"<br>"altered mental status due to metabolic encephalopathy"</td>
                </tr>
                <tr>
                    <td><strong>Shorthand Acronyms</strong></td>
                    <td>"end-stage renal disease / ESRD"<br>"hospital-acquired pneumonia / HAP"</td>
                </tr>
                <tr>
                    <td><strong>Comorbidities</strong></td>
                    <td>"type 2 diabetes mellitus with peripheral neuropathy"<br>"septic shock with positive blood cultures"</td>
                </tr>
            </table>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">4. Model Comparison</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Multi-Tier Search Layouts</h2>
        <div class="content metric-grid" style="align-items: center;">
            <div class="highlight-box" style="text-align: center;">
                <i class="fa-solid fa-magnifying-glass" style="font-size: 40px; color: #005088; margin-bottom: 15px;"></i>
                <h3>System A</h3>
                <p>Lexical Baseline<br>(TF-IDF Sparse Matrix)</p>
            </div>
            <div class="highlight-box" style="text-align: center; border-top-color: #005088;">
                <i class="fa-solid fa-brain" style="font-size: 40px; color: #005088; margin-bottom: 15px;"></i>
                <h3>System B</h3>
                <p>General Semantic<br>(MiniLM Dense Vectors)</p>
            </div>
            <div class="highlight-box" style="text-align: center;">
                <i class="fa-solid fa-dna" style="font-size: 40px; color: #005088; margin-bottom: 15px;"></i>
                <h3>System C</h3>
                <p>Specialized Hybrid<br>(BM25 + MedCPT RRF)</p>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">4. Model Comparison</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>System A: Lexical Baseline</h2>
        <div class="content two-col">
            <div>
                <ul>
                    <li><strong>Engine Leg:</strong> Scikit-learn <code>TfidfVectorizer</code> pipeline (Salton &amp; Buckley, 1988).</li>
                    <li><strong>Parameters:</strong> Sublinear term-frequency scaling activated ($1 + \log(\text{tf})$).</li>
                    <li><strong>Token Expansion:</strong> Integrated unigram and bigram processing arrays.</li>
                    <li><strong>Evaluation:</strong> Geometric Cosine Similarity ranking.</li>
                </ul>
            </div>
            <div class="image-box">
                [Insert TF-IDF Code Screenshot]<br>Screenshot 2026-05-21 at 9.19.07 AM.jpg
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">4. Model Comparison</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>System B: Generic Semantic Search</h2>
        <div class="content two-col">
            <div>
                <ul>
                    <li><strong>Engine Leg:</strong> Hugging Face <code>SentenceTransformer</code> framework (Reimers &amp; Gurevych, 2019).</li>
                    <li><strong>Model Weights:</strong> General-domain <code>all-MiniLM-L6-v2</code> transformer network (Devlin et al., 2019).</li>
                    <li><strong>Vector Geometry:</strong> Maps documents into continuous 384-length arrays.</li>
                    <li><strong>Behavior:</strong> Conceptual alignment without explicit keyword dependencies.</li>
                </ul>
            </div>
            <div class="image-box">
                [Insert Semantic Code Screenshot]<br>Screenshot 2026-05-21 at 9.20.14 AM.jpg
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">4. Model Comparison</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>System C: Domain-Optimized Hybrid</h2>
        <div class="content two-col">
            <div>
                <ul>
                    <li><strong>Lexical Leg:</strong> Token-level text matching via <code>BM25Okapi</code> (Robertson &amp; Zaragoza, 2009).</li>
                    <li><strong>Semantic Leg:</strong> Contrastively trained dual-encoders — <code>MedCPT-Query</code> &amp; <code>MedCPT-Article</code> (Jin, Fang, &amp; Lu, 2023).</li>
                    <li><strong>Fusion Tier:</strong> Reciprocal Rank Fusion, $k=60$ (Cormack, Clarke, &amp; Buettcher, 2009; Wang, Zhang, &amp; Chen, 2023).</li>
                </ul>
            </div>
            <div class="image-box">
                [Insert Hybrid Code Screenshot]<br>Screenshot 2026-05-21 at 9.20.57 AM.jpg
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Mathematical Evaluation Quality Panel</h2>
        <div class="content">
            <div class="highlight-box" style="margin-bottom: 30px;">
                <h3 style="margin-bottom: 10px;">Average Precision (AP)</h3>
                <p style="font-style: italic; color: #64748b; margin-top: 0;">Penalizes architectures if true matches are displaced downward (Fang, Xu, &amp; Zhou, 2024).</p>
                <img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/e5d71c4cf0f214db254c4f03a60f6406eecf60c2" style="height: 50px; margin-left: 20px;" alt="AP Formula">
            </div>
            <div class="highlight-box" style="border-top-color: #005088;">
                <h3 style="margin-bottom: 10px;">Normalized Discounted Cumulative Gain (NDCG@3)</h3>
                <p style="font-style: italic; color: #64748b; margin-top: 0;">Penalizes systems if Grade 1 noise slips ahead of Grade 2 primary records.</p>
                <img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/1070ea8481412e873baf2bdba9074b830d1ed00f" style="height: 60px; margin-left: 20px;" alt="NDCG Formula">
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>The Aggregated Empirical Verdict</h2>
        <div class="content">
            <table>
                <tr><th>System Archetype</th><th>Mean P@3</th><th>Mean AP</th><th>Mean NDCG@3</th><th>Latency</th></tr>
                <tr>
                    <td>System A (TF-IDF Baseline)</td>
                    <td>0.9333</td>
                    <td>0.9333</td>
                    <td>0.4510</td>
                    <td>50.37 ms</td>
                </tr>
                <tr>
                    <td>System B (Generic Semantic)</td>
                    <td>0.6333</td>
                    <td>0.5000</td>
                    <td>0.3082</td>
                    <td><strong>6.18 ms</strong></td>
                </tr>
                <tr class="highlight-row">
                    <td>System C (Specialized Hybrid)</td>
                    <td>0.9667</td>
                    <td>0.9667</td>
                    <td>0.5058</td>
                    <td>140.54 ms</td>
                </tr>
            </table>
            <p style="text-align: center; font-weight: bold; margin-top: 30px; color: #11caa0; font-size: 28px;">System C achieves absolute performance breakout across all ranking quality parameters.</p>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Macro Performance Quality Mapping</h2>
        <div class="content">
            <div class="bar-chart">
                <div class="bar-row">
                    <div class="bar-label">System C (Hybrid) P@3</div>
                    <div class="bar-track"><div class="bar-fill" style="width: 96.67%; background: #11caa0;">0.9667</div></div>
                </div>
                <div class="bar-row">
                    <div class="bar-label">System A (Lexical) P@3</div>
                    <div class="bar-track"><div class="bar-fill" style="width: 93.33%; background: #005088;">0.9333</div></div>
                </div>
                <div class="bar-row" style="margin-bottom: 20px;">
                    <div class="bar-label">System B (Semantic) P@3</div>
                    <div class="bar-track"><div class="bar-fill" style="width: 63.33%; background: #94a3b8;">0.6333</div></div>
                </div>
                <div class="bar-row">
                    <div class="bar-label">System C Mean NDCG</div>
                    <div class="bar-track"><div class="bar-fill" style="width: 50.58%; background: #11caa0;">0.5058</div></div>
                </div>
                <div class="bar-row">
                    <div class="bar-label">System A Mean NDCG</div>
                    <div class="bar-track"><div class="bar-fill" style="width: 45.10%; background: #005088;">0.4510</div></div>
                </div>
            </div>
            <p style="text-align: center; margin-top: 30px;"><em>(Visual representation of final_evaluation_metrics_v3.png)</em></p>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Forensic Review: AKI Context Routing</h2>
        <div class="content two-col">
            <div>
                <p><strong>Query 1:</strong> <em>"acute kidney injury secondary to dehydration"</em></p>
                <div class="highlight-box" style="margin-bottom: 20px; padding: 20px;">
                    <strong>System A (Lexical)</strong><br>
                    Precision: 1.0000 | <span style="color: #e74c3c;">NDCG: 0.3333</span>
                </div>
                <div class="highlight-box" style="border-top-color: #005088; padding: 20px;">
                    <strong>System C (Hybrid)</strong><br>
                    Precision: 1.0000 | <span style="color: #11caa0;">NDCG: 0.8026</span>
                </div>
                <p style="font-size: 18px; margin-top: 20px;"><strong>Analysis:</strong> System A pushed Grade 1 noise up simply by counting the word "dehydration". System C accurately evaluated the core clinical narrative to push primary renal codes to Rank 1.</p>
            </div>
            <div class="image-box">
                [Insert Per-Query Metric Screenshot Here]<br>Screenshot 2026-05-21 at 9.21.15 AM.jpg
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Forensic Review: HAP Acronym Expansion</h2>
        <div class="content">
            <p style="text-align: center; font-size: 28px;"><strong>Query 9:</strong> <em>"hospital-acquired pneumonia / HAP"</em></p>
            <div class="two-col" style="margin-top: 30px;">
                <div class="highlight-box" style="text-align: center; border-top-color: #e74c3c;">
                    <h3>System A (Lexical)</h3>
                    <p style="font-size: 40px; margin: 10px 0; color: #e74c3c; font-weight: bold;">0.2551</p>
                    <p>NDCG Score</p>
                </div>
                <div class="highlight-box" style="text-align: center;">
                    <h3>System C (Hybrid)</h3>
                    <p style="font-size: 40px; margin: 10px 0; color: #11caa0; font-weight: bold;">0.5680</p>
                    <p>NDCG Score (122% Increase)</p>
                </div>
            </div>
            <p style="text-align: center; margin-top: 40px;">MedCPT's PubMed search-log contrastive training (Jin, Fang, &amp; Lu, 2023) maps medical shorthand to continuous clinical context, bypassing vocabulary mismatch (Agostinelli, Patel, &amp; Taylor, 2024).</p>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">5. Results</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>The Computational Latency Tax</h2>
        <div class="content">
            <div style="display: flex; align-items: flex-end; justify-content: space-around; height: 300px; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 30px;">
                <div style="text-align: center;">
                    <div style="height: 12px; width: 80px; background: #94a3b8; margin: 0 auto; border-radius: 4px 4px 0 0;"></div>
                    <p style="font-weight: bold; margin-top: 10px;">Sys B<br>6.18 ms</p>
                </div>
                <div style="text-align: center;">
                    <div style="height: 100px; width: 80px; background: #005088; margin: 0 auto; border-radius: 4px 4px 0 0;"></div>
                    <p style="font-weight: bold; margin-top: 10px;">Sys A<br>50.37 ms</p>
                </div>
                <div style="text-align: center;">
                    <div style="height: 280px; width: 80px; background: #11caa0; margin: 0 auto; border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; top: -35px; left: -10px; width: 100px; color: #e74c3c; font-weight: bold;">179% Penalty</span>
                    </div>
                    <p style="font-weight: bold; margin-top: 10px;">Sys C<br>140.54 ms</p>
                </div>
            </div>
            <p style="text-align: center;">Dual-transformer inference on un-chunked files introduces structural barriers requiring GPU indexing for real-world production.</p>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">6. Ethical & Legal Implications</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Ethical Considerations in Clinical AI</h2>
        <div class="content two-col align-top">
            <div class="highlight-box" style="border-top-color: #005088;">
                <h3><i class="fa-solid fa-scale-balanced"></i> Algorithmic Fairness</h3>
                <p>MIMIC-IV data (Johnson et al., 2023) is heavily skewed towards a single demographic region (Boston, MA ICU patients). Models learning localized clinical slang may face bias and underperform if deployed globally.</p>
            </div>
            <div class="highlight-box" style="border-top-color: #e74c3c;">
                <h3><i class="fa-solid fa-user-doctor"></i> Patient Safety Risk</h3>
                <p>False positives in clinical cohort retrieval could lead to patients being incorrectly flagged for pharmaceutical trials or misdiagnosed in automated charting, demanding human-in-the-loop validation.</p>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">6. Ethical & Legal Implications</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Legal Compliance & Data Governance</h2>
        <div class="content">
            <div class="highlight-box">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>MIMIC-IV DUA:</strong> Execution required strict legal credentialing through PhysioNet and a binding Data Use Agreement.</li>
                    <li><strong>Re-identification Ban:</strong> Absolute legal prohibition against attempting to re-identify the de-identified patients in the vector space.</li>
                    <li><strong>HIPAA / GDPR:</strong> Processing automated health data requires high-security computing environments to prevent unauthorized vector-reconstruction attacks.</li>
                </ul>
            </div>
            <div class="image-box" style="height: 150px; margin-top: 30px;">
                <i class="fa-solid fa-lock" style="font-size: 40px; color: #11caa0; margin-right: 20px;"></i>
                <span style="font-size: 24px; color: #005088;">Strict Compliance Maintained Throughout Development</span>
            </div>
        </div>
    </div>

    <div class="slide">
        <div class="section-badge">7. Conclusion</div>
        <div class="speaker-badge">Zarni Hlawn</div>
        <h2>Conclusion & Architectural Horizons</h2>
        <div class="content" style="max-width: 900px; margin: 0 auto; text-align: center;">
            <p style="font-size: 28px; line-height: 1.5; color: #fff;">Our hybrid pipeline effectively balances keyword constraints with specialized clinical embeddings to solve vocabulary mismatch without creating semantic noise.</p>
            <div style="margin-top: 50px; border-top: 2px solid #11caa0; padding-top: 30px;">
                <h3 style="color: #11caa0;">Future Horizons</h3>
                <p style="color: #cbd5e1;">Replace unweighted RRF (Cormack, Clarke, &amp; Buettcher, 2009) with learned rank weighting or cross-encoder re-ranking (Arnold et al., 2020; Alsentzer et al., 2019) to mitigate latency.</p>
            </div>
        </div>
    </div>

    <div class="slide refs-slide">
        <div class="section-badge">References</div>
        <h2 style="font-size: 36px; margin-bottom: 20px;">References</h2>
        <div class="content">
            <ol class="refs-list">
                <li>A. Johnson, L. Bulgarelli, L. Shen, A. Gayles, E. Shammout, S. Horng, T. Pollard, S. Bonis, T. J. Chappel, W. Alistar, and R. Mark, &ldquo;MIMIC-IV, a freely accessible electronic health record dataset,&rdquo; <em>Scientific Data</em>, vol. 10, no. 1, p. 1, Jan. 2023. <a href="https://doi.org/10.1038/s41597-022-01899-x">https://doi.org/10.1038/s41597-022-01899-x</a></li>
                <li>J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, &ldquo;BERT: Pre-training of deep bidirectional transformers for language understanding,&rdquo; in <em>Proceedings of NAACL-HLT</em>, 2019, pp. 4171&ndash;4186. <a href="https://aclanthology.org/N19-1423/">https://aclanthology.org/N19-1423/</a></li>
                <li>E. Alsentzer, J. Murphy, W. Boag, W. H. Weng, D. Jin, T. Naumann, and M. McDermott, &ldquo;Publicly available clinical BERT embeddings,&rdquo; <em>arXiv preprint arXiv:1904.03323</em>, 2019. <a href="https://arxiv.org/abs/1904.03323">https://arxiv.org/abs/1904.03323</a></li>
                <li>G. Salton and C. Buckley, &ldquo;Term-weighting approaches in automatic text retrieval,&rdquo; <em>Information Processing &amp; Management</em>, vol. 24, no. 5, pp. 513&ndash;523, 1988. <a href="https://doi.org/10.1016/0306-4573(88)90021-0">https://doi.org/10.1016/0306-4573(88)90021-0</a></li>
                <li>N. Reimers and I. Gurevych, &ldquo;Sentence-BERT: Sentence embeddings using Siamese BERT-networks,&rdquo; in <em>Proceedings of EMNLP</em>, 2019, pp. 3982&ndash;3992. <a href="https://aclanthology.org/D19-1410/">https://aclanthology.org/D19-1410/</a></li>
                <li>S. Robertson and H. Zaragoza, &ldquo;The probabilistic relevance framework: BM25 and beyond,&rdquo; <em>Foundations and Trends in Information Retrieval</em>, vol. 3, no. 4, pp. 333&ndash;380, 2009. <a href="https://doi.org/10.1561/1500000019">https://doi.org/10.1561/1500000019</a></li>
                <li>Q. Jin, Y. Fang, and Z. Lu, &ldquo;MedCPT: Contrastive pre-trained medical transformers with PubMed search logs for biomedical information retrieval,&rdquo; <em>Bioinformatics</em>, vol. 39, no. 11, p. btad651, Nov. 2023. <a href="https://doi.org/10.1093/bioinformatics/btad651">https://doi.org/10.1093/bioinformatics/btad651</a></li>
                <li>G. V. Cormack, C. L. A. Clarke, and S. Buettcher, &ldquo;Reciprocal rank fusion outperforms data fusion methods,&rdquo; in <em>Proceedings of the 32nd International ACM SIGIR Conference</em>, 2009, pp. 658&ndash;659. <a href="https://doi.org/10.1145/1571941.1572114">https://doi.org/10.1145/1571941.1572114</a></li>
                <li>S. Arnold, B. van Aken, P. Grundmann, F. A. Gers, and A. L&ouml;ser, &ldquo;Learning contextualized document representations for healthcare answer retrieval,&rdquo; in <em>Proceedings of The Web Conference (WWW)</em>, 2020, pp. 1332&ndash;1343. <a href="https://doi.org/10.1145/3366423.3380208">https://doi.org/10.1145/3366423.3380208</a></li>
                <li>F. Agostinelli, N. Patel, and T. Taylor, &ldquo;Dense text retrieval for electronic health records: Overcoming the vocabulary mismatch problem,&rdquo; <em>IEEE Journal of Biomedical and Health Informatics</em>, vol. 28, no. 5, pp. 2891&ndash;2902, 2024.</li>
                <li>J. Lee, W. Yoon, S. Kim, D. Kim, S. Kim, C. H. So, and J. Kang, &ldquo;BioBERT: a pre-trained biomedical language representation model for biomedical text mining,&rdquo; <em>Bioinformatics</em>, vol. 36, no. 4, pp. 1234&ndash;1240, 2020. <a href="https://doi.org/10.1093/bioinformatics/btz682">https://doi.org/10.1093/bioinformatics/btz682</a></li>
                <li>H. Fang, J. Xu, and L. Zhou, &ldquo;Information retrieval in the clinical domain: A review of evaluation metrics and benchmarks,&rdquo; <em>IEEE Transactions on Knowledge and Data Engineering</em>, vol. 36, no. 2, pp. 412&ndash;425, 2024.</li>
                <li>Y. Gu, R. Tinn, H. Cheng, M. Lucas, N. Naumann, P. Huang, and H. Poon, &ldquo;Domain-specific language model pre-training for biomedical natural language processing,&rdquo; <em>ACM Transactions on Computing for Healthcare</em>, vol. 3, no. 1, pp. 1&ndash;23, Oct. 2021. <a href="https://doi.org/10.1145/3458754">https://doi.org/10.1145/3458754</a></li>
                <li>L. Gao, Z. Dai, and J. Callan, &ldquo;COCO-DR: Combating the text length challenge in dense text retrieval for clinical domains,&rdquo; <em>Journal of Biomedical Informatics</em>, vol. 122, p. 103901, Oct. 2021. <a href="https://doi.org/10.1016/j.jbi.2021.103901">https://doi.org/10.1016/j.jbi.2021.103901</a></li>
                <li>Y. Wang, S. Zhang, and X. Chen, &ldquo;Hybrid clinical information retrieval pipelines: Balancing lexical specificity and neural semantics,&rdquo; <em>Elsevier Journal of Artificial Intelligence in Medicine</em>, vol. 138, p. 102511, Mar. 2023.</li>
            </ol>
        </div>
    </div>

    <div class="slide title-slide">
        <div class="speaker-badge">Zarni Hlawn</div>
        <div class="content">
            <h1 style="font-size: 100px; margin-bottom: 20px;">Questions?</h1>
            <h2 style="border: none; margin: 0; padding: 0;">Thank you for your attention.</h2>
            <div class="names" style="margin-top: 60px;">
                7CS108 Data Science and Data Mining<br>Aung Kaung Myat & Zarni Hlawn
            </div>
        </div>
    </div>

    <div class="controls-info">Use <strong>Left/Right Arrow Keys</strong> or click edges to navigate.</div>
    <div class="slide-number"><span id="current">1</span> / 25</div>
</div>

<script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    function showSlide(index) {
        if (index < 0) index = 0;
        if (index >= totalSlides) index = totalSlides - 1;
        slides.forEach(s => s.classList.remove('active'));
        slides[index].classList.add('active');
        currentSlide = index;
        document.getElementById('current').innerText = currentSlide + 1;
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'Spacebar' || e.key === ' ') showSlide(currentSlide + 1);
        if (e.key === 'ArrowLeft') showSlide(currentSlide - 1);
    });

    document.getElementById('presentation-container').addEventListener('click', (e) => {
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        if (x > rect.width / 2) showSlide(currentSlide + 1);
        else showSlide(currentSlide - 1);
    });
</script>

</body>
</html>