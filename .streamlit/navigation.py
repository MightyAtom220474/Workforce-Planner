import streamlit as st
from homepage import homepage
from test_app import workforce


def render_navigation():
    with st.sidebar:
        st.image(
            "https://gettingitrightfirsttime.co.uk/wp-content/uploads/2022/06/NHS-England-Logo.png",
            width=150
        )

        st.title("📋 Navigation")

        pages = {
            "Homepage": "🏠 Homepage",
            "Workforce": "🧩 Workforce Calculator",
        }

        selected = st.radio(
            "Go to",
            list(pages.keys()),
            format_func=lambda x: pages[x],
            key="active_page",
        )

    if selected == "Homepage":
        homepage()
    elif selected == "Workforce":
        workforce()
