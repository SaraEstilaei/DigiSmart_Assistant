import csv
import os
import time
from datetime import datetime

from src.config import client

LOG_PATH = "logs/api_log.csv"
FIELDS = [
    "time", "task", "model", "latency_s",
    "prompt_tokens", "completion_tokens", "total_tokens",
    "cost_usd", "cost_toman",
]


def _log(row):
    os.makedirs("logs", exist_ok=True)
    new_file = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerow(row)


def _record(task, model, latency, usage):
    _log({
        "time": datetime.now().isoformat(timespec="seconds"),
        "task": task,
        "model": model,
        "latency_s": round(latency, 3),
        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
        "completion_tokens": getattr(usage, "completion_tokens", 0),
        "total_tokens": getattr(usage, "total_tokens", 0),
        "cost_usd": getattr(usage, "cost", 0) or 0,
        "cost_toman": getattr(usage, "total_cost_toman", 0) or 0,
    })


def chat(messages, model="openai/gpt-4o-mini", task="general", **kwargs):
    """مثل client.chat.completions.create ولی زمان و هزینه را ثبت می‌کند."""
    start = time.time()
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    _record(task, model, time.time() - start, resp.usage)
    return resp


def embed(texts, model="openai/text-embedding-3-small", task="embedding"):
    """مثل client.embeddings.create ولی زمان و هزینه را ثبت می‌کند."""
    start = time.time()
    resp = client.embeddings.create(model=model, input=texts)
    _record(task, model, time.time() - start, resp.usage)
    return resp


def _log_cache_hit(task, model, latency):
    _log({
        "time": datetime.now().isoformat(timespec="seconds"),
        "task": task + "_cached",
        "model": model,
        "latency_s": round(latency, 4),
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0,
        "cost_toman": 0,
    })
