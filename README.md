# neural-entity-matcher-failure-analysis

Which mistakes do neural entity matchers make, and which fixes actually work? Error analysis of embeddings,
reranking, fine-tuning and LLMs (with a TF-IDF baseline) on public benchmarks.

> **Status:** early work in progress (started November 2026). The project structure and environment are set up;
> the baselines and experiment scripts are not written yet. This README will be updated as each milestone lands.

## The problem, in simple words

**Entity matching** means deciding whether two records describe the same real-world thing. For example:

| Record A | Record B | Same product? |
|---|---|---|
| Apple iPhone 15, 128GB, Black | iPhone15 128 GB Midnight Blk | Yes |
| Sony XR-55A80L 55" OLED | Sony XR-65A80L 65" OLED | No |

Shops, libraries and databases do this all the time to merge duplicates or compare prices.

Neural matchers (models that turn text into vectors and compare them) do very well on clean data. On messy
product data they still make many mistakes. Papers usually report a single overall score (F1), and that score
hides **which kinds of mistakes are left**. For example, the matcher might confuse "Blk" with "Black", or treat
an "iPhone 15" as the same as an "iPhone 15 Pro".

People try several fixes: reranking, fine-tuning, or asking a large language model. But it is not clear
**which fix solves which kind of mistake**, or **what each fix costs**. This project measures exactly that.

## Research questions

- **RQ1:** What kinds of mistakes do simple matchers (TF-IDF and dense embeddings) make, and how often?
- **RQ2:** Which of those mistakes does hybrid retrieval (BM25 + dense) with a cross-encoder reranker fix,
  and which remain?
- **RQ3:** Does fine-tuning the embedding model on matched / unmatched pairs fix *different* mistakes than
  reranking does?
- **RQ4:** A small LoRA-tuned classifier vs a prompted LLM matcher: which mistakes does each fix, and what are
  the cost per 1,000 pairs and the latency?

### Planned outputs
1. A **failure taxonomy**: a named list of mistake types, with a written tagging guide others can apply.
2. A **"fixed / persists" matrix**: mistake type × method.
3. A **cost and quality table** across all methods.
4. Open, reproducible code, with every run logged in MLflow.

## Data

Three public benchmarks (DeepMatcher / Magellan versions), using their standard train / validation / test splits:

| Dataset | Domain | Why it is included |
|---|---|---|
| Abt-Buy | Electronics products | Messy product text, hard |
| Amazon-Google | Software products | Messy product text, hard |
| DBLP-ACM | Research papers | Clean data, nearly solved (control) |

The task is pairwise matching on each benchmark's fixed candidate pairs (not large-scale blocking).
The data is not stored in this repo; see "Download the data" below.

| Dataset | Records (A / B) | Train pairs (matches) | Valid pairs (matches) | Test pairs (matches) |
|---|---|---|---|---|
| Abt-Buy | 1,081 / 1,092 | 5,743 (616) | 1,916 (206) | 1,916 (206) |
| Amazon-Google | 1,363 / 3,226 | 6,874 (699) | 2,293 (234) | 2,293 (234) |
| DBLP-ACM | 2,616 / 2,294 | 7,417 (1,332) | 2,473 (444) | 2,473 (444) |

Note: the DeepMatcher versions are already lowercased and lightly tokenized (e.g. `ipod nano 8gb - silver`).

## How to run

### 1. Set up the environment

Requires Python 3 (tested with 3.14). Commands are for Windows Command Prompt.

```bat
git clone https://github.com/SriRam-Annamalai04/neural-entity-matcher-failure-analysis.git
cd neural-entity-matcher-failure-analysis
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

On macOS / Linux, activate the venv with `source .venv/bin/activate` instead.

**Two dependency files:**
- `requirements.txt` lists the 5 direct dependencies (pandas, scikit-learn, sentence-transformers, mlflow,
  torch) with minimum versions. Use this one.
- `requirements-lock-windows.txt` holds the exact versions of the original Windows environment. Use it only
  to recreate that environment exactly (Windows only).

**Known install issues:**
- *Windows "No such file or directory" error while installing torch:* torch has very long internal file
  paths. Either enable Windows long path support, or create the venv in a short folder (e.g. `C:\venvs\nem`).
- *GPU:* plain `pip install` on Windows installs the CPU version of torch. For a GPU, first install torch
  using the command for your CUDA version from pytorch.org, then run `pip install -r requirements.txt`.

### 2. Download the data

```bat
python -m src.download_data
```

This downloads the three DeepMatcher benchmarks from the UW-Madison Magellan group's server into
`data/abt_buy/`, `data/amazon_google/` and `data/dblp_acm/`. Each folder has `tableA.csv` and `tableB.csv` (the
records) plus `train.csv`, `valid.csv` and `test.csv` (pairs: `ltable_id, rtable_id, label`, with 1 = match).
The script checks every file's SHA-256 against the version used in this project and stops if one differs.
Re-running skips files that already exist; add `--force` to download again.

### 3. View experiment results

Every run is logged with MLflow in the local `mlruns/` folder. To browse runs:

```bat
mlflow ui
```

Then open http://127.0.0.1:5000.

### 4. Run the experiments

Coming soon: baselines (TF-IDF, then `all-MiniLM-L6-v2` embeddings), and the steps to
reproduce the headline table will be added here as they are built.

## Repository layout

```
data/                 benchmark data (not in git)
src/                  matcher code
notebooks/            quick experiments
results/error_logs/   CSVs of wrong pairs, tagged with a mistake type
paper/                the write-up
notes/                research log, findings, decisions, literature
```

## License

MIT. See [LICENSE](LICENSE).
