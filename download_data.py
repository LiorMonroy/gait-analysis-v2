"""Download the full PhysioNet "Gait in Parkinson's Disease" database (~290 MB).

    python download_data.py            # -> data/gaitpdb/

Tries the single zip first, then falls back to file-by-file using the
project's SHA256SUMS.txt listing. Safe to re-run: existing files are skipped.

Alternative (w/ command line):
    wget -r -N -c -np -nH --cut-dirs=3 -P data/gaitpdb https://physionet.org/files/gaitpdb/1.0.0/
"""
import argparse
import io
import shutil
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://physionet.org/files/gaitpdb/1.0.0/"
ZIP = "https://physionet.org/static/published-projects/gaitpdb/gait-in-parkinsons-disease-1.0.0.zip"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gait-v2-student-project"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/gaitpdb")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    try:
        print("downloading zip (one ~60 MB file)...")
        z = zipfile.ZipFile(io.BytesIO(get(ZIP)))
        for m in z.infolist():
            name = Path(m.filename).name
            if not name or m.is_dir():
                continue
            with z.open(m) as src, open(out / name, "wb") as dst:
                shutil.copyfileobj(src, dst)
        print(f"done: {len(list(out.glob('*.txt')))} .txt files in {out}/")
        return
    except Exception as e:
        print(f"zip download failed ({e}); falling back to file-by-file")

    listing = get(BASE + "SHA256SUMS.txt").decode()
    names = [line.split()[-1] for line in listing.splitlines() if line.strip()]
    names = [n for n in names if "/" not in n]
    for i, n in enumerate(names, 1):
        dst = out / n
        if dst.exists() and dst.stat().st_size > 0:
            continue
        print(f"[{i}/{len(names)}] {n}")
        dst.write_bytes(get(BASE + n))
    print(f"done: {len(list(out.glob('*.txt')))} .txt files in {out}/")


if __name__ == "__main__":
    main()
