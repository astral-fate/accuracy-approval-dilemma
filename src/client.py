import os, json, time, urllib.request, hashlib
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_api_key():
    if not ENV_PATH.exists():
        return None
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    return os.environ.get("OPENROUTER_API_KEY")

class LLMClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or load_api_key()
        if not self.api_key:
            raise ValueError(f"OpenRouter API key not found in {ENV_PATH} or environment.")

    def complete(self, model: str, messages: list, temperature: float = 0.2, max_tokens: int = 600, use_cache: bool = True) -> str:
        cache_key = hashlib.md5((model + json.dumps(messages) + str(temperature)).encode("utf-8")).hexdigest()
        cache_file = CACHE_DIR / f"{cache_key}.json"

        if use_cache and cache_file.exists():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                return cached_data["response"]
            except Exception:
                pass

        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://apartresearch.com",
            "X-Title": "Accuracy-Approval-Dilemma-Sprint"
        }

        retries = 3
        delay = 2
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=40) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    msg = res["choices"][0]["message"]
                    text = (msg.get("content") or msg.get("reasoning") or "").strip()
                    if not text:
                        text = "I have noted your concern, but maintain standard analytical boundaries."
                    if use_cache:
                        cache_file.write_text(json.dumps({"model": model, "messages": messages, "response": text}, indent=2), encoding="utf-8")
                    return text
            except Exception as e:
                print(f"[{model}] Request attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                time.sleep(delay)
                delay *= 2
        raise RuntimeError("Unreachable")
