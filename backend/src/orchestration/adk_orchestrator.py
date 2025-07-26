"""
Orchestrator Factory Module

This module builds the main orchestrator agent by assembling specialist agents.
"""
from google.adk.agents import Agent
from google.adk.tools import agent_tool

# Import the factory functions for ALL agents
from src.agents.general_knowledge_agent import create_general_knowledge_adk_agent
from src.agents.expense_agent import create_expense_adk_agent
from src.agents.investment_agent import create_investment_adk_agent
from src.agents.loan_agent import create_loan_adk_agent
from src.agents.net_worth_agent import create_net_worth_adk_agent
from src.agents.financial_health_auditor_agent import create_financial_health_auditor_adk_agent
from src.agents.goal_investment_strategy_agent import create_goal_investment_strategy_adk_agent

def create_financial_orchestrator(dal, model: str) -> Agent:
    """Builds and returns the main Financial Orchestrator Agent."""
    
    # 1. Create instances of all seven specialist ADK agents using their factories
    general_agent = create_general_knowledge_adk_agent(model)
    expense_agent = create_expense_adk_agent(dal, model)
    investment_agent = create_investment_adk_agent(dal, model)
    loan_agent = create_loan_adk_agent(dal, model)
    networth_agent = create_net_worth_adk_agent(dal, model)
    auditor_agent = create_financial_health_auditor_adk_agent(dal, model)
    
    # Create Goal & Investment Strategy Agent with specific users
    # User 1 (Male): 1313131313 (Balanced Growth Tracker)
    # User 2 (Female): 2222222222 (Wealthy Investor)
    goal_strategy_agent = create_goal_investment_strategy_adk_agent("1313131313", "2222222222", model)
    
    print("✅ All specialist ADK Agents instantiated via factories.")

    # 2. Wrap the specialist agents to be used as tools
    sub_agents_as_tools = [
        agent_tool.AgentTool(agent=general_agent),
        agent_tool.AgentTool(agent=expense_agent),
        agent_tool.AgentTool(agent=investment_agent),
        agent_tool.AgentTool(agent=loan_agent),
        agent_tool.AgentTool(agent=networth_agent),
        agent_tool.AgentTool(agent=auditor_agent),
        agent_tool.AgentTool(agent=goal_strategy_agent)
    ]

    # 3. Create and return the main orchestrator agent
    orchestrator_agent = Agent(
        name="Financial_Orchestrator_Agent",
        model=model,
        description=(
            "You are a master financial assistant. Your job is to understand a user's query, "
            "break it down, and delegate parts to the correct specialist agent. "
            "Use the General_Knowledge_Agent for public information like tax laws. "
            "Use the other agents for the user's personal financial data. "
            "Use the Goal_Investment_Strategy_Agent for savings recommendations, financial goals, "
            "investment timelines, and when users ask about reaching goals 'faster' or 'quicker'. "
            "Finally, synthesize the information into a single, comprehensive response."
        ),
        tools=sub_agents_as_tools,
    )
    print(f"✅ Orchestrator Agent '{orchestrator_agent.name}' created.")
    return orchestrator_agent