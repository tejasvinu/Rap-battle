import os
import json

# Import helpers
from utils.helpers import get_settings_path, load_settings

# Create an empty settings.json file if it doesn't exist
settings_path = get_settings_path()
settings = {}

# Try to load settings if the file exists, otherwise use empty default settings
try:
    with open(settings_path) as f:
        settings = json.load(f)
except FileNotFoundError:
    # Create the settings file with default empty structure
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, 'w') as f:
        json.dump({}, f)
    print(f"Created new settings file at {settings_path}")

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