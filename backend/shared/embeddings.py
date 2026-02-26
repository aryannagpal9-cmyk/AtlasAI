from langchain_huggingface import HuggingFaceEndpointEmbeddings

_embeddings_client = None

def get_embeddings_client():
    """Lazy-load the embeddings client (API-based) to avoid initializing on every import."""
    global _embeddings_client
    if _embeddings_client is None:
        # Using HuggingFace Inference API for embeddings (requires HUGGINGFACEHUB_API_TOKEN)
        # This keeps the package size small by avoiding local model downloads/torch.
        _embeddings_client = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
        )
    return _embeddings_client

def generate_embedding(text: str) -> list[float]:
    """Generate a 384-dimensional vector embedding for the given text via API."""
    client = get_embeddings_client()
    return client.embed_query(text)
