import os
import sys
from datetime import datetime
from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOllama

# Load Ollama model
llm = ChatOllama(model="mistral", temperature=0.2)

# Agents
researcher = Agent(
    role='AI Researcher',
    goal='Discover breakthroughs in open-source LLMs',
    backstory='You are a technical expert with deep understanding of recent LLM developments.',
    llm=llm
)

strategist = Agent(
    role='AI Strategist',
    goal='Turn research into growth strategies for AI content or business',
    backstory='You specialize in turning insights into content and branding moves.',
    llm=llm
)

# Map task to agent
def get_task(agent_name):
    if agent_name == "researcher":
        return Task(
            description="List 3 important recent developments in open-source language models.",
            expected_output="A list of 3 major open-source LLM projects with a one-line description each.",
            agent=researcher,
        )
    elif agent_name == "strategist":
        return Task(
            description="Based on recent research, give 3 content or strategy moves for an AI personal brand.",
            expected_output="3 tactical content or brand strategy ideas written clearly for LinkedIn or YouTube.",
            agent=strategist,
        )
    else:
        raise ValueError("Invalid agent name. Use 'researcher' or 'strategist'.")

# Save to markdown
def export_to_markdown(agent_name, result_text):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"exports/{agent_name}_{now}.md"
    with open(filename, "w") as f:
        f.write(f"# Result from {agent_name.capitalize()} Agent\n")
        f.write(f"**Timestamp**: {now}\n\n")
        f.write("## Output\n")
        f.write(result_text)
    print(f"📁 Exported result to `{filename}`")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_agent.py [researcher|strategist]")
        sys.exit(1)

    agent_name = sys.argv[1]
    task = get_task(agent_name)

    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    print("\n💡 Final Output:\n", result)

    export_to_markdown(agent_name, result)