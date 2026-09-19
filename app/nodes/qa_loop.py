from app.state import AgentState
from app.state import AgentState
from app.nodes.qa import (
    retrieve_chunks_node,
    answer_question_node,
)

def qa_loop_node(state: AgentState) -> AgentState:

    print("\n" + "=" * 60)
    print("RESEARCH Q&A")
    print("=" * 60)

    print("\nAsk questions about the selected papers.")
    print("Type 'exit' when you are finished.\n")

    while True:

        question = input("> ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("\n[QA] Ending research session.")
            return {
                "current_question": "",
            }

        # Store the current question in state
        state["current_question"] = question

        # Retrieve relevant chunks
        retrieval_state = retrieve_chunks_node(state)

        if retrieval_state.get("error"):
            print(
                f"\n[QA] {retrieval_state['error']}"
            )
            continue

        state.update(retrieval_state)

        # Generate answer
        answer_state = answer_question_node(state)

        if answer_state.get("error"):
            print(
                f"\n[QA] {answer_state['error']}"
            )
            continue

        state.update(answer_state)

        print("\n--- Answer ---")
        print(state["current_answer"])

        print("\n--- Sources ---")

        for chunk in state.get(
            "retrieved_chunks",
            [],
        ):
            print(
                f"- {chunk['title']} "
                f"(arXiv: {chunk['arxiv_id']}, "
                f"chunk: {chunk['chunk_id']})"
            )

        print()