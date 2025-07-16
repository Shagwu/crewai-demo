from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Set up local HuggingFace embedding model (instead of OpenAI)
from llama_index.core import Settings
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load TinyLlama model and tokenizer for local generation
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="cpu")

# Build generation pipeline
hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
)

# Register the HuggingFace pipeline as your LLM
Settings.llm = HuggingFaceLLM(
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
)

# Load the index from disk
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)

# Create a query engine
query_engine = index.as_query_engine()

# Ask your question
response = query_engine.query("What is the relationship between Stoicism and AI?")
print(response)