# atomic_stoic_agent.py
from typing import List
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
import instructor
import openai

# --- Connect to Ollama ---
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "ollama"  # dummy placeholder key

# --- Define schema ---
class StoicOutputSchema(BaseIOSchema):
    chat_message: str = Field(..., description="Agent response")
    suggested_questions: List[str] = Field(..., description="Follow-up questions")

# --- Define system prompt ---
system_prompt = SystemPromptGenerator(
    background=["You are a calm and thoughtful Stoic advisor."],
    steps=[
        "Understand the user's concern.",
        "Respond using insights from Stoicism (Marcus Aurelius, Epictetus, etc.).",
        "Suggest 3 follow-up questions for reflection."
    ],
    output_instructions=[
        "Keep answers brief but meaningful.",
        "End with 3 questions that encourage introspection."
    ]
)

# --- Build the agent ---
stoic_agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI()),
        model="mistral",  # ← Use your downloaded model
        system_prompt_generator=system_prompt,
        output_schema=StoicOutputSchema
    )
)

if __name__ == "__main__":
    response = stoic_agent.run("How do I stay calm when overwhelmed?")
    print("\n🧘 Stoic Reply:\n", response.chat_message)
    print("\n🧠 Reflect on:\n" + "\n".join(f"- {q}" for q in response.suggested_questions))