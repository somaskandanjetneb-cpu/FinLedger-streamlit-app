import streamlit as st
from database import get_categories,add_category,delete_category
from auth import require_login
from ui import inject_css,sidebar
st.set_page_config(page_title="Categories",page_icon="📂"); require_login(); inject_css(); sidebar()
st.title("📂 Category Master")
a,b=st.columns(2)
with a:
    with st.form("cat",clear_on_submit=True):
        n=st.text_input("Category Name"); t=st.selectbox("Type",["Income","Expense"])
        if st.form_submit_button("Add Category"):
            ok,msg=add_category(n,t); (st.success if ok else st.error)(msg)
            if ok: st.rerun()
with b:
    rows=get_categories()
    if rows:
        opts={f"{r['type']} - {r['name']}":r["id"] for r in rows}
        s=st.selectbox("Delete Category",list(opts))
        if st.button("Delete"):
            ok,msg=delete_category(opts[s]); (st.success if ok else st.error)(msg)
            if ok: st.rerun()
st.dataframe([dict(r) for r in get_categories()],use_container_width=True,hide_index=True)
