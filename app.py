import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# 1. Load the secret API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Setup the Web Page UI
st.set_page_config(page_title="Savr")
st.title("Savr")
st.write("I remember our conversation! Paste your expenses, tell me your salary, or ask follow-up questions.")

# 3. BULLETPROOF FALLBACK
if not api_key:
    st.sidebar.header("🔑 API Setup Required")
    api_key = st.sidebar.text_input("Paste your Gemini API Key here:", type="password")

# 4. MEMORY BANK: Initialize the Chat Session and History
if "messages" not in st.session_state:
    st.session_state.messages = []

# FIX: Save the Google connection itself to permanent memory so it doesn't close
if "ai_client" not in st.session_state and api_key:
    st.session_state.ai_client = genai.Client(api_key=api_key)

# Create the chat session using the saved memory connection
if "chat_session" not in st.session_state and api_key:
    system_prompt = """
    You are an expert Personal Finance Intelligence AI. 
    You will receive a user's raw expenses, salary information, or general finance questions.
    Your goals:
    1. Provide highly detailed, comprehensive financial breakdowns.
    2. If given expenses, analyze where their money went and identify high budget areas.
    3. Provide specific, advanced saving, budgeting, and investing strategies. Do not limit your tips; give as much detail as necessary.
    Format your response in clean Markdown. Be conversational, professional, and act like a dedicated financial advisor.
    """
    
    st.session_state.chat_session = st.session_state.ai_client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        )
    )

# 5. DRAW THE CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. THE NEW INPUT BOX
if prompt := st.chat_input("Enter your expenses, salary, or ask a question..."):
    
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar to proceed.")
    else:
        # Show user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
