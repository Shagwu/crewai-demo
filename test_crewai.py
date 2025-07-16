from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="mistral", temperature=0.2)

# Agent 1: Researcher
researcher = Agent(
    role='AI Researcher',
    goal='Discover breakthroughs in open-source LLMs',
    backstory='You are a technical expert with deep understanding of recent LLM developments. You stay updated with open-source innovation.',
    llm=llm
)

# Agent 2: Strategist
strategist = Agent(
    role='AI Strategist',
    goal='Turn research into action steps for content and business strategy',
    backstory='You specialize in converting technical insights into creative ideas for AI content, personal brand growth, and monetization.',
    llm=llm
)

# Task 1: Research
research_task = Task(
    description="List 3 important recent developments in open-source language models.",
    agent=researcher,
)

# Task 2: Strategy based on research
strategy_task = Task(
    description="Based on the research, suggest 3 ways we can use this information to grow an AI-focused personal brand or startup.",
    agent=strategist,
    depends_on=[research_task]
)

# Crew
crew = Crew(
    agents=[researcher, strategist],
    tasks=[research_task, strategy_task],
    verbose=True
)

result = crew.kickoff()
print("\n🧠 Final Strategy Output:\n", result)