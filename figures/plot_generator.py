import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_FILE = PROJECT_ROOT / "experiments" / "metrics_summary.json"
FIGS_DIR = PROJECT_ROOT / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# Set clean styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

MODEL_DISPLAY_NAMES = {
    "openai/gpt-4o-mini": "GPT-4o-mini",
    "google/gemini-2.5-flash": "Gemini-2.5-Flash",
    "deepseek/deepseek-chat": "DeepSeek-V3",
    "z-ai/glm-5.3-flash": "GLM-5-Flash",
    "qwen/qwen-2.5-72b-instruct": "Qwen-2.5-72B",
    "mistralai/mistral-small-24b-instruct-2501": "Mistral-Small-3",
    "meta-llama/llama-3.1-8b-instruct": "Llama-3.1-8B"
}

PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
]

def generate_plots():
    if not SUMMARY_FILE.exists():
        print(f"Summary file {SUMMARY_FILE} not found yet. Cannot generate plots.")
        return

    summary = json.loads(SUMMARY_FILE.read_text(encoding="utf-8"))
    models = list(summary.keys())
    model_labels = [MODEL_DISPLAY_NAMES.get(m, m.split("/")[-1]) for m in models]

    # ==========================================
    # FIGURE 1: Turn-by-Turn Firmness Trajectories
    # ==========================================
    fig, (ax_base, ax_guard) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300, sharey=True)
    turns = [1, 2, 3]

    for idx, m in enumerate(models):
        lbl = MODEL_DISPLAY_NAMES.get(m, m.split("/")[-1])
        c = PALETTE[idx % len(PALETTE)]
        
        base_traj = summary[m]["Baseline"]["turn_firmness_trajectory"]
        guard_traj = summary[m]["Epistemic_Guardian"]["turn_firmness_trajectory"]

        ax_base.plot(turns, base_traj, marker='o', linestyle='--', color=c, label=lbl, alpha=0.85, linewidth=2)
        ax_guard.plot(turns, guard_traj, marker='s', linestyle='-', color=c, label=lbl, linewidth=2.2)

    ax_base.set_title("Baseline Assistants: Severe Capitulation", pad=12, fontweight='bold', color='#c0392b')
    ax_base.set_xlabel("Turn (1: Flawed Plan → 2: Pushback → 3: Ultimatum)")
    ax_base.set_ylabel("Epistemic Firmness (1=Capitulated, 5=Firm)")
    ax_base.set_xticks(turns)
    ax_base.set_xticklabels(["Turn 1: Initial", "Turn 2: Pushback", "Turn 3: Ultimatum"])
    ax_base.set_ylim(1.0, 5.2)
    ax_base.axhspan(1.0, 2.5, color='#ffcccc', alpha=0.3, label="Capitulation Zone")

    ax_guard.set_title("Epistemic Guardian Scaffold: Sustained Firmness", pad=12, fontweight='bold', color='#27ae60')
    ax_guard.set_xlabel("Turn (1: Flawed Plan → 2: Pushback → 3: Ultimatum)")
    ax_guard.set_xticks(turns)
    ax_guard.set_xticklabels(["Turn 1: Initial", "Turn 2: Pushback", "Turn 3: Ultimatum"])
    ax_guard.axhspan(1.0, 2.5, color='#ffcccc', alpha=0.3)
    ax_guard.legend(bbox_to_anchor=(1.04, 1), loc="upper left", frameon=True, fontsize=9)

    plt.tight_layout()
    f1_path = FIGS_DIR / "fig1_capitulation_curves.png"
    plt.savefig(f1_path, dpi=300)
    plt.close()
    print(f"Saved {f1_path.name}")

    # ==========================================
    # FIGURE 2: Multi-Model Capitulation & Firmness Comparison
    # ==========================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    x = np.arange(len(models))
    width = 0.38

    base_cap = [summary[m]["Baseline"]["capitulation_rate"] for m in models]
    guard_cap = [summary[m]["Epistemic_Guardian"]["capitulation_rate"] for m in models]

    rects1 = ax1.bar(x - width/2, base_cap, width, label='Baseline Assistant', color='#e74c3c', alpha=0.9)
    rects2 = ax1.bar(x + width/2, guard_cap, width, label='Epistemic Guardian', color='#2ecc71', alpha=0.9)

    ax1.set_title("Capitulation Rate Under Ultimatum (%)", fontweight='bold', pad=10)
    ax1.set_ylabel("Capitulation Rate (%) [Lower is Better]")
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_labels, rotation=25, ha='right')
    ax1.set_ylim(0, 105)
    ax1.legend(frameon=True, loc="upper right")
    for r in rects1: 
        ax1.annotate(f"{r.get_height():.0f}%", (r.get_x() + r.get_width()/2, r.get_height() + 2), ha='center', fontsize=8.5, fontweight='bold')
    for r in rects2: 
        ax1.annotate(f"{r.get_height():.0f}%", (r.get_x() + r.get_width()/2, r.get_height() + 2), ha='center', fontsize=8.5, fontweight='bold')

    base_firm = [summary[m]["Baseline"]["avg_firmness"] for m in models]
    guard_firm = [summary[m]["Epistemic_Guardian"]["avg_firmness"] for m in models]

    r1 = ax2.bar(x - width/2, base_firm, width, label='Baseline Assistant', color='#3498db', alpha=0.9)
    r2 = ax2.bar(x + width/2, guard_firm, width, label='Epistemic Guardian', color='#1abc9c', alpha=0.9)

    ax2.set_title("Average Epistemic Firmness (1-5 Scale)", fontweight='bold', pad=10)
    ax2.set_ylabel("Epistemic Firmness [Higher is Better]")
    ax2.set_xticks(x)
    ax2.set_xticklabels(model_labels, rotation=25, ha='right')
    ax2.set_ylim(1.0, 5.2)
    ax2.legend(frameon=True, loc="upper left")
    for r in r1: 
        ax2.annotate(f"{r.get_height():.2f}", (r.get_x() + r.get_width()/2, r.get_height() + 0.1), ha='center', fontsize=8.5)
    for r in r2: 
        ax2.annotate(f"{r.get_height():.2f}", (r.get_x() + r.get_width()/2, r.get_height() + 0.1), ha='center', fontsize=8.5)

    plt.tight_layout()
    f2_path = FIGS_DIR / "fig2_model_comparison.png"
    plt.savefig(f2_path, dpi=300)
    plt.close()
    print(f"Saved {f2_path.name}")

    # ==========================================
    # FIGURE 3: The Pareto Frontier of Truth vs Constructive De-escalation
    # ==========================================
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)

    for idx, m in enumerate(models):
        lbl = MODEL_DISPLAY_NAMES.get(m, m.split("/")[-1])
        c = PALETTE[idx % len(PALETTE)]
        
        b_firm = summary[m]["Baseline"]["avg_firmness"]
        b_deesc = summary[m]["Baseline"]["avg_deescalation"]
        g_firm = summary[m]["Epistemic_Guardian"]["avg_firmness"]
        g_deesc = summary[m]["Epistemic_Guardian"]["avg_deescalation"]

        # Baseline point
        ax.scatter(b_deesc, b_firm, s=140, color='#e74c3c', marker='o', alpha=0.8, edgecolors='black', linewidth=1)
        ax.annotate(f"{lbl} (Base)", (b_deesc + 0.04, b_firm - 0.08), fontsize=8.5, color='#7f1d1d')

        # Guardian point
        ax.scatter(g_deesc, g_firm, s=180, color='#27ae60', marker='^', alpha=0.9, edgecolors='black', linewidth=1)
        ax.annotate(f"{lbl} (Guardian)", (g_deesc + 0.04, g_firm + 0.06), fontsize=8.5, fontweight='bold', color='#14532d')

        # Vector showing improvement
        ax.annotate('', xy=(g_deesc, g_firm), xytext=(b_deesc, b_firm),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.8, ls="-", alpha=0.7))

    # Quadrant annotations
    ax.axvline(3.0, color='gray', linestyle=':', alpha=0.5)
    ax.axhline(3.0, color='gray', linestyle=':', alpha=0.5)
    ax.text(1.2, 4.8, "Rigid Refusal Zone\n(High Firmness, Low Empathy)", color='#666', fontsize=8, style='italic')
    ax.text(1.2, 1.4, "Catastrophic Sycophancy\n(Low Firmness, Low De-escalation)", color='#c0392b', fontsize=8, style='italic')
    ax.text(3.4, 4.8, "Pareto Ideal: Constructive Truth\n(High Firmness, High De-escalation)", color='#27ae60', fontsize=8.5, fontweight='bold')
    ax.text(3.4, 1.4, "Compliant Appeasement\n(Low Firmness, Soft Delivery)", color='#d35400', fontsize=8, style='italic')

    ax.set_title("The Pareto Frontier: Epistemic Firmness vs. Constructive De-escalation", fontweight='bold', pad=12)
    ax.set_xlabel("Constructive De-escalation (1-5 Scale) [Higher is Better]")
    ax.set_ylabel("Epistemic Firmness (1-5 Scale) [Higher is Better]")
    ax.set_xlim(1.0, 5.0)
    ax.set_ylim(1.0, 5.2)

    # Custom legend
    p1 = ax.scatter([], [], s=100, color='#e74c3c', marker='o', label='Baseline Assistant')
    p2 = ax.scatter([], [], s=120, color='#27ae60', marker='^', label='Epistemic Guardian Scaffold')
    ax.legend(handles=[p1, p2], loc='lower right', frameon=True, fontsize=10)

    plt.tight_layout()
    f3_path = FIGS_DIR / "fig3_pareto_frontier.png"
    plt.savefig(f3_path, dpi=300)
    plt.close()
    print(f"Saved {f3_path.name}")

if __name__ == "__main__":
    generate_plots()
