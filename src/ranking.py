import pandas as pd


def add_bayesian_score(df, m=20):
    """امتیاز بیزی: محصولات کم‌نظر به میانگین کل نزدیک می‌شوند.

    Rate در داده 0 تا 100 است، پس به مقیاس 0 تا 5 تبدیل می‌شود.
    m = وزن میانگین کل (هرچه بزرگ‌تر، محصولات کم‌نظر بیشتر کشیده می‌شوند).
    """
    df = df.copy()
    df["rate5"] = df["Rate"] / 20
    valid = df["rate5"].notna() & (df["Rate_cnt"] > 0)
    c = df.loc[valid, "rate5"].mean()  # میانگین کل
    v = df["Rate_cnt"].fillna(0)
    r = df["rate5"].fillna(c)
    df["bayes_score"] = (v / (v + m)) * r + (m / (v + m)) * c
    return df


def add_recommend_score(df, m=20):
    """درصد پیشنهاد بیزی: محصولات با نظر برچسب‌دار کم به میانگین کل نزدیک می‌شوند.

    خروجی rec_score بین 0 و 1 است.
    """
    df = df.copy()
    n = df["n_labeled_comments"].fillna(0)
    p = (df["recommended_pct"] / 100).fillna(0)
    valid = df["n_labeled_comments"].fillna(0) > 0
    c = (df.loc[valid, "recommended_pct"] / 100).mean()  # میانگین کل
    df["rec_score"] = (n / (n + m)) * p + (m / (n + m)) * c
    return df


def add_final_score(df, w_bayes=0.6, w_rec=0.4):
    """امتیاز نهایی = ترکیب وزن‌دار امتیاز بیزی (نرمال‌شده) و درصد پیشنهاد بیزی."""
    df = df.copy()
    df["final_score"] = w_bayes * (df["bayes_score"] / 5) + w_rec * df["rec_score"]
    return df
