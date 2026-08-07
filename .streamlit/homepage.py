import streamlit as st

def homepage():

    st.set_page_config(layout="wide")

    col1, col2 = st.columns([3.8, 1.2])
    with col1:
        st.header("🏠 ErlangC Calculator Homepage")
    with col2:
        st.image("https://gettingitrightfirsttime.co.uk/wp-content/uploads/2022/06/cropped-GIRFT-Logo-300-RGB-Large.jpg", width=300)
        #st.write("Email: info@gettingitrightfirsttime.co.uk")

    st.divider()
    
    # with open("style.css") as css:
    #     st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    #global_page_style('static/css/style.css')



    st.subheader("Welcome to the **GIRFT ErlangC Calculator Tool**.")

    st.markdown(
    """
     Insert some text here
    """
    )