# test_crew.py
import os
os.environ["DISABLE_TELEMETRY"] = "true"  # 👈 Disable telemetry timeout

from crewai import Agent, Task, Crew, LLM

# Use CrewAI's LLM class
llm = LLM(
    model="ollama/qwen:7b",
    base_url="http://localhost:11434",
    temperature=0.7,
    max_tokens=512
)

# Define agent
mindful_guide = Agent(
    role="Mindful Tech Guide",
    goal="Share one simple, actionable way to use technology more intentionally",
    backstory=(
        "You are a calm and insightful guide who helps people reconnect with presence "
        "in a distracted world. You offer practical, science-backed tips that anyone "
        "can apply today."
    ),
    llm=llm,
    verbose=True
)

# Define task with agent assigned
task = Task(
    description="Tell me one small habit I can start today to be more mindful with my phone use.",
    expected_output="One clear, actionable tip in simple language.",
    agent=mindful_guide
)

# Create crew
crew = Crew(
    agents=[mindful_guide],
    tasks=[task],
    verbose=True
)

# Run
if __name__ == "__main__":
    print("🐝 Qween Bee says: Starting your mindful AI crew...\n")
    result = crew.kickoff()
    print("\n✨ Final Output:")
    print(result)