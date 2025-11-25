"""
LangGraph workflow definition.

This module defines the graph structure, nodes, edges, and compilation
with persistence/checkpointing enabled.
"""

import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from common_assets.config import d_chat_modes_graph, checkpoint_sqlitite_loc, default_user_id

from backend.utils import save_thread_metadata, get_user_threads, delete_user_threads, get_thread_details
from .state import GraphState
from .nodes import chatbot_node, human_node


class ChatBotGraph:
    def __init__(self, user_id: str = str(default_user_id)):
        self.user_id = user_id
        self.checkpointer = self.get_checkpointer()
        self.graph = self.get_graph()
        
        # self.d_graph = {}
        # for chat_mode in d_chat_modes_graph.keys():
        #     graph_fn = d_chat_modes_graph[chat_mode]['graph_fn']
        #     self.d_graph[chat_mode] = self.add_checkpointer_to_graph(graph_fn=graph_fn)


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
        invoke_object = {"chat_mode": chat_mode, "last_human_message":human_message}
        response_state = self.graph.invoke(invoke_object,config )
        response_answer = response_state['messages'][-1].content

        print('CHAT_MODE: ', chat_mode, '\t query: ', human_message)

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
        ### Currently there's only 1 state for all subgraphs. Can change it later if required.
        graph_builder = StateGraph(GraphState)
        
        for chat_mode in d_chat_modes_graph:
            chat_mode_subgraphs = d_chat_modes_graph[chat_mode]['graph_fn']().compile()
            graph_builder.add_node("subgraph_"+chat_mode, chat_mode_subgraphs )

        routing_fn = lambda x:  x['chat_mode'] 

        graph_builder.add_conditional_edges(START, routing_fn, {chat_mode: 'subgraph_'+chat_mode for chat_mode in d_chat_modes_graph.keys()})

        if not hasattr(self,"checkpointer"):
            self.checkpointer =   self.get_checkpointer()
 
        graph = graph_builder.compile(checkpointer=self.checkpointer)
        return graph



    # def add_checkpointer_to_graph(self, graph_fn):
    #     graph_builder = graph_fn()
    #     # Compile the graph with checkpointing enabled
    #     # This allows conversation history to persist across invocations and restarts
    #     if not hasattr(self,"checkpointer"):
    #         self.checkpointer =   self.get_checkpointer()
 
    #     graph = graph_builder.compile(checkpointer=self.checkpointer)
    #     return graph
