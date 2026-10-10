import streamlit as st
from database import get_connection
from config import DB_PATH
from auth import require_login
from ui import inject_css,sidebar
require_login(); inject_css(); sidebar()
st.set_page_config(page_title="Backup",page_icon="💾")
st.title("💾 Database Backup")
if DB_PATH.exists():
    st.download_button("⬇️ Download SQLite Backup",DB_PATH.read_bytes(),"income_expense_backup.db","application/octet-stream",use_container_width=True)
    st.success(f"Database stored at: {DB_PATH}")
