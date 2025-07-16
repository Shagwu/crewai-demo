import json
import os

def run_strategy_agent(user_goal):
    prd = {
        "project_goal": user_goal,
        "user_persona": "AI-curious creator or marketer",
        "target_outcome": "Deploy a working micro-app or automation",
        "success_metrics": [
            "Working MVP",
            "SEO-optimized content",
            "Deployment via Vercel"
        ],
        "recommended_tools": ["Cursor", "Claude", "Firecrawl"]
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/prd.md", "w") as f:
        f.write("# Product Requirement Document\n\n")
        f.write(json.dumps(prd, indent=2))

    return prd