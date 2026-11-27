import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chat import chat_answer

for q in [
    "یک کیف برای استفاده روزمره می‌خوام که خیلی گرون نباشه و خریدارها هم ازش راضی باشن",
    "یک کتاب کودک زیر دویست هزار تومان",
]:
    out = chat_answer(q)
    print("پرسش:", q)
    print("فیلترهای استخراج‌شده:", out["parsed"])
    print("محصولات:", [(r["id"], r["title_fa"][:30]) for r in out["results"]])
    print("جواب:", out["answer"])
    print("-" * 40)
