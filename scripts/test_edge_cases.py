import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chat import chat_answer
from src.compare import compare
from src.manager import top_complaints
from src.product_search import search_products

CASES = {
    "compare_شناسه_نامعتبر": lambda: compare([1, 2], "تست"),
    "compare_یک_شناسه": lambda: compare([2829072], "تست"),
    "compare_معتبر_و_نامعتبر": lambda: compare([2829072, 1], "تست"),
    "chat_رشته_بی_معنی": lambda: chat_answer("asdf qwer"),
    "chat_بیرون_از_دامنه": lambda: chat_answer("هوای تهران فردا چطوره؟"),
    "chat_قیمت_غیرممکن": lambda: chat_answer("یک کیف زیر ۱۰۰ تومان"),
    "search_فیلتر_خالی": lambda: search_products("", {}, top_k=3),
    "search_کلمه_ناموجود": lambda: search_products("زززززز", {}, top_k=3),
    "manager_دسته_ناموجود": lambda: top_complaints("نامعتبر"),
}
for name, fn in CASES.items():
    try:
        out = fn()
        print("OK   ", name)
    except Exception as e:
        print("خطا  ", name, "->", type(e).__name__, str(e)[:100])
