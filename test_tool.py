# test_tool.py
from tools import scrape_tool

result = scrape_tool.run("https://www.mindful.org/what-is-mindfulness/")
print(result)