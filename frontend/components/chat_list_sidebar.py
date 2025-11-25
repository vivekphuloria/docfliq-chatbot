import streamlit as st
import sys
from pathlib import Path

# Add backend to path


def display_chat_list_sidebar():

    chatbot = st.session_state.chatbot
    d_list_chats = chatbot.get_sidebar_json()
    d_list_chats = d_list_chats if type(d_list_chats)==dict else dict()

    with st.sidebar:
        st.title("💬 Chats")

        # New Chat button at the top
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            # Go to an empty chat screen -> Create fresh logic
            st.session_state.selected_thread_id = None
            st.toast(f"Send message to start new chat")
            # # st.rerun()
        if st.button("🗑️ Delete All Chats", use_container_width=True, type="primary"):
            # Go to an empty chat screen -> Create fresh logic
            chatbot.delete_all_threads()
            st.toast(f"Send message to start new chat")

        st.divider()


        # Display list of chats
        st.subheader("Recent Chats")

        for thread_id,thread_info in d_list_chats.items() :
            # Chat summary as a single clickable line
            if st.button(
                thread_info['first_message'],
                key=f"chat_{thread_id}",
                use_container_width=True
            ):
                # Set selected thread ID
                st.session_state.selected_thread_id = thread_id
