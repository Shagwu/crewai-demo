from crewai_tools.tools.tool import Tool

HypothesisGenerator = Tool(
    name="hypothesis_generator",
    description="Generates 3 hypotheses that could solve the user's goal.",
    func=lambda input: (
        f"Based on the goal '{input}', here are 3 hypotheses:\n"
        f"1. Creating daily video content will 3x audience growth.\n"
        f"2. Targeting 1 niche per week improves engagement.\n"
        f"3. Leveraging DMs converts 2x better than landing pages."
    )
)