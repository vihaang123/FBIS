
"""pages/1_Form.py — Smart Adaptive Financial Data Collection Form"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import initialize_db, insert_user
from utils import inject_global_css

st.set_page_config(page_title="FBIS — Submit Your Profile", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
initialize_db()
inject_global_css()

with st.sidebar:
    st.markdown('<div style="padding:18px 16px 20px;margin-bottom:8px;border-bottom:1px solid #243050;"><div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;"><div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#f5c842,#e8a020);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;color:#0a0a0a;">F</div><span style="font-size:17px;font-weight:800;color:#e8ecf5;">FBIS</span></div><p style="color:#5a6890;font-size:0.75rem;margin:0;">Financial Intelligence System</p></div>', unsafe_allow_html=True)

# Page header
st.markdown('<div style="background:linear-gradient(90deg,rgba(61,142,245,0.07) 0%,transparent 100%);border-left:3px solid #3d8ef5;border-radius:0 12px 12px 0;padding:20px 26px;margin-bottom:24px;"><h1 style="color:#e8ecf5;font-size:1.6rem;font-weight:800;margin:0 0 5px 0;">📋 Financial Profile Form</h1><p style="color:#5a6890;margin:0;font-size:0.9rem;">Your data is stored locally and used only for personalised analysis.</p></div>', unsafe_allow_html=True)

# Progress bar
st.markdown('<div style="display:flex;align-items:center;background:#131928;border:1px solid #243050;border-radius:12px;padding:14px 20px;margin-bottom:28px;gap:0;"><div style="display:flex;align-items:center;gap:8px;"><div style="width:22px;height:22px;border-radius:50%;background:#3d8ef5;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff;">1</div><span style="color:#3d8ef5;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Identity</span></div><div style="flex:1;height:1px;background:#243050;margin:0 12px;"></div><div style="display:flex;align-items:center;gap:8px;"><div style="width:22px;height:22px;border-radius:50%;background:#3d8ef5;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#fff;">2</div><span style="color:#3d8ef5;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Financials</span></div><div style="flex:1;height:1px;background:#243050;margin:0 12px;"></div><div style="display:flex;align-items:center;gap:8px;"><div style="width:22px;height:22px;border-radius:50%;background:#1e2840;border:1px solid #243050;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#5a6890;">3</div><span style="color:#5a6890;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Behaviour</span></div><div style="flex:1;height:1px;background:#243050;margin:0 12px;"></div><div style="display:flex;align-items:center;gap:8px;"><div style="width:22px;height:22px;border-radius:50%;background:#1e2840;border:1px solid #243050;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;color:#5a6890;">4</div><span style="color:#5a6890;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;">Goals</span></div></div>', unsafe_allow_html=True)


def divider(step, title):
    st.markdown(f'<div style="display:flex;align-items:center;gap:14px;margin:28px 0 16px 0;"><div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;background:linear-gradient(135deg,#3d8ef5,#7c5cfc);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#fff;">{step}</div><span style="color:#e8ecf5;font-size:0.82rem;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;">{title}</span><div style="flex:1;height:1px;background:#243050;"></div></div>', unsafe_allow_html=True)


with st.form("fbis_form", clear_on_submit=True):

    # ── Section 01: Identity ────────────────────────────────────────────────
    divider("01", "Identity")
    col_a, col_b, col_c = st.columns([1.2, 1.2, 1])
    with col_a:
        name = st.text_input("Full Name *", placeholder="e.g. Rahul Sharma")
    with col_b:
        user_type = st.selectbox(
            "I am a … *",
            ["— Select —", "Student", "Working Professional", "Business Owner", "Other"],
        )
    with col_c:
        user_type_other = ""
        if user_type == "Other":
            user_type_other = st.text_input("Describe your occupation", placeholder="e.g. Freelancer")
        else:
            st.empty()

    # ── Section 02: Basic Info ──────────────────────────────────────────────
    divider("02", "Basic Info")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (years) *", min_value=16, max_value=90, value=25, step=1)

    # ── Section 03: Monthly Financials ─────────────────────────────────────
    divider("03", "Monthly Financials")
    st.markdown('<p style="color:#5a6890;font-size:0.82rem;margin:-8px 0 12px 0;">All amounts in ₹ (Indian Rupees)</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        income = st.number_input("💰 Monthly Income *", min_value=0.0, value=50000.0, step=1000.0, format="%.0f")
    with col2:
        expenses = st.number_input("🧾 Monthly Expenses *", min_value=0.0, value=30000.0, step=1000.0, format="%.0f")
    with col3:
        savings = st.number_input("🏦 Monthly Savings *", min_value=0.0, value=10000.0, step=500.0, format="%.0f")

    st.markdown('<p style="color:#3a4560;font-size:0.8rem;margin:10px 0 4px 0;">Optional — discretionary spending</p>', unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    with col4:
        daily_spending = st.number_input("☕ Daily Discretionary Spending", min_value=0.0, value=0.0, step=50.0, format="%.0f")
    with col5:
        weekly_spending = st.number_input("🛍️ Weekly Extra Spending", min_value=0.0, value=0.0, step=100.0, format="%.0f")

    # ── Section 04: Expense Categories ─────────────────────────────────────
    divider("04", "Expense Categories")
    expense_categories = st.multiselect(
        "Where does your money go? (select all that apply)",
        options=["🍔 Food / Dining", "🛍️ Shopping", "🏠 Rent / Living", "✈️ Travel", "🎬 Entertainment", "📱 Subscriptions", "📚 Education", "🏥 Healthcare", "Other"],
        default=[],
        placeholder="Select categories …",
    )

    # ── Section 05: Spending Behaviour ─────────────────────────────────────
    divider("05", "Spending Behaviour")
    col1, col2 = st.columns(2)
    with col1:
        spending_habit = st.selectbox(
            "🧠 Spending Style *",
            ["— Select —", "Needs-Based", "Balanced", "Lifestyle-Heavy"],
            help="Needs-Based = essentials only | Balanced = mix | Lifestyle-Heavy = comfort & luxury.",
        )
        tracking = st.selectbox("📊 Do you track expenses? *", ["— Select —", "Yes", "No"])
    with col2:
        discipline = st.selectbox(
            "💪 Savings Discipline *",
            ["— Select —", "Fixed % each month", "Random / whenever possible"],
        )
        overspending = st.selectbox("⚠️ Do you overspend regularly? *", ["— Select —", "No", "Yes"])

    # ── Section 06: Investment ──────────────────────────────────────────────
    divider("06", "Investment")
    investment = st.radio("Do you currently invest? *", ["Yes", "No"], horizontal=True, index=None)

    investment_amount = 0.0
    investment_types = []

    if investment == "Yes":
        col1, col2 = st.columns(2)
        with col1:
            investment_amount = st.number_input("📈 Monthly Investment Amount (₹)", min_value=0.0, value=5000.0, step=500.0, format="%.0f")
        with col2:
            investment_types = st.multiselect(
                "Investment Instruments",
                ["Mutual Funds (SIP)", "Stocks / Equity", "Cryptocurrency", "Fixed Deposits", "Gold / SGBs", "PPF / NPS", "Other"],
                default=[],
                placeholder="Select instruments …",
            )

    # ── Section 07: Financial Stability ────────────────────────────────────
    divider("07", "Financial Stability")
    col1, col2 = st.columns(2)
    with col1:
        emergency_fund = st.selectbox(
            "🛡️ Emergency Fund Coverage *",
            ["— Select —", "0 months", "1–3 months", "3–6 months", "6+ months"],
        )
    with col2:
        stress = st.slider("😰 Financial Stress Level *", min_value=1, max_value=10, value=5, help="1 = stress-free · 10 = very stressed")

    # ── Section 08: Goal ───────────────────────────────────────────────────
    divider("08", "Financial Goal (Optional)")
    goal = st.selectbox(
        "🎯 Primary Financial Goal",
        ["— Not set yet —", "Save more money", "Grow investments", "Reduce debt", "Achieve financial independence", "Buy a home", "Build emergency fund", "Other"],
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 Submit My Financial Profile", use_container_width=True)


# ── On Submit ──────────────────────────────────────────────────────────────
if submitted:
    errors = []
    if not name or name.strip() == "":
        errors.append("Full name is required.")
    if user_type == "— Select —":
        errors.append("Please select your occupation type.")
    if income <= 0:
        errors.append("Monthly income must be greater than ₹0.")
    if expenses < 0:
        errors.append("Monthly expenses cannot be negative.")
    if savings < 0:
        errors.append("Monthly savings cannot be negative.")
    if savings > income:
        errors.append("Savings cannot exceed income.")
    if age < 16 or age > 90:
        errors.append("Please enter a valid age between 16 and 90.")
    if spending_habit == "— Select —":
        errors.append("Please select your spending style.")
    if tracking == "— Select —":
        errors.append("Please indicate whether you track expenses.")
    if discipline == "— Select —":
        errors.append("Please select your savings discipline.")
    if overspending == "— Select —":
        errors.append("Please indicate whether you overspend.")
    if investment is None:
        errors.append("Please indicate whether you invest.")
    if emergency_fund == "— Select —":
        errors.append("Please select your emergency fund coverage.")

    if errors:
        for err in errors:
            st.markdown(f'<div style="background:rgba(255,77,106,0.08);border:1px solid rgba(255,77,106,0.3);border-left:3px solid #ff4d6a;border-radius:0 10px 10px 0;padding:11px 16px;margin-bottom:7px;"><p style="color:#ff4d6a;margin:0;font-size:0.87rem;font-weight:600;">❌ {err}</p></div>', unsafe_allow_html=True)
    else:
        # Clean sentinel values
        clean_user_type = user_type if user_type != "— Select —" else "Other"
        clean_spending_habit = spending_habit if spending_habit != "— Select —" else ""
        clean_tracking = tracking if tracking != "— Select —" else "No"
        clean_discipline = discipline if discipline != "— Select —" else ""
        clean_overspending = overspending if overspending != "— Select —" else "No"
        clean_emergency = emergency_fund if emergency_fund != "— Select —" else "0"
        clean_goal = goal if goal != "— Not set yet —" else ""
        clean_investment = investment if investment else "No"

        record = {
            "user_type": clean_user_type, "user_type_other": user_type_other,
            "age": int(age), "income": float(income), "expenses": float(expenses),
            "savings": float(savings), "daily_spending": float(daily_spending),
            "weekly_spending": float(weekly_spending), "expense_categories": expense_categories,
            "spending_habit": clean_spending_habit, "tracking": clean_tracking,
            "discipline": clean_discipline, "overspending": clean_overspending,
            "investment": clean_investment, "investment_amount": float(investment_amount),
            "investment_types": investment_types, "emergency_fund": clean_emergency,
            "stress": int(stress), "goal": clean_goal,
        }

        new_id = insert_user(record)
        st.session_state["last_user_id"] = new_id

        spct = round((savings / income) * 100, 1) if income > 0 else 0
        sc = "#00e07a" if spct >= 20 else "#f5c842" if spct >= 10 else "#ff4d6a"
        ic = "#00e07a" if clean_investment == "Yes" else "#ff4d6a"
        it = "Yes ✓" if clean_investment == "Yes" else "No ✗"

        st.markdown(
            f'<div style="background:linear-gradient(135deg,#0b1e14 0%,#0e1a10 100%);border:1px solid rgba(0,224,122,0.3);border-left:3px solid #00e07a;border-radius:0 16px 16px 0;padding:28px 32px;margin-top:24px;">'
            f'<h2 style="color:#00e07a;margin:0 0 6px 0;font-size:1.2rem;font-weight:800;">✅ Profile Submitted — Welcome, {name.strip()}!</h2>'
            f'<p style="color:#5a6890;margin:0 0 20px 0;font-size:0.88rem;">Record ID: <strong style="color:#e8ecf5;font-family:JetBrains Mono,monospace;background:#131928;border:1px solid #243050;border-radius:5px;padding:2px 8px;">#{new_id}</strong>. Navigate to Dashboard to see your analysis.</p>'
            f'<div style="display:flex;gap:28px;flex-wrap:wrap;">'
            f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1.5px;">Monthly Income</p><p style="color:#e8ecf5;font-size:1.4rem;font-weight:800;margin:3px 0 0 0;font-family:JetBrains Mono,monospace;">₹{income:,.0f}</p></div>'
            f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1.5px;">Monthly Savings</p><p style="color:#e8ecf5;font-size:1.4rem;font-weight:800;margin:3px 0 0 0;font-family:JetBrains Mono,monospace;">₹{savings:,.0f}</p></div>'
            f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1.5px;">Savings Rate</p><p style="color:{sc};font-size:1.4rem;font-weight:800;margin:3px 0 0 0;font-family:JetBrains Mono,monospace;">{spct}%</p></div>'
            f'<div><p style="color:#3a4560;font-size:0.68rem;margin:0;text-transform:uppercase;letter-spacing:1.5px;">Investor</p><p style="color:{ic};font-size:1.4rem;font-weight:800;margin:3px 0 0 0;">{it}</p></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        st.balloons()
        st.markdown('<br><p style="text-align:center;color:#5a6890;">👈 Navigate to <strong style="color:#7c5cfc;">Dashboard</strong> in the sidebar.</p>', unsafe_allow_html=True)
