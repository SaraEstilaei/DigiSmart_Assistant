import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import client, BASE_URL

print("URL:", BASE_URL)

models = client.models.list()
print("Number of models:", len(models.data))

chat = client.chat.completions.create(
    model="openai/gpt-4.1-mini",
    messages=[{"role": "user", "content": "Just write: Ready"}],
)
print("Chat response:", chat.choices[0].message.content)

print([m.id for m in models.data])

emb = client.embeddings.create(
    model="openai/text-embedding-3-small",
    input="hello",
)

print("Embedding dim:", len(emb.data[0].embedding))
