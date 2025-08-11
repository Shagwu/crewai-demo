# agents.py
from crewai import Agent, LLM

# Use Ollama via CrewAI's LLM
llm = LLM(model="ollama/qwen:7b", base_url="http://localhost:11434")

researcher = Agent(
    role="Research Specialist",
    goal="Find the latest evidence-based practices for mindful technology use",
    backstory="You're a meticulous researcher who digs deep to find credible, up-to-date insights.",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Turn research into engaging, human-friendly blog content",
    backstory="You write warm, clear, and inspiring content that helps people live with more intention.",
    llm=llm,
    verbose=True
)