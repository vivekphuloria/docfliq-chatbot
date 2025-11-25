import streamlit as st
from uuid_utils import uuid7
from backend.langgraph_workflow.graph import ChatBotGraph
from backend.utils import save_thread_metadata
from common_assets.config import d_modes_graph, default_user_id, dynamodb_table_name

def create_new_thread(user: str = str(default_user_id)) -> str:
    thread_id = str(uuid7())

    return thread_id

def init_st_session_state():
    if "chatbot" not in st.session_state:
        chatbot = ChatBotGraph(user_id=str(default_user_id))
        st.session_state.chatbot = chatbot
    if "selected_thread_id" not in st.session_state:
        st.session_state.selected_thread_id = None
    if 'all_thread_details' not in st.session_state:
        if 'chatbot' in st.session_state:
            st.session_state.all_thread_details = st.session_state.chatbot.get_sidebar_json()
        else:
            st.session_state.all_thread_details = dict()
    if 'selected_chat_mode' not in st.session_state:
        st.session_state.selected_chat_mode = list(d_modes_graph.keys())[0]
