import json

# Load settings from settings.json
with open('settings.json') as f:
    settings = json.load(f)

import streamlit as st
from pages import home, rap_battle

def main():
    st.set_page_config(page_title="AI Rap Battle", layout="wide")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Home", "Rap Battle", "Other Page"))

    if page == "Home":
        home.render_home()
    elif page == "Rap Battle":
        rap_battle.render_rap_battle()
    else:
        st.write("This is another page.")

if __name__ == "__main__":
    main()