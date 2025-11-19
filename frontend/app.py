import streamlit as st
from components import display_chat_history, handle_chat_input

# Page config
st.set_page_config(page_title="Simple Chatbot", page_icon="💬")

# Title
st.title("💬 Simple Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
display_chat_history()

# Chat input
handle_chat_input()
