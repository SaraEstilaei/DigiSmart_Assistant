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
