"""
LangGraph workflow definition.

This module defines the graph structure, nodes, edges, and compilation
with persistence/checkpointing enabled.
"""

import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from common_assets.config import checkpoint_sqlitite_loc, dynamodb_table_name, default_user_id

from backend.utils import save_thread_metadata, get_user_threads, delete_user_threads, get_thread_details
from .state import GraphState
from .nodes import chatbot_node, human_node


class ChatBotGraph:
    def __init__(self, user_id: str = str(default_user_id)):
        self.user_id = user_id
        self.checkpointer = self.get_checkpointer()
        self.graph = self.get_graph()
        print('New Graph Object created')

    def get_checkpointer(self):
        # Use direct sqlite3 connection instead of from_conn_string()
        # from_conn_string() returns a context manager, not a direct instance
        conn = sqlite3.connect(checkpoint_sqlitite_loc, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        return checkpointer


    def get_all_thread_ids(self):
        # Get thread IDs from DynamoDB for the current user
        thread_ids = get_user_threads(self.user_id)
        return thread_ids

        # Legacy SQLite/MemorySaver logic - commented out but kept for reference
        # if isinstance(self.checkpointer, SqliteSaver):
        #     # SQLite-specific logic (e.g., direct SQL query)
        #     try:
        #         cursor = self.checkpointer.conn.execute(
        #             "SELECT DISTINCT thread_id FROM checkpoints"
        #         )
        #         thread_ids = set([row[0] for row in cursor.fetchall()])
        #     except:
        #         return []
        # elif isinstance(self.checkpointer, MemorySaver):
        #     # MemorySaver-specific logic
        #     thread_ids = set([
        #         val.config['configurable']['thread_id']
        #         for val in self.checkpointer.list({})
        #     ])
        # else:
        #     raise AssertionError("Only SqlliteSaver and MemmorySaver checkpointers allowed")
        # return list(thread_ids)

    
    def delete_all_threads(self):
        l_all_threads = self.get_all_thread_ids()
        try:
            # Delete from SQLite checkpointer
            for thread in l_all_threads:
                self.checkpointer.delete_thread(thread)

            # Delete from DynamoDB
            delete_user_threads(self.user_id)

            return True
        except:
            return False
        

    def get_sidebar_json(self):
        d_threads = {}
        l_threads = self.get_all_thread_ids()
        for thread in l_threads:
            thread_details = get_thread_details(user_id=self.user_id, thread_id=thread)
            thread_first_message = self.get_thread_state_messages(thread)['messages'][0].content
            d_threads[thread] = {
                'first_message' : thread_first_message,
                'chat_mode' : thread_details['chat_mode'] if 'chat_mode' in thread_details else thread_details['mode'],
                'created_date': thread_details['created_date'],
                'update_date' : thread_details['update_date']
            }



        return d_threads


    # def get_all_threads(self):

    def get_response(self, thread_id, human_message, chat_mode, new_thread ):
        config = {"configurable": {"thread_id": thread_id}}
        invoke_object = {"last_human_message":human_message}
        response_state = self.graph.invoke(invoke_object,config )
        response_answer = response_state['messages'][-1].content

        # Save or update thread metadata in DynamoDB
        # If thread exists, updates update_date; if new, creates with created_date and update_date
        save_thread_metadata(self.user_id, thread_id, chat_mode=chat_mode,  new_thread = new_thread)

        return response_answer

    def get_thread_state_messages(self, thread_id:str):
        config = {"configurable": {"thread_id": thread_id}}

        state = self.graph.get_state(config).values
        messages = state['messages']
        return {'state':state, 'messages':messages}
    
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
