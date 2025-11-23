"""
State definitions for the LangGraph workflow.

This module defines the state structure used throughout the graph execution.
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    State schema for the chat graph.

    Attributes:
        messages: List of conversation messages. The add_messages annotation
                 ensures new messages are appended to the list automatically.
    """
    last_human_message: str
    messages: Annotated[list, add_messages]

