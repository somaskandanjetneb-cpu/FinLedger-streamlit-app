import streamlit as st
from pathlib import Path
from database import get_company,save_company
from config import ASSETS_DIR
from auth import require_login
from ui import inject_css,sidebar
st.set_page_config(page_title="Company Settings",page_icon="⚙️"); require_login(); inject_css(); sidebar()
if st.session_state.user["role"]!="Admin": st.warning("Admin only."); st.stop()
c=get_company(); st.title("⚙️ Company & Branding")
with st.form("company"):
    name=st.text_input("Company Name",c["company_name"]); addr=st.text_area("Address",c["address"] or "")
    phone=st.text_input("Phone",c["phone"] or ""); email=st.text_input("Email",c["email"] or "")
    gst=st.text_input("GSTIN",c["gstin"] or ""); currency=st.text_input("Currency Symbol",c["currency_symbol"] or "₹")
    logo=st.file_uploader("Logo",type=["png","jpg","jpeg"])
    if st.form_submit_button("Save Settings"):
        lp=c["logo_path"] or ""
        if logo:
            lp=str(ASSETS_DIR/("company_logo"+Path(logo.name).suffix.lower()))
            Path(lp).write_bytes(logo.getbuffer())
        save_company(name,addr,phone,email,gst,lp,currency); st.success("Saved."); st.rerun()
if c["logo_path"] and Path(c["logo_path"]).exists(): st.image(c["logo_path"],width=200)
