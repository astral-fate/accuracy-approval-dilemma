import json

path = r"D:\ins respinse\AI x Epistemics Research Sprint\06_Our_Project\accuracy_approval_dilemma\experiments\raw_results\all_dialogue_runs.json"
with open(path, "r", encoding="utf-8") as f:
    runs = json.load(f)

for r in runs:
    if r["model"] == "openai/gpt-4o-mini" and r["vignette_id"] == "leg_01":
        print(f"=== CONDITION: {r['condition']} ===")
        for t in r["trajectory"]:
            print(f"--- Turn {t['turn']} ---")
            print("USER:", t["user"][:120])
            print("ASSISTANT:", t["assistant"][:250])
            print("METRICS:", t["metrics"])
            print()
