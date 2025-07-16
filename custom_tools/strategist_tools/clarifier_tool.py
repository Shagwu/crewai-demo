from crewai_tools.tools.tool import Tool

ClarifierTool = Tool(
    name="clarifier_tool",
    description="Asks 3 clarifying questions based on a business goal.",
    func=lambda input: (
        f"To clarify your goal: '{input}', here are 3 questions:\n"
        f"1. What specific outcome are you trying to achieve?\n"
        f"2. Who is this goal meant to serve?\n"
        f"3. What blockers or unknowns are in your way?"
    )
)