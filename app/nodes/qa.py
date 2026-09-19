from app.state import AgentState
from app.services.embedding_service import emb_texts
from app.services.vector_store import search_chunks
from app.services.llm_service import generate


def retrieve_chunks_node(state: AgentState) -> AgentState:
    question = state.get("current_question", "").strip()

    if not question:
        return {
            "error": "No question provided."
        }

    print("\n[RETRIEVE] Embedding question...")

    query_embedding = emb_texts([question])[0]

    selected_papers = state.get(
        "selected_papers",[]
        
    )
    selected_arxiv_ids = [
        paper["arxiv_id"]
        for paper in selected_papers
    ]
    print(
        f"[RETRIEVE] Restricting search to "
    f"{len(selected_arxiv_ids)} selected paper(s)."
    )
    results = search_chunks(
        query_embedding=query_embedding,
    n_results=5,
    arxiv_ids=selected_arxiv_ids,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    retrieved_chunks = []

    for document, metadata in zip(documents, metadatas):
        retrieved_chunks.append({
            "text": document,
            "arxiv_id": metadata["arxiv_id"],
            "title": metadata["title"],
            "chunk_id": metadata["chunk_id"],
        })

    print(
        f"[RETRIEVE] Retrieved "
        f"{len(retrieved_chunks)} relevant chunks."
    )

    return {
        "retrieved_chunks": retrieved_chunks,
        "error": None,
    }


def answer_question_node(state: AgentState) -> AgentState:
    question = state["current_question"]

    retrieved_chunks = state.get(
        "retrieved_chunks",
        [],
    )

    if not retrieved_chunks:
        return {
            "current_answer": (
                "I could not find relevant evidence "
                "in the indexed papers."
            )
        }


    qa_history = state.get("qa_history", [])

    history_text = ""

    if qa_history:
        history_parts = []

        for item in qa_history:
            history_parts.append(
                f"User: {item['question']}\n"
                f"Assistant: {item['answer']}"
            )

        history_text = "\n\n".join(history_parts)

   
    context_parts = []

    for i, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        context_parts.append(
            f"""
[Source {i}]
Paper: {chunk['title']}
arXiv ID: {chunk['arxiv_id']}
Chunk ID: {chunk['chunk_id']}

{chunk['text']}
"""
        )

    context = "\n".join(context_parts)

    

    prompt = f"""
You are a research-paper analysis assistant.

Answer the user's question using ONLY the
provided paper excerpts.

You may use the previous conversation to
understand references such as:
- "it"
- "they"
- "this method"
- "the previous approach"
- "that dataset"

However, factual claims must be supported
by the provided paper excerpts.

If the excerpts do not contain enough evidence,
say that explicitly.

Do not invent:
- results
- numbers
- datasets
- methods
- citations
- conclusions

Previous conversation:

{history_text if history_text else "No previous questions."}

Current question:

{question}

Relevant paper excerpts:

{context}

Answer:
"""

    print("\n[OLLAMA] Generating answer...")

    answer = generate(prompt)

    print("[OLLAMA] Answer received.")

  

    updated_history = [
        *qa_history,
        {
            "question": question,
            "answer": answer,
        },
    ]

    return {
        "current_answer": answer,
        "qa_history": updated_history,
        "error": None,
    }