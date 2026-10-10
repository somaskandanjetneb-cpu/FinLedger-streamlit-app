import streamlit as st
from database import get_users,add_user,update_user_status,change_password
from auth import require_login
from ui import inject_css,sidebar
st.set_page_config(page_title="Users",page_icon="👥"); require_login(); inject_css(); sidebar()
u=st.session_state.user; st.title("👥 User Management")
if u["role"]!="Admin": st.warning("Admin only."); st.stop()
with st.form("new",clear_on_submit=True):
    a,b=st.columns(2); un=a.text_input("Username"); fn=b.text_input("Full Name")
    pw=a.text_input("Password",type="password"); role=b.selectbox("Role",["User","Admin"])
    if st.form_submit_button("Create User"):
        ok,msg=add_user(un,fn,pw,role); (st.success if ok else st.error)(msg)
        if ok: st.rerun()
rows=get_users(); st.dataframe([dict(r) for r in rows],use_container_width=True,hide_index=True)
opts={r["username"]:r for r in rows}; s=st.selectbox("User",list(opts)); r=opts[s]
if r["id"]!=u["id"]:
    if st.button("Activate" if not r["active"] else "Deactivate"):
        update_user_status(r["id"],not bool(r["active"])); st.rerun()
st.subheader("Change My Password")
with st.form("pwchange",clear_on_submit=True):
    p1=st.text_input("New Password",type="password"); p2=st.text_input("Confirm",type="password")
    if st.form_submit_button("Change Password"):
        if len(p1)<6 or p1!=p2: st.error("Password must be 6+ characters and match.")
        else: change_password(u["id"],p1); st.success("Password changed.")
