# tools/extract_and_index.py
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.ollama import OllamaEmbedding
import os

def extract_and_index_docs(folder_path="data/ingested_docs", storage_path="llamaindex/vector_store"):
    # Load and parse docs
    documents = SimpleDirectoryReader(folder_path).load_data()

    # Set up embeddings using Ollama
    embed_model = OllamaEmbedding(model_name="nomic-embed-text")  # or mistral, llama3, etc.

    # Store or load index
    if os.path.exists(storage_path):
        storage_context = StorageContext.from_defaults(persist_dir=storage_path)
        index = load_index_from_storage(storage_context)
    else:
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        index.storage_context.persist(persist_dir=storage_path)

    return "Documents indexed successfully!"