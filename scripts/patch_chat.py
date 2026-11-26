p = "src/chat.py"
s = open(p, encoding="utf-8").read()
old = """    if not results and kw:
        results = search_products("", filters, top_k=top_k)
        relaxed = True
"""
new = """    if not results and kw and "category" in filters:
        f2 = {k: v for k, v in filters.items() if k != "category"}
        results = search_products(kw, f2, top_k=top_k)
        relaxed = True
"""
assert old in s, "متن قدیمی پیدا نشد"
open(p, "w", encoding="utf-8").write(s.replace(old, new))
print("OK")
