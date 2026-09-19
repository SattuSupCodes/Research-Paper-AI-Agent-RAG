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

    query_embedding = emb_texts([question])[0]

    results = search_chunks(
        query_embedding=query_embedding,
        n_results=5,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    retrieved_chunks = []

    for document, metadata in zip(
        documents,
        metadatas,
    ):
        retrieved_chunks.append({
            "text": document,
            "arxiv_id": metadata["arxiv_id"],
            "title": metadata["title"],
            "chunk_id": metadata["chunk_id"],
        })

    print(
        f"[RETRIEVE] Retrieved "
        f"{len(retrieved_chunks)} chunks"
    )

    return {
        "retrieved_chunks": retrieved_chunks,
        "error": None,
    }
def amnswer_question_node(state:AgentState)->AgentState:
    question=state["current_question"]
    retrieved_chunks = state.get("retrieved_chunks",[],)
    if not retrieved_chunks:
        return{
             "current_answer": (
                "I could not find relevant evidence "
                "in the indexed papers."
            )
        }
    context_parts = []
    for i , chunk in enumerate(
        retrieved_chunks, start=1,
    ):
        context_parts.append(
            f"[Source {i}]\n"
            f"Paper: {chunk['title']}\n"
            f"arXiv ID: {chunk['arxiv_id']}\n"
            f"{chunk['text']}"
        )
    context = "\n\n".join(context_parts)
    prompt = f"""
You are a research-paper analysis assistant.

Answer the user's question using ONLY the
provided paper excerpts.

If the excerpts do not contain enough evidence,
say so explicitly.

Do not invent results, numbers, claims, or citations.

Question:
{question}

Paper excerpts:
{context}

Answer:
"""
    answer = generate(prompt)
    return{
         "current_answer": answer,
        "qa_history": [
            *state.get("qa_history", []),
            {
                "question": question,
                "answer": answer,
            },
        ],
        "error": None,
    }