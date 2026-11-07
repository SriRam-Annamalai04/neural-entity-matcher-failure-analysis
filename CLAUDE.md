# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Project: neural-entity-matcher-failure-analysis. Read this before doing anything in this repo.

## Current state (2026-11-07)
Only code so far: `src/download_data.py`. `notes/*.md` are blank templates. README covers problem, RQs,
data, setup and download; its "Run the experiments" section is a placeholder to fill as scripts land.
There is no test suite, no linter config and no matcher/experiment script yet.
Do not invent commands for these; add them here once they exist.

## Commands (cmd)
```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m src.download_data    :: fetch the 3 benchmarks into data\ (stdlib only; --force to re-download)
mlflow ui                      :: view runs stored in .\mlruns at http://127.0.0.1:5000
```
Two dependency files:
- `requirements.txt`: the 5 direct dependencies (pandas, scikit-learn, sentence-transformers, mlflow, torch)
  with `>=` minimums. Cross-platform; this is what the README and strangers should use.
  When adding a new direct dependency, add it here with a `>=` minimum.
- `requirements-lock-windows.txt`: full `pip freeze` of the original Windows env (exact pins, includes the
  Windows-only `pywin32`). Use it only to recreate the exact author environment on Windows:
  `pip install -r requirements-lock-windows.txt`. Regenerate with `pip freeze > requirements-lock-windows.txt`.

Install gotchas (verified 2026-11-07, Python 3.14, fresh venv):
- torch 2.15 wheels contain ~200-char internal paths. On Windows without Long Path support, `pip install`
  fails with `OSError: [Errno 2] No such file or directory ... torch-2.15.0.dist-info\licenses\...` when the
  venv path is long. Fix: enable Windows long paths, or put the venv in a short path (e.g. `C:\venvs\nem`).
- Plain `pip install` on Windows gives the CPU build (`torch 2.15.0+cpu`). For GPU, install torch from the
  PyTorch index URL for your CUDA version first, then `pip install -r requirements.txt`.

## What this project is
A 13-week research project (Nov 2026 – Jan 2027) that studies **why neural entity matchers fail**
and **which fixes actually work for which kind of mistake**.

Entity matching = deciding whether two records describe the same real-world thing.
Example: "Apple iPhone 15, 128GB, Black" vs "iPhone15 128 GB Midnight Blk" -> same product.

Plain-language problem: papers report one overall score (F1). That hides *which* mistakes remain.
Nobody clearly shows which fix (reranking, fine-tuning, an LLM) fixes which type of mistake, or what each fix costs.

Working paper title: "Why Do Neural Entity Matchers Fail? A Failure Taxonomy Across Reranking, Fine-tuning and LLM Matching"

Planned contributions:
1. A failure taxonomy with a written tagging guide others can apply.
2. A "fixed / persists" matrix: failure type x method.
3. A cost and quality table across all methods.
4. Open, reproducible code with every run logged in MLflow.

## Research questions
- RQ1: What failure types do TF-IDF and dense embedding matchers make, and how often?
- RQ2: Which failures does hybrid retrieval (BM25 + dense) + cross-encoder reranking fix, and which remain?
- RQ3: Does fine-tuning the embedding model on matched/unmatched pairs fix *different* failures than reranking?
- RQ4: Small LoRA-tuned classifier vs a prompted LLM matcher: which failures each fixes, cost per 1,000 pairs, latency.

## Evidence the problem is real (published results)
- Ditto (Li et al., 2020) scores ~75.6 F1 on Amazon-Google; older methods score 43.6–62.8 on Abt-Buy.
- GPT-4 scored ~76.4 F1 on Amazon-Google (Peeters, Steiner, Bizer, arXiv:2310.11244).
- Clean data is nearly solved: ~99 F1 on DBLP-ACM. So the claim is "matchers still fail often on messy product data".
- One study reports Ditto dropping from 0.821 to ~0.283 F1 on Abt-Buy with random instead of standard splits (arXiv:2211.06975).

## Biggest open risk (do this first)
Peeters et al. (arXiv:2310.11244) already use GPT-4 to identify error classes from wrong decisions.
Before building beyond M1, finish the literature check in `notes/literature.md` and make sure this project
adds something new. Planned differentiators: compare several fixes on the *same* error types, and add cost/latency.

## Scope and hard rules
- Data: Abt-Buy, Amazon-Google, DBLP-ACM (DeepMatcher / Magellan benchmark versions), standard published splits.
- Task: pairwise matching on the benchmarks' fixed candidate pairs (not large-scale blocking).
- Public data and own code only. Never add code, data or names from any employer or client.
- TF-IDF is included only as a non-neural baseline.
- Say "prompted LLM matcher", not "LLM-as-judge" (the LLM is matching, not evaluating).

## Milestones (Week 1 = week of 2026-11-02)
| Milestone | Weeks | Dates | Deliverable |
|---|---|---|---|
| M1 Baselines | 1–3 | Nov 2 – Nov 22 | TF-IDF + dense baselines, tracked in MLflow; error log of wrong pairs |
| M2 Hybrid + reranking | 4–5 | Nov 23 – Dec 6 | P/R/F1 vs baselines; which error types it fixes |
| M3 Fine-tuned embeddings | 6–8 | Dec 7 – Dec 27 | sentence-transformers fine-tuned (PyTorch); error types before vs after |
| M4 LoRA vs LLM matcher | 9–10 | Dec 28 – Jan 10 | accuracy, cost, latency, where each fails |
| M5 Taxonomy + paper | 11–13 | Jan 11 – Jan 31 | failure taxonomy, arXiv preprint + workshop submission, 1-page decision note |

Success criteria:
- Every RQ answered with numbers on the test splits.
- Taxonomy stability: re-tag a 100-pair sample ~2 weeks later without looking; report Cohen's kappa (target >= 0.7).
- A stranger can reproduce the headline table from the README.

## Repo layout
```
data/                 benchmark data (gitignored; download via script)
src/                  matcher code
notebooks/            quick experiments
results/error_logs/   CSVs of wrong pairs with failure-type tags
paper/                the write-up
notes/research-log.md dated diary, after every session
notes/findings.md     confirmed results only, with evidence (MLflow run id / error-log file)
notes/decisions.md    choices + why
notes/literature.md   papers read + how this work differs
```
- Metrics live in MLflow (`mlruns/`, gitignored). Do not copy numbers by hand into notes; cite the run id.
- Error-log CSVs should include at least: dataset, left record, right record, true label, predicted label, score, failure_type, notes.
- Keep failure_type labels consistent across M1–M4; define each label in `notes/decisions.md` before using it.
- Starter failure types (refine during M1): abbreviation / short form (Blk = Black), model or number mismatch
  (XR-55 vs XR55, iPhone 15 vs 15 Pro), missing attribute, near-duplicate but different product, word order / formatting.
- Taxonomy is weakest with one annotator: besides the self re-tag check, a second annotator on a 100-pair sample is stronger.

## Data layout (from `src/download_data.py`)
- `data/{abt_buy,amazon_google,dblp_acm}/` each hold `tableA.csv`, `tableB.csv` (column `id` + attributes)
  and `train.csv`, `valid.csv`, `test.csv` (`ltable_id, rtable_id, label`; join ids to tableA/tableB `id`).
- Attributes differ: Abt-Buy `name, description, price` (DeepMatcher "Textual"); Amazon-Google
  `title, manufacturer, price`; DBLP-ACM `title, authors, venue, year`. Prices are often empty.
- Text is already lowercased/tokenized by DeepMatcher, so case-only failures cannot occur in this data.
- Files are SHA-256-pinned in the script; a mismatch means upstream changed and results are not comparable.

## M1 starting defaults (suggestions, not fixed decisions)
- Baseline 1: TF-IDF + cosine similarity, threshold tuned on the validation split.
- Baseline 2: sentence-transformers `all-MiniLM-L6-v2` + cosine similarity, threshold tuned on validation.
- Log per run in MLflow: dataset, model, threshold, precision, recall, F1.
- Export false positives and false negatives to `results/error_logs/` and tag them.

## Repo facts
- GitHub: SriRam-Annamalai04/neural-entity-matcher-failure-analysis (public, MIT license).
- Description: "Which mistakes do neural entity matchers make, and which fixes actually work? Error analysis of
  embeddings, reranking, fine-tuning and LLMs (with a TF-IDF baseline) on public benchmarks."
- Topics: entity-matching, entity-resolution, error-analysis, sentence-transformers, llm, nlp, machine-learning.
- Expect M3 (December) to run slower because of other commitments that month.

## Environment
- Windows, Command Prompt (cmd). Give cmd commands by default, not bash.
- Python virtual env in `.venv` (activate: `.venv\Scripts\activate.bat`).
- Installed: pandas, scikit-learn, sentence-transformers, mlflow, torch (see "Commands" for the two requirements files).

## How to work with me
- Explain simply first; go technical only when I ask.
- Back claims with evidence (sources, run ids, actual output).
- Point out mistakes or risky assumptions directly; suggest better approaches.
- When you create or edit files, end with a changelog: created / changed / left untouched.
- Put assumptions in a separate "Assumptions" section at the end.
- After each work session, remind me to add an entry to `notes/research-log.md`.

## Next steps (as of 2026-11-07)
1. Write the README (problem, RQs, how to run).
2. Script to download the three benchmarks into `data/`.
3. TF-IDF baseline -> dense baseline -> MLflow logging -> export wrong pairs to `results/error_logs/`.
4. Literature check (Peeters et al. first).
