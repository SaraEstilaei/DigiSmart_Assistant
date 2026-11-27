import re

import duckdb
import pandas as pd

F = "data/raw/comments_clean.parquet"
OUT = "data/processed/product_pros_cons.parquet"
PLACEHOLDERS = {"ندارد", "نداره", "ندارم", "ندارن", "نداشت", "هیچ", "هیچی",
                "هیچکدام", "هیچ کدام", "ندیدم", "نداشت", "ندیده", "-", "."}


def clean(s):
    s = s.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    return re.sub(r"\s+", " ", s).strip(" .،,؛;:-–_*")


def split_items(text):
    if not isinstance(text, str):
        return []
    out = []
    for part in re.split(r"\||\n", text):
        p = clean(part)
        if 2 < len(p) <= 60 and p not in PLACEHOLDERS:
            out.append(p)
    return out


P = pd.read_parquet("data/processed/sample_products_3k.parquet")
con = duckdb.connect()
con.register("prod", P[["id"]])
df = con.sql(f"""
select c.product_id, c.id as comment_id, c.advantages, c.disadvantages
from '{F}' c join prod p on c.product_id = p.id
where c.is_repeat_in_product = false
""").df()
print("نظرات خوانده‌شده:", len(df))

rows = []
for side, col in [("advantage", "advantages"), ("disadvantage", "disadvantages")]:
    for pid, cid, text in zip(df["product_id"], df["comment_id"], df[col]):
        for item in set(split_items(text)):
            rows.append((pid, side, item, cid))
long = pd.DataFrame(rows, columns=["product_id", "side", "phrase", "comment_id"])

g = (long.groupby(["product_id", "side", "phrase"])
     .agg(count=("comment_id", "size"),
          example_comment_ids=("comment_id", lambda x: [int(i) for i in list(x)[:3]]))
     .reset_index())
g = g[g["count"] >= 2]  # فقط موارد تکرارشده
g = (g.sort_values(["product_id", "side", "count"], ascending=[True, True, False])
     .groupby(["product_id", "side"]).head(5))
g.to_parquet(OUT, index=False)

print("ذخیره شد:", OUT, g.shape)
print("محصولات دارای مزیت پرتکرار:", g[g.side == "advantage"].product_id.nunique())
print("محصولات دارای عیب پرتکرار:", g[g.side == "disadvantage"].product_id.nunique())
print(g[g.product_id == 134367].to_string())


