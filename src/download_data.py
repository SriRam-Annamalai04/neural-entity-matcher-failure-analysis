"""Download the three DeepMatcher benchmark datasets into data/.

Usage (from the repo root):
    python -m src.download_data            # download missing files, verify checksums
    python -m src.download_data --force    # re-download everything

Source: DeepMatcher benchmark (Mudgal et al., SIGMOD 2018), hosted by the UW-Madison Magellan group.
Each dataset folder gets:
    tableA.csv, tableB.csv          the two record tables (column "id" + attributes)
    train.csv, valid.csv, test.csv  the standard splits: ltable_id, rtable_id, label (1 = match)

Uses only the Python standard library.
"""

import argparse
import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

BASE_URL = "https://pages.cs.wisc.edu/~anhai/data1/deepmatcher_data"

# local folder name -> path on the server
DATASETS = {
    "abt_buy": "Textual/Abt-Buy/exp_data",
    "amazon_google": "Structured/Amazon-Google/exp_data",
    "dblp_acm": "Structured/DBLP-ACM/exp_data",
}

FILES = ["tableA.csv", "tableB.csv", "train.csv", "valid.csv", "test.csv"]

# SHA-256 of each file as first downloaded. A mismatch means the upstream file changed,
# which would make results non-comparable, so the script stops. Recorded 2026-11-07.
CHECKSUMS = {
    "abt_buy/tableA.csv": "20b79995258c4ef80bb96b731762a6fe869650cc42dcb2c58994bda91b0d81aa",
    "abt_buy/tableB.csv": "e6ebe54c98fd69c5ad4b8364dde53c323ae872c49cf3c2ad5f7b9acd246e1eb6",
    "abt_buy/train.csv": "efa7ee36e35915aa2e5c8218bb90a94ff11a6cc7a9c4a45cefff1bfc16d64061",
    "abt_buy/valid.csv": "25ac7b6035327c82a9e45c93e02e24dd2fffe7afff779ae9381e5c32f727c3c0",
    "abt_buy/test.csv": "fd815442d37368cecc4cd3b5a0af33930ce5b7b353b222b810d8079211e81d9a",
    "amazon_google/tableA.csv": "04a797511d83af9e27469778081c50397857b199d49e2f83c119390f14301947",
    "amazon_google/tableB.csv": "00c0d19c0dcd014b00d6d341e15e2b3b3caa616b4f6d710d0c9cd2dfc3f4717f",
    "amazon_google/train.csv": "cdc5e88d714e77febc26a81a61c3295a0000baa51d6debf93043f0cbd5193b9f",
    "amazon_google/valid.csv": "4999067ea47fa2ae03e0c4a68fee60cf68728943208fcde46415cb895844dd22",
    "amazon_google/test.csv": "09e376c0c5391bd4a6c6d8efde148c994441b6043ef6b7f9eab2a8772a6fb362",
    "dblp_acm/tableA.csv": "a83dfac196a4e263f3adac7aaf095c7198254a98fcaed0ec68d59130c74c43a7",
    "dblp_acm/tableB.csv": "bd103ffdccdff4d8b9d04c18d90d04110b70b6fc87dec83c4e52e9616c58431a",
    "dblp_acm/train.csv": "ad94b36b178bbf76023d3cee689565fbda1fe01b19d9a3926a51db382f45f0a5",
    "dblp_acm/valid.csv": "862f848ed3f3f005ae6c8997ecf571984bd575f6bbd319fc1a2170830a91132b",
    "dblp_acm/test.csv": "e49adc4590d24c18b1a9bbd96011d9c745e10432e10e93e050d856a206fac394",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "neural-entity-matcher-failure-analysis"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as out:
        out.write(resp.read())
    tmp.replace(dest)


def split_stats(path: Path) -> str:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    matches = sum(1 for r in rows if r["label"].strip() == "1")
    return f"{len(rows)} pairs, {matches} matches"


def table_stats(path: Path) -> str:
    with open(path, newline="", encoding="utf-8") as f:
        n = sum(1 for _ in csv.DictReader(f))
    return f"{n} records"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="re-download files that already exist")
    args = parser.parse_args()

    failed = False
    for name, remote in DATASETS.items():
        folder = DATA_DIR / name
        folder.mkdir(parents=True, exist_ok=True)
        print(f"\n{name}  ({BASE_URL}/{remote})")
        for fname in FILES:
            dest = folder / fname
            key = f"{name}/{fname}"
            if args.force or not dest.exists():
                download(f"{BASE_URL}/{remote}/{fname}", dest)
                action = "downloaded"
            else:
                action = "exists"

            digest = sha256(dest)
            expected = CHECKSUMS.get(key)
            if expected is None:
                check = f"no checksum on record (sha256 {digest})"
            elif digest == expected:
                check = "checksum OK"
            else:
                check = f"CHECKSUM MISMATCH (expected {expected}, got {digest})"
                failed = True

            stats = table_stats(dest) if fname.startswith("table") else split_stats(dest)
            print(f"  {fname:<11} {action:<10} {stats:<28} {check}")

    if failed:
        print("\nERROR: at least one file differs from the recorded version. Results would not be comparable.")
        return 1
    print(f"\nDone. Data is in {DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
