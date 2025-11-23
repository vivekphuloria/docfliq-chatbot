"""
Chat chain implementation using LangChain.

This module provides the core chat functionality with the LLM model.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the chat model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def chain_chat_response(messages: list, system_prompt: str = None) -> str:
    """
    Invoke the chat model with messages and optional system prompt.

    Args:
        messages: List of message objects or dicts with 'role' and 'content'
        system_prompt: Optional system prompt to prepend to messages

    Returns:
        str: The AI-generated response content
    """
    # Prepend system prompt if provided
    if system_prompt:
        messages_with_system = [SystemMessage(content=system_prompt)] + messages
    else:
        messages_with_system = messages

    # Invoke the model
    response = model.invoke(messages_with_system)

    return response.content
