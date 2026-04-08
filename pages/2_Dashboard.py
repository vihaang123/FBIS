"""pages/2_Dashboard.py — FBIS Analytics Dashboard"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import initialize_db, fetch_all_users
from utils import (inject_global_css, section_header, metric_card, score_badge, savings_pct, project_wealth, generate_improvements, ALLOCATION, PROFILE_RATES)
from analysis import (prepare_df, overview_stats, run_anova_tests, run_manova, chart_age_group_metrics, chart_anova_pvalues, chart_wealth_projection, chart_behavior_segments, chart_investment_profiles, chart_expense_categories, chart_savings_distribution, chart_stress_vs_savings, chart_manova_group_means, PLOTLY_LAYOUT, COLORS)

st.set_page_config(page_title="FBIS — Analytics Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
initialize_db()
inject_global_css()

with st.sidebar:
    st.markdown('<div style="padding:18px 16px 20px;margin-bottom:8px;border-bottom:1px solid #243050;"><div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;"><div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#f5c842,#e8a020);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;color:#0a0a0a;">F</div><span style="font-size:17px;font-weight:800;color:#e8ecf5;">FBIS</span></div><p style="color:#5a6890;font-size:0.75rem;margin:0;">Financial Intelligence System</p></div>', unsafe_allow_html=True)

st.markdown('<div style="background:linear-gradient(90deg,rgba(124,92,252,0.07) 0%,transparent 100%);border-left:3px solid #7c5cfc;border-radius:0 12px 12px 0;padding:20px 26px;margin-bottom:28px;"><h1 style="color:#e8ecf5;font-size:1.6rem;font-weight:800;margin:0 0 5px 0;">📊 Analytics Dashboard</h1><p style="color:#5a6890;margin:0;font-size:0.9rem;">Live statistical analysis · ANOVA &amp; MANOVA · Wealth projections · Personalised insights</p></div>', unsafe_allow_html=True)

raw_df = fetch_all_users()

if raw_df.empty:
    st.markdown('<div style="text-align:center;padding:72px 32px;background:#131928;border:1px dashed #243050;border-radius:20px;margin-top:32px;"><div style="font-size:3rem;margin-bottom:16px;">📭</div><h2 style="color:#e8ecf5;font-size:1.2rem;margin:0 0 10px 0;">No Data Yet</h2><p style="color:#5a6890;margin:0;">Submit your financial profile first using the <strong style="color:#3d8ef5;">Form</strong> page.</p></div>', unsafe_allow_html=True)
    st.stop()

df = prepare_df(raw_df)

# ─── SECTION 1: OVERVIEW ────────────────────────────────────────────────────
section_header("01 — Platform Overview", f"{len(df)} users in the system")

stats = overview_stats(df)
avg_sp  = stats.get("avg_savings_pct", 0)
pct_inv = stats.get("pct_investors", 0)
insight_color = "#00e07a" if avg_sp >= 20 else "#f5c842" if avg_sp >= 15 else "#ff4d6a"
insight_label = "above target" if avg_sp >= 20 else "approaching target" if avg_sp >= 15 else "below the recommended 20%"

st.markdown(f'<div style="background:linear-gradient(135deg,#0f1a2e 0%,#12172a 100%);border:1px solid #243050;border-left:3px solid {insight_color};border-radius:0 12px 12px 0;padding:14px 22px;margin-bottom:20px;"><p style="color:#e8ecf5;margin:0;font-size:0.9rem;">🔍 <strong>Key Insight:</strong> <span style="color:{insight_color};font-weight:700;">{avg_sp:.1f}%</span> average savings rate — <span style="color:{insight_color};">{insight_label}</span>. <strong style="color:#7c5cfc;">{pct_inv:.0f}%</strong> of users invest actively.</p></div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: metric_card("Total Users", str(stats.get("total_users", 0)), color="#3d8ef5")
with c2: metric_card("Avg Income", f"₹{stats.get('avg_income',0):,.0f}", color="#7c5cfc")
with c3: metric_card("Avg Savings", f"{avg_sp:.1f}%", delta="Target: 20%+", color="#00e07a")
with c4: metric_card("Investors", f"{pct_inv:.1f}%", color="#00d4aa")
with c5: metric_card("Avg Score", f"{stats.get('avg_fin_score',0):.1f}", color="#f5c842")

st.markdown("<br>", unsafe_allow_html=True)
col_l, col_r = st.columns(2)
with col_l: st.plotly_chart(chart_savings_distribution(df), use_container_width=True)
with col_r: st.plotly_chart(chart_stress_vs_savings(df), use_container_width=True)

# ─── SECTION 2: AGE GROUP ───────────────────────────────────────────────────
section_header("02 — Age Group Analysis", "How different age cohorts compare on savings, investment, and stress")
st.plotly_chart(chart_age_group_metrics(df), use_container_width=True)
age_tbl = df.groupby("age_group").agg(Users=("id","count"), Avg_Income=("income", lambda x: f"₹{x.mean():,.0f}"), Avg_Savings_Pct=("savings_pct", lambda x: f"{x.mean():.1f}%"), Investor_Rate=("investment", lambda x: f"{(x.str.lower()=='yes').mean()*100:.1f}%"), Avg_Stress=("stress", lambda x: f"{x.mean():.1f}/10")).reset_index().rename(columns={"age_group":"Age Group"})
st.dataframe(age_tbl, use_container_width=True, hide_index=True)

# ─── SECTION 3: ANOVA ───────────────────────────────────────────────────────
section_header("03 — ANOVA Analysis", "One-way ANOVA — are group differences statistically significant?")
anova_results = run_anova_tests(df)

if not anova_results:
    st.markdown('<div style="background:#131928;border:1px solid #243050;border-left:3px solid #f5c842;border-radius:0 10px 10px 0;padding:14px 18px;"><p style="color:#f5c842;margin:0;font-size:0.88rem;font-weight:600;">⚠ Need at least 2 distinct groups with ≥2 users each for ANOVA. Add more data!</p></div>', unsafe_allow_html=True)
else:
    st.plotly_chart(chart_anova_pvalues(anova_results), use_container_width=True)
    for res in anova_results:
        c = "#00e07a" if res["significant"] else "#5a6890"
        b = "rgba(0,224,122,0.2)" if res["significant"] else "#243050"
        sig_text = "Significant ✓" if res["significant"] else "Not Significant"
        st.markdown(
            f'<div style="background:#131928;border:1px solid {b};border-left:3px solid {c};border-radius:0 10px 10px 0;padding:14px 20px;margin-bottom:10px;">'
            f'<p style="color:#e8ecf5;font-weight:800;margin:0 0 5px 0;font-size:0.9rem;">{res["test_name"]}</p>'
            f'<p style="color:#5a6890;margin:0 0 10px 0;font-size:0.83rem;line-height:1.5;">{res["interpretation"]}</p>'
            f'<div style="display:flex;gap:20px;">'
            f'<span style="color:#3a4560;font-size:0.76rem;font-family:JetBrains Mono,monospace;">F = {res["f_stat"]}</span>'
            f'<span style="color:#3a4560;font-size:0.76rem;font-family:JetBrains Mono,monospace;">p = {res["p_value"]}</span>'
            f'<span style="color:{c};font-size:0.76rem;font-weight:700;font-family:JetBrains Mono,monospace;">{sig_text}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

# ─── SECTION 4: MANOVA ──────────────────────────────────────────────────────
section_header("04 — MANOVA Analysis", "Multivariate ANOVA on savings, stress, and projected wealth jointly")
manova_group = st.selectbox("Group variable for MANOVA", ["spending_habit","investment","tracking","overspending"], format_func=lambda x: x.replace("_"," ").title(), key="manova_group")
manova_result = run_manova(df, manova_group)

if not manova_result.get("success"):
    st.markdown(f'<div style="background:#131928;border:1px solid #243050;border-left:3px solid #f5c842;border-radius:0 10px 10px 0;padding:14px 18px;"><p style="color:#f5c842;margin:0;font-size:0.88rem;font-weight:600;">⚠ MANOVA could not run: {manova_result.get("message")}. Add more varied data.</p></div>', unsafe_allow_html=True)
else:
    sig = manova_result["significant"]
    c = "#00e07a" if sig else "#5a6890"
    b = "rgba(0,224,122,0.2)" if sig else "#243050"
    sig_label = "Statistically Significant ✓" if sig else "Not Significant"
    st.markdown(
        f'<div style="background:#131928;border:1px solid {b};border-left:3px solid {c};border-radius:0 12px 12px 0;padding:20px 24px;margin-bottom:16px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">'
        f'<p style="color:#e8ecf5;font-size:0.92rem;font-weight:800;margin:0;">MANOVA — Grouped by: <span style="color:#7c5cfc;">{manova_group.replace("_"," ").title()}</span></p>'
        f'<span style="background:{c}18;color:{c};border:1px solid {c}44;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:800;text-transform:uppercase;">{sig_label}</span>'
        f'</div>'
        f'<p style="color:#5a6890;margin:10px 0 0 0;font-size:0.85rem;line-height:1.55;">{manova_result.get("explanation","")}</p>'
        f'<div style="display:flex;gap:20px;margin-top:12px;">'
        f'<span style="color:#3a4560;font-size:0.75rem;font-family:JetBrains Mono,monospace;">Wilks\' λ = {manova_result.get("stat","N/A")}</span>'
        f'<span style="color:#3a4560;font-size:0.75rem;font-family:JetBrains Mono,monospace;">p = {manova_result.get("p_value","N/A")}</span>'
        f'</div></div>',
        unsafe_allow_html=True
    )
    if "group_means" in manova_result:
        st.plotly_chart(chart_manova_group_means(manova_result["group_means"]), use_container_width=True)

# ─── SECTION 5: BEHAVIORAL SEGMENTS ────────────────────────────────────────
section_header("05 — Behavioral Segmentation", "How users cluster based on spending and saving habits")
col_l, col_r = st.columns([1, 1.2])
with col_l: st.plotly_chart(chart_behavior_segments(df), use_container_width=True)
with col_r:
    seg_stats = df.groupby("behavior").agg(Count=("id","count"), Avg_Income=("income", lambda x: f"₹{x.mean():,.0f}"), Avg_Savings=("savings_pct", lambda x: f"{x.mean():.1f}%"), Avg_Score=("fin_score", lambda x: f"{x.mean():.1f}")).reset_index().rename(columns={"behavior":"Segment"})
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(seg_stats, use_container_width=True, hide_index=True)

# ─── SECTION 6: INVESTMENT PROFILES ────────────────────────────────────────
section_header("06 — Investment Profiles", "Distribution of risk profiles and projected wealth")
st.plotly_chart(chart_investment_profiles(df), use_container_width=True)

profile_colors = {"Conservative": "#00d4aa", "Moderate": "#3d8ef5", "Aggressive": "#7c5cfc"}
st.markdown('<div style="background:#131928;border:1px solid #243050;border-radius:12px;padding:18px 20px;margin-top:8px;">', unsafe_allow_html=True)
st.markdown('<p style="color:#5a6890;font-size:0.7rem;margin:0 0 14px 0;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Recommended Asset Allocation by Profile</p>', unsafe_allow_html=True)
for profile, alloc in ALLOCATION.items():
    pc = profile_colors.get(profile, "#3d8ef5")
    badges = "".join([f'<span style="background:rgba(255,255,255,0.04);border:1px solid #243050;border-radius:7px;padding:6px 12px;display:inline-flex;align-items:center;gap:6px;margin:3px;"><span style="color:#e8ecf5;font-size:0.78rem;font-weight:700;">{asset}</span><span style="color:{pc};font-size:0.78rem;font-weight:800;font-family:JetBrains Mono,monospace;">{pct}%</span></span>' for asset, pct in alloc.items()])
    st.markdown(f'<div style="margin-bottom:14px;"><p style="color:{pc};font-size:0.8rem;font-weight:800;margin:0 0 8px 0;text-transform:uppercase;">{profile}</p><div style="display:flex;flex-wrap:wrap;gap:4px;">{badges}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── SECTION 7: EXPENSE CATEGORIES ─────────────────────────────────────────
section_header("07 — Expense Category Analysis", "Top spending categories across all users")
st.plotly_chart(chart_expense_categories(df), use_container_width=True)

# ─── SECTION 8: EMERGENCY FUND & TRACKING ───────────────────────────────────
section_header("08 — Emergency Fund & Expense Tracking", "Distribution of financial safety net and tracking habits")
col_l, col_r = st.columns(2)
total = len(df)

with col_l:
    ef_counts = df["emergency_fund"].value_counts()
    ef_colors = {"0 months": "#ff4d6a", "1–3 months": "#f5c842", "3–6 months": "#3d8ef5", "6+ months": "#00e07a"}
    st.markdown('<div style="background:#131928;border:1px solid #243050;border-radius:12px;padding:18px 20px;">', unsafe_allow_html=True)
    st.markdown('<p style="color:#5a6890;font-size:0.7rem;margin:0 0 14px 0;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Emergency Fund Coverage</p>', unsafe_allow_html=True)
    for cat, cnt in ef_counts.items():
        pct = (cnt / total) * 100
        color = ef_colors.get(str(cat), "#5a6890")
        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#e8ecf5;font-size:0.83rem;font-weight:600;">{cat}</span><span style="color:{color};font-size:0.8rem;font-weight:700;font-family:JetBrains Mono,monospace;">{pct:.0f}%</span></div><div style="background:#243050;border-radius:3px;height:5px;overflow:hidden;"><div style="background:{color};border-radius:3px;height:5px;width:{min(pct,100):.0f}%;"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    track_counts = df["tracking"].value_counts()
    st.markdown('<div style="background:#131928;border:1px solid #243050;border-radius:12px;padding:18px 20px;">', unsafe_allow_html=True)
    st.markdown('<p style="color:#5a6890;font-size:0.7rem;margin:0 0 14px 0;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Expense Tracking Adoption</p>', unsafe_allow_html=True)
    for val, cnt in track_counts.items():
        pct = (cnt / total) * 100
        color = "#00e07a" if str(val).lower() == "yes" else "#ff4d6a"
        label = "Tracking ✓" if str(val).lower() == "yes" else "Not Tracking"
        st.markdown(f'<div style="margin-bottom:12px;"><div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="color:#e8ecf5;font-size:0.83rem;font-weight:600;">{label}</span><span style="color:{color};font-size:0.8rem;font-weight:700;font-family:JetBrains Mono,monospace;">{cnt} users · {pct:.0f}%</span></div><div style="background:#243050;border-radius:3px;height:5px;overflow:hidden;"><div style="background:{color};border-radius:3px;height:5px;width:{min(pct,100):.0f}%;"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── SECTION 9: PERSONAL ANALYSIS ───────────────────────────────────────────
section_header("09 — Personal Analysis", "Select your record ID to view personalised financial analysis")

user_ids = df["id"].tolist()
default_idx = user_ids.index(st.session_state["last_user_id"]) if "last_user_id" in st.session_state and st.session_state["last_user_id"] in user_ids else 0
selected_id = st.selectbox("Select User Record ID", options=user_ids, index=default_idx, format_func=lambda x: f"Record #{x}")

user_row = df[df["id"] == selected_id].iloc[0]
income   = user_row["income"]
savings  = user_row["savings"]
stress   = user_row["stress"]
spct     = user_row["savings_pct"]
score    = user_row["fin_score"]
segment  = user_row["behavior"]
profile  = user_row["inv_profile"]
age_grp  = user_row["age_group"]

same_age   = df[df["age_group"] == age_grp]["savings_pct"]
percentile = int((same_age < spct).mean() * 100) if len(same_age) > 1 else 50
sc = "#00e07a" if spct >= 20 else "#f5c842" if spct >= 10 else "#ff4d6a"
stc = "#ff4d6a" if stress >= 7 else "#f5c842" if stress >= 5 else "#00e07a"
score_pct = min(score, 100)

st.markdown(
    f'<div style="background:linear-gradient(135deg,#0f1420 0%,#131928 100%);border:1px solid #243050;border-radius:16px;padding:28px 32px;margin:16px 0;">'
    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px;">'
    f'<div><p style="color:#5a6890;font-size:0.7rem;margin:0 0 8px 0;text-transform:uppercase;letter-spacing:2px;font-weight:700;">Financial Health Score</p>'
    f'<div style="font-size:3.8rem;font-weight:800;line-height:1;background:linear-gradient(135deg,#3d8ef5,#7c5cfc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-family:JetBrains Mono,monospace;">{score:.0f}<span style="font-size:1.4rem;color:#3a4560;-webkit-text-fill-color:#3a4560;">/100</span></div>'
    f'<div style="margin-top:12px;">{score_badge(score)}</div>'
    f'<div style="margin-top:14px;width:180px;height:5px;background:#243050;border-radius:3px;overflow:hidden;"><div style="height:100%;border-radius:3px;width:{score_pct}%;background:linear-gradient(90deg,#3d8ef5,#7c5cfc);"></div></div></div>'
    f'<div style="display:flex;gap:28px;flex-wrap:wrap;">'
    f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1px;">Segment</p><p style="color:#e8ecf5;font-size:1rem;font-weight:800;margin:5px 0 0 0;">{segment}</p></div>'
    f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1px;">Inv. Profile</p><p style="color:#e8ecf5;font-size:1rem;font-weight:800;margin:5px 0 0 0;">{profile}</p></div>'
    f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1px;">Age Group</p><p style="color:#e8ecf5;font-size:1rem;font-weight:800;margin:5px 0 0 0;">{age_grp}</p></div>'
    f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1px;">Savings Rate</p><p style="color:{sc};font-size:1rem;font-weight:800;margin:5px 0 0 0;font-family:JetBrains Mono,monospace;">{spct:.1f}%</p></div>'
    f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1px;">Stress</p><p style="color:{stc};font-size:1rem;font-weight:800;margin:5px 0 0 0;font-family:JetBrains Mono,monospace;">{stress}/10</p></div>'
    f'</div></div>'
    f'<div style="margin-top:16px;padding:12px 16px;background:rgba(61,142,245,0.07);border:1px solid rgba(61,142,245,0.2);border-radius:8px;">'
    f'<p style="color:#3d8ef5;font-size:0.86rem;margin:0;">📊 You save more than <strong>{percentile}%</strong> of users in the {age_grp} age group. Financial stress: {stress}/10 — {"check the improvement plan below." if stress >= 6 else "well managed!"}</p>'
    f'</div></div>',
    unsafe_allow_html=True
)

st.plotly_chart(chart_wealth_projection(savings, f"Record #{selected_id}"), use_container_width=True)

proj_data = [{"Scenario": l, "5-Year": f"₹{project_wealth(savings,5,r):,.0f}", "10-Year": f"₹{project_wealth(savings,10,r):,.0f}", "20-Year": f"₹{project_wealth(savings,20,r):,.0f}"} for l, r in [("Conservative (4%)", 0.04), ("Moderate (8%)", 0.08), ("Aggressive (12%)", 0.12)]]
st.dataframe(pd.DataFrame(proj_data), use_container_width=True, hide_index=True)

# ─── SECTION 10: IMPROVEMENT ENGINE ─────────────────────────────────────────
section_header("10 — Personalised Improvement Plan", "Actionable recommendations with estimated 10-year financial impact")
improvements = generate_improvements(user_row)

if not improvements:
    st.markdown('<div style="background:linear-gradient(135deg,#0b1e14,#0e1a10);border:1px solid rgba(0,224,122,0.3);border-left:3px solid #00e07a;border-radius:0 14px 14px 0;padding:22px 26px;"><h3 style="color:#00e07a;margin:0 0 8px 0;font-size:1.1rem;font-weight:800;">🏆 Outstanding Financial Health!</h3><p style="color:#5a6890;margin:0;font-size:0.88rem;line-height:1.6;">No significant issues detected. Keep maintaining your savings rate, investing regularly, and growing your emergency fund.</p></div>', unsafe_allow_html=True)
else:
    for i, imp in enumerate(improvements, 1):
        st.markdown(
            f'<div style="background:#131928;border:1px solid #243050;border-radius:12px;padding:20px 22px;margin-bottom:12px;position:relative;">'
            f'<div style="position:absolute;top:14px;right:16px;background:rgba(124,92,252,0.1);border:1px solid rgba(124,92,252,0.25);border-radius:20px;padding:2px 12px;font-size:0.72rem;color:#7c5cfc;font-weight:800;font-family:JetBrains Mono,monospace;">#{i:02d}</div>'
            f'<div style="margin-bottom:10px;"><span style="color:#ff4d6a;font-size:0.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;">⚠ Problem</span><p style="color:#e8ecf5;margin:4px 0 0 0;font-size:0.88rem;line-height:1.5;">{imp["problem"]}</p></div>'
            f'<div style="height:1px;background:#1e2840;margin:10px 0;"></div>'
            f'<div style="margin-bottom:10px;padding-left:12px;border-left:2px solid #243050;"><span style="color:#3d8ef5;font-size:0.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;">→ Solution</span><p style="color:#8892a4;margin:4px 0 0 0;font-size:0.85rem;line-height:1.5;">{imp["solution"]}</p></div>'
            f'<div style="background:rgba(0,224,122,0.06);border:1px solid rgba(0,224,122,0.15);border-radius:7px;padding:8px 12px;"><span style="color:#00e07a;font-size:0.68rem;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;">💰 Impact</span><p style="color:#00e07a;margin:3px 0 0 0;font-size:0.86rem;font-weight:700;font-family:JetBrains Mono,monospace;">{imp["impact"]}</p></div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#1e2840;font-size:0.75rem;padding-top:20px;border-top:1px solid #1e2840;font-family:JetBrains Mono,monospace;">FBIS Analytics Dashboard &mdash; SQLite local storage &nbsp;|&nbsp; SciPy · Statsmodels · Plotly</div>', unsafe_allow_html=True)