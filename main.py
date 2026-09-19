from app.graph import agent


def main():
    query = input("Research topic or arXiv ID: ").strip()

    state = agent.invoke({
        "user_query": query,
        "qa_history": [],
    })

    print("\n--- Agent State ---")
    print(f"Query: {state['user_query']}")
    print(f"Type: {state['query_type']}")
    print(f"Normalized: {state['normalized_query']}")
    # if state.get("arxiv_results"):
    #     print("\n ----- papers found -----")
    #     for i , paper in enumerate(state['arxiv_results'],start=1):
    #         print(f"\n{i}. {paper['title']}")
    #         print(f"  arxiv ID: {paper['arxiv_id']}")
    #         print(f"  PDF:{paper['pdf_url']}")
    # # if state.get("selected_paper"):
    #     paper=state["selected_paper"]
    #     print("\n--- Selected Paper ---")
    #     print(f"Title: {paper['title']}")
    #     print(f"Authors: {', '.join(paper['authors'])}")
    #     print(f"arXiv ID: {paper['arxiv_id']}")
    #     print(f"PDF: {paper['pdf_url']}")
    if state.get("briefing"):
        print("\n--- Executive Briefing ---")
        print(state["briefing"]["content"])
    if state.get("error"):
        print("\n--- Error ---")
        print(state["error"])

if __name__ == "__main__":
    main()
    
