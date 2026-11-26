import duckdb
import pandas as pd

F = "data/raw/comments_clean.parquet"
P = pd.read_parquet("data/processed/sample_products_3k.parquet")
con = duckdb.connect()
con.register("prod", P[["id"]])

d = con.sql(f"""
select c.product_id, c.advantages, c.disadvantages
from '{F}' c join prod p on c.product_id = p.id
where c.advantages is not null and c.disadvantages is not null
limit 8
""").df()
for _, r in d.iterrows():
    print("محصول:", r["product_id"])
    print("  مزایا:", repr(r["advantages"]))
    print("  معایب:", repr(r["disadvantages"]))
