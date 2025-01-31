import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from user_management import (
    signup,
    login,
    get_chat_history,
    save_chat,
    chat_session,
    process_user_input,
    display_chat_history
)

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not properly loaded!")

st.title("SmartChat 💬: Your Intelligent Conversational Partner 🤖")

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

option = st.sidebar.selectbox(
    "**Welcome back!**  \n\nLog in or sign up to get smarter responses, upload files and images, and more.",
    ["Stay Logged Out", "Login", "Sign Up"]
)

if option == "Sign Up":
    st.subheader("Sign Up")
    name = st.text_input("Enter your name:", key="signup_name")
    mobile = st.text_input("Enter your mobile number:", key="signup_mobile")
    email = st.text_input("Enter your email:", key="signup_email")
    
    if st.button("Sign Up"):
        user_id = signup(name, mobile, email)
        st.success("Sign up successful!")
        st.session_state.user_id = user_id

elif option == "Login":
    st.subheader("Login")
    
    if st.session_state.user_id is None:  # Show email input only if not logged in
        email = st.text_input("Enter your email:", key="login_email")
        
        if st.button("Login"):
            user_id = login(email)
            if user_id:
                st.success("Login successful!")
                st.session_state.user_id = user_id
                st.session_state.chat_history = display_chat_history(user_id)  # Fetch chat history
            else:
                st.error("Wrong credentials. Please sign up.")


elif option == "Stay Logged Out":
    st.info("**Note:** You can chat with the AI, but your chat won't be saved.")


if st.session_state.user_id is not None or option == "Stay Logged Out":
    if st.session_state.user_id is not None:
        # Display chat history in sidebar
        chat_history = display_chat_history(st.session_state.user_id)
        st.sidebar.text_area("Chat History", chat_history, height=300)
        
    session_id, chat_history = chat_session(st.session_state.user_id)  # Start chat session
    user_input = st.text_input("You:", key="user_input")
    
    if st.button("Generate Response"):
        response = process_user_input(st.session_state.user_id, user_input, chat_history, session_id)  
        
        if response:
            st.text_area("AI:", response, height=300)
