"""OCR of the licensed, image-only ISO/IEC 27701:2025 PDF. Integration tooling, not part of any agent.
Input (read-only): /in/norma.pdf   Output: /out/ISO27701-2025.md and /out/ocr_report.json (git-ignored).
Output is DERIVED, possibly noisy text. Per-page mean confidence is recorded so weak pages can be spot-checked."""
import glob
import json
import subprocess
import tempfile
import os

SRC, OUT = "/in/norma.pdf", "/out"
os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()
subprocess.run(["pdftoppm", "-r", "220", "-gray", "-png", SRC, f"{tmp}/p"], check=True)
pages, report = [], []
for img in sorted(glob.glob(f"{tmp}/p-*.png")):
    n = int(img.rsplit("-", 1)[1].split(".")[0])
    txt = subprocess.run(["tesseract", img, "-", "-l", "spa+eng", "--psm", "3"],
                         capture_output=True, text=True).stdout
    tsv = subprocess.run(["tesseract", img, "-", "-l", "spa+eng", "--psm", "3", "tsv"],
                         capture_output=True, text=True).stdout.splitlines()[1:]
    conf = [float(r.split("\t")[10]) for r in tsv if r.count("\t") >= 11 and r.split("\t")[10] not in ("-1", "conf")]
    report.append({"page": n, "chars": len(txt), "mean_conf": round(sum(conf) / len(conf), 1) if conf else None})
    pages.append(f"\n\n<!-- page {n} -->\n\n{txt.strip()}")
open(f"{OUT}/ISO27701-2025.md", "w", encoding="utf-8").write("# ISO/IEC 27701:2025 (OCR, texto derivado)\n" + "".join(pages))
json.dump({"tool": "tesseract (spa+eng, 220 dpi, psm 3)", "pages": report}, open(f"{OUT}/ocr_report.json", "w"), indent=1)
low = [r for r in report if (r["mean_conf"] or 0) < 70]
print(f"pages={len(report)} chars={sum(r['chars'] for r in report)} low_conf_pages={[r['page'] for r in low]}")
