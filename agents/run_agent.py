from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM
import requests
from bs4 import BeautifulSoup
import sys
import os
import json
from agents.strategy_agent import run_strategy_agent
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# === LLM Setup ===
llm = OllamaLLM(model="phi3:mini")

# === Scraper Function ===
def scrape_text_from_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        if "429 Too Many Requests" in text or response.status_code == 429:
            return "[Scrape Error] Rate limited. Try again later or change headers."

        return text[:5000]

    except Exception as e:
        return f"[Scrape Error] {e}"

# === Agent Logic ===
def run_agent(url):
    scraped_text = scrape_text_from_url(url)

     # New strategy agent run
    strategy_output = run_strategy_agent("Summarize and repurpose this URL into a PRD")

     # Summary agent starts here
    summary_agent = Agent(
        role="AI Researcher",
        goal="Digest and summarize long online content",
        backstory="You're a sharp summarizer trained to extract deep insights from messy webpages.",
        verbose=True,
        llm=llm,
    )

    summary_task = Task(
        description=f"Summarize this article in 3–5 bullet points. Focus on what's most insightful:\n\n{scraped_text}",
        agent=summary_agent,
        expected_output="A clear list of 3–5 key takeaways in bullet form"
    )

    rewriter_agent = Agent(
        role="Content Alchemist",
        goal="Turn complex summaries into social media gold",
        backstory="You write like a human — clear, concise, and punchy. Your rewrites are made for Instagram, LinkedIn, and TikTok scripts.",
        verbose=True,
        llm=llm,
    )

    rewrite_task = Task(
        description="Take the bullet point summary from the researcher and rewrite it into a short Instagram caption or carousel draft.",
        agent=rewriter_agent,
        expected_output="A rewritten caption or carousel content ready for social media"
    )

    crew = Crew(
        agents=[summary_agent, rewriter_agent],
        tasks=[summary_task, rewrite_task],
        verbose=True
    )

    results = crew.kickoff()
    return {
        "summary": results[0],
        "rewrite": results[1]
    }

# === Optional CLI Usage ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py https://example.com")
        sys.exit(1)

    url = sys.argv[1]
    output = run_agent(url)
    print(json.dumps(output, indent=2))