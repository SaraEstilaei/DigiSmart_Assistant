import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.ranking import add_bayesian_score

df = pd.read_parquet("data/processed/sample_products_3k.parquet")
df = add_bayesian_score(df, m=20)

cols = ["id", "title_fa", "Rate", "Rate_cnt", "bayes_score"]
print("=== 10 تای اول بر اساس امتیاز خام ===")
print(df.sort_values("Rate", ascending=False)[cols].head(10).to_string())
print()
print("=== 10 تای اول بر اساس امتیاز بیزی ===")
print(df.sort_values("bayes_score", ascending=False)[cols].head(10).to_string())
