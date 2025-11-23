import streamlit as st
from frontend.helper import create_new_thread


def render_chat_interface():
    """
    Render the complete chat interface - history display and input handling.

    This follows Streamlit's recommended pattern of combining history display
    and input handling in a single flow to ensure immediate UI updates.
    """
    chatbot = st.session_state.chatbot
    thread_id = st.session_state.selected_thread_id

    # Display existing message history
    _display_message_history(chatbot, thread_id)

    # Handle new user input
    _handle_new_message(chatbot, thread_id)


def _display_message_history(chatbot, thread_id):
    """Display existing messages from the backend for the current thread."""
    if thread_id is None:
        return

    messages = chatbot.get_thread_state_messages(thread_id)['messages']
    for message in messages:
        with st.chat_message(message.type):
            st.markdown(message.content)


def _handle_new_message(chatbot, thread_id):
    """Handle new user input, get AI response, and display both immediately."""
    if user_input := st.chat_input("Type your message here..."):
        # Create new thread if none selected
        if thread_id is None:
            thread_id = create_new_thread(user="VIVEK")

        # Display user message immediately
        _display_user_message(user_input)

        # Get AI response from backend
        ai_response = chatbot.get_response(
            human_message=user_input,
            thread_id=thread_id
        )

        # Display AI response immediately
        _display_ai_response(ai_response)

        # Update session state for subsequent reruns
        st.session_state.selected_thread_id = thread_id


def _display_user_message(content):
    """Render a user message in the chat interface."""
    with st.chat_message("human"):
        st.markdown(content)


def _display_ai_response(content):
    """Render an AI response in the chat interface."""
    with st.chat_message("ai"):
        st.markdown(content)
