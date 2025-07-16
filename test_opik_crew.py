from dotenv import load_dotenv
import os
from opik import track
from crewai import Crew, Agent, Task
from litellm import completion

# Load environment variables
load_dotenv()

# ✅ Define a wrapper class with a `.call()` method
class OllamaLLMWrapper:
    def __init__(self, model="ollama/llama3"):
        self.model = model

    def call(self, messages, **kwargs):
        response = completion(
            model=self.model,
            messages=messages,
            api_base="http://localhost:11434",  # Local Ollama
        )
        return response["choices"][0]["message"]["content"]

# ✅ Pass the wrapper into the agent
local_llm = OllamaLLMWrapper()

agent = Agent(
    role="Tester",
    goal="Test Opik integration",
    backstory="An AI agent helping verify observability.",
    llm=local_llm,
    verbose=True
)

task = Task(
    description="Say hello and explain what you're doing.",
    expected_output="A friendly greeting and explanation.",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

@track
def run_crew():
    return crew.kickoff()

if __name__ == "__main__":
    result = run_crew()
    print("\n🎯 Final result:")
    print(result)