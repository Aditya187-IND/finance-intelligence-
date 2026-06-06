import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# 1. Load the secret API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Setup the Web Page UI
st.set_page_config(page_title="AI Finance Intelligence", page_icon="💰")
st.title("💰 AI Personal Finance Assistant")
st.write("I remember our conversation! Paste your expenses, tell me your salary, or ask follow-up questions.")

# 3. BULLETPROOF FALLBACK
if not api_key:
    st.sidebar.header("🔑 API Setup Required")
    api_key = st.sidebar.text_input("Paste your Gemini API Key here:", type="password")

# 4. MEMORY BANK: Initialize the Chat Session and History
# This creates a notebook in the app's brain to remember the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# This creates the actual Gemini AI brain with our upgraded prompt
if "chat_session" not in st.session_state and api_key:
    client = genai.Client(api_key=api_key)
    
    # THE UPGRADED PROMPT: We removed the "3 tips" limit and told it to be detailed
    system_prompt = """
    You are an expert Personal Finance Intelligence AI. 
    You will receive a user's raw expenses, salary information, or general finance questions.
    Your goals:
    1. Provide highly detailed, comprehensive financial breakdowns.
    2. If given expenses, analyze where their money went and identify high budget areas.
    3. Provide specific, advanced saving, budgeting, and investing strategies. Do not limit your tips; give as much detail as necessary.
    Format your response in clean Markdown. Be conversational, professional, and act like a dedicated financial advisor.
    """
    
    # We use client.chats.create() instead of generate_content() to enable memory!
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        )
    )

# 5. DRAW THE CHAT HISTORY: Show all past messages on the screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. THE NEW INPUT BOX: A modern chat bar at the bottom of the screen
if prompt := st.chat_input("Enter your expenses, salary, or ask a question..."):
    
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar to proceed.")
    else:
        # Show the user's message on the screen and save it to memory
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show a loading spinner while the AI thinks
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Send the message to the AI (it automatically remembers past context!)
                    response = st.session_state.chat_session.send_message(prompt)
                    
                    # Print the response and save it to memory
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")