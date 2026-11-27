import duckdb

F = "data/raw/comments_clean.parquet"
con = duckdb.connect()

print("=== تعداد نظرات و محصولات ===")
print(con.sql(f"select count(*) as n_rows, count(distinct product_id) as n_products from '{F}'").df())

print("\n=== ستون‌ها ===")
print(con.sql(f"describe select * from '{F}'").df()[["column_name", "column_type"]].to_string())

print("\n=== توزیع recommendation_status ===")
print(con.sql(f"select recommendation_status, count(*) as n from '{F}' group by 1 order by 2 desc").df())
