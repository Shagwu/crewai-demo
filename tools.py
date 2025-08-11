# tools.py
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool

class ScrapeWebsiteInput(BaseModel):
    url: str = Field(..., description="The URL to scrape. Must be a valid http or https link.")

class CustomScrapeWebsiteTool(BaseTool):
    name: str = "Read website content"
    description: str = "Use this to scrape content from a website when researching mindful tech practices."
    args_schema: type[BaseModel] = ScrapeWebsiteInput

    def _run(self, url: str) -> str:
        try:
            # Clean and validate URL
            url = url.strip().split()[0]
            if not url.startswith("http"):
                url = "https://" + url

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "aside", "header", "form"]):
                element.decompose()

            # Extract readable text
            content = "\n".join([
                element.get_text(strip=True)
                for element in soup.find_all(["p", "h1", "h2", "h3"])
                if len(element.get_text(strip=True)) > 20
            ])

            return content[:4000]  # Return top 4000 chars

        except requests.exceptions.RequestException as e:
            return f"Failed to fetch page: {str(e)}"
        except Exception as e:
            return f"Scraping error: {str(e)}"

# Instantiate the tool
scrape_tool = CustomScrapeWebsiteTool()
