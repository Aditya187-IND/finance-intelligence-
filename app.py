import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# 1. Try to load the secret API key from the hidden file first
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Setup the Web Page UI
st.set_page_config(page_title="AI Finance Intelligence", page_icon="💰")
st.title("💰 Personal Finance Intelligence System")
st.write("Paste your raw bank statement or expense list below to get instant AI analysis.")

# 3. BULLETPROOF FALLBACK: If the .env file failed, create a sidebar input box
if not api_key:
    st.sidebar.header("🔑 API Setup Required")
    st.sidebar.warning("Your .env file wasn't detected by Windows.")
    api_key = st.sidebar.text_input("Paste your Gemini API Key here:", type="password")
    st.sidebar.info("Get a free key from: https://aistudio.google.com/")

# 4. Create a text box for the user to type/paste expenses
expenses_text = st.text_area(
    "Your Expenses:", 
    height=200, 
    placeholder="Example:\nUber $45\nWhole Foods $120\nStarbucks $6"
)

# 5. Create the Submit Button and define what happens when it is clicked
if st.button("Analyze Spending"):
    
    # Check if we have an API key from either the file OR the sidebar box
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar to proceed.")
    elif not expenses_text.strip():
        st.warning("Please enter some expenses to analyze.")
    else:
        # Show a loading spinner while the AI thinks
        with st.spinner("Analyzing your spending..."):
            try:
                # Configure the modern Gemini AI Client with the active key
                client = genai.Client(api_key=api_key)
                
                # The core intelligence instructions
                system_prompt = """
                You are an expert Personal Finance Intelligence AI. 
                You will receive raw, unformatted text containing a user's recent expenses. 
                Analyze the data and provide:
                1. A brief summary of where their money went.
                2. An alert identifying where their budget seems unusually high.
                3. Exactly three distinct, actionable tips on where they can save money based ONLY on the data provided.
                Format your response in clean Markdown with clear headings. Keep it concise.
                """
                
                # Send it to Gemini
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"User Expense Data:\n{expenses_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                
                # Print the AI's response to the screen
                st.subheader("AI Financial Insights")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")