from app.state import AgentState
from app.services.embedding_service import emb_texts
from app.services.vector_store import add_chunks


def index_chunks_node(state: AgentState) -> AgentState:
    chunks = state.get("chunks", [])

    if not chunks:
        return {
            "error": "No chunks available for indexing."
        }

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"[EMBED] Generating embeddings for "
        f"{len(texts)} chunks..."
    )

    embeddings = emb_texts(texts)

    collection_name = add_chunks(
        chunks,
        embeddings,
    )

    print(
        f"[VECTOR] Indexed {len(chunks)} chunks "
        f"into '{collection_name}'"
    )

    return {
        "vector_collection": collection_name,
        "error": None,
    }