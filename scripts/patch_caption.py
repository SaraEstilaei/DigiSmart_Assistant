u = "src/ui/app.py"
t = open(u, encoding="utf-8").read()
old = "چون با دسته‌ی انتخاب‌شده نتیجه‌ای نبود، دسته نادیده گرفته شد."
new = "چون نتیجه‌ها با دسته‌ی حدس‌زده‌شده کم بود، بدون دسته هم جست‌وجو شد."
assert old in t, "جمله پیدا نشد"
open(u, "w", encoding="utf-8").write(t.replace(old, new))
print("OK")
