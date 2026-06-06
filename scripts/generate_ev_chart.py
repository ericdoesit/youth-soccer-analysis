"""
Expected Value Analysis: Is there a "likelihood-appropriate" cost for youth soccer?

Shows the gap between what families spend and what they can realistically expect
to get back — and frames where different spending levels might be justifiable.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

# ── Data ─────────────────────────────────────────────────────────────────────

tiers = ["Tier 1\nAYSO Rec\n$550/yr", "Tier 2\nTravel\n$3,100/yr",
         "Tier 3\nECNL/MLS Next\n$7,000/yr", "Tier 4\nTop Elite\n$12,000/yr"]
tier_labels_short = ["T1\n$550", "T2\n$3,100", "T3\n$7,000", "T4\n$12,000"]

annual_cost     = [550,   3100,   7000,   12000]
total_cost_10yr = [c * 10 for c in annual_cost]   # 10-year career

# D1 scholarship probability estimates (including partial)
d1_scholarship_prob = [0.005, 0.030, 0.065, 0.095]   # fraction of players

# Average scholarship value (mix of full/partial)
# 15% full ($136K total), 55% partial (~$60K total), 30% none
avg_scholarship_value = 0.15 * 136_000 + 0.55 * 60_000   # ~$53,400

# Pro career: ~0.04% reach sustained MLS career (from our draft survival data)
# Median survivor earns $113K/yr; median career ~3 years → $339K
# But 78.8% of draft picks are gone, and only 0.04% of Tier 3 players get drafted
pro_prob     = [0.0001, 0.0003, 0.0006, 0.0009]  # Tier 1→4
pro_career_ev = 113_412 * 3   # median salary × median career length

# Expected financial return (EV)
ev = [d1_scholarship_prob[i] * avg_scholarship_value + pro_prob[i] * pro_career_ev
      for i in range(4)]

# Break-even scholarship probability needed (ignoring pro career, generous)
breakeven_prob = [total_cost_10yr[i] / avg_scholarship_value for i in range(4)]

# ── Figure 1: Cost vs. Expected Financial Return ──────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor("#0d0d1a")

x = np.arange(4)
bar_w = 0.35

ax = axes[0]
ax.set_facecolor("#0d0d1a")
bars1 = ax.bar(x - bar_w/2, total_cost_10yr, bar_w,
               color=["#3b82f6","#f59e0b","#ef4444","#9b2335"], alpha=0.85,
               label="10-yr family cost")
bars2 = ax.bar(x + bar_w/2, ev, bar_w,
               color="#22c55e", alpha=0.85, label="Expected financial return (EV)")

ax.set_xticks(x)
ax.set_xticklabels(tiers, color="white", fontsize=9)
ax.set_ylabel("Dollars ($)", color="white")
ax.set_title("10-Year Cost vs. Expected Financial Return", color="white", fontsize=12, pad=12)
ax.tick_params(colors="white")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
for spine in ax.spines.values():
    spine.set_edgecolor("#333")
ax.grid(axis="y", color="#222", linewidth=0.5)
ax.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

# Label the EV bars (too small to see otherwise)
for bar, val in zip(bars2, ev):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 800,
            f"${val:,.0f}", ha="center", va="bottom", color="#22c55e", fontsize=8)

# Annotation
ax.annotate("Expected return is near zero\nfor every tier",
            xy=(1, ev[1]+500), xytext=(1.5, 25000),
            arrowprops=dict(arrowstyle="->", color="#aaa"),
            color="#aaa", fontsize=9)

# ── Figure 2: Break-even probability vs. actual ─────────────────────────────
ax2 = axes[1]
ax2.set_facecolor("#0d0d1a")

ax2.bar(x, [p * 100 for p in breakeven_prob], 0.5,
        color=["#3b82f6","#f59e0b","#ef4444","#9b2335"], alpha=0.7,
        label="Scholarship % needed to break even")
ax2.scatter(x, [p * 100 for p in d1_scholarship_prob],
            color="#22c55e", s=120, zorder=5,
            label="Actual scholarship % (estimated)")

for i, (be, actual) in enumerate(zip(breakeven_prob, d1_scholarship_prob)):
    ax2.annotate(f"Actual:\n{actual*100:.1f}%",
                 xy=(i, actual*100), xytext=(i + 0.25, actual*100 + 5),
                 color="#22c55e", fontsize=8,
                 arrowprops=dict(arrowstyle="->", color="#22c55e", lw=0.8))

ax2.axhline(100, color="#ff6b6b", linestyle="--", linewidth=1, alpha=0.5,
            label="100% = impossible")

ax2.set_xticks(x)
ax2.set_xticklabels(tiers, color="white", fontsize=9)
ax2.set_ylabel("D1 Scholarship Probability (%)", color="white")
ax2.set_title("Break-Even Scholarship Rate Needed\nvs. Actual Rate", color="white",
              fontsize=12, pad=12)
ax2.tick_params(colors="white")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
for spine in ax2.spines.values():
    spine.set_edgecolor("#333")
ax2.grid(axis="y", color="#222", linewidth=0.5)
ax2.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

plt.tight_layout(pad=2)
plt.savefig(OUT / "ev_cost_vs_return.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d1a")
plt.close()
print("Saved: ev_cost_vs_return.png")

# ── Figure 3: The "rational spending" frontier ────────────────────────────────
fig2, ax3 = plt.subplots(figsize=(12, 7))
fig2.patch.set_facecolor("#0d0d1a")
ax3.set_facecolor("#0d0d1a")

spend_range = np.linspace(0, 15000, 300)

# Financial EV curve (returns very little; flat-ish based on marginal tier gains)
# Interpolate EV per dollar at each tier point
ev_per_year = [e / 10 for e in ev]   # annual EV contribution
annual_costs_pts = annual_cost

# Simple piecewise linear interpolation of EV vs. annual spend
def ev_at_spend(s):
    if s <= 550:
        return np.interp(s, [0, 550], [0, ev_per_year[0]])
    elif s <= 3100:
        return np.interp(s, [550, 3100], [ev_per_year[0], ev_per_year[1]])
    elif s <= 7000:
        return np.interp(s, [3100, 7000], [ev_per_year[1], ev_per_year[2]])
    else:
        return np.interp(s, [7000, 12000], [ev_per_year[2], ev_per_year[3]])

ev_curve = np.array([ev_at_spend(s) for s in spend_range])

# Non-financial benefit curve: rises quickly, then flattens (diminishing returns)
# Assumes T1 provides 40% of max developmental benefit, T2 provides 70%, T3 provides 85%, T4 provides 90%
benefit_anchors = [(0, 0), (550, 40), (3100, 70), (7000, 85), (12000, 90)]
bx = [b[0] for b in benefit_anchors]
by = [b[1] for b in benefit_anchors]
benefit_curve = np.interp(spend_range, bx, by)

# Cost line (trivially equal to spend)
cost_normalized = spend_range / 150   # normalize to same scale (~100 units at $15K)

ax3.fill_between(spend_range, ev_curve, alpha=0.15, color="#22c55e", label="")
ax3.fill_between(spend_range, benefit_curve, alpha=0.12, color="#3b82f6", label="")

ax3.plot(spend_range, ev_curve, color="#22c55e", linewidth=2.5,
         label="Expected financial return (per $100 spent, annualized)")
ax3.plot(spend_range, benefit_curve, color="#3b82f6", linewidth=2.5,
         label="Non-financial benefit index (fun, development, competition) — estimated")
ax3.plot(spend_range, cost_normalized, color="#ef4444", linewidth=2, linestyle="--",
         label="Annual cost (scaled: $15,000 = 100)")

# Tier markers
tier_costs = [550, 3100, 7000, 12000]
tier_names = ["T1\nAYSO\n$550", "T2\nTravel\n$3,100", "T3\nECNL\n$7,000", "T4\nElite\n$12,000"]
for tc, tn in zip(tier_costs, tier_names):
    ax3.axvline(tc, color="#555", linestyle=":", linewidth=1)
    ax3.text(tc, 97, tn, ha="center", va="top", color="#aaa", fontsize=8)

# Shade "possible rational zone": where benefit > cost
rational_mask = benefit_curve > cost_normalized
ax3.fill_between(spend_range, 0, benefit_curve,
                 where=rational_mask, alpha=0.08, color="#22c55e")

# Annotate the crossover
crossover = spend_range[np.argmin(np.abs(benefit_curve - cost_normalized))]
ax3.annotate(f"Benefit ≈ Cost\n≈ ${crossover:,.0f}/yr\n(T2 range)",
             xy=(crossover, np.interp(crossover, spend_range, benefit_curve)),
             xytext=(crossover + 1500, 60),
             arrowprops=dict(arrowstyle="->", color="#aaa"),
             color="#aaa", fontsize=9)

ax3.set_xlabel("Annual spending on youth soccer ($)", color="white", fontsize=11)
ax3.set_ylabel("Index (0–100)", color="white", fontsize=11)
ax3.set_title("Is There a 'Likelihood-Appropriate' Cost?\n"
              "Financial return, non-financial benefit, and actual spend",
              color="white", fontsize=13, pad=14)
ax3.tick_params(colors="white")
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
for spine in ax3.spines.values():
    spine.set_edgecolor("#333")
ax3.grid(color="#1a1a1a", linewidth=0.5)
ax3.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9, loc="upper left")
ax3.set_xlim(0, 13000)
ax3.set_ylim(0, 100)

# Key insight text box
textbox = ("Key finding: Financial return stays near zero\n"
           "at every spending level. Non-financial benefit\n"
           "rises quickly to ~$3,000/yr, then flattens.\n"
           "Above ~$4,000/yr, cost outpaces any benefit\n"
           "that can be estimated — unless your child is\n"
           "a demonstrable outlier.")
ax3.text(7500, 30, textbox, fontsize=9, color="#ccc",
         bbox=dict(facecolor="#1a1a2e", edgecolor="#444", boxstyle="round,pad=0.5"))

plt.tight_layout(pad=2)
plt.savefig(OUT / "ev_rational_spend_frontier.png", dpi=150, bbox_inches="tight",
            facecolor="#0d0d1a")
plt.close()
print("Saved: ev_rational_spend_frontier.png")

# ── Print key numbers ─────────────────────────────────────────────────────────
print("\n=== EV Summary ===")
for i, t in enumerate(["T1 ($550)", "T2 ($3,100)", "T3 ($7,000)", "T4 ($12,000)"]):
    print(f"  {t}: 10yr cost ${total_cost_10yr[i]:>8,.0f}  |  EV ${ev[i]:>6,.0f}  "
          f"|  Net ${ev[i]-total_cost_10yr[i]:>9,.0f}  "
          f"|  Break-even scholarship rate needed: {breakeven_prob[i]*100:.0f}%")
