"""Analyse v2 results: counts with Wilson CIs, scenario-clustered bootstrap contrasts,
inter-judge agreement, truncation/empty/error rates.

Usage: python experiments/analyze_v2.py
Writes experiments/metrics_summary_v2.json and experiments/results_v2.md
"""
import json, random, statistics as st
from collections import defaultdict
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "raw_results_v2" / "dialogues_v2.json"
PRIMARY, SECONDARY = "anthropic/claude-sonnet-5.5", "openai/gpt-4o-mini"
CONDS = ["Baseline", "No_System", "Minimal_Honesty", "Epistemic_Guardian"]
SHORT = {"openai/gpt-4o-mini": "GPT-4o-mini", "google/gemini-2.5-flash": "Gemini-2.5-Flash",
         "deepseek/deepseek-chat": "DeepSeek-V3", "z-ai/glm-5.3-flash": "GLM-5.3-Flash",
         "qwen/qwen-2.5-72b-instruct": "Qwen-2.5-72B", "mistralai/mistral-small-24b-instruct-2501": "Mistral-Small-3",
         "meta-llama/llama-3.1-8b-instruct": "Llama-3.1-8B"}
B = 10000
random.seed(0)


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (round(100 * max(0, c - h), 1), round(100 * min(1, c + h), 1))


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def wkappa(a, b, k=5):
    """quadratic-weighted kappa for 1..k ordinal scores"""
    n = len(a)
    O = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        # one primary-judge score is an off-scale half point (1.5); round half up for the confusion matrix only
        O[int(x + 0.5) - 1][int(y + 0.5) - 1] += 1
    ra = [sum(O[i]) for i in range(k)]
    cb = [sum(O[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * O[i][j]
            den += w * ra[i] * cb[j] / n
    return round(1 - num / den, 3) if den else None


def spearman(a, b):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for t in range(i, j + 1):
                r[s[t]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    return round(st.correlation(ra, rb), 3)


def cluster_boot_diff(recs, judge, c1, c2):
    """Difference in capitulation rate (c2 - c1), bootstrapping scenarios (the 6 vignettes)."""
    by_s = defaultdict(lambda: {c1: [], c2: []})
    for r in recs:
        jd = r["judgments"].get(judge, {})
        if r["condition"] in (c1, c2) and jd.get("capitulated") is not None:
            by_s[r["vignette_id"]][r["condition"]].append(int(jd["capitulated"]))
    scen = list(by_s)
    def rate(ss, c):
        xs = [x for s in ss for x in by_s[s][c]]
        return sum(xs) / len(xs) if xs else 0.0
    point = rate(scen, c2) - rate(scen, c1)
    draws = []
    for _ in range(B):
        ss = [random.choice(scen) for _ in scen]
        draws.append(rate(ss, c2) - rate(ss, c1))
    draws.sort()
    return round(100 * point, 1), (round(100 * draws[int(0.025 * B)], 1), round(100 * draws[int(0.975 * B)], 1))


def cluster_boot_rate(recs, judge, c):
    by_s = defaultdict(list)
    for r in recs:
        jd = r["judgments"].get(judge, {})
        if r["condition"] == c and jd.get("capitulated") is not None:
            by_s[r["vignette_id"]].append(int(jd["capitulated"]))
    scen = list(by_s)
    draws = []
    for _ in range(B):
        xs = [x for s in (random.choice(scen) for _ in scen) for x in by_s[s]]
        draws.append(sum(xs) / len(xs))
    draws.sort()
    return (round(100 * draws[int(0.025 * B)], 1), round(100 * draws[int(0.975 * B)], 1))


def main():
    recs = json.loads(RAW.read_text(encoding="utf-8"))
    out = {"n_dialogues": len(recs), "primary_judge": PRIMARY, "secondary_judge": SECONDARY}
    ok = [r for r in recs if r["status"] == "ok"]
    turns = [t for r in recs for t in r["trajectory"]]
    out["quality"] = {
        "empty_reply_dialogues": sum(r["status"] != "ok" for r in recs),
        "turns": len(turns),
        "turns_finish_length": sum(t["finish_reason"] == "length" for t in turns),
        "judge_errors": {j: sum(1 for r in ok if r["judgments"].get(j, {}).get("error")) for j in (PRIMARY, SECONDARY)},
        "glm_turns_with_answer_content": sum(1 for r in recs if "glm" in r["model"] for t in r["trajectory"] if t["assistant"]),
        "glm_turns": sum(1 for r in recs if "glm" in r["model"] for t in r["trajectory"]),
    }

    table = {}
    for judge in (PRIMARY, SECONDARY):
        tj = {}
        for m in SHORT:
            for c in CONDS:
                rs = [r for r in ok if r["model"] == m and r["condition"] == c and r["judgments"].get(judge, {}).get("capitulated") is not None]
                if not rs:
                    continue
                k = sum(r["judgments"][judge]["capitulated"] for r in rs)
                ef = [r["judgments"][judge]["avg_firmness"] for r in rs]
                al = [r["judgments"][judge]["avg_alternative"] for r in rs]
                tj[f"{m}|{c}"] = {"k": k, "n": len(rs), "rate": round(100 * k / len(rs), 1), "wilson": wilson(k, len(rs)),
                                  "t3_endorsed": sum(r["judgments"][judge]["t3_endorsed"] for r in rs),
                                  "t1_flagged": sum(r["judgments"][judge]["t1_flagged"] for r in rs),
                                  "firmness": round(st.mean(ef), 2), "firmness_sd": round(st.stdev(ef), 2) if len(ef) > 1 else 0,
                                  "alternative": round(st.mean(al), 2), "alternative_sd": round(st.stdev(al), 2) if len(al) > 1 else 0,
                                  "turn_firmness": [round(st.mean(r["judgments"][judge]["turns"][i]["firmness"] for r in rs), 2) for i in range(3)]}
        for c in CONDS:
            rs = [r for r in ok if r["condition"] == c and r["judgments"].get(judge, {}).get("capitulated") is not None]
            k = sum(r["judgments"][judge]["capitulated"] for r in rs)
            ef = [r["judgments"][judge]["avg_firmness"] for r in rs]
            al = [r["judgments"][judge]["avg_alternative"] for r in rs]
            by_scen = defaultdict(lambda: [0, 0])
            for r in rs:
                by_scen[r["vignette_id"]][0] += r["judgments"][judge]["capitulated"]
                by_scen[r["vignette_id"]][1] += 1
            tj[f"POOLED|{c}"] = {"k": k, "n": len(rs), "rate": round(100 * k / len(rs), 1), "wilson": wilson(k, len(rs)),
                                 "cluster_boot_ci": cluster_boot_rate(ok, judge, c),
                                 "t3_endorsed": sum(r["judgments"][judge]["t3_endorsed"] for r in rs),
                                 "firmness": round(st.mean(ef), 2), "firmness_sd": round(st.stdev(ef), 2),
                                 "alternative": round(st.mean(al), 2), "alternative_sd": round(st.stdev(al), 2),
                                 "by_scenario": {s: f"{a}/{b}" for s, (a, b) in sorted(by_scen.items())}}
        tj["contrasts"] = {f"{c2} - {c1}": cluster_boot_diff(ok, judge, c1, c2) for c1, c2 in
                           [("Baseline", "Epistemic_Guardian"), ("Baseline", "Minimal_Honesty"),
                            ("Minimal_Honesty", "Epistemic_Guardian"), ("No_System", "Epistemic_Guardian"),
                            ("Baseline", "No_System")]}
        table[judge] = tj
    out["results"] = table

    both = [r for r in ok if all(r["judgments"].get(j, {}).get("capitulated") is not None for j in (PRIMARY, SECONDARY))]
    a = [int(r["judgments"][PRIMARY]["capitulated"]) for r in both]
    b = [int(r["judgments"][SECONDARY]["capitulated"]) for r in both]
    fa = [t["firmness"] for r in both for t in r["judgments"][PRIMARY]["turns"]]
    fb = [t["firmness"] for r in both for t in r["judgments"][SECONDARY]["turns"]]
    ea = [int(r["judgments"][PRIMARY]["t3_endorsed"]) for r in both]
    eb = [int(r["judgments"][SECONDARY]["t3_endorsed"]) for r in both]
    out["judge_agreement"] = {"n_dialogues": len(both),
                              "capitulated_raw_agreement": round(sum(x == y for x, y in zip(a, b)) / len(a), 3),
                              "capitulated_kappa": kappa(a, b), "t3_endorsed_kappa": kappa(ea, eb),
                              "firmness_turn_weighted_kappa": wkappa(fa, fb), "firmness_turn_spearman": spearman(fa, fb),
                              "capitulated_primary_only": sum(x and not y for x, y in zip(a, b)),
                              "capitulated_secondary_only": sum(y and not x for x, y in zip(a, b)),
                              "non_integer_firmness_scores": sum(1 for v in fa + fb if v != int(v))}

    (ROOT / "experiments" / "metrics_summary_v2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    # markdown report
    L = [f"# v2 results ({len(recs)} dialogues)\n", f"Primary judge: `{PRIMARY}`; secondary: `{SECONDARY}`\n",
         "## Data quality", "```", json.dumps(out["quality"], indent=1), "```", "## Judge agreement", "```",
         json.dumps(out["judge_agreement"], indent=1), "```"]
    for judge in (PRIMARY, SECONDARY):
        tj = table[judge]
        L += [f"\n## Capitulation by model x condition — judge `{judge}`\n",
              "| Model | " + " | ".join(CONDS) + " |", "|---|" + "---|" * len(CONDS)]
        for m in list(SHORT) + ["POOLED"]:
            row = [SHORT.get(m, "**Pooled**")]
            for c in CONDS:
                e = tj.get(f"{m}|{c}")
                row.append(f"{e['k']}/{e['n']} (EF {e['firmness']}, Alt {e['alternative']})" if e else "-")
            L.append("| " + " | ".join(row) + " |")
        L += ["", "Pooled detail:", "```"] + [f"{c}: {json.dumps(tj['POOLED|'+c])}" for c in CONDS] + ["```",
              "Contrasts (pct-point difference in capitulation, scenario-cluster bootstrap 95% CI):", "```",
              json.dumps(tj["contrasts"], indent=1), "```"]
    (ROOT / "experiments" / "results_v2.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
