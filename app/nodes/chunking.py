from app.state import AgentState
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

def chunk_text(text:str)->list[str]:
    chunks = []
    start = 0
    text_length = len(text)
    while start<text_length:
        end = start+CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks
def chunk_papers_node(state:AgentState)->AgentState:
    parsed_papers = state.get("parsed_papers",[])
    if not parsed_papers:
        return{
            "error":"No parsed papers available for chunking"
        }
    all_chunks = []
    for paper in parsed_papers:
        chunks = chunk_text(paper["text"])
        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "arxiv_id": paper["arxiv_id"],
                "title": paper["title"],
                "chunk_id": index,
                "text": chunk,
            })
        print(
            f"[CHUNK] {paper['title']}: "
            f"{len(chunks)} chunks"
        )
    return{
        "chunks":all_chunks,
        "error":None,
    }