# debug_agent.py
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from tools import scrape_tool
import os

# Disable telemetry
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Use phi3:mini directly
llm = ChatOllama(
    model="phi3:mini",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Define tools
tools = [
    Tool(
        name="Read website content",
        func=scrape_tool._run,
        description="Use this to scrape content from a website when researching mindful tech practices."
    )
]

# Define prompt
prompt = PromptTemplate.from_template("""
You are a mindful tech guide. Your job is to find one actionable habit for using technology more intentionally.

Task: Visit {url} and extract one specific, actionable habit for using technology more mindfully. Summarize it in 1-2 sentences.

Only return the habit — no extra text.
""")

# Create chain
chain = prompt | llm

# Run
print("🐝 Qween Bee says: Testing direct Ollama call...\n")
result = chain.invoke({"url": "https://www.mindful.org/what-is-mindfulness/"})
print("✅ Success! Here's what the AI said:\n")
print(result.content)