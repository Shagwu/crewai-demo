from crewai import Crew, Task
from agents.clarity_agent import clarity_agent  # Import your agent
from tools_old.scraper_tool import ScraperTool  # If using a scraping tool

response = clarity_agent.run("Summarize the main ideas from Marcus Aurelius' *Meditations*.")
print(response)

def run_agent(url: str):
    # Optional: you can use a tool to scrape the page content
    scraper = ScraperTool()
    content = scraper.scrape_from_url(url)

    # Define the task for the agent
    task = Task(
        description=f"Summarize the key ideas from this content:\n\n{content}",
        expected_output="Return 3 responses: a summary, a rewritten version, and a strategy.",
        agent=clarity_agent,
        output_file="clarity_output.md"
    )

    # Create the crew
    crew = Crew(
        agents=[clarity_agent],
        tasks=[task],
        verbose=True
    )

    # Run the crew and return the result
    result = crew.kickoff()
    return result.split("###")  # Optional: split into summary/rewrite/strategy