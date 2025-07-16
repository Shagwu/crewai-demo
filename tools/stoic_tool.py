from crewai_tools import BaseTool
from atomic.atomic_stoic_agent import stoic_agent

class StoicAdvisorTool(BaseTool):
    name = "stoic_advisor"
    description = "Responds to mindset or focus struggles using Stoic wisdom."

    def _run(self, query: str) -> str:
        result = stoic_agent.run(query)
        return f"{result.chat_message}\n\nReflect on:\n" + "\n".join(f"- {q}" for q in result.suggested_questions)