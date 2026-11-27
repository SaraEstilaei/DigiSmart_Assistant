import duckdb
import pandas as pd

F = "data/raw/comments_clean.parquet"
P = pd.read_parquet("data/processed/sample_products_3k.parquet")
con = duckdb.connect()
con.register("prod", P[["id"]])

q = f"""
select c.product_id, count(*) as n_comments,
       count(c.recommendation_status) as n_labeled
from '{F}' c join prod p on c.product_id = p.id
group by 1
"""
d = con.sql(q).df()
print("محصولات پیدا شده:", len(d), "از", len(P))
print("کل نظرات:", d["n_comments"].sum())
print(d[["n_comments", "n_labeled"]].describe())
print("محصولات با حداقل ۱۰ نظر دارای برچسب:", (d["n_labeled"] >= 10).sum())
