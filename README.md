# DigiSmart_Assistant
Smart e-commerce assistant using LLM for product reviews and recommendations.


## بخش جست‌وجو، مقایسه، چت، تحلیل مدیر و UI (امیرعلی)

### نصب
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt

کلید API را در فایل `.env` بگذارید (هرگز commit نشود):

    QBC13_API_KEY=کلید-گروه

### داده‌ها (در گیت نیستند)
- `data/processed/sample_products_3k.parquet` (از پوشه‌ی LLM در Drive)
- `data/raw/comments_clean.parquet` (از `comments_clean.zip` در همان پوشه)

### ساخت فایل‌های میانی
    python scripts\build_product_cards.py
    python scripts\build_pros_cons.py

اولی `data/processed/product_cards.parquet` (درصد پیشنهاد و تعداد نظر هر محصول) و دومی `data/processed/product_pros_cons.parquet` (مزایا و معایب پرتکرار با comment_id) را می‌سازد.

### اجرای برنامه
    streamlit run src\ui\app.py

تب‌ها: دستیار (چت)، جست‌وجوی محصول، مقایسه، تحلیل مدیر.

### فایل‌های کلیدی
- `src/ranking.py`: امتیاز بیزی، درصد پیشنهاد بیزی و امتیاز نهایی (۰.۶ و ۰.۴، وزن‌ها دستی)
- `src/product_search.py`: `search_products(query, filters, top_k)`
- `src/compare.py`: جدول مقایسه با کد و جمع‌بندی مدل در سه بخش (داده مستقیم، شواهد نظرات، استنتاج)
- `src/chat.py`: استخراج فیلتر از پرسش فارسی و پاسخ (نسخه‌ی موقت)
- `src/manager.py`: تحلیل دسته برای مدیر (بدون مدل زبانی)
- `src/llm_logger.py`: ثبت زمان، توکن و هزینه‌ی هر تماس در `logs/api_log.csv`
- `src/llm_cache.py`: کش پاسخ‌ها روی دیسک

### ارزیابی
    python scripts\measure_latency.py
    python scripts\analyze_log.py
    python scripts\check_grounding.py
    python scripts\test_edge_cases.py

نتایج زمان و هزینه در پوشه‌ی `reports/` ذخیره می‌شود.

### نکته‌ها و محدودیت‌ها
- قیمت‌ها تومان هستند. `Rate` محصولات ۰ تا ۱۰۰ و `rate` نظرات ۰ تا ۵ است.
- درصد پیشنهاد فقط روی نظرهای دارای برچسب `recommendation_status` حساب می‌شود.
- مزایا و معایب با شمارش عبارت‌های یکسان استخراج می‌شوند؛ عبارت‌های مترادف جدا شمرده می‌شوند.
- جست‌وجو هنوز کلمه‌ای است و معنایی نیست؛ ممکن است نتیجه‌ی نامرتبط بدهد.
