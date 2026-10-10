import streamlit as st, pandas as pd
from datetime import date
from database import add_opening_balance,get_opening_rows,get_opening_balance
from auth import require_login
from ui import inject_css,sidebar
from config import money
st.set_page_config(page_title="Opening Balance",page_icon="🏦"); require_login(); inject_css(); sidebar()
st.title("🏦 Opening Balance")
st.caption("Use a positive amount for an opening cash/bank balance. Adjustments may be negative.")
with st.form("opening",clear_on_submit=True):
    d=st.date_input("Balance Date",date.today()); amount=st.number_input("Opening / Adjustment Amount (₹)",step=100.0)
    details=st.text_input("Details")
    if st.form_submit_button("Save Balance"):
        add_opening_balance(d,amount,details,st.session_state.user["id"]); st.success("Opening balance saved."); st.rerun()
st.metric("Current Opening Balance",money(get_opening_balance(date.today())))
rows=get_opening_rows()
if rows: st.dataframe(pd.DataFrame([dict(r) for r in rows]),use_container_width=True,hide_index=True)
