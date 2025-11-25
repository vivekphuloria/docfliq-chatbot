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
├── utils/                  # Utility functions
│   └── dynamodb_helper.py  # DynamoDB operations for thread metadata
frontend/
├── app.py                  # Main Streamlit entry point
├── helper.py               # Utility functions (create_new_thread)
└── components/             # Modular UI components
    ├── chat_history.py     # display_chat_history()
    ├── chat_input.py       # handle_chat_input()
    └── chat_list_sidebar.py # display_chat_list_sidebar()
common_assets/
└── config.py               # Global configuration (dynamodb_table_name, etc.)
```

## Environment Setup

Required environment variables (create a `.env` file):

```
OPENAI_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your_aws_region
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

The application uses a dual-persistence architecture:

**DynamoDB Table (Thread Metadata)**
- Table name: Configured in `common_assets/config.py` as `dynamodb_table_name`
- **Source of truth** for thread management and conversation metadata
- Schema:
  - `user_id` (Partition Key): User identifier
  - `thread_id` (Sort Key): Thread identifier
  - `mode`: Chat mode (e.g., "QnA", "Content Generation")
  - `created_date`: ISO format timestamp when thread was created
  - `update_date`: ISO format timestamp when thread was last updated
- Operations in `backend/utils/dynamodb_helper.py`:
  - `save_thread_metadata()`: Create or update thread metadata
  - `get_user_threads()`: Fetch all thread IDs for a user
  - `delete_thread_metadata()`: Delete a single thread
  - `delete_user_threads()`: Delete all threads for a user

**SQLite Database (Message History)**
- Uses `SqliteSaver` with `checkpoints.db` for conversation message persistence
- Stores the actual message content and conversation state via LangGraph checkpointing
- Thread-based state management via `thread_id` in config
- Supports both `SqliteSaver` and `MemorySaver` checkpointers

**Key Principle**: DynamoDB tracks which conversations exist and their metadata. SQLite stores the detailed message history for each conversation.

### Data Flow

1. User input → `handle_chat_input()` component
2. Creates/uses thread ID → `save_thread_metadata()` saves/updates thread metadata in DynamoDB
3. `ChatBotGraph.get_response(thread_id, message)` processes the message
4. Graph invokes nodes → LLM chain processes messages
5. Response persisted in SQLite via LangGraph checkpointing → returned to frontend
6. `display_chat_history()` retrieves messages via `get_thread_state_messages()` from SQLite
7. Sidebar uses `get_user_threads()` to fetch thread list from DynamoDB

### Backend-Frontend Integration

**CRITICAL ARCHITECTURAL PRINCIPLE**: The frontend MUST ONLY interact with the backend through the `ChatBotGraph` object.

**NEVER directly import or call**:
- `backend.utils.dynamodb_helper` functions
- Any other backend utility modules
- Backend configuration modules (except `common_assets.config` for global settings)

**ONLY allowed backend import**:
```python
from backend.langgraph_workflow.graph import ChatBotGraph
```

All backend operations (saving threads, retrieving messages, deleting threads, etc.) must be exposed as methods on the `ChatBotGraph` class. The graph acts as the single interface between frontend and backend.

Session state keys:
- `st.session_state.chatbot` - ChatBotGraph instance (ONLY backend interaction point)
- `st.session_state.selected_thread_id` - Current conversation thread
- `st.session_state.list_messages_to_display` - Messages for display

### Modular Design Philosophy

- Backend modules contain pure logic with no UI dependencies
- Frontend components handle UI/UX and call backend functions ONLY through ChatBotGraph
- Each frontend feature should be a component in `frontend/components/`
- `app.py` should only orchestrate components, not contain implementation logic
- Frontend never directly accesses DynamoDB, chains, or other backend utilities

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

## Working with Thread Persistence

**Important Guidelines:**

1. **Always use DynamoDB as the source of truth** for thread management:
   - To get all conversations for a user, call `get_user_threads(user_id)` from DynamoDB
   - When creating a new thread, call `save_thread_metadata(user_id, thread_id, mode)`
   - When deleting threads, call `delete_thread_metadata()` or `delete_user_threads()`

2. **Message content lives in SQLite**:
   - Use LangGraph's checkpoint methods to retrieve message history
   - The `checkpoints.db` contains the actual conversation messages
   - Never query DynamoDB for message content

3. **Thread lifecycle**:
   - Create: Call `save_thread_metadata()` before first message
   - Update: Automatically updated on each message via `save_thread_metadata()`
   - Delete: Call `delete_thread_metadata()` for single thread or `delete_user_threads()` for all
   - List: Call `get_user_threads()` to get all thread IDs

4. **Error handling**:
   - All DynamoDB operations return boolean success indicators
   - Check return values and handle failures gracefully
   - Print statements in helper functions aid debugging

## Additional Requirements

- Whenever you want to create or modify code for langchain, langgraph, or streamlit, use the context7 tool to check the latest documentation.
