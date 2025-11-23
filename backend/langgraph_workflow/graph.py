"""
LangGraph workflow definition.

This module defines the graph structure, nodes, edges, and compilation
with persistence/checkpointing enabled.
"""

import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver


from .state import GraphState
from .nodes import chatbot_node, human_node


class ChatBotGraph:
    def __init__(self):
        self.checkpointer = self.get_checkpointer()
        self.graph = self.get_graph()
        print('New Graph Object created')

    def get_checkpointer(self):
        # Use direct sqlite3 connection instead of from_conn_string()
        # from_conn_string() returns a context manager, not a direct instance
        conn = sqlite3.connect('checkpoints.db', check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        return checkpointer


    def get_all_thread_ids(self):
        if isinstance(self.checkpointer, SqliteSaver):
            # SQLite-specific logic (e.g., direct SQL query)
            cursor = self.checkpointer.conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints"
            )
            thread_ids = set([row[0] for row in cursor.fetchall()])
            
        elif isinstance(self.checkpointer, MemorySaver):
            # MemorySaver-specific logic
            thread_ids = set([
                val.config['configurable']['thread_id'] 
                for val in self.checkpointer.list({})
            ])
        else:
            raise AssertionError("Only SqlliteSaver and MemmorySaver checkpointers allowed")
        return list(thread_ids)

    
    def delete_all_threads(self):
        l_all_threads = self.get_all_thread_ids()
        try:
            for thread in l_all_threads:
                self.checkpointer.delete_thread(thread)
            return True
        except:
            return False
        

    def get_sidebar_json(self):
        d_messages = {}
        l_threads = self.get_all_thread_ids()
        for thread in l_threads:
            thread_first_message = self.get_thread_state_messages(thread)['messages'][0].content
            d_messages[thread] = thread_first_message
        return d_messages


    # def get_all_threads(self):

    def get_response(self, thread_id, human_message):
        config = {"configurable": {"thread_id": thread_id}}
        invoke_object = {"last_human_message":human_message}
        response_state = self.graph.invoke(invoke_object,config )
        response_answer = response_state['messages'][-1].content

        return response_answer

    def get_thread_state_messages(self, thread_id:str):
        config = {"configurable": {"thread_id": thread_id}}

        state = self.graph.get_state(config).values
        messages = state['messages']
        return {'state':state, 'messages':messages}
    


        
    # def get_thread_state(self, thread_id: str):
    #     config = {"configurable": {"thread_id": thread_id}}

    #     try:
    #         state = self.checkpointer.get(config)
    #         if state:
    #             return state
    #         return None
    #     except Exception as e:
    #         print(f"Error retrieving thread state: {e}")
    #         return None

    def get_graph(self):
        # Create the graph builder with ChatState schema
        graph_builder = StateGraph(GraphState)

        # Add the chatbot node to the graph
        graph_builder.add_node("human", human_node)
        graph_builder.add_node("chatbot", chatbot_node)

        # Define the edges: START -> chatbot -> END
        graph_builder.add_edge(START, "human")
        graph_builder.add_edge("human", "chatbot")
        graph_builder.add_edge("chatbot", END)




        # Compile the graph with checkpointing enabled
        # This allows conversation history to persist across invocations and restarts
        if not hasattr(self,"checkpointer"):
            self.checkpointer =   self.get_checkpointer()
 

        graph = graph_builder.compile(checkpointer=self.checkpointer)
        return graph
