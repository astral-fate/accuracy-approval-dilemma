import json, os, time, sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.client import LLMClient
from src.prompts import BASELINE_SYSTEM_PROMPT, EPISTEMIC_GUARDIAN_SYSTEM_PROMPT
from src.evaluator import EpistemicEvaluator
from src.runner import MultiTurnRunner

def main():
    print("=== Initializing Multi-Model Accuracy-Approval Dilemma Benchmark ===")
    vignettes_file = PROJECT_ROOT / "data" / "vignettes.jsonl"
    vignettes = [json.loads(l) for l in vignettes_file.read_text(encoding="utf-8").splitlines()]
    print(f"Loaded {len(vignettes)} total vignettes.")

    client = LLMClient()
    # Calibrated evaluator judge
    evaluator = EpistemicEvaluator(client=client, judge_model="openai/gpt-4o-mini")
    runner = MultiTurnRunner(client=client, evaluator=evaluator)

    # 7 diverse models across global lineages
    MODELS = [
        "openai/gpt-4o-mini",
        "google/gemini-2.5-flash",
        "deepseek/deepseek-chat",
        "z-ai/glm-5.3-flash",
        "qwen/qwen-2.5-72b-instruct",
        "mistralai/mistral-small-24b-instruct-2501",
        "meta-llama/llama-3.1-8b-instruct"
    ]

    CONDITIONS = [
        ("Baseline", BASELINE_SYSTEM_PROMPT),
        ("Epistemic_Guardian", EPISTEMIC_GUARDIAN_SYSTEM_PROMPT)
    ]

    # Representative core benchmark scenarios (2 per domain)
    selected_ids = ["res_01", "res_02", "org_01", "org_02", "leg_01", "leg_02"]
    selected_vignettes = [v for v in vignettes if v["id"] in selected_ids]
    print(f"Benchmarking {len(MODELS)} models across {len(selected_vignettes)} scenarios in 2 conditions ({len(MODELS)*len(CONDITIONS)*len(selected_vignettes)} total dialogues)...")

    output_dir = PROJECT_ROOT / "experiments" / "raw_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / "all_dialogue_runs.json"

    # Load existing results if resuming
    results = []
    completed_keys = set()
    if results_file.exists():
        try:
            results = json.loads(results_file.read_text(encoding="utf-8"))
            for r in results:
                completed_keys.add((r["model"], r["condition"], r["vignette_id"]))
            print(f"Resuming: found {len(results)} existing dialogue runs.")
        except Exception:
            results = []

    total_runs = len(MODELS) * len(CONDITIONS) * len(selected_vignettes)
    count = len(results)

    for model in MODELS:
        print(f"\n========================================================")
        print(f">>> Benchmarking Model: {model}")
        print(f"========================================================")
        for cond_name, sys_prompt in CONDITIONS:
            print(f"\n  --- Condition: {cond_name} ---")
            for v in selected_vignettes:
                key = (model, cond_name, v["id"])
                if key in completed_keys:
                    print(f"    [SKIP] Already completed: {model} | {cond_name} | {v['id']}")
                    continue

                count += 1
                print(f"    [{count}/{total_runs}] Running [{v['domain']}] {v['id']}: {v['title']}...")
                try:
                    res = runner.run_dialogue(
                        model=model,
                        system_prompt=sys_prompt,
                        vignette=v,
                        condition_name=cond_name
                    )
                    results.append(res)
                    completed_keys.add(key)
                    # Incremental save
                    results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
                    print(f"      -> Firmness T1-T3: {[t['metrics']['epistemic_firmness'] for t in res['trajectory']]} | Final Capitulation: {res['final_capitulated']}")
                except Exception as e:
                    print(f"      -> ERROR running {v['id']}: {e}")
                time.sleep(0.5)

    print(f"\nAll runs completed! Total saved: {len(results)} to {results_file}")

    # Compute aggregate statistics
    summary = {}
    for model in MODELS:
        summary[model] = {}
        for cond_name, _ in CONDITIONS:
            runs = [r for r in results if r["model"] == model and r["condition"] == cond_name]
            if not runs:
                continue
            
            n = len(runs)
            cap_rate = sum(1 for r in runs if r["final_capitulated"]) / n
            avg_firm = sum(r["avg_firmness"] for r in runs) / n
            avg_decay = sum(r["firmness_decay"] for r in runs) / n
            avg_deesc = sum(r["avg_deescalation"] for r in runs) / n
            avg_syco = sum(r["avg_sycophancy"] for r in runs) / n

            # Turn-by-turn firmness curves
            turn_firmness = [0.0, 0.0, 0.0]
            for r in runs:
                for t_idx in range(3):
                    turn_firmness[t_idx] += r["trajectory"][t_idx]["metrics"]["epistemic_firmness"]
            turn_firmness = [f / n for f in turn_firmness]

            summary[model][cond_name] = {
                "n_scenarios": n,
                "capitulation_rate": round(cap_rate * 100, 1),
                "avg_firmness": round(avg_firm, 2),
                "firmness_decay": round(avg_decay, 2),
                "turn_firmness_trajectory": [round(x, 2) for x in turn_firmness],
                "avg_deescalation": round(avg_deesc, 2),
                "avg_sycophancy": round(avg_syco, 2)
            }

    summary_file = PROJECT_ROOT / "experiments" / "metrics_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved aggregated metrics summary to {summary_file}")
    print("\n=== FINAL MULTI-MODEL EXPERIMENTAL SUMMARY ===")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
