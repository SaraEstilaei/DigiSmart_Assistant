import re

_AR2FA = str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه", "ة": "ه"})
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩0123456789", "01234567890123456789")
_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670\u0640]")  # اعراب و کشیده


def normalize(text) -> str:
    if not isinstance(text, str):
        return ""
    text = text.translate(_AR2FA).translate(_DIGITS)
    text = _DIACRITICS.sub("", text)
    text = text.replace("\u200c", " ")  
    text = re.sub(r"[^\w\s]", " ", text)  
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text) -> list[str]:
    return normalize(text).split()
