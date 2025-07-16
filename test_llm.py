from langchain_ollama import OllamaLLM as Ollama

llm = Ollama(model="phi3:mini")

try:
    response = llm.invoke("Give me 3 tips for staying focused.")
    print("✅ LLM responded:")
    print(response)
except Exception as e:
    print("❌ LLM failed with error:")
    print(e)