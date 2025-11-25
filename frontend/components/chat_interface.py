import streamlit as st
from frontend.helper import create_new_thread
from common_assets.config import default_user_id

def render_chat_interface():
    """
    Render the complete chat interface - history display and input handling.

    This follows Streamlit's recommended pattern of combining history display
    and input handling in a single flow to ensure immediate UI updates.
    """
    chatbot = st.session_state.chatbot
    thread_id = st.session_state.selected_thread_id

    ## Only for debugging. 
    st.json(st.session_state, expanded=False)

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

        _display_user_message(user_input)

        # Create new thread if none selected
        new_thread = False
        if thread_id is None:
            thread_id = create_new_thread(default_user_id)
            new_thread = True
            ### Update Session State to add new chat
            st.session_state.all_thread_details = st.session_state.chatbot.get_sidebar_json()

        # Update session state for subsequent reruns
        st.session_state.selected_thread_id = thread_id

        if thread_id in st.session_state.all_thread_details:
            chat_mode = st.session_state.all_thread_details[thread_id]['chat_mode']
        else:
            chat_mode = st.session_state.selected_chat_mode
        



        # Display user message immediately

        # Get AI response from backend
        ai_response = chatbot.get_response(
            human_message=user_input,
            thread_id=thread_id,
            chat_mode=chat_mode,
            new_thread = new_thread
        )

        # Display AI response immediately
        _display_ai_response(ai_response)

        if new_thread:
            st.session_state.all_thread_details = st.session_state.chatbot.get_sidebar_json()
            
        st.rerun()



def _display_user_message(content):
    """Render a user message in the chat interface."""
    with st.chat_message("human"):
        st.markdown(content)


def _display_ai_response(content):
    """Render an AI response in the chat interface."""
    with st.chat_message("ai"):
        st.markdown(content)
