import json
import os

def some_helper_function(data):
    # Example utility function for data processing
    processed_data = data * 2  # Placeholder for actual processing logic
    return processed_data

def format_output(output):
    # Example utility function for formatting output
    return f"Formatted Output: {output}"

def get_settings_path():
    """Get the path to the settings file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "settings.json")

def save_settings(settings):
    """Save settings to a JSON file."""
    try:
        with open(get_settings_path(), 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings():
    """Load settings from a JSON file."""
    settings_path = get_settings_path()
    if not os.path.exists(settings_path):
        return {}
    
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}
