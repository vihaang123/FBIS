"""
analysis.py — Statistical analysis engine for FBIS.
All functions operate on a cleaned DataFrame from prepare_df().
Charts use a unified PLOTLY_LAYOUT for the luxury dark fintech theme.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# ── Design Tokens (mirror CSS vars) ───────────────────────────────────────
COLORS = {
    "cyan":   "#00e5ff",
    "violet": "#7c6aff",
    "green":  "#00d084",
    "amber":  "#ffb547",
    "red":    "#ff4f6a",
    "pink":   "#ff6eb4",
    "teal":   "#00c9b1",
}
PALETTE = list(COLORS.values())

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(19,25,41,0.7)",
    font=dict(family="Epilogue, sans-serif", color="#a8b4cc", size=12),
    title_font=dict(family="Syne, sans-serif", size=15, color="#f0f4ff"),
    legend=dict(
        bgcolor="rgba(13,18,32,0.85)",
        bordercolor="rgba(255,255,255,0.07)",
        borderwidth=1,
        font=dict(size=11, color="#a8b4cc"),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.07)",
        tickfont=dict(color="#5a6680", size=11),
        title_font=dict(color="#a8b4cc", size=12),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.07)",
        tickfont=dict(color="#5a6680", size=11),
        title_font=dict(color="#a8b4cc", size=12),
    ),
    margin=dict(t=52, b=44, l=44, r=24),
    hoverlabel=dict(
        bgcolor="#1b2236",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(family="Epilogue, sans-serif", color="#f0f4ff", size=12),
    ),
)


# ── Data Preparation ───────────────────────────────────────────────────────

def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    from utils import (savings_pct, expense_ratio, assign_age_group,
                       classify_behavior, assign_investment_profile,
                       financial_score, project_wealth, PROFILE_RATES)

    d = df.copy()
    for col in ["income", "expenses", "savings", "daily_spending",
                "weekly_spending", "investment_amount", "stress", "age"]:
        d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0)

    d["savings_pct"]           = d.apply(lambda r: savings_pct(r["income"], r["savings"]), axis=1)
    d["expense_ratio"]         = d.apply(lambda r: expense_ratio(r["income"], r["expenses"]), axis=1)
    d["age_group"]             = d["age"].apply(assign_age_group)
    d["behavior"]              = d.apply(classify_behavior, axis=1)
    d["inv_profile"]           = d.apply(assign_investment_profile, axis=1)
    d["fin_score"]             = d.apply(financial_score, axis=1)
    d["wealth_10y_conservative"] = d["savings"].apply(lambda s: project_wealth(s, 10, 0.04))
    d["wealth_10y_moderate"]     = d["savings"].apply(lambda s: project_wealth(s, 10, 0.08))
    d["wealth_10y_aggressive"]   = d["savings"].apply(lambda s: project_wealth(s, 10, 0.12))
    return d


# ── Overview Stats ─────────────────────────────────────────────────────────

def overview_stats(df: pd.DataFrame) -> dict:
    total = len(df)
    if total == 0:
        return {}
    investors = (df["investment"].str.lower() == "yes").sum()
    trackers  = (df["tracking"].str.lower() == "yes").sum()
    return {
        "total_users":     total,
        "avg_income":      df["income"].mean(),
        "avg_savings_pct": df["savings_pct"].mean(),
        "pct_investors":   investors / total * 100,
        "pct_trackers":    trackers  / total * 100,
        "avg_stress":      df["stress"].mean(),
        "avg_fin_score":   df["fin_score"].mean(),
    }


# ── ANOVA ──────────────────────────────────────────────────────────────────

def run_anova_tests(df: pd.DataFrame) -> list[dict]:
    tests = [
        ("Spending Habit → Savings %",         "spending_habit",  "savings_pct",         "spending habit",        "savings rate"),
        ("Expense Tracking → Savings %",        "tracking",        "savings_pct",         "expense tracking",      "savings rate"),
        ("Investment Status → 10-Year Wealth",  "investment",      "wealth_10y_moderate", "investment behaviour",  "projected 10-year wealth"),
        ("User Type → Savings %",               "user_type",       "savings_pct",         "user type",             "savings rate"),
    ]
    results = []
    for test_name, grp_col, met_col, readable, metric_r in tests:
        groups = [g[met_col].dropna().values for _, g in df.groupby(grp_col) if len(g) >= 2]
        if len(groups) < 2:
            continue
        f_stat, p_value = stats.f_oneway(*groups)
        sig = p_value < 0.05
        if sig:
            interpretation = (
                f"{readable.capitalize()} significantly affects {metric_r} "
                f"(F={f_stat:.2f}, p={p_value:.4f}). The difference between groups is statistically meaningful."
            )
        else:
            interpretation = (
                f"{readable.capitalize()} does not show a statistically significant effect on "
                f"{metric_r} (F={f_stat:.2f}, p={p_value:.4f})."
            )
        results.append({
            "test_name":     test_name,
            "f_stat":        round(f_stat, 4),
            "p_value":       round(p_value, 6),
            "significant":   sig,
            "interpretation": interpretation,
        })
    return results


# ── MANOVA ─────────────────────────────────────────────────────────────────

def run_manova(df: pd.DataFrame, group_col: str = "spending_habit") -> dict:
    try:
        from statsmodels.multivariate.manova import MANOVA
        dep_vars = ["savings_pct", "stress", "wealth_10y_moderate"]
        data = df[[group_col] + dep_vars].dropna()
        data = data[data[group_col].notna() & (data[group_col] != "")]

        if len(data) < 10 or data[group_col].nunique() < 2:
            return {"success": False, "message": "Need ≥10 rows and ≥2 groups for MANOVA."}

        mv   = MANOVA.from_formula(f"savings_pct + stress + wealth_10y_moderate ~ C({group_col})", data=data)
        res  = mv.mv_test()
        wilks = res.results[f"C({group_col})"]["stat"]
        p_val = float(wilks.loc["Wilks' lambda", "Pr > F"])
        stat  = float(wilks.loc["Wilks' lambda", "Value"])
        sig   = p_val < 0.05

        explanation = (
            f"MANOVA (Wilks' λ={stat:.4f}, p={p_val:.4f}): "
            + (
                f"{'✅' if sig else '⚪'} {group_col.replace('_',' ').capitalize()} "
                + ("jointly influences savings, stress, and projected wealth significantly." if sig
                   else "does not jointly influence the outcome variables significantly.")
            )
        )
        return {
            "success":     True,
            "stat":        round(stat, 6),
            "p_value":     round(p_val, 6),
            "significant": sig,
            "explanation": explanation,
            "group_means": data.groupby(group_col)[dep_vars].mean().round(2),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ── Charts ─────────────────────────────────────────────────────────────────

def _apply_layout(fig, title="", height=360, **kwargs):
    """Apply shared layout and optional overrides."""
    layout = {**PLOTLY_LAYOUT, "title": title, "height": height, **kwargs}
    fig.update_layout(**layout)
    return fig


def chart_age_group_metrics(df: pd.DataFrame) -> go.Figure:
    age_order = ["18–22", "23–30", "31–40", "40+"]
    grp = df.groupby("age_group").agg(
        savings_pct=("savings_pct", "mean"),
        stress=("stress", "mean"),
        investment_rate=("investment", lambda x: (x.str.lower() == "yes").mean() * 100),
    ).reindex(age_order).reset_index()

    fig = go.Figure()
    for name, col, color in [
        ("Avg Savings %", "savings_pct",      COLORS["cyan"]),
        ("Investor %",    "investment_rate",   COLORS["violet"]),
        ("Avg Stress",    "stress",            COLORS["amber"]),
    ]:
        fig.add_trace(go.Bar(
            name=name, x=grp["age_group"], y=grp[col],
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            text=grp[col].round(1), textposition="auto",
            textfont=dict(color="#f0f4ff", size=11),
        ))
    return _apply_layout(fig, "Age Group Analysis", barmode="group")


def chart_anova_pvalues(results: list[dict]) -> go.Figure:
    names  = [r["test_name"] for r in results]
    pvals  = [r["p_value"]   for r in results]
    colors = [C["green"] if r["significant"] else C["red"] for r in results]

    fig = go.Figure(go.Bar(
        x=pvals, y=names, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"p={p:.4f}" for p in pvals], textposition="auto",
        textfont=dict(color="#f0f4ff", size=11),
    ))
    fig.add_vline(x=0.05, line_dash="dot", line_color=C["amber"], line_width=1.5,
                  annotation_text="α = 0.05", annotation_font_color=C["amber"],
                  annotation_font_size=11)
    return _apply_layout(fig, "ANOVA p-values (green = significant, red = not significant)",
                         height=max(280, len(results) * 62), xaxis_title="p-value")


def chart_wealth_projection(monthly_savings: float, label: str = "User", years: int = 10) -> go.Figure:
    from utils import project_wealth
    yr = list(range(0, years + 1))
    scenarios = [
        ("Conservative (4%)", 0.04, COLORS["teal"]),
        ("Moderate (8%)",     0.08, COLORS["cyan"]),
        ("Aggressive (12%)",  0.12, COLORS["violet"]),
    ]
    fig = go.Figure()
    for name, rate, color in scenarios:
        vals = [project_wealth(monthly_savings, y, rate) for y in yr]
        fig.add_trace(go.Scatter(
            x=yr, y=vals, mode="lines+markers", name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color, line=dict(width=1, color="rgba(0,0,0,0.4)")),
            fill="tozeroy",
            # ✅ FIXED LINE (only change)
            fillcolor="rgba(0,201,177,0.03)" if color == COLORS["teal"] else \
                      "rgba(0,229,255,0.03)" if color == COLORS["cyan"] else \
                      "rgba(124,106,255,0.03)",
            hovertemplate=f"{name}<br>Year %{{x}}: ₹%{{y:,.0f}}<extra></extra>",
        ))
    # Fill workaround for hex colors
    fig2 = go.Figure()
    fill_colors = ["rgba(0,201,177,0.04)", "rgba(0,229,255,0.05)", "rgba(124,106,255,0.05)"]
    for (name, rate, color), fc in zip(scenarios, fill_colors):
        vals = [project_wealth(monthly_savings, y, rate) for y in yr]
        fig2.add_trace(go.Scatter(
            x=yr, y=vals, mode="lines+markers", name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            fill="tozeroy", fillcolor=fc,
            hovertemplate=f"{name}<br>Year %{{x}}: ₹%{{y:,.0f}}<extra></extra>",
        ))
    return _apply_layout(fig2, f"{years}-Year Wealth Projection — {label}",
                         height=380, xaxis_title="Years", yaxis_title="Projected Wealth (₹)")

def chart_behavior_segments(df: pd.DataFrame) -> go.Figure:
    counts = df["behavior"].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    seg_colors = {"Wealth Builder": COLORS["green"], "Saver": COLORS["cyan"],
                  "Balanced": COLORS["amber"], "Overspender": COLORS["red"]}
    fig = go.Figure(go.Pie(
        labels=counts["segment"], values=counts["count"], hole=0.58,
        marker=dict(
            colors=[seg_colors.get(s, COLORS["violet"]) for s in counts["segment"]],
            line=dict(color="#0d1220", width=3),
        ),
        textinfo="label+percent",
        textfont=dict(size=11, color="#f0f4ff"),
        hovertemplate="%{label}: %{value} users (%{percent})<extra></extra>",
    ))
    return _apply_layout(fig, "Behaviour Segments", height=340)


def chart_investment_profiles(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("inv_profile").agg(
        count=("id", "count"),
        avg_savings=("savings_pct", "mean"),
        avg_wealth=("wealth_10y_moderate", "mean"),
    ).reset_index()

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Users by Profile", "Avg 10Y Wealth (₹)"),
                        horizontal_spacing=0.12)
    pcols = {"Conservative": COLORS["teal"], "Moderate": COLORS["cyan"], "Aggressive": COLORS["violet"]}
    bc = [pcols.get(p, COLORS["amber"]) for p in grp["inv_profile"]]

    fig.add_trace(go.Bar(x=grp["inv_profile"], y=grp["count"], marker_color=bc, name="Users",
                         text=grp["count"], textposition="auto",
                         textfont=dict(color="#f0f4ff", size=11),
                         marker_line_width=0), row=1, col=1)
    fig.add_trace(go.Bar(x=grp["inv_profile"], y=grp["avg_wealth"], marker_color=bc, name="Wealth",
                         text=grp["avg_wealth"].apply(lambda v: f"₹{v:,.0f}"),
                         textposition="auto",
                         textfont=dict(color="#f0f4ff", size=11),
                         marker_line_width=0), row=1, col=2)

    fig.update_layout(**PLOTLY_LAYOUT, title="Investment Profile Overview",
                      height=330, showlegend=False)
    for ax in ["xaxis", "yaxis", "xaxis2", "yaxis2"]:
        fig.update_layout(**{ax: dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(color="#5a6680", size=11),
        )})
    return fig


def chart_expense_categories(df: pd.DataFrame) -> go.Figure:
    from collections import Counter
    all_cats = [c for cats in df["expense_categories"] if isinstance(cats, list) for c in cats]
    if not all_cats:
        fig = go.Figure()
        return _apply_layout(fig, "No expense category data yet")
    cat_df = pd.DataFrame(Counter(all_cats).items(), columns=["category", "count"]).sort_values("count")

    n = len(cat_df)
    colors = [f"rgba(0,229,255,{0.4 + 0.6 * i / max(n - 1, 1):.2f})" for i in range(n)]

    fig = go.Figure(go.Bar(
        x=cat_df["count"], y=cat_df["category"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=cat_df["count"], textposition="auto",
        textfont=dict(color="#f0f4ff", size=11),
    ))
    return _apply_layout(fig, "Top Expense Categories",
                         height=max(300, n * 44), xaxis_title="Number of Users")


def chart_savings_distribution(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["savings_pct"].clip(0, 100), nbinsx=20,
        marker=dict(color=COLORS["cyan"], opacity=0.75, line=dict(color="#0d1220", width=1)),
        hovertemplate="Savings %: %{x:.1f}<br>Users: %{y}<extra></extra>",
    ))
    fig.add_vline(x=20, line_dash="dot", line_color=COLORS["amber"], line_width=1.5,
                  annotation_text="20% target", annotation_font_color=COLORS["amber"],
                  annotation_font_size=11)
    return _apply_layout(fig, "Savings % Distribution",
                         xaxis_title="Savings % of Income", yaxis_title="Users", height=320)


def chart_stress_vs_savings(df: pd.DataFrame) -> go.Figure:
    seg_colors = {"Wealth Builder": COLORS["green"], "Saver": COLORS["cyan"],
                  "Balanced": COLORS["amber"], "Overspender": COLORS["red"]}
    fig = go.Figure()
    for seg, color in seg_colors.items():
        sub = df[df["behavior"] == seg]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["stress"], y=sub["savings_pct"], mode="markers", name=seg,
            marker=dict(color=color, size=11, opacity=0.8,
                        line=dict(color="rgba(0,0,0,0.5)", width=1),
                        symbol="circle"),
            hovertemplate=f"<b>{seg}</b><br>Stress: %{{x}}<br>Savings: %{{y:.1f}}%<extra></extra>",
        ))
    return _apply_layout(fig, "Stress vs Savings Rate",
                         xaxis_title="Stress Score (1–10)", yaxis_title="Savings % of Income", height=340)


def chart_manova_group_means(group_means: pd.DataFrame) -> go.Figure:
    metrics = ["savings_pct", "stress", "wealth_10y_moderate"]
    labels  = ["Avg Savings %", "Avg Stress", "Proj. Wealth (÷1K)"]
    colors  = [COLORS["cyan"], COLORS["amber"], COLORS["violet"]]

    fig = go.Figure()
    for metric, label, color in zip(metrics, labels, colors):
        vals = group_means[metric].copy()
        if metric == "wealth_10y_moderate":
            vals = vals / 1000
        fig.add_trace(go.Bar(
            name=label, x=group_means.index.astype(str), y=vals,
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            text=vals.round(1), textposition="auto",
            textfont=dict(color="#f0f4ff", size=11),
        ))
    return _apply_layout(fig, "MANOVA — Group Means (Wealth ÷1,000)",
                         barmode="group", height=340)