import streamlit as st
import time
from utils.api_helpers import generate_gemini_rap, generate_openai_rap, get_gemini_models, get_openai_models
from utils.helpers import save_settings, load_settings

# Use existing helper functions
def generate_verse(config, rapper, opponent, previous_verse=None):
    if rapper["api"] == "gemini":
        return generate_gemini_rap(
            config['gemini_api_key'],
            config['gemini_model'],
            config['topic'],
            rapper["name"],
            opponent["name"],
            previous_verse
        )
    else:
        return generate_openai_rap(
            config['openai_api_key'],
            config['openai_endpoint'],
            config['openai_model'],
            config['topic'],
            rapper["name"],
            opponent["name"],
            previous_verse
        )

def display_verse(verse):
    st.markdown(f"""
    <div style="border-left:4px solid; padding:8px; margin:4px 0;">
      <h4>{verse["avatar"]} {verse["name"]}</h4>
      <p>{verse["text"]}</p>
    </div>
    """, unsafe_allow_html=True)

def init_battle_state():
    if 'battle_state' not in st.session_state:
        st.session_state.battle_state = {
            'in_progress': False,
            'automated': False,
            'current_round': 1,
            'current_rapper': 0,
            'verses': [],
            'generating': False
        }

def render_rap_battle():
    # Add custom CSS for styling - IMPROVED FOR BETTER SPACE USAGE
    st.markdown("""<style>
        .battle-title {
            text-align: center;
            font-size: 2.5rem;
            background: linear-gradient(90deg, #FF6B6B, #4472CA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem;
        }
        .rapper-card {
            border-radius: 10px;
            padding: 0.7rem;
            margin: 0.3rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .rapper-card:hover {
            transform: translateY(-3px);
        }
        .gemini-card {
            background: linear-gradient(135deg, #6e48aa, #9d50bb);
            color: white;
        }
        .openai-card {
            background: linear-gradient(135deg, #134e5e, #71b280);
            color: white;
        }
        .rapper-avatar {
            font-size: 2rem;
            margin-bottom: 0.1rem;
        }
        .rapper-name {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 0.1rem;
        }
        .rapper-model {
            font-size: 0.7rem;
            opacity: 0.8;
        }
        .vs-container {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: bold;
            color: #FF4500;
            padding: 0.3rem;
        }
        .compact-verse {
            border-left: 4px solid;
            padding: 0.4rem 0.6rem;
            margin: 0.3rem 0;
            border-radius: 4px;
            animation: fadeIn 0.5s;
            font-size: 0.9rem;
        }
        .full-verse {
            border-left: 4px solid;
            padding: 0.6rem 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            animation: fadeIn 0.5s;
        }
        .gemini-verse {
            border-color: #9d50bb;
            background-color: rgba(157, 80, 187, 0.05);
        }
        .openai-verse {
            border-color: #71b280;
            background-color: rgba(113, 178, 128, 0.05);
        }
        .topic-banner {
            background: #333;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 5px;
            text-align: center;
            margin: 0.4rem 0;
            font-size: 0.9rem;
        }
        .round-title {
            text-align: center;
            font-size: 1.2rem;
            margin: 0.7rem 0 0.4rem 0;
            padding: 0.2rem;
            background: #f0f0f0;
            border-radius: 5px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .battle-complete {
            text-align: center;
            padding: 0.8rem;
            margin-top: 0.8rem;
            background: linear-gradient(90deg, #FF6B6B, #4472CA);
            color: white;
            border-radius: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        .battle-progress {
            margin: 0.7rem 0;
            height: 8px;
            border-radius: 4px;
            background: #f0f0f0;
            overflow: hidden;
        }
        .battle-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #FF6B6B, #4472CA);
            transition: width 0.3s ease;
        }
        .compact-verse h4 {
            margin: 0 0 0.2rem 0;
            font-size: 0.85rem;
        }
        .compact-verse p {
            margin: 0;
            font-size: 0.8rem;
            white-space: pre-line;
            line-height: 1.2;
        }
        .full-verse h4 {
            margin: 0 0 0.3rem 0;
            font-size: 1rem;
        }
        .full-verse p {
            margin: 0;
            font-size: 0.9rem;
            white-space: pre-line;
            line-height: 1.3;
        }
        .verse-title {
            font-weight: bold;
            font-size: 0.9rem;
            margin-bottom: 0.2rem;
        }
        .condensed-content {
            max-height: 250px;
            overflow-y: auto;
            padding-right: 10px;
            border: 1px solid #eee;
            border-radius: 5px;
            padding: 8px;
            margin-bottom: 10px;
        }
        .battle-area {
            padding: 10px;
            border-radius: 8px;
            background-color: #f9f9f9;
            margin-bottom: 10px;
        }
        .battle-controls {
            margin: 10px 0;
            display: flex;
            gap: 10px;
        }
        .status-indicator {
            padding: 8px;
            border-radius: 4px;
            background-color: #f0f8ff;
            margin: 8px 0;
            border-left: 3px solid #4472CA;
        }
        .stButton button {
            font-weight: bold;
        }
        .tab-content {
            padding: 10px 0;
        }
        .rapper-info {
            font-size: 0.8rem;
        }
        .results-container {
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
        }
        .results-header {
            font-size: 1.5rem;
            text-align: center;
            margin-bottom: 15px;
            color: #4472CA;
        }
        .animate-text {
            animation: colorChange 4s infinite;
        }
        @keyframes colorChange {
            0% { color: #FF6B6B; }
            50% { color: #4472CA; }
            100% { color: #FF6B6B; }
        }
        .emoji-pulse {
            display: inline-block;
            animation: emojiBounce 1s infinite;
        }
        @keyframes emojiBounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        .header-area {
            margin-bottom: 5px;
        }
        /* Optimize container spacing */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>""", unsafe_allow_html=True)

    # Page header
    st.markdown('<div class="header-area">', unsafe_allow_html=True)
    st.markdown("<h1 class='battle-title'>AI Rap Battle</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Load saved settings if they exist
    if 'rap_battle_config' not in st.session_state:
        saved_settings = load_settings()
        st.session_state.rap_battle_config = saved_settings.get('rap_battle', {})
    
    if 'config_ready' not in st.session_state:
        st.session_state.config_ready = bool(st.session_state.rap_battle_config)

    # Setup tabs
    setup_tab, battle_tab, results_tab = st.tabs(["Setup", "Battle Arena", "Battle History"])

    with setup_tab:
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Gemini Rapper")
            gemini_api_key = st.text_input("Gemini API Key",
                                        value=st.session_state.rap_battle_config.get("gemini_api_key", ""),
                                        type="password", key="gemini_api_input")
            gemini_model_options = get_gemini_models()
            gemini_model_index = st.selectbox(
                "Model",
                range(len(gemini_model_options)),
                index=gemini_model_options.index(st.session_state.rap_battle_config.get("gemini_model")) if "gemini_model" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("gemini_model") in gemini_model_options else 0,
                format_func=lambda i: gemini_model_options[i],
                key="gemini_model_select"
            )
            gemini_name = st.text_input("Rapper Name",
                                        value=st.session_state.rap_battle_config.get("gemini_name", "G-Flow"),
                                        key="gemini_name_input")
        
        with col2:
            st.header("OpenAI Rapper")
            openai_api_key = st.text_input("OpenAI API Key",
                                        value=st.session_state.rap_battle_config.get("openai_api_key", ""),
                                        type="password", key="openai_api_input")
            openai_model_options = get_openai_models()
            openai_model_index = st.selectbox(
                "Model",
                range(len(openai_model_options)),
                index=openai_model_options.index(st.session_state.rap_battle_config.get("openai_model")) if "openai_model" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("openai_model") in openai_model_options else 0,
                format_func=lambda i: openai_model_options[i],
                key="openai_model_select"
            )
            openai_name = st.text_input("Rapper Name",
                                        value=st.session_state.rap_battle_config.get("openai_name", "GPT-MC"),
                                        key="openai_name_input")
            
            # OpenAI endpoint (optional)
            use_custom_endpoint = st.checkbox("Custom Endpoint",
                                            value=st.session_state.rap_battle_config.get("use_custom_endpoint", False),
                                            key="use_endpoint_check") 
            openai_endpoint = None
            if use_custom_endpoint:
                openai_endpoint = st.text_input("Endpoint URL",
                                                value=st.session_state.rap_battle_config.get("openai_endpoint", ""),
                                                key="openai_endpoint_input")

        # Battle settings in a more compact layout
        st.header("Battle Settings")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            topic = st.text_input("Topic",
                                value=st.session_state.rap_battle_config.get("topic", "Artificial Intelligence"),
                                key="topic_input")
        
        with col2:
            rounds = st.slider("Rounds", min_value=1, max_value=5,
                            value=st.session_state.rap_battle_config.get("rounds", 2),
                            key="rounds_slider")
        
        with col3:
            # First rapper selection
            rapper_options = [gemini_name, openai_name]
            first_rapper_index = st.radio(
                "First Turn",
                range(len(rapper_options)),
                index=rapper_options.index(st.session_state.rap_battle_config.get("first_rapper")) if "first_rapper" in st.session_state.rap_battle_config and st.session_state.rap_battle_config.get("first_rapper") in rapper_options else 0,
                format_func=lambda i: rapper_options[i],
                key="first_rapper_radio",
                horizontal=True
            )
            first_rapper = rapper_options[first_rapper_index]

        # Get the actual model names from indices
        gemini_model = gemini_model_options[gemini_model_index]
        openai_model = openai_model_options[openai_model_index]
        
        # Save settings button
        if st.button("💾 Save Settings", key="save_settings_btn", use_container_width=True):
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
        if not st.session_state.config_ready:
            st.info("Please set up your API keys and battle settings in the Setup tab first.")
            return

        config = st.session_state.rap_battle_config
        init_battle_state()
        
        # Setup rappers based on config
        if 'rappers' not in st.session_state:
            if config['first_rapper'] == config['gemini_name']:
                st.session_state.rappers = [
                    {"name": config['gemini_name'], "api": "gemini", "avatar": "🤖", "model": config['gemini_model']},
                    {"name": config['openai_name'], "api": "openai", "avatar": "🧠", "model": config['openai_model']}
                ]
            else:
                st.session_state.rappers = [
                    {"name": config['openai_name'], "api": "openai", "avatar": "🧠", "model": config['openai_model']},
                    {"name": config['gemini_name'], "api": "gemini", "avatar": "🤖", "model": config['gemini_model']}
                ]
        rappers = st.session_state.rappers

        # Display header
        st.markdown(f"<h2 style='text-align:center;'>Battle on: {config['topic'].upper()}</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div style='text-align:center;'>{rappers[0]['avatar']} {rappers[0]['name']}<br>{rappers[0]['model']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='text-align:center;'>VS</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='text-align:center;'>{rappers[1]['avatar']} {rappers[1]['name']}<br>{rappers[1]['model']}</div>", unsafe_allow_html=True)
        
        # If battle not started, show start buttons
        if not st.session_state.battle_state['in_progress']:
            st.markdown("<hr>", unsafe_allow_html=True)
            manual = st.button("Start Manual Battle", key="start_manual")
            auto = st.button("Start Automated Battle", key="start_auto")
            if manual:
                st.session_state.battle_state['in_progress'] = True
                st.session_state.battle_state['automated'] = False
            elif auto:
                st.session_state.battle_state['in_progress'] = True
                st.session_state.battle_state['automated'] = True
            st.stop()
        
        # Battle in progress
        battle_state = st.session_state.battle_state
        st.markdown(f"<h3 style='text-align:center;'>Round {battle_state['current_round']} of {config['rounds']}</h3>", unsafe_allow_html=True)
        
        # Display previous verses
        if battle_state['verses']:
            st.markdown("<div style='max-height:300px; overflow-y:auto; border:1px solid #ccc; padding:4px; margin-bottom:8px;'>", unsafe_allow_html=True)
            for v in battle_state['verses']:
                display_verse(v)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Check if battle finished
        if battle_state['current_round'] > config['rounds']:
            battle_state['in_progress'] = False
            st.success("Battle Complete!")
            st.markdown("<h3>Final Battle Results</h3>", unsafe_allow_html=True)
            for v in battle_state['verses']:
                display_verse(v)
            if st.button("Start New Battle"):
                st.session_state.battle_state = {
                    'in_progress': False,
                    'automated': False,
                    'current_round': 1,
                    'current_rapper': 0,
                    'verses': [],
                    'generating': False
                }
                st.experimental_rerun()
            st.stop()
        
        # Generation control
        status_container = st.empty()
        control_container = st.empty()
        
        if not battle_state['generating']:
            if battle_state['automated']:
                battle_state['generating'] = True
            else:
                if st.button("Generate Next Verse", key="next_verse"):
                    battle_state['generating'] = True
        
        if battle_state['generating']:
            status_container.info("Generating verse...")
            current_rapper = rappers[battle_state['current_rapper']]
            opponent = rappers[1 - battle_state['current_rapper']]
            prev_text = battle_state['verses'][-1]["text"] if battle_state['verses'] else None
            verse_text = generate_verse(config, current_rapper, opponent, prev_text)
            new_verse = {
                "name": current_rapper["name"],
                "text": verse_text,
                "class": "gemini-verse" if current_rapper["api"]=="gemini" else "openai-verse",
                "avatar": current_rapper["avatar"],
                "round": battle_state['current_round']
            }
            battle_state['verses'].append(new_verse)
            battle_state['current_rapper'] = 1 - battle_state['current_rapper']
            if battle_state['current_rapper'] == 0:
                battle_state['current_round'] += 1
            battle_state['generating'] = False
            # Rerun to update UI
            if battle_state['automated']:
                time.sleep(1)
            st.rerun()
        
    with results_tab:
        st.header("Battle History")
        
        if 'battle_state' not in st.session_state or not st.session_state.battle_state.get('history'):
            st.info("No battles completed yet. Battle results will appear here after you complete your first battle.")
        else:
            # Show list of past battles
            battles = st.session_state.battle_state['history']
            
            for i, battle in enumerate(reversed(battles)):
                with st.expander(f"Battle #{len(battles)-i}: {battle['topic']} - {battle['date']}"):
                    st.write(f"**Topic:** {battle['topic']}")
                    st.write(f"**Rounds:** {battle['rounds']}")
                    st.write(f"**Rappers:** {battle['rappers'][0]['name']} vs {battle['rappers'][1]['name']}")
                    
                    # Display verses by round
                    for round_num in range(1, battle['rounds'] + 1):
                        st.markdown(f"#### Round {round_num}")
                        round_verses = [v for v in battle['verses'] if v.get('round') == round_num]
                        
                        if round_verses:
                            col1, col2 = st.columns(2)
                            with col1:
                                if len(round_verses) > 0:
                                    display_verse(round_verses[0])
                            with col2:
                                if len(round_verses) > 1:
                                    display_verse(round_verses[1])
