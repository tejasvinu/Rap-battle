import streamlit as st

def render_home():
    st.title("Welcome to AI Rap Battle")
    st.write("An application that lets AI models battle it out in a rap contest!")
    
    st.markdown("""
    ### Features:
    - Set up rap battles between Gemini and OpenAI models
    - Customize rapper names and topics
    - Multiple battle rounds
    - See how different AI models approach creative tasks
    - View battle history and analyze past performances
    
    Navigate to the 'Rap Battle' page to get started!
    """)
    
    # Add interactive elements here
    if st.button("Learn More"):
        st.write("This app uses both Google's Gemini and OpenAI APIs to generate rap verses.")
        st.write("You'll need to provide your own API keys to use the application.")
    
    st.sidebar.header("Navigation")
    st.sidebar.write("Use the sidebar to navigate through the app.")
    
    st.markdown("[Go to Battle History](#)", unsafe_allow_html=True)
    
# Call the render_home function to display the content
if __name__ == "__main__":
    render_home()
