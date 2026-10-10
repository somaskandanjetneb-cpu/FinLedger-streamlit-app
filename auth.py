import streamlit as st
from database import authenticate

def require_login():
    if "authenticated" not in st.session_state: st.session_state.authenticated=False
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align:center'>💰 Income & Expense Manager</h1>",unsafe_allow_html=True)
        _,mid,_=st.columns([1,1.2,1])
        with mid:
            st.subheader("Secure Login")
            with st.form("login"):
                u=st.text_input("Username")
                p=st.text_input("Password",type="password")
                if st.form_submit_button("Login",use_container_width=True):
                    user=authenticate(u,p)
                    if user:
                        st.session_state.authenticated=True; st.session_state.user=user; st.rerun()
                    else: st.error("Invalid username or password.")
        st.stop()

def logout():
    st.session_state.authenticated=False
    st.session_state.user=None
    st.rerun()
