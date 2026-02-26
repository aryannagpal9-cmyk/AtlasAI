import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.shared.embeddings import get_embeddings_client

def verify_client():
    print("Checking embeddings client...")
    try:
        client = get_embeddings_client()
        print(f"Client initialized: {type(client)}")
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        if isinstance(client, HuggingFaceEndpointEmbeddings):
            print("SUCCESS: Client is HuggingFaceEndpointEmbeddings (API-based)")
        else:
            print(f"FAILURE: Client is of type {type(client)}")
    except Exception as e:
        print(f"Error during client initialization: {e}")

if __name__ == "__main__":
    verify_client()
