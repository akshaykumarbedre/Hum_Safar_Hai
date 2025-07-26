"""
General Knowledge Agent with Search Capability.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search


def create_general_knowledge_adk_agent(model: str) -> Agent:
    """
    Factory function to create the General Knowledge ADK Agent.
    This agent uses a search tool to answer questions outside the user's personal data.
    """
    return Agent(
        name="General_Knowledge_Agent",
        model=model,
        description=(
            "Answers general financial questions using real-time search. "
            "Use this for topics like tax laws (e.g., 'tax on gold', '80C benefits'), "
            "financial regulations, market trends, and definitions of financial terms. "
            "Do not use this for questions about the user's personal financial data."
        ),
        tools=[google_search],
    )