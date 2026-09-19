from typing import Any, TypedDict

class AgentState(TypedDict, total = False):
    user_query: str
    query_type: str
    normalized_query:str
    arxiv_results: list[dict[str, Any]]
    selected_papers: list[dict[str, Any]]
    pdf_path: str
    parsed_text:str
    chunks:list[dict[str,Any]]
    vector_collection: str
    retrieved_chunks:list[dict[str,Any]]
    briefing: dict[str, Any]
    current_question:str
    current_answer:str
    qa_history:list[dict[str,Any]]
    error: str | None
    downloaded_papers:list[dict[str,str]]
    parsed_papers: list[dict[str, Any]]
    search_pool: list[dict[str, Any]]
    shown_count:int
    vector_collection: str