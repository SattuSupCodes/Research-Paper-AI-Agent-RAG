from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.nodes.retrieval import search_arx_node, select_topic_paper_node
from app.services.arxive_service import get_paper
from app.nodes.download import download_papers_node
from app.nodes.parsing import parse_papers_node
from app.nodes.chunking import chunk_papers_node
from app.nodes.indexing import index_chunks_node
from app.nodes.summarization import briefing_node
from app.nodes.qa_loop import qa_loop_node
def query_understanding(state:AgentState)->AgentState:
    query=state["user_query"].strip()
    if any(char.isdigit() for char in query) and "." in query:
        query_type="paper"
    else:
        query_type="topic"
    return{
        "query_type": query_type,
        "normalized_query": query,
    }
def route_query(state:AgentState)->str:
    #decides what branch of the graph should be executed next
    if state["query_type"] =="topic":
        return "search"
    return "paper"
def fetch_paper_node(state:AgentState)->AgentState:
    arxiv_id = state["normalized_query"]
    try:
        paper=get_paper(arxiv_id)
        
        return{
            "selected_papers":[paper],
            "error":None,
        }
    except Exception as e:
        return{"error":str(e)}
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("query_understanding", query_understanding)
    graph.add_node("search_arxiv", search_arx_node,)
    graph.add_node("fetch_paper", fetch_paper_node)
    graph.add_node("select_topic_paper", select_topic_paper_node,)
    graph.add_node("download_papers", download_papers_node,) 
    graph.add_node("parse_papers", parse_papers_node)
    graph.add_node("chunk_papers", chunk_papers_node)
    graph.add_node("index_chunks", index_chunks_node)
    graph.add_node("briefing", briefing_node)
    graph.add_node("qa_loop", qa_loop_node)
    graph.add_edge(START, "query_understanding")
    graph.add_conditional_edges(
        "query_understanding", route_query,
        {
            "search":"search_arxiv",
            "paper":"fetch_paper",
        }
    )#we're telling our langgraph to ask route_query which branch to take, "topic" or "paper"
    graph.add_edge(
        "search_arxiv", "select_topic_paper",
    )
    graph.add_edge("select_topic_paper", "download_papers",)
    graph.add_edge("fetch_paper", "download_papers")
    
    graph.add_edge("download_papers", "parse_papers",)
    graph.add_edge("parse_papers", "chunk_papers",)
    graph.add_edge("chunk_papers", "index_chunks")
    graph.add_edge("index_chunks","briefing")
    graph.add_edge("briefing", "qa_loop",)
    graph.add_edge("qa_loop",END)      
    # graph.add_edge("query_understanding", END)
    return graph.compile()
agent=build_graph()