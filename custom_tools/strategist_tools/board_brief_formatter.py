from crewai_tools.tools.tool import Tool

BoardBriefFormatter = Tool(
    name="board_brief_formatter",
    description="Formats a summary for presenting to decision-makers.",
    func=lambda input: (
        f"📋 Board-ready Brief:\nGoal: {input}\nApproach: Clarify → Hypothesize → Test\nNext Steps: Approve test plan."
    )
)
