from app.state import AgentState
from app.services.llm_service import generate


def briefing_node(state: AgentState) -> AgentState:

    print("\n[BRIEFING] Starting executive briefing...")

    parsed_papers = state.get("parsed_papers", [])

    if not parsed_papers:
        return {
            "error": "No parsed papers available."
        }

    sections = []

    for paper in parsed_papers:

        text = paper["text"]

        excerpt = text[:12000]

        sections.append(
            f"""
Paper: {paper['title']}

arXiv ID: {paper['arxiv_id']}

{excerpt}
"""
        )

    context = "\n\n".join(sections)

    prompt = f"""
You are a research assistant.

Create an executive research briefing from
the following papers.

For each paper provide:

1. Research problem
2. Method
3. Main findings
4. Limitations
5. Important technical contribution

Then provide:

6. Cross-paper comparison
7. Key research gaps
8. Useful directions for further investigation

Only use information present in the provided text.
Do not invent results.

Papers:

{context}
"""

    print("[BRIEFING] Sending context to Ollama...")

    briefing = generate(prompt)

    print("[BRIEFING] Ollama returned the briefing.")

    print("\n" + "=" * 60)
    print("EXECUTIVE BRIEFING")
    print("=" * 60)
    print("\n" + briefing)
    print("\n" + "=" * 60)

    return {
        "briefing": {
            "content": briefing
        },
        "error": None
    }