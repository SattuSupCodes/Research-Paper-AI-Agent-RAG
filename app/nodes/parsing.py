import pymupdf
from app.state import AgentState

def parse_papers_node(state:AgentState)->AgentState:
    downloaded_papers= state.get("downloaded_papers",[])
    if not downloaded_papers:
        return{
            "error":"No downloaded papers available for parsing"
            
        }
    parsed_papers=[]
    for paper in downloaded_papers:
        try:
            doc = pymupdf.open(paper["pdf_path"])
            pages=[]
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages.append(text)
            doc.close()
            full_text="\n".join(pages)
            parsed_papers.append({
                "arxiv_id": paper["arxiv_id"],
                "title": paper["title"],
                "text": full_text,
            })
            print(f"[PARSE] Parsed: {paper['title']} "
                f"({len(full_text)} characters)")
        except Exception as e:
            print(F"[PARSE] failed: {paper['title']},{e}")
    if not parsed_papers:
        return {
            "error": "Failed to parse the downloaded papers."
        }
    return{
            "parsed_papers": parsed_papers,
            "error": None,
        }