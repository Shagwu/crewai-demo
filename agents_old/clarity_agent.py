from crewai import Agent
from langchain_community.llms import Ollama

llm = Ollama(model="mistral:latest")

clarity_agent = Agent(
    role="Clarity Expert",
    goal="Extract and clarify complex ideas from dense text",
    backstory="A specialist in making difficult material easier to digest",
    llm=llm
)