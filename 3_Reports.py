import streamlit as st, pandas as pd
from datetime import date
from database import get_transactions,summary,get_company
from reports.excel_report import excel_bytes
from reports.pdf_report import report_pdf
from auth import require_login
from ui import inject_css,sidebar
from config import money
st.set_page_config(page_title="Reports",page_icon="📑",layout="wide"); require_login(); inject_css(); sidebar()
st.title("📑 Monthly / Yearly Reports")
mode=st.radio("Report Period",["Monthly","Yearly"],horizontal=True)
if mode=="Monthly":
    c=st.date_input("Select Month",date.today())
    start=c.replace(day=1)
    import calendar
    end=c.replace(day=calendar.monthrange(c.year,c.month)[1])
else:
    y=st.number_input("Year",2020,date.today().year+10,value=date.today().year,step=1)
    start=date(int(y),1,1); end=date(int(y),12,31)
rows=get_transactions(start,end)
inc,exp,bal=summary(start,end)
a,b,c=st.columns(3); a.metric("Income",money(inc)); b.metric("Expense",money(exp)); c.metric("Net",money(bal))
if rows:
    df=pd.DataFrame([dict(r) for r in rows])
    st.dataframe(df[["trans_date","trans_type","category","amount","details","reference_no"]],use_container_width=True,hide_index=True)
    eb=excel_bytes(rows,get_company(),start,end); pb=report_pdf(rows,get_company(),start,end)
    a,b=st.columns(2)
    a.download_button("⬇️ Excel Report",eb,"income_expense_report.xlsx",use_container_width=True)
    b.download_button("⬇️ PDF Report",pb,"income_expense_report.pdf",use_container_width=True)
else: st.info("No data for the selected period.")
