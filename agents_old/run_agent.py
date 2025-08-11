from crewai import Agent
from langchain_community.llms import QianfanLLMEndpoint  # Qwen API via LangChain

# Create a Qwen LLM instance
llm = QianfanLLMEndpoint(
    model="qwen-plus",   # Or exact model name like "qwen2-72b-instruct"
    temperature=0.7
)

# Define the Qwen-powered agent
qwen_agent = Agent(
    role="Mindful Tech Guide",
    goal="Help people use technology more intentionally and mindfully",
    backstory=(
        "You are a friendly digital wellness expert who blends stoic thinking "
        "with practical tips to reduce digital overwhelm."
    ),
    llm=llm  # This forces CrewAI to use Qwen instead of OpenAI
)