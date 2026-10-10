import streamlit as st
from datetime import date
import pandas as pd
from database import get_categories,add_transaction,get_transactions,update_transaction,delete_transaction
from auth import require_login
from ui import inject_css,sidebar

st.set_page_config(page_title="Transactions",page_icon="📝",layout="wide")
require_login(); inject_css(); sidebar()
user=st.session_state.user
st.title("📝 Transaction Entry")

with st.container(border=True):
    st.subheader("Add Income / Expense")
    with st.form("tx",clear_on_submit=True):
        a,b,c=st.columns(3)
        d=a.date_input("Date",date.today())
        typ=b.selectbox("Type",["Income","Expense"])
        cats=get_categories(typ); cmap={x["name"]:x["id"] for x in cats}
        cat=c.selectbox("Category",list(cmap) or ["Create a category first"])
        x,y=st.columns(2)
        amount=x.number_input("Amount (₹)",min_value=0.01,step=100.0)
        ref=y.text_input("Reference No.")
        details=st.text_input("Details / Narration")
        if st.form_submit_button("💾 Save Transaction",use_container_width=True):
            if cats:
                add_transaction(d,typ,cmap[cat],amount,details,ref,user_id=user["id"]); st.success("Saved."); st.rerun()
            else: st.error("Create a category first.")

st.divider()
st.subheader("Transaction Register")
a,b,c=st.columns(3)
start=a.date_input("From",date.today().replace(day=1))
end=b.date_input("To",date.today())
ft=c.selectbox("Filter Type",["All","Income","Expense"])
rows=get_transactions(start,end,None if ft=="All" else ft)
if rows:
    df=pd.DataFrame([dict(r) for r in rows])
    st.dataframe(df[["id","trans_date","trans_type","category","amount","details","reference_no","username"]],use_container_width=True,hide_index=True)
    ids=df.id.tolist(); sid=st.selectbox("Edit/Delete Transaction ID",ids)
    r=next(x for x in rows if x["id"]==sid)
    with st.form("edit"):
        ed=st.date_input("Date",date.fromisoformat(r["trans_date"]))
        et=st.selectbox("Type",["Income","Expense"],index=0 if r["trans_type"]=="Income" else 1)
        cs=get_categories(et); cm={x["name"]:x["id"] for x in cs}
        names=list(cm); current=r["category"] if r["category"] in names else names[0]
        ec=st.selectbox("Category",names,index=names.index(current))
        ea=st.number_input("Amount",value=float(r["amount"]),min_value=0.01)
        er=st.text_input("Reference",value=r["reference_no"] or "")
        ee=st.text_input("Details",value=r["details"] or "")
        u,v=st.columns(2); upd=u.form_submit_button("✏️ Update"); dele=v.form_submit_button("🗑️ Delete")
    if upd: update_transaction(sid,ed,et,cm[ec],ea,ee,er); st.success("Updated."); st.rerun()
    if dele: delete_transaction(sid); st.success("Deleted."); st.rerun()
else: st.info("No transactions found.")
