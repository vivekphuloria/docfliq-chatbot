from backend.langgraph_workflow.nodes import human_node, chatbot_node, hello_world_node
from backend.langgraph_workflow.state import GraphState
from langgraph.graph import StateGraph, START, END


def get_graph_qna():
    graph_builder = StateGraph(GraphState)

    # Add the chatbot node to the graph
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("chatbot", chatbot_node)

    # Define the edges: START -> chatbot -> END
    graph_builder.add_edge(START, "human")
    graph_builder.add_edge("human", "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder

def get_graph_content_gen():
    graph_builder = StateGraph(GraphState)

    # Add the chatbot node to the graph
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("hello_world", hello_world_node)

    # Define the edges: START -> chatbot -> END
    graph_builder.add_edge(START, "human")
    graph_builder.add_edge("human", "hello_world")
    graph_builder.add_edge("hello_world", END)
    return graph_builder


