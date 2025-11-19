import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from chain import get_response


def handle_chat_input():
    """
    Handle user input from the chat interface.

    Displays a chat input widget, processes user messages,
    gets AI responses from the backend, and updates the chat history.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if user_input := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response from backend, passing full conversation history for memory
        ai_response = get_response(st.session_state.messages)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)
