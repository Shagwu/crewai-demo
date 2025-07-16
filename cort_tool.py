from crewai.tools.base_tool import BaseTool
import subprocess

class CoRTTool(BaseTool):
    name: str = "CoRT Recursive Thinking Tool"
    description: str = "Uses recursive self-evaluation to improve answers to complex questions."

    def _run(self, query: str) -> str:
        try:
            result = subprocess.run(
                [
                    "python3",
                    "crewai-CORT/recursive_thinking_ai.py",
                    "--prompt", query
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        
