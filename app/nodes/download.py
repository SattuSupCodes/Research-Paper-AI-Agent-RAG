from app.state import AgentState
from app.services.pdf_service import download_pdf


def download_papers_node(state: AgentState) -> AgentState:
    """
    Download all papers selected by the user.
    """

    selected_papers = state.get("selected_papers", [])
    print("\n[DOWNLOAD] State keys:", list(state.keys()))
    print("[DOWNLOAD] Selected papers:", selected_papers)
    if not selected_papers:
        return {
            "error": "No papers were selected for download."
        }

    downloaded_papers = []

    for paper in selected_papers:
        try:
            pdf_path = download_pdf(
                pdf_url=paper["pdf_url"],
                arxiv_id=paper["arxiv_id"],
            )

            downloaded_papers.append({
                "arxiv_id": paper["arxiv_id"],
                "title": paper["title"],
                "pdf_path": pdf_path,
            })

            print(
                f"[DOWNLOAD] Downloaded: {paper['title']}"
            )

        except Exception as exc:
            print(
                f"[DOWNLOAD] Failed: "
                f"{paper['title']} — {exc}"
            )

    if not downloaded_papers:
        return {
            "error": "Failed to download all selected papers."
        }

    return {
        "downloaded_papers": downloaded_papers,
        "error": None,
    }