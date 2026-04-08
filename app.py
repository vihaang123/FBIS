"""
app.py - FBIS Entry Point — Premium UI
"""
import streamlit as st
from database import initialize_db
from utils import inject_global_css

st.set_page_config(
    page_title="FBIS — Financial Behavior Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_db()
inject_global_css()

# ✅ IMPORTANT: Ensure navigation shows
st.sidebar.title("📌 Navigation")

# ✅ Your branding (no layout change)
st.sidebar.markdown(
    '<div style="padding:18px 16px 20px;margin-bottom:8px;border-bottom:1px solid #243050;">'
    '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
    '<div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#f5c842,#e8a020);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;color:#0a0a0a;">F</div>'
    '<span style="font-size:17px;font-weight:800;color:#e8ecf5;">FBIS</span>'
    '</div>'
    '<p style="color:#5a6890;font-size:0.75rem;margin:0;">Financial Intelligence System</p>'
    '</div>',
    unsafe_allow_html=True
)

# Hero Section (UNCHANGED)
st.markdown(
    '<div style="background:linear-gradient(135deg,#0e1420 0%,#12172a 50%,#0e1420 100%);border:1px solid #243050;border-radius:20px;padding:52px 48px 44px;margin-bottom:28px;position:relative;overflow:hidden;">'
    '<div style="position:absolute;top:-60px;right:-40px;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(61,142,245,0.1) 0%,transparent 70%);"></div>'
    '<p style="color:#f5c842;font-size:0.72rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;margin:0 0 14px 0;">Financial Intelligence Platform</p>'
    '<h1 style="font-size:clamp(2rem,4vw,3rem);font-weight:800;margin:0 0 18px 0;line-height:1.05;background:linear-gradient(135deg,#e8ecf5 30%,#7c5cfc 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Financial Behavior<br>Intelligence System</h1>'
    '<p style="color:#5a6890;font-size:1rem;max-width:520px;line-height:1.7;margin:0 0 34px 0;">Understand your financial DNA. Submit your profile once and unlock ANOVA/MANOVA-powered insights, 10-year wealth projections, behavioral segmentation, and a personalised improvement roadmap.</p>'
    '<div style="display:flex;gap:14px;flex-wrap:wrap;">'
    '<div style="background:rgba(61,142,245,0.08);border:1px solid rgba(61,142,245,0.25);border-radius:10px;padding:12px 20px;"><span style="font-size:1.2rem;">📋</span><span style="color:#e8ecf5;font-weight:700;margin-left:8px;font-size:.9rem;">Smart Adaptive Form</span></div>'
    '<div style="background:rgba(124,92,252,0.08);border:1px solid rgba(124,92,252,0.25);border-radius:10px;padding:12px 20px;"><span style="font-size:1.2rem;">📊</span><span style="color:#e8ecf5;font-weight:700;margin-left:8px;font-size:.9rem;">Statistical Analysis</span></div>'
    '<div style="background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.25);border-radius:10px;padding:12px 20px;"><span style="font-size:1.2rem;">🚀</span><span style="color:#e8ecf5;font-weight:700;margin-left:8px;font-size:.9rem;">Wealth Projections</span></div>'
    '</div></div>',
    unsafe_allow_html=True
)

# Steps Section (UNCHANGED)
col1, col2, col3 = st.columns(3)

features = [
    ("📋", "Step 1 — Submit Form", "Fill in your financial profile: income, expenses, habits, and goals.", "#3d8ef5"),
    ("📊", "Step 2 — View Dashboard", "Explore group analytics, ANOVA/MANOVA results, and market comparisons.", "#7c5cfc"),
    ("💡", "Step 3 — Get Insights", "Receive personalised improvement plans, projections, and investment profiles.", "#00d4aa"),
]

for col, (icon, title, desc, color) in zip([col1, col2, col3], features):
    with col:
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#131928 0%,#0e1420 100%);border:1px solid #243050;border-top:3px solid {color};border-radius:14px;padding:26px 22px;height:100%;">'
            f'<div style="font-size:1.8rem;margin-bottom:14px;">{icon}</div>'
            f'<h3 style="color:#e8ecf5;font-size:0.95rem;font-weight:800;margin:0 0 10px 0;letter-spacing:.3px;text-transform:uppercase;">{title}</h3>'
            f'<p style="color:#5a6890;font-size:0.85rem;line-height:1.6;margin:0;">{desc}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

# Bottom Info (UNCHANGED)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div style="background:#131928;border:1px solid #243050;border-left:3px solid #f5c842;border-radius:0 10px 10px 0;padding:14px 20px;">'
    '<p style="color:#5a6890;margin:0;font-size:0.88rem;">👈 Use the <strong style="color:#e8ecf5;">sidebar</strong> to navigate to <strong style="color:#3d8ef5;">Form</strong> or <strong style="color:#7c5cfc;">Dashboard</strong></p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;color:#243050;font-size:0.75rem;margin-top:48px;padding-top:20px;border-top:1px solid #1e2840;font-family:\'JetBrains Mono\',monospace;">'
    'FBIS — Financial Behavior Intelligence System | Python · Streamlit · SQLite · SciPy · Statsmodels'
    '</div>',
    unsafe_allow_html=True
)
