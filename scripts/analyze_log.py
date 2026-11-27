from pathlib import Path

import pandas as pd

df = pd.read_csv("logs/api_log.csv")
df = df[~df["task"].str.startswith("test")].copy()
df["از_کش"] = df["task"].str.endswith("_cached")
df["کار"] = df["task"].str.replace("_cached", "", regex=False)

g = (df.groupby(["کار", "از_کش"])
       .agg(تعداد=("task", "size"),
            میانگین_ثانیه=("latency_s", "mean"),
            p95_ثانیه=("latency_s", lambda x: x.quantile(0.95)),
            مجموع_توکن=("total_tokens", "sum"),
            هزینه_تومان=("cost_toman", "sum"))
       .round(4).reset_index())
print(g.to_string(index=False))

llm = df[~df["از_کش"]]
print("\nمجموع تماس‌های واقعی به API:", len(llm))
print("مجموع توکن:", int(llm["total_tokens"].sum()))
print("مجموع هزینه (تومان):", round(llm["cost_toman"].sum(), 1))
print("برخورد به کش:", int(df["از_کش"].sum()), "از", len(df), "ردیف")

Path("reports").mkdir(exist_ok=True)
g.to_csv("reports/latency_cost_summary.csv", index=False, encoding="utf-8-sig")
print("\nذخیره شد: reports/latency_cost_summary.csv")
