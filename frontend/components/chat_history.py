import streamlit as st


def display_chat_history():
    """
    Display all messages from the chat history stored in session state.

    Iterates through st.session_state.messages and renders each message
    with the appropriate role (user/assistant).
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
