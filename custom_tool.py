# custom_tool.py
from crewai import BaseTool  # ← This is the correct import
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup

class ScrapeWebsiteInput(BaseModel):
    url: str = Field(..., description="The URL to scrape")

class LocalWebScraperTool(BaseTool):
    name: str = "Local Web Scraper"
    description: str = "Scrapes content from a given URL and returns readable text."
    args_schema: type[BaseModel] = ScrapeWebsiteInput

    def _run(self, url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()

            text = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2'])])
            return text[:2000]
        except Exception as e:
            return f"Error: {str(e)}"