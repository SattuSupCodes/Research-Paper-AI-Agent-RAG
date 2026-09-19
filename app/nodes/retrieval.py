from app.state import AgentState
from app.services.arxive_service import search_papers
BATCH_SIZE = 5
MAX_SEARCH_RESULTS = 20
def search_arx_node(state: AgentState) -> AgentState:
    query = state["normalized_query"]

    print(f"\n[SEARCH] Query: {query}")

    papers = search_papers(
        query=query,
        max_results=MAX_SEARCH_RESULTS,
    )

    print(f"[SEARCH] Found {len(papers)} papers")

    return {
        "arxiv_results": papers[:BATCH_SIZE],
        "search_pool": papers,
        "shown_count": 0,
        "error": None,
    }


def display_papers(papers: list[dict]) -> None:
    print("\n--- Papers Found ---")

    for i, paper in enumerate(papers, start=1):
        print(f"\n[{i}] {paper['title']}")
        print(f"    arXiv ID: {paper['arxiv_id']}")
        print(f"    Authors: {', '.join(paper['authors'])}")
        print(f"    PDF: {paper['pdf_url']}")


def select_topic_paper_node(state: AgentState) -> AgentState:

    search_pool = state.get("search_pool", [])
    shown_count = state.get("shown_count", 0)

    if not search_pool:
        return {
            "error": "No papers found for the requested topic."
        }

    while True:


        batch = search_pool[
            shown_count : shown_count + BATCH_SIZE
        ]

        if not batch:
            print("\n[SEARCH] No more papers available.")
            print("Try 'refine' to search with a different query.")

        else:
           
            display_papers(
                [
                    {
                        **paper,
                        "_display_index": shown_count + i + 1,
                    }
                    for i, paper in enumerate(batch)
                ]
            )

        shown_count += len(batch)

        print("\nOptions:")
        print("  1,3      → select papers")
        print("  more     → show another batch")
        print("  refine   → modify the research query")
        print("  quit     → exit")

        choice = input("\n> ").strip().lower()
        if choice == "quit":
            return {
                "error": "Search cancelled by user."
            }

        if choice == "more":

            if shown_count >= len(search_pool):
                print(
                    "\n[SEARCH] You've reached the end "
                    "of the current results."
                )

                continue

            continue

        
        if choice=="refine":
            print(
                f"\nCurrent query: "
                f"{state['normalized_query']}"
            )

            new_query = input(
                "New research query: "
            ).strip()

            if not new_query:
                print("\n[SEARCH] Query cannot be empty.")
                continue

            print(f"\n[SEARCH] Query: {new_query}")

            try:
                new_papers = search_papers(
                    query=new_query,
                    max_results=MAX_SEARCH_RESULTS,
                )

                print(
                    f"[SEARCH] Found "
                    f"{len(new_papers)} papers"
                )

                if not new_papers:
                    print(
                        "[SEARCH] No papers found. "
                        "Try another query."
                    )
                    continue

               
                search_pool = new_papers
                shown_count = 0

                state["normalized_query"] = new_query
                state["search_pool"] = new_papers

                continue

            except Exception as exc:
                print(
                    f"[SEARCH] Refined search failed: {exc}"
                )
                continue

     
        try:
            indices = [
                int(index.strip()) - 1
                for index in choice.split(",")
            ]

            if not indices:
                raise ValueError

            if any(
                index < 0 or index >= len(search_pool)
                for index in indices
            ):
                raise ValueError

          
            indices = list(dict.fromkeys(indices))

            selected_papers = [
                search_pool[index]
                for index in indices
            ]

            print(
                f"\n[SELECT] Selected "
                f"{len(selected_papers)} paper(s)."
            )

            return {
                "selected_papers": selected_papers,
                "shown_count": shown_count,
                "search_pool": search_pool,
                "error": None,
            }

        except ValueError:
            print(
                "\nInvalid selection."
                "\nUse something like: 1,3"
            )
'''
it simply gives the query to the arx service and takes
those results and put them back into state. Nothing to do with
how and what and when arxiv works. 
'''
'''
we added a solution for a situation where maybe the user
isnt satisfied with the current 5 results and may wish to
either ask for 5 more, change query, or simply quit.
'''
