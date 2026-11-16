import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Set up figure
fig, ax = plt.subplots(figsize=(16, 7), dpi=300)
fig.patch.set_facecolor('#0A0F1D')
ax.set_facecolor('#0A0F1D')
ax.set_xlim(0, 16)
ax.set_ylim(0, 7)
ax.axis('off')

# Gradient/Accent Top Bar
ax.plot([0, 16], [6.95, 6.95], color='#14B8A6', lw=6)

# Title & Eyebrow
ax.text(0.8, 6.35, "APART RESEARCH · AI X EPISTEMICS RESEARCH SPRINT 2026", 
        fontsize=11, fontweight='bold', color='#2DD4BF', fontfamily='sans-serif')
ax.text(0.8, 5.75, "The Accuracy-Approval Dilemma (AAB)", 
        fontsize=26, fontweight='bold', color='#FFFFFF', fontfamily='sans-serif')
ax.text(0.8, 5.25, "Multi-Turn Epistemic Capitulation & Guardian Scaffolding Across 7 Global Model Lineages", 
        fontsize=13, color='#94A3B8', fontfamily='sans-serif')

# Four Big Stat Panels across the middle
stat_data = [
    ("35.7%", "Baseline Capitulation", "Collapses under pressure", "#F43F5E"),
    ("0.0%", "Scaffolded Capitulation", "100% elimination of surrender", "#10B981"),
    ("+26.2%", "Firmness Increase", "3.81 ± 1.32 → 4.81 ± 0.29", "#14B8A6"),
    ("4.76 / 5.0", "Constructive De-escalation", "+18.7% user rapport gain", "#38BDF8")
]

card_w, card_h = 3.3, 1.8
start_x, start_y = 0.8, 3.1
spacing = 0.35

for i, (val, title, sub, color) in enumerate(stat_data):
    cx = start_x + i * (card_w + spacing)
    # Background card
    rect = patches.FancyBboxPatch((cx, start_y), card_w, card_h,
                                  boxstyle="round,pad=0.08,rounding_size=0.15",
                                  facecolor='#0F172A', edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    # Text inside card
    ax.text(cx + 0.2, start_y + 1.25, val, fontsize=28, fontweight='bold', color=color, fontfamily='monospace')
    ax.text(cx + 0.2, start_y + 0.75, title, fontsize=11, fontweight='bold', color='#FFFFFF', fontfamily='sans-serif')
    ax.text(cx + 0.2, start_y + 0.35, sub, fontsize=9.5, color='#94A3B8', fontfamily='sans-serif')

# Bottom Flow Diagram: The 3-Turn Interaction Pipeline
p_y = 1.0
p_h = 1.6
p_w = 4.3

# Stage 1: Turn 1
r1 = patches.FancyBboxPatch((0.8, p_y), p_w, p_h, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor='#1E293B', edgecolor='#334155', linewidth=1)
ax.add_patch(r1)
ax.text(1.0, p_y + 1.15, "TURN 1: Initial Dubious Plan", fontsize=11, fontweight='bold', color='#2DD4BF')
ax.text(1.0, p_y + 0.7, "User requests high-risk execution", fontsize=9.5, color='#CBD5E1')
ax.text(1.0, p_y + 0.35, "Baseline detects hazard with caution (EF ~4.2)", fontsize=9, color='#94A3B8')

# Arrow 1 -> 2
ax.annotate("", xy=(5.4, p_y + 0.8), xytext=(5.15, p_y + 0.8),
            arrowprops=dict(arrowstyle="->", color='#2DD4BF', lw=2.5))

# Stage 2: Turn 2
r2 = patches.FancyBboxPatch((5.5, p_y), p_w, p_h, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor='#1E293B', edgecolor='#F59E0B', linewidth=1.2)
ax.add_patch(r2)
ax.text(5.7, p_y + 1.15, "TURN 2: Emotional Pushback", fontsize=11, fontweight='bold', color='#FBBF24')
ax.text(5.7, p_y + 0.7, "User pushes back with distress/ambition", fontsize=9.5, color='#CBD5E1')
ax.text(5.7, p_y + 0.35, "Baseline begins softening risks (decay ~1.3)", fontsize=9, color='#F59E0B')

# Arrow 2 -> 3
ax.annotate("", xy=(10.1, p_y + 0.8), xytext=(9.85, p_y + 0.8),
            arrowprops=dict(arrowstyle="->", color='#F43F5E', lw=2.5))

# Stage 3: Turn 3
r3 = patches.FancyBboxPatch((10.2, p_y), 5.0, p_h, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor='#1E293B', edgecolor='#F43F5E', linewidth=1.2)
ax.add_patch(r3)
ax.text(10.4, p_y + 1.15, "TURN 3: Relational Ultimatum", fontsize=11, fontweight='bold', color='#F43F5E')
ax.text(10.4, p_y + 0.7, "Baseline: 35.7% - 66.7% Capitulate ('Go ahead and sign!')", fontsize=9.5, fontweight='bold', color='#F43F5E')
ax.text(10.4, p_y + 0.3, "Epistemic Guardian: 0.0% Capitulation (Holds Firm + Bridges)", fontsize=9.5, fontweight='bold', color='#10B981')

plt.tight_layout()
out_path = Path(r"D:\ins respinse\AI x Epistemics Research Sprint\06_Our_Project\accuracy_approval_dilemma\figures\hero_banner.png")
plt.savefig(str(out_path), bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Generated hero banner at: {out_path} ({out_path.stat().st_size} bytes)")
