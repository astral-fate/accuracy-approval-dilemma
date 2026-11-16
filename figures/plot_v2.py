"""v2 figures from experiments/metrics_summary_v2.json (primary judge).

fig1_capitulation_curves.png : mean judge-rated firmness per turn, pooled over models, 4 conditions
fig2_model_comparison.png    : capitulation rate per model x condition with Wilson 95% CIs
fig3_pareto_frontier.png     : firmness vs constructive alternative, one point per model x condition
Written to figures/ and paper/figures/.
"""
import json, shutil
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "experiments" / "metrics_summary_v2.json").read_text(encoding="utf-8"))
J = S["primary_judge"]
R = S["results"][J]
CONDS = ["Baseline", "No_System", "Minimal_Honesty", "Epistemic_Guardian"]
LABEL = {"Baseline": "Supportive baseline", "No_System": "No system prompt",
         "Minimal_Honesty": "Minimal honesty prompt", "Epistemic_Guardian": "EGS"}
COLOR = dict(zip(CONDS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]))  # validated categorical slots 1-4
MODELS = {"openai/gpt-4o-mini": "GPT-4o-mini", "google/gemini-2.5-flash": "Gemini-2.5-Flash",
          "deepseek/deepseek-chat": "DeepSeek-V3", "z-ai/glm-5.3-flash": "GLM-5.3-Flash",
          "qwen/qwen-2.5-72b-instruct": "Qwen-2.5-72B", "mistralai/mistral-small-24b-instruct-2501": "Mistral-Small-3",
          "meta-llama/llama-3.1-8b-instruct": "Llama-3.1-8B"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False})
FIG = ROOT / "figures"
out = []

# ---- Fig 1: firmness by turn (pooled over models)
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=300)
ends = {}
for c in CONDS:
    traj = np.mean([R[f"{m}|{c}"]["turn_firmness"] for m in MODELS if f"{m}|{c}" in R], axis=0)
    ax.plot([1, 2, 3], traj, color=COLOR[c], lw=2, marker="o", ms=5, mec=SURF, mew=1.5, label=LABEL[c])
    ends[c] = traj[2]
# direct labels at the line ends, nudged apart so none overlap (min gap 0.24 on the y scale)
placed = []
for c in sorted(ends, key=ends.get, reverse=True):
    y = ends[c]
    if placed and placed[-1] - y < 0.24:
        y = placed[-1] - 0.24
    placed.append(y)
    ax.annotate(LABEL[c], (3, ends[c]), xytext=(3.08, y), textcoords="data", va="center", color=INK, fontsize=8)
ax.set_xticks([1, 2, 3], ["Turn 1\nflawed plan", "Turn 2\npushback", "Turn 3\nultimatum"])
ax.set_xlim(0.85, 3.9)
ax.set_ylim(1, 5.1)
ax.set_ylabel("Mean judge-rated firmness (1–5)")
ax.grid(axis="y", color=GRID, lw=0.6)
ax.legend(frameon=False, fontsize=8, loc="lower left")
ax.set_title(f"Firmness across turns, mean of 7 models (judge: {J.split('/')[1]})", color=INK, fontsize=9.5, loc="left")
fig.tight_layout()
out.append(FIG / "fig1_capitulation_curves.png")
fig.savefig(out[-1])
plt.close(fig)

# ---- Fig 2: capitulation by model x condition with Wilson CIs
fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=300)
x = np.arange(len(MODELS))
w = 0.2
for i, c in enumerate(CONDS):
    rates, lo, hi = [], [], []
    for m in MODELS:
        e = R[f"{m}|{c}"]
        rates.append(e["rate"])
        lo.append(e["rate"] - e["wilson"][0])
        hi.append(e["wilson"][1] - e["rate"])
    pos = x + (i - 1.5) * w
    ax.bar(pos, rates, w - 0.03, color=COLOR[c], label=LABEL[c], zorder=2)
    ax.errorbar(pos, rates, yerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=0.7, capsize=1.5, zorder=3)
ax.set_xticks(x, list(MODELS.values()), fontsize=8)
ax.set_ylabel("Turn-3 capitulation (% of 18 dialogues)")
ax.set_ylim(0, 100)
ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.13))
fig.tight_layout()
out.append(FIG / "fig2_model_comparison.png")
fig.savefig(out[-1])
plt.close(fig)

# ---- Fig 3: firmness vs constructive alternative
fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=300)
for c in CONDS:
    xs = [R[f"{m}|{c}"]["firmness"] for m in MODELS]
    ys = [R[f"{m}|{c}"]["alternative"] for m in MODELS]
    ax.scatter(xs, ys, s=46, color=COLOR[c], edgecolor=SURF, linewidth=1.5, label=LABEL[c], zorder=3)
ax.set_xlabel("Mean judge-rated firmness (1–5)")
ax.set_ylabel("Mean constructive alternative (1–5)")
ax.set_xlim(1, 5.1)
ax.set_ylim(1, 5.1)
ax.grid(color=GRID, lw=0.6, zorder=0)
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_title("One point per model × condition", color=INK, fontsize=9.5, loc="left")
fig.tight_layout()
out.append(FIG / "fig3_pareto_frontier.png")
fig.savefig(out[-1])
plt.close(fig)

for p in out:
    shutil.copy(p, ROOT / "paper" / "figures" / p.name)
    print("wrote", p)
