import chromadb

CHROMA_PATH = "data/chroma"
client = chromadb.PersistentClient(path=CHROMA_PATH)
def get_collection(name:str = "research_papers"):
    return client.get_or_create_collection(
        name=name,
        metadata={
            "hnsw:space": "cosine"
        },
    )
def add_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
):
    collection = get_collection()

    ids = []
    documents = []
    metadatas = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        chunk_id = (
            f"{chunk['arxiv_id']}_"
            f"{chunk['chunk_id']}_"
            f"{index}"
        )

        ids.append(chunk_id)
        documents.append(chunk["text"])

        metadatas.append({
            "arxiv_id": chunk["arxiv_id"],
            "title": chunk["title"],
            "chunk_id": chunk["chunk_id"],
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return collection.name


def search_chunks(
    query_embedding,
    n_results=5,
    arxiv_ids=None,
):
    collection = get_collection()

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
    }

    if arxiv_ids:
        query_kwargs["where"] = {
            "arxiv_id": {
                "$in": arxiv_ids
            }
        }

    return collection.query(**query_kwargs)