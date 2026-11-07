# Research Log
Dated diary. Write after every work session, even 3 lines.

## YYYY-MM-DD
- Tried:
- Result: (MLflow run id: )
- Surprise:
- Next:

## 2026-11-07
- Tried: project setup (Week 1, M1). Added a CLAUDE.md. Split dependencies into a short `requirements.txt`
  (5 packages with `>=` minimums) and `requirements-lock-windows.txt` (full pip freeze), then tested a fresh
  venv. Wrote the README (problem, RQs, data, how to run). Wrote `src/download_data.py`, which fetches the
  3 DeepMatcher benchmarks into `data/` and pins a SHA-256 for each file.
- Result: (MLflow run id: none, no experiments yet). The fresh venv install passed `pip check`, and all 5 packages
  imported (torch 2.15.0+cpu). Downloaded data matches the published DeepMatcher sizes: Abt-Buy 9,575 pairs /
  1,028 matches, Amazon-Google 11,460 / 1,167, DBLP-ACM 12,363 / 2,220.
- Surprise: (1) The torch 2.15 install fails on Windows when the venv path is long, because long-path support
  is off on this machine. (2) The DeepMatcher text is already lowercased and tokenized, so case-only
  failures cannot appear. (3) Each dataset has different columns, so the record-to-text step needs a decision.
- Next: commit this setup. Log in `decisions.md` how records are turned into text. Build the TF-IDF baseline
  (threshold tuned on valid) with MLflow logging. Start the Peeters et al. literature check.
