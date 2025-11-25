from backend.langgraph_workflow.chat_mode_graphs import get_graph_content_gen, get_graph_qna
d_chat_modes_graph = { 
    'qna': {
        'display_name':'QnA',
        'graph_fn' : get_graph_qna
    },
    'content_gen':{
        'display_name':'Content Generation',
        'graph_fn' : get_graph_content_gen
    }
}



checkpoint_sqlitite_loc = "./storage/checkpoints.db"
dynamodb_table_name = "docfliq_vp_gmail"
default_user_name = "VIVEK"
default_user_id = "10001"

