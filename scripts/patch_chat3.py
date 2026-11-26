p = "src/chat.py"
s = open(p, encoding="utf-8").read()
old = """    if not results and kw and "category" in filters:
        f2 = {k: v for k, v in filters.items() if k != "category"}
        results = search_products(kw, f2, top_k=top_k)
        relaxed = True
"""
new = """    if len(results) < top_k and kw and "category" in filters:
        f2 = {k: v for k, v in filters.items() if k != "category"}
        extra = search_products(kw, f2, top_k=top_k)
        seen = {r["id"] for r in results}
        results = results + [r for r in extra if r["id"] not in seen]
        results = sorted(results, key=lambda r: r["final_score"], reverse=True)[:top_k]
        relaxed = True
"""
assert old in s, "متن قدیمی chat.py پیدا نشد"
open(p, "w", encoding="utf-8").write(s.replace(old, new))

u = "src/ui/app.py"
t = open(u, encoding="utf-8").read()
old2 = 'st.json(out["filters"])'
assert old2 in t, "خط st.json پیدا نشد"
open(u, "w", encoding="utf-8").write(t.replace(old2, 'st.json(out["parsed"])'))
print("OK")
