import streamlit as st
from database import get_company
from auth import logout

def inject_css():
    st.markdown("""<style>
    .block-container{padding-top:1.2rem;padding-bottom:2rem}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#0f172a 0%,#172554 100%)}
    [data-testid="stSidebar"] *{color:#f8fafc}
    .metric-card{padding:16px;border-radius:14px;background:#f8fafc;border:1px solid #e2e8f0}
    .small-muted{color:#64748b;font-size:.9rem}
    </style>""",unsafe_allow_html=True)

def sidebar():
    user=st.session_state.user; company=get_company()
    st.sidebar.markdown("## 💰 FinLedger")
    st.sidebar.caption(company["company_name"] if company else "Income & Expense")
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 **{user['full_name']}**")
    st.sidebar.caption(user["role"])
    if st.sidebar.button("🚪 Logout",use_container_width=True): logout()
