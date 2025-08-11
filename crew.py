from crewai import Agent, Task, Crew, LLM

# Step 1: Define the LLM
llm = LLM(model="ollama/qwen:7b", base_url="http://localhost:11434")

# Step 2: Create the Agent (✅ includes required `backstory`)
qwen_agent = Agent(
    role="Mindful Tech Guide",
    goal="Provide three ways to practice mindful technology use in daily life.",
    backstory=(
        "You are a calm and insightful technology advisor who helps people use digital tools "
        "with intention and awareness. You promote digital well-being, focus, and balance."
    ),
    llm=llm,
    verbose=True,
)

# Step 3: Define the Task
task = Task(
    description="List three practical and actionable ways to practice mindful technology use in daily life.",
    agent=qwen_agent,
    expected_output="A numbered list of three realistic, easy-to-implement mindful tech habits."
)

# Step 4: Create the Crew
crew = Crew(
    agents=[qwen_agent],
    tasks=[task],
    verbose=True
)

# Step 5: Run the Crew
if __name__ == "__main__":
    print("🚀 Starting the crew...")
    result = crew.kickoff()
    print("\n✅ Result:")
    print(result)