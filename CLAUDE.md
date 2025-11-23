# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph-based chatbot application with a Streamlit frontend. The project uses LangGraph for stateful conversation management with SQLite persistence, LangChain for LLM interactions, and Streamlit for the UI.

## Project Structure

```
backend/
├── langgraph_workflow/     # LangGraph orchestration
│   ├── graph.py            # ChatBotGraph class - main entry point
│   ├── state.py            # GraphState TypedDict definition
│   └── nodes.py            # Graph nodes (human_node, chatbot_node)
├── chains/                 # LangChain chain implementations
│   └── chat_chain.py       # chain_chat_response() using GPT-4o-mini
├── config/                 # Configuration and prompts
│   ├── prompts_chatbot.py  # CHATBOT_SYSTEM_PROMPT
│   └── prompts_ingestion.py
frontend/
├── app.py                  # Main Streamlit entry point
├── helper.py               # Utility functions (create_new_thread)
└── components/             # Modular UI components
    ├── chat_history.py     # display_chat_history()
    ├── chat_input.py       # handle_chat_input()
    └── chat_list_sidebar.py # display_chat_list_sidebar()
```

## Environment Setup

Required environment variables (create a `.env` file):

```
OPENAI_API_KEY=your_key_here
```

Optional (for LangSmith tracing):
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=your_project_name
```

## Running the Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run frontend/app.py
```

## Architecture

### LangGraph Workflow

The chatbot uses a two-node LangGraph graph with SQLite checkpointing:

```
START → human_node → chatbot_node → END
```

- **human_node**: Converts user input to HumanMessage and adds to state
- **chatbot_node**: Invokes the LLM chain and returns AIMessage

State schema (`GraphState`):
- `last_human_message`: str - Current user input
- `messages`: Annotated[list, add_messages] - Conversation history

### Persistence

- Uses `SqliteSaver` with `checkpoints.db` for conversation persistence
- Thread-based state management via `thread_id` in config
- Supports both `SqliteSaver` and `MemorySaver` checkpointers

### Data Flow

1. User input → `handle_chat_input()` component
2. Creates/uses thread ID → `ChatBotGraph.get_response(thread_id, message)`
3. Graph invokes nodes → LLM chain processes messages
4. Response persisted in SQLite → returned to frontend
5. `display_chat_history()` retrieves messages via `get_thread_state_messages()`

### Backend-Frontend Integration

The frontend imports backend modules using relative imports from the project root:

```python
from backend.langgraph_workflow.graph import ChatBotGraph
```

Session state keys:
- `st.session_state.chatbot` - ChatBotGraph instance
- `st.session_state.selected_thread_id` - Current conversation thread
- `st.session_state.list_messages_to_display` - Messages for display

### Modular Design Philosophy

- Backend modules contain pure logic with no UI dependencies
- Frontend components handle UI/UX and call backend functions
- Each frontend feature should be a component in `frontend/components/`
- `app.py` should only orchestrate components, not contain implementation logic

## Adding New Features

**New LangGraph node:**
1. Add node function in `backend/langgraph_workflow/nodes.py`
2. Register node in `graph.py` via `graph_builder.add_node()`
3. Add edges to connect the node

**New LangChain chain:**
1. Create chain in `backend/chains/`
2. Export from `backend/chains/__init__.py`
3. Import and use in nodes or other chains

**New UI component:**
1. Create component in `frontend/components/`
2. Export from `frontend/components/__init__.py`
3. Import and call in `frontend/app.py`

## Additional Requirements

- Whenever you want to create or modify code for langchain, langgraph, or streamlit, use the context7 tool to check the latest documentation.
