"""utils.py - Shared utility functions for FBIS"""

import pandas as pd
import numpy as np
import streamlit as st


def savings_pct(income, savings):
    if income <= 0: return 0.0
    return round((savings / income) * 100, 2)

def expense_ratio(income, expenses):
    if income <= 0: return 0.0
    return round((expenses / income) * 100, 2)

def project_wealth(monthly_savings, years, annual_rate):
    if monthly_savings <= 0 or annual_rate < 0: return 0.0
    r = annual_rate / 12
    n = years * 12
    if r == 0: return monthly_savings * n
    return monthly_savings * (((1 + r) ** n - 1) / r)

def financial_score(row):
    score = 0.0
    income = row.get("income", 0) or 0
    savings = row.get("savings", 0) or 0
    expenses = row.get("expenses", 0) or 0
    sp = savings_pct(income, savings)
    if sp >= 30: score += 30
    elif sp >= 20: score += 22
    elif sp >= 10: score += 14
    elif sp > 0: score += 6
    er = expense_ratio(income, expenses)
    if er <= 40: score += 20
    elif er <= 60: score += 14
    elif er <= 80: score += 7
    if str(row.get("investment", "No")).lower() == "yes":
        inv_pct = savings_pct(income, row.get("investment_amount", 0) or 0)
        if inv_pct >= 10: score += 20
        elif inv_pct >= 5: score += 14
        else: score += 8
    ef_map = {"0": 0, "1–3 months": 5, "3–6 months": 10, "6+ months": 15}
    score += ef_map.get(str(row.get("emergency_fund", "0")), 0)
    if str(row.get("tracking", "No")).lower() == "yes": score += 5
    score += max(0, 10 - (row.get("stress", 5) or 5))
    return min(round(score, 1), 100.0)

def assign_age_group(age):
    if age <= 22: return "18–22"
    elif age <= 30: return "23–30"
    elif age <= 40: return "31–40"
    else: return "40+"

def classify_behavior(row):
    income = row.get("income", 0) or 1
    savings = row.get("savings", 0) or 0
    expenses = row.get("expenses", 0) or 0
    invests = str(row.get("investment", "No")).lower() == "yes"
    sp = savings_pct(income, savings)
    er = expense_ratio(income, expenses)
    if sp >= 25 and invests: return "Wealth Builder"
    elif sp >= 20: return "Saver"
    elif sp >= 10 or er <= 70: return "Balanced"
    else: return "Overspender"

def assign_investment_profile(row):
    age = row.get("age", 30) or 30
    stress = row.get("stress", 5) or 5
    sp = savings_pct(row.get("income", 1) or 1, row.get("savings", 0) or 0)
    if stress >= 7 or sp < 10: return "Conservative"
    elif age <= 30 and sp >= 20: return "Aggressive"
    else: return "Moderate"

ALLOCATION = {
    "Conservative": {"Equity": 30, "Debt/FD": 50, "Gold": 10, "Emergency/Cash": 10},
    "Moderate":     {"Equity": 50, "Debt/FD": 30, "Gold": 10, "REITs/Other": 10},
    "Aggressive":   {"Equity": 75, "Debt/FD": 10, "Gold": 5,  "Crypto/Alt": 10},
}
PROFILE_RATES = {"Conservative": 0.04, "Moderate": 0.08, "Aggressive": 0.12}

def generate_improvements(row):
    improvements = []
    income = row.get("income", 0) or 1
    savings = row.get("savings", 0) or 0
    expenses = row.get("expenses", 0) or 0
    sp = savings_pct(income, savings)
    er = expense_ratio(income, expenses)
    if er > 70:
        improvements.append({"problem": f"Your expenses consume {er:.0f}% of income — above the healthy 60% threshold", "solution": "Identify and cut top 2 expense categories by 10–15%", "impact": f"₹{project_wealth(income*0.10,10,0.08):,.0f} extra wealth in 10 years"})
    if sp < 15:
        gap = income * 0.15 - savings
        if gap > 0:
            improvements.append({"problem": f"You save only {sp:.1f}% of income — experts recommend 20%+", "solution": "Automate a fixed monthly transfer to savings on salary day", "impact": f"₹{project_wealth(gap,10,0.08):,.0f} additional wealth in 10 years"})
    if str(row.get("investment", "No")).lower() == "no":
        improvements.append({"problem": "You are not investing — savings alone won't beat inflation", "solution": "Start a SIP of ₹500–₹5,000/month in index funds", "impact": f"₹{project_wealth(savings*0.5,10,0.08):,.0f} projected wealth at 8% in 10 years"})
    if str(row.get("tracking", "No")).lower() == "no":
        improvements.append({"problem": "You don't track expenses — invisible leaks drain 10–20% of income", "solution": "Use any budgeting app (Walnut, Money Manager) for 30 days", "impact": "Typically reveals ₹2,000–₹8,000/month in unnecessary spending"})
    if str(row.get("emergency_fund", "0")) == "0":
        improvements.append({"problem": "No emergency fund — one unexpected event can derail your finances", "solution": f"Build a ₹{expenses*3:,.0f} emergency fund (3× monthly expenses) in a liquid FD", "impact": "Prevents debt spiral and financial stress during crises"})
    if (row.get("stress", 5) or 5) >= 7:
        improvements.append({"problem": f"Financial stress is {row.get('stress',5)}/10 — chronic stress impairs decisions", "solution": "Create a simple monthly budget and review it every Sunday for 8 weeks", "impact": "Clarity and control reduce financial anxiety significantly"})
    return improvements


# ─── UI Helpers ────────────────────────────────────────────────────────────

def inject_global_css():
    css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--void:#080b12;--surface:#0e1420;--card:#131928;--line:#243050;--gold:#f5c842;--blue:#3d8ef5;--purple:#7c5cfc;--teal:#00d4aa;--red:#ff4d6a;--green:#00e07a;--text:#e8ecf5;--muted:#5a6890;}
html,body,[class*="css"]{font-family:'Syne',sans-serif!important;background-color:var(--void)!important;color:var(--text)!important;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding:1.5rem 2.5rem 3rem!important;max-width:1280px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0e1420 0%,#080b12 100%)!important;border-right:1px solid #243050!important;}
[data-testid="stSidebar"] *{color:#e8ecf5!important;}
.stTextInput input,.stNumberInput input,.stSelectbox select,.stTextArea textarea{background:#131928!important;border:1px solid #243050!important;border-radius:8px!important;color:#e8ecf5!important;font-family:'Syne',sans-serif!important;}
.stTextInput input:focus,.stNumberInput input:focus{border-color:#3d8ef5!important;box-shadow:0 0 0 3px rgba(61,142,245,0.15)!important;}
.stButton>button{background:linear-gradient(135deg,#3d8ef5,#7c5cfc)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:800!important;font-family:'Syne',sans-serif!important;padding:0.6rem 2rem!important;text-transform:uppercase!important;letter-spacing:0.5px!important;transition:all 0.2s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(61,142,245,0.35)!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #243050!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#5a6890!important;border:none!important;padding:8px 20px!important;font-weight:700!important;font-family:'Syne',sans-serif!important;text-transform:uppercase!important;letter-spacing:0.5px!important;}
.stTabs [aria-selected="true"]{background:rgba(61,142,245,0.1)!important;color:#3d8ef5!important;border-bottom:2px solid #3d8ef5!important;}
.stRadio label,.stCheckbox label{color:#e8ecf5!important;}
[data-testid="stRadioButton"]>label{background:#131928!important;border:1px solid #243050!important;border-radius:8px!important;padding:7px 16px!important;font-weight:600!important;}
[data-testid="stDataFrame"]{border-radius:12px!important;overflow:hidden!important;border:1px solid #243050!important;}
[data-baseweb="multi-select"]{background:#131928!important;border:1px solid #243050!important;border-radius:8px!important;}
.streamlit-expanderHeader{background:#131928!important;border-radius:10px!important;border:1px solid #243050!important;font-weight:700!important;}
.stAlert{background:#131928!important;border:1px solid #243050!important;border-radius:10px!important;}
</style>"""
    st.markdown(css, unsafe_allow_html=True)


def metric_card(label, value, delta="", color="#3d8ef5"):
    d = f'<p style="color:#00e07a;font-size:0.75rem;margin:3px 0 0 0;font-family:JetBrains Mono,monospace;">{delta}</p>' if delta else ""
    st.markdown(
        f'<div style="background:#131928;border:1px solid #243050;border-top:3px solid {color};border-radius:12px;padding:16px 18px;margin-bottom:6px;">'
        f'<p style="color:#5a6890;font-size:0.7rem;margin:0 0 7px 0;text-transform:uppercase;letter-spacing:1.8px;font-weight:700;">{label}</p>'
        f'<p style="color:{color};font-size:1.65rem;font-weight:800;margin:0;font-family:JetBrains Mono,monospace;letter-spacing:-1px;">{value}</p>'
        f'{d}</div>',
        unsafe_allow_html=True
    )


def section_header(title, subtitle=""):
    sub = f'<p style="color:#5a6890;font-size:0.88rem;margin:3px 0 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div style="margin:36px 0 18px 0;">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
        f'<div style="width:3px;height:22px;flex-shrink:0;border-radius:2px;background:linear-gradient(180deg,#3d8ef5,#7c5cfc);"></div>'
        f'<h2 style="color:#e8ecf5;font-size:1.1rem;font-weight:800;margin:0;text-transform:uppercase;">{title}</h2>'
        f'</div>{sub}'
        f'<div style="height:1px;margin-top:10px;background:linear-gradient(90deg,#243050 0%,transparent 80%);"></div>'
        f'</div>',
        unsafe_allow_html=True
    )


def score_badge(score):
    if score >= 75:   c, l = "#00e07a", "Excellent"
    elif score >= 55: c, l = "#f5c842",  "Good"
    elif score >= 35: c, l = "#ff8c40",  "Fair"
    else:             c, l = "#ff4d6a",  "Needs Work"
    return f'<span style="background:{c}18;color:{c};border:1px solid {c}44;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;">{l}</span>'