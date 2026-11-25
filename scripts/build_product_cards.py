import duckdb
import pandas as pd

F = "data/raw/comments_clean.parquet"
OUT = "data/processed/product_cards.parquet"

P = pd.read_parquet("data/processed/sample_products_3k.parquet")
con = duckdb.connect()
con.register("prod", P[["id"]])

# 1) آمار پیشنهاد (فقط روی نظرهای دارای برچسب)
stats = con.sql(f"""
select c.product_id,
       count(*) as n_comments_all,
       count(c.recommendation_status) as n_labeled_comments,
       sum(case when c.recommendation_status = 'recommended' then 1 else 0 end) as n_recommended,
       sum(case when c.recommendation_status = 'not_recommended' then 1 else 0 end) as n_not_recommended,
       sum(case when c.recommendation_status = 'no_idea' then 1 else 0 end) as n_no_idea,
       avg(c.rate) as avg_comment_rate
from '{F}' c join prod p on c.product_id = p.id
group by 1
""").df()

stats["recommended_pct"] = (
    stats["n_recommended"] / stats["n_labeled_comments"].where(stats["n_labeled_comments"] > 0)
) * 100
stats["not_recommended_pct"] = (
    stats["n_not_recommended"] / stats["n_labeled_comments"].where(stats["n_labeled_comments"] > 0)
) * 100

# 2) نظرات نمونه برای ارجاع (۳ نظر با بیشترین لایک برای هر محصول)
samples = con.sql(f"""
select product_id, list(id order by likes desc)[:3] as sample_comment_ids
from (
  select c.product_id, c.id, c.likes
  from '{F}' c join prod p on c.product_id = p.id
  where c.is_short_body = false and c.is_repeat_in_product = false
)
group by 1
""").df()
samples["sample_comment_ids"] = samples["sample_comment_ids"].apply(lambda x: [int(i) for i in x])

cards = P.merge(stats, left_on="id", right_on="product_id", how="left").drop(columns=["product_id"])
cards = cards.merge(samples, left_on="id", right_on="product_id", how="left").drop(columns=["product_id"])

cards.to_parquet(OUT, index=False)
print("ذخیره شد:", OUT, cards.shape)
print(cards[["n_comments_all", "n_labeled_comments", "recommended_pct"]].describe())
