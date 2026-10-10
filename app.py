import streamlit as st
from datetime import date
from database import init_db, summary, get_opening_balance, get_transactions, generate_recurring_until, get_company
from auth import require_login
from ui import inject_css, sidebar
from config import money

st.set_page_config(page_title="FinLedger",page_icon="💰",layout="wide",initial_sidebar_state="expanded")
init_db(); require_login(); inject_css(); sidebar()

user=st.session_state.user
company=get_company()
today=date.today()
generate_recurring_until(today,user["id"])

st.title("📊 Executive Dashboard")
st.caption(f"Welcome back, {user['full_name']} • {today:%d %B %Y}")

c1,c2,c3,c4=st.columns(4)
inc,exp,net=summary(today.replace(day=1),today)
opening=get_opening_balance(today)
c1.metric("Monthly Income",money(inc))
c2.metric("Monthly Expense",money(exp))
c3.metric("Monthly Net",money(net))
c4.metric("Available Balance",money(opening+net))

st.divider()
rows=get_transactions(today.replace(day=1),today)
if rows:
    import pandas as pd
    df=pd.DataFrame([dict(r) for r in rows])
    left,right=st.columns(2)
    with left:
        st.subheader("Income vs Expense")
        chart=df.groupby(["trans_date","trans_type"])["amount"].sum().unstack(fill_value=0)
        st.bar_chart(chart)
    with right:
        st.subheader("Expense by Category")
        ex=df[df.trans_type=="Expense"]
        if not ex.empty: st.bar_chart(ex.groupby("category")["amount"].sum())
        else: st.info("No expenses this month.")
    st.subheader("Recent Transactions")
    show=df[["trans_date","trans_type","category","amount","details"]].head(10)
    show.columns=["Date","Type","Category","Amount","Details"]
    st.dataframe(show,use_container_width=True,hide_index=True)
else:
    st.info("No transactions for this month. Open Transaction Entry to add one.")
