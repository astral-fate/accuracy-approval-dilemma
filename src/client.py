import os, json, time, urllib.request, hashlib
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Models served from Adaption's hosted Responses API (sprint credits) instead of OpenRouter.
# Key: the model name used throughout the study; value: Adaption's hosted model id.
ADAPTION_MODELS = {"z-ai/glm-5.3-flash": "glm-53-flash"}


def load_env_var(name):
    """Read NAME from the sprint-level .env, then the process environment."""
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    return os.environ.get(name)

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
        self._adaption = None
        if load_env_var("ADAPTION_API_KEY") and not os.environ.get("ADAPTION_API_KEY"):
            os.environ["ADAPTION_API_KEY"] = load_env_var("ADAPTION_API_KEY")

    def complete_full(self, model: str, messages: list, temperature: float = 0.2, max_tokens: int = 4000,
                      extra: dict = None, sample: int = 0, use_cache: bool = True) -> dict:
        """v2 call: returns {content, finish_reason, reasoning_chars, completion_tokens}.

        Only the user-facing `content` is ever returned as the answer. Reasoning traces are
        never substituted for it, and an empty answer is reported (content == "") rather
        than replaced with placeholder text. The cache key covers every request parameter.
        """
        extra = extra or {}
        provider = "adaption" if model in ADAPTION_MODELS else "openrouter"
        key = {"v": 2, "model": model, "messages": messages, "temperature": temperature,
               "max_tokens": max_tokens, "extra": extra, "sample": sample}
        if provider == "adaption":
            key["provider"] = "adaption"  # never collide with OpenRouter cache entries
        key_src = json.dumps(key, sort_keys=True)
        cache_file = CACHE_DIR / f"v2_{hashlib.md5(key_src.encode('utf-8')).hexdigest()}.json"
        if use_cache and cache_file.exists():
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))["result"]
            except Exception:
                pass

        if provider == "adaption":
            result = self._adaption_call(ADAPTION_MODELS[model], messages, temperature, max_tokens, extra)
            if use_cache:
                cache_file.write_text(json.dumps({"request": {"provider": "adaption", "model": ADAPTION_MODELS[model],
                                                              "temperature": temperature, "max_tokens": max_tokens, **extra},
                                                  "messages": messages, "result": result}, indent=2), encoding="utf-8")
            return result

        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, **extra}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://apartresearch.com",
            "X-Title": "Accuracy-Approval-Dilemma-Sprint"
        }
        delay = 3
        for attempt in range(5):
            try:
                req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                                             data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=180) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                choice = res["choices"][0]
                msg = choice["message"]
                result = {
                    "content": (msg.get("content") or "").strip(),
                    "finish_reason": choice.get("finish_reason"),
                    "reasoning_chars": len(msg.get("reasoning") or ""),
                    "completion_tokens": (res.get("usage") or {}).get("completion_tokens"),
                }
                if use_cache:
                    cache_file.write_text(json.dumps({"request": {k: v for k, v in payload.items() if k != "messages"},
                                                      "messages": messages, "result": result}, indent=2), encoding="utf-8")
                return result
            except Exception as e:
                print(f"[{model}] attempt {attempt+1} failed: {e}")
                if attempt == 4:
                    raise
                time.sleep(delay)
                delay *= 2

    def _adaption_call(self, model_id: str, messages: list, temperature: float, max_tokens: int, extra: dict) -> dict:
        """GLM via Adaption's hosted Responses API (sprint credits). Same contract as complete_full:
        only the answer text is returned; reasoning items are counted, never substituted."""
        from adaption import Adaption  # optional dependency, only needed for Adaption-hosted models
        if self._adaption is None:
            self._adaption = Adaption(timeout=180)
        delay = 3
        for attempt in range(5):
            try:
                r = self._adaption.responses.create(model=model_id, input=messages, temperature=temperature,
                                                    max_output_tokens=max_tokens, store=False,
                                                    extra_body=extra or None)
                reasoning = sum(len(p.get("text", "")) if isinstance(p, dict) else len(getattr(p, "text", "") or "")
                                for it in r.output if it.type == "reasoning" for p in (getattr(it, "summary", None) or []))
                if r.status == "completed":
                    finish = "stop"
                elif r.status == "incomplete":
                    why = getattr(r.incomplete_details, "reason", None) or "incomplete"
                    finish = "length" if "token" in why else why
                else:
                    raise RuntimeError(f"Adaption response status={r.status} error={r.error}")
                return {"content": (r.output_text or "").strip(), "finish_reason": finish,
                        "reasoning_chars": reasoning, "completion_tokens": r.usage.output_tokens if r.usage else None,
                        "reasoning_tokens": ((r.usage.output_tokens_details or {}).get("reasoning_tokens") if r.usage else None),
                        "provider": "adaption"}
            except Exception as e:
                print(f"[adaption/{model_id}] attempt {attempt+1} failed: {e}")
                if attempt == 4:
                    raise
                time.sleep(delay)
                delay *= 2

    def complete(self, model: str, messages: list, temperature: float = 0.2, max_tokens: int = 600, use_cache: bool = True) -> str:
        """Legacy v1 call, kept only so v1 results can be replayed from cache.

        Known defects (fixed in complete_full): falls back to reasoning traces when content is
        empty, substitutes placeholder text, and omits max_tokens from the cache key.
        """
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
