import streamlit as st, pandas as pd
from datetime import date
from database import get_categories,add_recurring,get_recurring,toggle_recurring,delete_recurring
from auth import require_login
from ui import inject_css,sidebar
st.set_page_config(page_title="Recurring",page_icon="🔁"); require_login(); inject_css(); sidebar()
user=st.session_state.user
st.title("🔁 Recurring Income / Expenses")
with st.form("recurring",clear_on_submit=True):
    name=st.text_input("Recurring Name")
    typ=st.selectbox("Type",["Expense","Income"])
    cats=get_categories(typ); cm={x["name"]:x["id"] for x in cats}
    cat=st.selectbox("Category",list(cm) or ["No categories"])
    amount=st.number_input("Amount (₹)",min_value=0.01,step=100.0)
    day=st.number_input("Day of Month",1,31,1)
    start=st.date_input("Start Date",date.today())
    end=st.date_input("End Date (optional)",None)
    details=st.text_input("Details")
    if st.form_submit_button("Create Recurring Rule"):
        if cm: add_recurring(name,typ,cm[cat],amount,details,day,start,end,user["id"]); st.success("Recurring rule created."); st.rerun()
rows=get_recurring()
if rows:
    df=pd.DataFrame([dict(r) for r in rows]); st.dataframe(df,use_container_width=True,hide_index=True)
    opts={f"{r['name']} ({r['trans_type']})":r for r in rows}; s=st.selectbox("Select Rule",list(opts)); r=opts[s]
    a,b=st.columns(2)
    if a.button("Deactivate" if r["active"] else "Activate"): toggle_recurring(r["id"],not bool(r["active"])); st.rerun()
    if b.button("Delete Rule"): delete_recurring(r["id"]); st.rerun()
else: st.info("No recurring rules.")
