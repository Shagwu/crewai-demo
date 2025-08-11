# crew_mindful.py
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests
from bs4 import BeautifulSoup
import os

# Disable telemetry
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Use phi3:mini
llm = ChatOllama(
    model="phi3:mini",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Simple scraper
def scrape_mindful_site():
    url = "https://www.mindful.org/what-is-mindfulness/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()
        content = "\n".join([
            p.get_text(strip=True) 
            for p in soup.find_all("p") 
            if len(p.get_text(strip=True)) > 50
        ])
        return content[:4000]
    except Exception as e:
        return f"Error: {str(e)}"

# Run the crew
if __name__ == "__main__":
    print("🐝 Qween Bee says: Starting the Mindful Tech Crew...\n")
    
    # Step 1: Scrape
    print("🔍 Researching...")
    content = scrape_mindful_site()
    print("✅ Scraped content:", content[:200], "...\n")
    
    # Step 2: Extract habit
    print("🧠 Extracting habit...")
    habit_prompt = ChatPromptTemplate.from_template("""
You are a Mindful Tech Guide.
Based on this article, extract one specific, actionable habit for using technology more mindfully.

Article:
{content}

Return only the habit — 1-2 sentences.
""")
    habit_chain = habit_prompt | llm | StrOutputParser()
    habit = habit_chain.invoke({"content": content})
    print("✅ Habit:", habit, "\n")
    
    # Step 3: Write blog
    print("✍️ Writing blog...")
    blog_prompt = ChatPromptTemplate.from_template("""
Write a warm, 300-word blog post titled "One Small Habit to Use Tech More Mindfully".

Habit: {habit}

Use markdown. Conversational tone.
""")
    blog_chain = blog_prompt | llm | StrOutputParser()
    blog = blog_chain.invoke({"habit": habit})
    print("✅ Blog Post:\n")
    print(blog)
    
    # Step 4: Save
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/mindful_blog.md", "w") as f:
        f.write(f"# One Small Habit to Use Tech More Mindfully\n\n{blog}")
    print("\n💾 Saved to outputs/mindful_blog.md")