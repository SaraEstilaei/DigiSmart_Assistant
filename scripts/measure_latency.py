import csv
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import llm_cache
from src.chat import chat_answer
from src.compare import compare
from src.manager import brand_summary, low_recommend_products, top_complaints

SCENARIOS = {
    "chat_ساده": lambda: chat_answer("یک کتاب کودک زیر دویست هزار تومان"),
    "chat_ترکیبی": lambda: chat_answer("یک کیف برای استفاده روزمره می‌خوام که خیلی گرون نباشه و خریدارها هم ازش راضی باشن"),
    "chat_مبهم": lambda: chat_answer("یه چیز خوب برای سفر"),
    "compare_2محصول": lambda: compare([2829072, 7294595], "یک کیف ارزان"),
    "compare_3محصول": lambda: compare([2829072, 7294595, 4260784], "یک کیف ارزان"),
    "compare_5محصول": lambda: compare([3405355, 4993147, 8682753, 2829072, 4260784], "یک کیف با رضایت بالا"),
    "manager_بدون_LLM": lambda: (low_recommend_products("beauty"), brand_summary("beauty"), top_complaints("beauty")),
}
REPS = 2

rows = []
for rep in range(1, REPS + 1):
    llm_cache._cache.clear()
    for mode in ("بدون کش", "با کش"):
        for name, fn in SCENARIOS.items():
            t = time.time()
            fn()
            rows.append((name, mode, rep, round(time.time() - t, 4)))
            print(rep, mode, name, rows[-1][3])

Path("reports").mkdir(exist_ok=True)
with open("reports/latency_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["scenario", "mode", "rep", "seconds"])
    w.writerows(rows)

print("\n=== میانگین زمان (ثانیه) ===")
for name in SCENARIOS:
    a = [r[3] for r in rows if r[0] == name and r[1] == "بدون کش"]
    b = [r[3] for r in rows if r[0] == name and r[1] == "با کش"]
    print(f"{name}: بدون کش {statistics.mean(a):.2f} | با کش {statistics.mean(b):.4f}")
