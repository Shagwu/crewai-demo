# build_index.py
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

# 1. Set up open-source models
Settings.llm = Ollama(model="llama3")  # You must have Ollama + LLaMA3 installed
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 2. Load all text/markdown/pdf files from the 'data' folder
documents = SimpleDirectoryReader("data").load_data()

# 3. Build and save the vector index
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist()

print("✅ Index created and saved to /storage")