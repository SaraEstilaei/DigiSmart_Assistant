import hashlib
import json
import time

from diskcache import Cache

from src import llm_logger

_cache = Cache("cache/llm")
STATS = {"hits": 0, "misses": 0}


def _key(kind, model, payload):
    raw = json.dumps([kind, model, payload], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cached_chat(messages, model="openai/gpt-4o-mini", task="general", **kwargs):
    """مثل llm_logger.chat ولی جواب را کش می‌کند. خروجی: (متن جواب، از_کش_بود)."""
    key = _key("chat", model, [messages, kwargs])
    start = time.time()
    if key in _cache:
        STATS["hits"] += 1
        llm_logger._log_cache_hit(task, model, time.time() - start)
        return _cache[key], True
    STATS["misses"] += 1
    resp = llm_logger.chat(messages, model=model, task=task, **kwargs)
    text = resp.choices[0].message.content
    _cache[key] = text
    return text, False


def cached_embed(text, model="openai/text-embedding-3-small", task="embedding"):
    """مثل llm_logger.embed ولی بردار را کش می‌کند. خروجی: (بردار، از_کش_بود)."""
    key = _key("embed", model, text)
    start = time.time()
    if key in _cache:
        STATS["hits"] += 1
        llm_logger._log_cache_hit(task, model, time.time() - start)
        return _cache[key], True
    STATS["misses"] += 1
    resp = llm_logger.embed(text, model=model, task=task)
    vec = resp.data[0].embedding
    _cache[key] = vec
    return vec, False
