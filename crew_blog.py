# crew_blog.py
import os
os.environ["DISABLE_TELEMETRY"] = "true"

from crewai import Agent, Task, Crew
from tools import scrape_tool

# ✅ Use ChatOllama directly — no CrewAI LLM wrapper
from langchain_ollama import ChatOllama

# Connect directly to Ollama
llm = ChatOllama(
    model="phi3:mini",
    base_url="http://localhost:11434",  # Where Ollama is running
    temperature=0.7,
    num_predict=1024,
    repeat_last_n=64
)

# Define researcher
researcher = Agent(
    role="Research Specialist",
    goal="Find one clear, actionable mindful tech habit from trusted sources",
    backstory="You extract key insights from articles without getting distracted by ads or navigation.",
    llm=llm,
    tools=[scrape_tool],
    verbose=True
)

# Define writer
writer = Agent(
    role="Content Writer",
    goal="Turn research into warm, engaging blog content",
    backstory="You write clearly and kindly, helping people live with more intention.",
    llm=llm,
    verbose=True
)

# Research task
research_task = Task(
    description="Visit https://www.mindful.org/what-is-mindfulness/ and find one specific, actionable habit for using technology more mindfully. Summarize it in 1-2 sentences.",
    expected_output="One clear, actionable habit with a brief explanation (1-2 sentences).",
    agent=researcher
)

# Write task
write_task = Task(
    description="Write a 300-word blog post titled 'One Small Habit to Use Tech More Mindfully' based on the research. Use a warm, conversational tone.",
    expected_output="A complete blog post in markdown format.",
    agent=writer
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

# Run
if __name__ == "__main__":
    print("🐝 Qween Bee says: Creating your mindful tech blog...\n")
    result = crew.kickoff()
    print("\n📝 Final Output:")
    print(result)