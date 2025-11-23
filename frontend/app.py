import streamlit as st
from frontend.components import display_chat_history, handle_chat_input, display_chat_list_sidebar, render_chat_interface
from frontend.helper import init_st_session_state

# Page config
def main():
    ### Initialize st.session_state
    init_st_session_state()

    st.set_page_config(page_title="Simple Chatbot", page_icon="💬", layout="wide")
    display_chat_list_sidebar()

    # Title
    st.title("💬 Simple Chatbot")

    # Display chat messages for selected thread
    # display_chat_history()
    # handle_chat_input()
    render_chat_interface()

if __name__ == "__main__":
    main()