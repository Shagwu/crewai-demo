from custom_tools.strategist_tools.clarifier_tool import ClarifierTool
from custom_tools.strategist_tools.hypothesis_generator import HypothesisGenerator
from custom_tools.strategist_tools.board_brief_formatter import BoardBriefFormatter

from crewai import Agent, Crew

tools = [ClarifierTool, HypothesisGenerator, BoardBriefFormatter]

strategist = Agent(
    role="AI Consultant",
    goal="Help the user turn their business goal into a clear, testable strategy.",
    backstory="You're an expert strategist who helps users clarify goals and design smart experiments.",
    tools=tools,
    allow_delegation=False,
    verbose=True
)

crew = Crew(agents=[strategist])
output = crew.run("I want to 10x my audience in 60 days")

print("\n🧠 Output from StrategistAgent:\n")
print(output)