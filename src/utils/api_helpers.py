import os
import google.generativeai as genai
from google.generativeai import types
import openai

def get_gemini_models():
    """Return available Gemini models."""
    return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-pro", "gemini-2.0-flash"]

def get_openai_models():
    """Return available OpenAI models."""
    return ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]

def get_rap_battle_prompt(rapper_name, opponent_name, topic, previous_verse=None):
    """Generate a consistent system prompt for rap battles."""
    system_instruction = f"""You are {rapper_name}, a legendary freestyle battle rapper with your own unique style and flow.
You're known for:
- Clever wordplay and double entendres
- Strong punchlines that hit hard
- Creative metaphors and similes
- Technical rhyming skills with internal rhyme schemes
- A confident, unshakeable attitude

You're in a rap battle against {opponent_name} on the topic of "{topic}".

Rules for your verse:
1. Write 6-10 lines of authentic rap lyrics
2. Stay on topic while also dissing your opponent
3. Be creative with your wordplay and metaphors
4. Keep a consistent flow and rhythm
5. End with a powerful punchline

IMPORTANT: Output ONLY the rap verse. No explanations, no conversation, no quotes."""

    user_prompt = f"Topic: {topic}"
    if previous_verse:
        user_prompt += f"\n\n{opponent_name}'s verse:\n{previous_verse}\n\nYour response verse (counter their points and attack weaknesses in their verse):"
    else:
        user_prompt += "\n\nStart the battle with your opening verse! Set the tone and come out strong!"

    return system_instruction, user_prompt

def generate_gemini_rap(api_key, model, topic, rapper_name, opponent_name, previous_verse=None):
    """Generate a rap verse using Gemini."""
    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)

    system_instruction, user_prompt = get_rap_battle_prompt(rapper_name, opponent_name, topic, previous_verse)

    try:
        response = model_instance.generate_content(
            [system_instruction, user_prompt],  # Send both as separate parts
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating Gemini response: {str(e)}"

def generate_openai_rap(api_key, endpoint, model, topic, rapper_name, opponent_name, previous_verse=None):
    """Generate a rap verse using OpenAI."""
    if endpoint:
        client = openai.OpenAI(base_url=endpoint, api_key=api_key)
    else:
        client = openai.OpenAI(api_key=api_key)

    system_instruction, user_prompt = get_rap_battle_prompt(rapper_name, opponent_name, topic, previous_verse)

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.9,
            max_tokens=2048
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating OpenAI response: {str(e)}"
