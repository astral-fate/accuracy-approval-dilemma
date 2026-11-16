"""v2 experiment (post-review re-run).

Fixes relative to run_experiment.py (v1):
- Answers are `content` only; reasoning traces are never scored or fed back (GLM bug).
- GLM-5.3-Flash is served from Adaption's hosted Responses API (sprint credits), id
  glm-53-flash; all other targets and both judges use OpenRouter. It is run with reasoning effort "low"; at default effort it exhausts even
  8,000 tokens on reasoning and returns no answer.
- max_tokens raised from 350 to 4,000 and finish_reason recorded per turn (truncation).
- Four arms: Baseline (supportive), No system prompt, Minimal honesty prompt, EGS.
- k=3 samples per cell at temperature 0.7.
- Two condition-blind, full-dialogue judges: gpt-4o-mini (also a target) and
  claude-sonnet-5.5 (a family not among the targets).

Usage:  python experiments/run_v2.py [--workers 8] [--dry-run]
"""
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.client import LLMClient, ADAPTION_MODELS
from src.prompts import (BASELINE_SYSTEM_PROMPT, NO_SYSTEM_PROMPT, MINIMAL_HONESTY_SYSTEM_PROMPT,
                         EPISTEMIC_GUARDIAN_SYSTEM_PROMPT)
from src.evaluator_v2 import DialogueJudge

MODELS = [
    "openai/gpt-4o-mini",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat",
    "z-ai/glm-5.3-flash",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-small-24b-instruct-2501",
    "meta-llama/llama-3.1-8b-instruct",
]
MODEL_EXTRA = {"z-ai/glm-5.3-flash": {"reasoning": {"effort": "low"}}}
CONDITIONS = [
    ("Baseline", BASELINE_SYSTEM_PROMPT),
    ("No_System", NO_SYSTEM_PROMPT),
    ("Minimal_Honesty", MINIMAL_HONESTY_SYSTEM_PROMPT),
    ("Epistemic_Guardian", EPISTEMIC_GUARDIAN_SYSTEM_PROMPT),
]
SCENARIOS = ["res_01", "res_02", "org_01", "org_02", "leg_01", "leg_02"]
SAMPLES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 4000
JUDGES = ["openai/gpt-4o-mini", "anthropic/claude-sonnet-5.5"]

OUT = PROJECT_ROOT / "experiments" / "raw_results_v2" / "dialogues_v2.json"


def run_dialogue(client, model, cond, sys_prompt, v, sample):
    messages = [] if sys_prompt is None else [{"role": "system", "content": sys_prompt}]
    traj = []
    for turn, text in [(1, v["turn1_plan"]), (2, v["turn2_pushback"]), (3, v["turn3_ultimatum"])]:
        messages.append({"role": "user", "content": text})
        r = client.complete_full(model, messages, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
                                 extra=MODEL_EXTRA.get(model), sample=sample)
        traj.append({"turn": turn, "user": text, "assistant": r["content"], "finish_reason": r["finish_reason"],
                     "reasoning_chars": r["reasoning_chars"], "completion_tokens": r["completion_tokens"]})
        if not r["content"]:
            return {"status": "empty_reply", "trajectory": traj}
        messages.append({"role": "assistant", "content": r["content"]})
    return {"status": "ok", "trajectory": traj}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true", help="one dialogue per model, Baseline only")
    args = ap.parse_args()

    vignettes = {v["id"]: v for v in (json.loads(l) for l in
                 (PROJECT_ROOT / "data" / "vignettes.jsonl").read_text(encoding="utf-8").splitlines())}
    client = LLMClient()
    judges = [DialogueJudge(client, j) for j in JUDGES]

    jobs = [(m, c, p, s, k) for m in MODELS for c, p in CONDITIONS for s in SCENARIOS for k in range(SAMPLES)]
    if args.dry_run:
        jobs = [(m, "Baseline", BASELINE_SYSTEM_PROMPT, "res_01", 0) for m in MODELS]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() and not args.dry_run else []
    done = {(r["model"], r["condition"], r["vignette_id"], r["sample"]) for r in results}
    jobs = [j for j in jobs if (j[0], j[1], j[3], j[4]) not in done]
    if not os.environ.get("ADAPTION_API_KEY"):
        held = [j for j in jobs if j[0] in ADAPTION_MODELS]
        jobs = [j for j in jobs if j[0] not in ADAPTION_MODELS]
        if held:
            print(f"ADAPTION_API_KEY not set: holding {len(held)} Adaption-hosted dialogues for a later resume")
    print(f"{len(done)} done, {len(jobs)} to run")
    lock = threading.Lock()

    def work(job):
        m, c, p, s, k = job
        d = run_dialogue(client, m, c, p, vignettes[s], k)
        rec = {"model": m, "condition": c, "vignette_id": s, "domain": vignettes[s]["domain"], "sample": k,
               "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS, "model_extra": MODEL_EXTRA.get(m),
               "provider": "adaption" if m in ADAPTION_MODELS else "openrouter", **d,
               "judgments": {}}
        if d["status"] == "ok":
            for j in judges:
                rec["judgments"][j.judge_model] = j.judge(vignettes[s], d["trajectory"])
        return rec

    t0 = time.time()
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(work, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                rec = f.result()
            except Exception as e:
                print("ERROR", futs[f][:2], futs[f][3:], e)
                continue
            with lock:
                results.append(rec)
                if not args.dry_run and (i % 10 == 0 or i == len(jobs)):
                    OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
            caps = {jm.split('/')[1]: jd.get("capitulated") for jm, jd in rec["judgments"].items()}
            fr = [t["finish_reason"] for t in rec["trajectory"]]
            print(f"[{i}/{len(jobs)} {time.time()-t0:.0f}s] {rec['model'].split('/')[1]:<32} {rec['condition']:<18} "
                  f"{rec['vignette_id']} s{rec['sample']} {rec['status']} finish={fr} cap={caps}", flush=True)
    if args.dry_run:
        print(json.dumps(results, indent=1, ensure_ascii=False)[:6000])
    else:
        OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
        print("saved", OUT, len(results))


if __name__ == "__main__":
    main()
