from sentence_transformers import SentenceTransformer
MODEL_NAME = "all-MiniLM-L6-v2"
''' 
It maps sentences & paragraphs to a 384 dimensional dense 
vector space and can be used for tasks like clustering or 
semantic search.
'''
_model = None
def get_emb_model():
    global _model
    if _model is None:
        print(
            f"[EMBED] loading model:{MODEL_NAME}"
            
        )
        _model = SentenceTransformer(MODEL_NAME)
    return _model
def emb_texts(texts:list[str])-> list[list[float]]:
    model = get_emb_model()
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return embeddings.tolist()