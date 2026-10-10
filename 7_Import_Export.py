import streamlit as st, pandas as pd
from io import BytesIO
from database import get_categories,add_transaction
from auth import require_login
from ui import inject_css,sidebar
from openpyxl import Workbook
st.set_page_config(page_title="Import Export",page_icon="📤",layout="wide"); require_login(); inject_css(); sidebar()
user=st.session_state.user
st.title("📤 Excel Import / Export")
st.caption("Import columns: Date, Type, Category, Amount, Details, Reference. Type must be Income or Expense.")

uploaded=st.file_uploader("Import Excel",type=["xlsx"])
if uploaded:
    try:
        df=pd.read_excel(uploaded)
        st.dataframe(df.head(20),use_container_width=True)
        if st.button("Import Rows"):
            cm={(c["type"],c["name"]):c["id"] for c in get_categories()}
            good=0; bad=[]
            for i,r in df.iterrows():
                try:
                    typ=str(r["Type"]).title(); cat=str(r["Category"]); amount=float(r["Amount"])
                    cid=cm[(typ,cat)]
                    add_transaction(pd.to_datetime(r["Date"]).date(),typ,cid,amount,str(r.get("Details","")),str(r.get("Reference","")),user["id"])
                    good+=1
                except Exception as e: bad.append(f"Row {i+2}: {e}")
            st.success(f"Imported {good} row(s).")
            if bad: st.warning("\\n".join(bad[:10]))
    except Exception as e: st.error(f"Could not read Excel: {e}")

st.subheader("Download Excel Template")
wb=Workbook(); ws=wb.active; ws.append(["Date","Type","Category","Amount","Details","Reference"])
out=BytesIO(); wb.save(out); out.seek(0)
st.download_button("⬇️ Excel Template",out.getvalue(),"transaction_import_template.xlsx")
