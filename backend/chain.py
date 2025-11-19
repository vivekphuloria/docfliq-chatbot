from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the chat model (gpt-4o-mini for cost-effectiveness)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def get_response(conversation_history):
    """
    Generate AI response using LangChain with conversation memory.

    Args:
        conversation_history: List of message dicts with 'role' and 'content' keys
                            e.g., [{"role": "user", "content": "Hello"}, ...]

    Returns:
        str: AI-generated response content
    """
    # Invoke the model with the full conversation history
    # LangChain automatically handles the message format
    response = model.invoke(conversation_history)

    # Return just the content string
    return response.content
