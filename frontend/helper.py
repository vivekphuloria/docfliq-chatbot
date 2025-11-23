from datetime import datetime
import streamlit as st
from backend.langgraph_workflow.graph import ChatBotGraph
def create_new_thread(user: str = "VIVEK") -> str:
    """
    Create a new thread ID with user and timestamp.

    Args:
        user: Username to include in thread ID (default: "VIVEK")

    Returns:
        Thread ID in format: chat_<user>_<yyyyMMdd_HHmmss>
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    thread_id = f"chat_{user}_{timestamp}"
    return thread_id

def init_st_session_state():
    if "chatbot" not in st.session_state:
        chatbot = ChatBotGraph()
        st.session_state.chatbot = chatbot
    if "selected_thread_id" not in st.session_state:
        st.session_state.selected_thread_id = None
    if 'list_messages_to_display' not in st.session_state:
        st.session_state.list_messages_to_display = []
