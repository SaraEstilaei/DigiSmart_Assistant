import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.compare import compare

SETS = [
    [134367, 2829072],
    [134367, 2829072, 7294595],
    [134367, 4260784],
    [2829072, 4260784, 7294595],
    [3405355, 4993147, 8682753],
    [335087, 3281173],
]


def evidence_ids(ev_map):
    ids = set()
    for ev in ev_map.values():
        for side in ("advantages", "disadvantages"):
            for item in ev[side]:
                ids.update(item["comment_ids"])
    return ids


total = ok = 0
fake = []
for s in SETS:
    out = compare(s, "مقایسه برای انتخاب بهتر")
    allowed = evidence_ids(out["evidence"])
    found = set(int(x) for x in re.findall(r"\b\d{5,9}\b", out["summary"]))
    found -= set(s)                      # شناسه‌ی محصول‌ها comment_id نیست
    good = found & allowed
    bad = found - allowed
    total += len(found)
    ok += len(good)
    fake += [(s, b) for b in bad]
    print(s, "| شناسه‌ی نظر در جواب:", len(found), "| درست:", len(good), "| ساختگی:", len(bad))

print("\nمجموع شناسه‌های نظر در جواب‌ها:", total)
print("شناسه‌های پشتیبانی‌شده با شواهد:", ok)
if total:
    print(f"نرخ Grounding: {100 * ok / total:.0f}٪")
print("موارد ساختگی:", fake)
