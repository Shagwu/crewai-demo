import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fastapi import FastAPI
from pydantic import BaseModel
from agents.run_agent import run_agent  # ✅ Direct import
import litellm
litellm.provider = "ollama"
from dotenv import load_dotenv
import os

load_dotenv()  # this loads the .env file into os.environ

# Optional: confirm it worked
print("Opik Key:", os.getenv("OPIK_API_KEY"))
print("Workspace:", os.getenv("OPIK_WORKSPACE"))

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "Server is running fine!"}

class AgentInput(BaseModel):
    url: str

@app.post("/ask")
def ask_agent(data: AgentInput):
    try:
        results = run_agent(data.url)
        return {
            "summary": results[0],
            "rewrite": results[1],
            "strategy": results[2]
        }
    except Exception as e:
        return {"error": str(e)}