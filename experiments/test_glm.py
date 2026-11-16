import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
from src.client import LLMClient

client = LLMClient()
candidates = [
    "z-ai/glm-4.5",
    "z-ai/glm-4.7-flash",
    "z-ai/glm-5",
    "z-ai/glm-5.3-flash"
]

for m in candidates:
    try:
        resp = client.complete(m, [{"role": "user", "content": "Respond with OK and your model name in 10 words."}], max_tokens=30, use_cache=False)
        print(f"SUCCESS {m}: {resp.strip()[:80]}")
    except Exception as e:
        print(f"FAILED {m}: {e}")
