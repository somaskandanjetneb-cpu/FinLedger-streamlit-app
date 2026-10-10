import streamlit as st, pandas as pd
from datetime import date
from database import next_invoice_no,add_invoice,get_invoices,get_company,get_invoice
from reports.invoice_pdf import invoice_pdf
from auth import require_login
from ui import inject_css,sidebar
from config import money
st.set_page_config(page_title="Invoices",page_icon="🧾",layout="wide"); require_login(); inject_css(); sidebar()
user=st.session_state.user; company=get_company()
st.title("🧾 PDF Invoice Generator")
with st.form("invoice",clear_on_submit=True):
    a,b=st.columns(2)
    no=a.text_input("Invoice No.",value=next_invoice_no()); d=b.date_input("Invoice Date",date.today())
    customer=st.text_input("Customer Name"); address=st.text_area("Customer Address")
    phone,email=st.columns(2)
    ph=phone.text_input("Phone"); em=email.text_input("Email")
    desc=st.text_area("Description / Service")
    x,y,z=st.columns(3)
    amount=x.number_input("Amount (₹)",min_value=0.0,step=100.0)
    tax_pct=y.number_input("Tax %",min_value=0.0,step=1.0)
    tax=amount*tax_pct/100
    z.metric("Total",money(amount+tax))
    notes=st.text_input("Notes")
    save=st.form_submit_button("💾 Save Invoice",use_container_width=True)
if save:
    total=amount+tax
    add_invoice(no,d,customer,address,ph,em,desc,amount,tax,total,notes,user["id"])
    st.session_state["last_invoice_id"]=no
    st.success(f"Invoice {no} saved.")
    st.rerun()
rows=get_invoices()
if rows:
    df=pd.DataFrame([dict(r) for r in rows]); st.dataframe(df,use_container_width=True,hide_index=True)
    ids={f"{r['invoice_no']} - {r['customer_name']}":r["id"] for r in rows}
    s=st.selectbox("Invoice to download",list(ids)); r=get_invoice(ids[s])
    st.download_button("⬇️ Download Invoice PDF",invoice_pdf(r,company),"invoice_"+r["invoice_no"]+".pdf","application/pdf",use_container_width=True)
