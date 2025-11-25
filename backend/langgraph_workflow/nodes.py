"""
Node implementations for the LangGraph workflow.

This module contains all node functions that process the graph state.
"""
from typing import Any, Dict
from langchain_core.messages import AIMessage, HumanMessage
from .state import GraphState
from backend.config import CHATBOT_SYSTEM_PROMPT
from backend.chains import chain_chat_response

def router_node(state:GraphState)-> Dict[str, Any]:
    return state
    

def human_node(state: GraphState)-> Dict[str, Any]:
    return {'messages':HumanMessage(state['last_human_message'])} 

def chatbot_node(state: GraphState) -> dict:
    # Get the current messages from state
    
    messages = state["messages"]
    # Invoke the chat model with system prompt
    response_content = chain_chat_response(messages, system_prompt=CHATBOT_SYSTEM_PROMPT)

    # Return the response as a message to be added to state
    # The add_messages annotation in ChatState will automatically append it

    return {"messages": AIMessage(content=response_content)}

def hello_world_node(state: GraphState)-> Dict[str, Any]:
    return {'messages':AIMessage(content='Hello World')} 
