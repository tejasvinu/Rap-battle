import streamlit as st
import time
from utils.api_helpers import (
    generate_gemini_rap,
    generate_openai_rap,
    get_gemini_models,
    get_openai_models
)
from utils.helpers import save_settings, load_settings

def render_rap_battle():
    st.title("AI Rap Battle")
    st.write("Set up a rap battle between two AI models!")

    # Load saved settings if they exist
    if 'rap_battle_config' not in st.session_state:
        saved_settings = load_settings()
        st.session_state.rap_battle_config = saved_settings.get('rap_battle', {})
    
    if 'config_ready' not in st.session_state:
        st.session_state.config_ready = bool(st.session_state.rap_battle_config)

    # Setup tabs
    setup_tab, battle_tab = st.tabs(["Setup", "Battle Arena"])

    with setup_tab:
        st.header("API Setup")

        # Gemini setup - using unique keys for all widgets
        st.subheader("Gemini Setup")
        gemini_api_key = st.text_input("Gemini API Key",
                                       value=st.session_state.rap_battle_config.get("gemini_api_key", ""),
                                       type="password", key="gemini_api_input")
        gemini_model_options = get_gemini_models()
        gemini_model_index = st.selectbox(
            "Select Gemini Model",
            range(len(gemini_model_options)),
            index=gemini_model_options.index(st.session_state.rap_battle_config.get("gemini_model")) if "gemini_model" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("gemini_model") in gemini_model_options else 0,
            format_func=lambda i: gemini_model_options[i],
            key="gemini_model_select"
        )
        gemini_name = st.text_input("Gemini Rapper Name",
                                     value=st.session_state.rap_battle_config.get("gemini_name", "G-Flow"),
                                     key="gemini_name_input")

        # OpenAI setup - using unique keys for all widgets
        st.subheader("OpenAI Setup")
        openai_api_key = st.text_input("OpenAI API Key",
                                       value=st.session_state.rap_battle_config.get("openai_api_key", ""),
                                       type="password", key="openai_api_input")
        use_custom_endpoint = st.checkbox("Use Custom Endpoint",
                                          value=st.session_state.rap_battle_config.get("use_custom_endpoint", False),
                                          key="use_endpoint_check")
        openai_endpoint = None
        if use_custom_endpoint:
            openai_endpoint = st.text_input("OpenAI Endpoint URL",
                                             value=st.session_state.rap_battle_config.get("openai_endpoint", ""),
                                             key="openai_endpoint_input")

        openai_model_options = get_openai_models()
        openai_model_index = st.selectbox(
            "Select OpenAI Model",
            range(len(openai_model_options)),
            index=openai_model_options.index(st.session_state.rap_battle_config.get("openai_model")) if "openai_model" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("openai_model") in openai_model_options else 0,
            format_func=lambda i: openai_model_options[i],
            key="openai_model_select"
        )
        openai_name = st.text_input("OpenAI Rapper Name",
                                     value=st.session_state.rap_battle_config.get("openai_name", "GPT-MC"),
                                     key="openai_name_input")

        # Battle settings - using unique keys for all widgets
        st.header("Battle Settings")
        topic = st.text_input("Rap Battle Topic",
                               value=st.session_state.rap_battle_config.get("topic", "Artificial Intelligence"),
                               key="topic_input")
        rounds = st.slider("Number of Rounds", min_value=1, max_value=5,
                           value=st.session_state.rap_battle_config.get("rounds", 2),
                           key="rounds_slider")

        # Get the actual model names from indices
        gemini_model = gemini_model_options[gemini_model_index]
        openai_model = openai_model_options[openai_model_index]

        # First rapper selection
        rapper_options = [gemini_name, openai_name]
        first_rapper_index = st.radio(
            "Who goes first?",
            range(len(rapper_options)),
            index=rapper_options.index(st.session_state.rap_battle_config.get("first_rapper")) if "first_rapper" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("first_rapper") in rapper_options else 0,
            format_func=lambda i: rapper_options[i],
            key="first_rapper_radio"
        )
        first_rapper = rapper_options[first_rapper_index]

        # Save settings button with a callback
        if st.button("Save Settings", key="save_settings_btn"):
            if not gemini_api_key or not openai_api_key:
                st.error("Please provide API keys for both AI services.")
            else:
                # Store the data in session state
                st.session_state.config_ready = True
                st.session_state.rap_battle_config = {
                    "gemini_api_key": gemini_api_key,
                    "gemini_model": gemini_model,
                    "gemini_name": gemini_name,
                    "openai_api_key": openai_api_key,
                    "openai_endpoint": openai_endpoint,
                    "openai_model": openai_model,
                    "openai_name": openai_name,
                    "topic": topic,
                    "rounds": rounds,
                    "first_rapper": first_rapper,
                    "use_custom_endpoint": use_custom_endpoint,
                }
                
                # Save to persistent storage
                save_settings({'rap_battle': st.session_state.rap_battle_config})
                st.success("Settings saved! Go to the Battle Arena tab to start.")

    with battle_tab:
        st.header("Rap Battle Arena")

        if not st.session_state.config_ready:
            st.info("Please set up API keys and battle settings in the Setup tab first.")
            return

        config = st.session_state.rap_battle_config
        st.write(f"Topic: **{config['topic']}**")
        st.write(f"Battle: **{config['gemini_name']}** vs **{config['openai_name']}**")

        if st.button("Start Battle!", key="start_battle_btn"):
            # Battle logic
            try:
                rappers = []
                if config['first_rapper'] == config['gemini_name']:
                    rappers = [
                        {"name": config['gemini_name'], "api": "gemini"},
                        {"name": config['openai_name'], "api": "openai"}
                    ]
                else:
                    rappers = [
                        {"name": config['openai_name'], "api": "openai"},
                        {"name": config['gemini_name'], "api": "gemini"}
                    ]

                # Start the battle
                st.subheader("🎤 Battle Results 🎤")
                previous_verse = None

                for round_num in range(1, config['rounds'] + 1):
                    st.markdown(f"### Round {round_num}")

                    for i, rapper in enumerate(rappers):
                        with st.spinner(f"{rapper['name']} is thinking..."):
                            time.sleep(1)  # A small delay for dramatic effect

                            opponent_name = rappers[1 - i]["name"]

                            if rapper["api"] == "gemini":
                                verse = generate_gemini_rap(
                                    config['gemini_api_key'],
                                    config['gemini_model'],
                                    config['topic'],
                                    rapper["name"],
                                    opponent_name,
                                    previous_verse
                                )
                            else:
                                verse = generate_openai_rap(
                                    config['openai_api_key'],
                                    config['openai_endpoint'],
                                    config['openai_model'],
                                    config['topic'],
                                    rapper["name"],
                                    opponent_name,
                                    previous_verse
                                )

                            st.markdown(f"#### {rapper['name']}")
                            st.markdown(f"_{verse}_")
                            previous_verse = verse

                st.success("Battle completed! Who won? You decide!")

            except Exception as e:
                st.error(f"Error during battle: {str(e)}")
