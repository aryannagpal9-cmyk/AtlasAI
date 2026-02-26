from langchain_huggingface import HuggingFaceEmbeddings

_embeddings_client = None

def get_embeddings_client():
    """Lazy-load the embeddings client to avoid initializing on every import."""
    global _embeddings_client
    if _embeddings_client is None:
        # Using a fast, lightweight local model for embeddings (no API key required)
        _embeddings_client = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings_client

def generate_embedding(text: str) -> list[float]:
    """Generate a 384-dimensional vector embedding for the given text."""
    client = get_embeddings_client()
    return client.embed_query(text)
