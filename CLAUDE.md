# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Langchain-based chatbot application with a Streamlit frontend. The project follows a clean separation between backend (Langchain logic) and frontend (Streamlit UI).

## Project Structure

- `backend/` - Langchain components and business logic
  - `chain.py` - Core Langchain chain/response logic
- `frontend/` - Streamlit UI components
  - `app.py` - Main Streamlit application entry point

## Running the Application

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the Streamlit app:
```bash
streamlit run frontend/app.py
```

## Architecture Notes

### Backend-Frontend Integration
The frontend imports backend modules using dynamic path manipulation:
```python
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
from chain import get_response
```

When adding new backend modules, ensure they can be imported this way from the frontend.

### Chat State Management
- Chat history is stored in `st.session_state.messages`
- Each message is a dict with `role` (user/assistant) and `content` fields
- The backend `get_response()` function receives user messages and returns AI responses

### Modular Design Philosophy
- Backend modules should contain pure logic with no UI dependencies
- Frontend components should handle UI/UX and call backend functions
- Keep backend functions simple and focused on single responsibilities
