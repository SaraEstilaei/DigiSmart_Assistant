import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.manager import (list_categories, low_recommend_products,
                         brand_summary, top_complaints)

cats = list_categories()
print("دسته‌ها:", cats[:8])
cat = cats[0]
print("\n=== دسته:", cat, "===")
print("\n--- پرنظر با درصد پیشنهاد پایین ---")
print(low_recommend_products(cat, top=5).to_string())
print("\n--- برندها ---")
print(brand_summary(cat, top=5).to_string())
print("\n--- شکایت‌های پرتکرار ---")
print(top_complaints(cat, top=5).to_string())
