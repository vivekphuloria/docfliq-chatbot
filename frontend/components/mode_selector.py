import streamlit as st
from common_assets.config import d_modes_graph


def display_mode_selector():
    """
    Display mode selection interface.

    If thread exists: Show mode as header (no buttons)
    If new conversation: Show mode selection buttons
    """
    # Get all available modes from config
    modes = list(d_modes_graph.keys())

    # Check if we're viewing an existing thread
    selected_thread_id = st.session_state.selected_thread_id
    thread_exists = (
        selected_thread_id is not None
        and selected_thread_id in st.session_state.all_thread_details
    )

    if thread_exists:
        # Existing thread: Display mode as header only
        active_mode = st.session_state.all_thread_details[selected_thread_id]['chat_mode']
        st.markdown("### " + active_mode)
    else:
        # New conversation: Display mode selection buttons
        active_mode = st.session_state.chat_mode
        cols = st.columns(len(modes))

        for idx, chat_mode in enumerate(modes):
            # Highlight currently selected mode as primary
            button_type = "primary" if chat_mode == active_mode else "secondary"

            # Render mode selection button
            button_clicked = cols[idx].button(
                chat_mode,
                key=f"mode_btn_{chat_mode}",
                type=button_type,
                use_container_width=True
            )

            # Update mode on button click
            if button_clicked:
                st.session_state.chat_mode = chat_mode
                st.rerun()
