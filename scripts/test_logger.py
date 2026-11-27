import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm_logger import chat, embed

r = chat(
    [{"role": "user", "content": "یک جمله درباره کیف روزمره بنویس"}],
    task="test",
    max_tokens=60,
)
print(r.choices[0].message.content)

e = embed("کیف روزمره", task="test")
print("طول بردار:", len(e.data[0].embedding))
