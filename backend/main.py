"""
ADK Orchestrator - Main Application Runner
This script initializes and runs the Humsafar Financial AI Assistant.
"""
import os
import asyncio
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from src.fi_mcp_data_access import FIMCPDataAccess
from src.orchestration.adk_orchestrator import create_financial_orchestrator


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> Sending Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
        print(f"\n<<< Agent Response: {final_response_text}")
        return final_response_text
    except Exception as e:
        error_msg = f"Error during agent execution: {str(e)}"
        print(f"<<< Error: {error_msg}")
        return error_msg


"""Main function to set up and run the orchestrated agent system."""
# --- 1. Initial Setup & Instantiation ---
load_dotenv()
#os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "hum-safer-hai-produciotn")
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Define user context
USER_ID = "4444444444"  # Using the "Debt-Heavy Low Performer" for a rich test case

# Instantiate DAL
dal = FIMCPDataAccess(phone_number=USER_ID)

# --- 2. Create the orchestrator using the factory function ---
model = "gemini-2.0-flash"
orchestrator_agent = create_financial_orchestrator(dal, model)

async def main():
    # --- 3. Implement the ADK Runner ---
    session_service = InMemorySessionService()
    APP_NAME = "humsafar_financial_ai"
    SESSION_ID = "session_001"
    
    # Create the session first
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"✅ Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    
    runner = Runner(
        agent=orchestrator_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    print(f"✅ ADK Runner created for agent '{runner.agent.name}'.")

    # Define a complex query to test the end-to-end functionality
    complex_query = ("Provide a detailed summary of my assets, liabilities, and expenses for the last 30 days. "
                    "Also, analyze any unusual spending patterns, review my investment performance, "
                    "check my credit score, and suggest ways to optimize my financial health.")
    complex_query = ("Provide a detailed summary of  expenses for the last 7 days.  ")
    complex_query = ("What is my total net worth? ")
    complex_query = ("What are my top 3 spending  in the last 90 days? ")
    complex_query = ("What is 80C will save my money ")
    complex_query = ("what is top income on this year  ")
    complex_query = ("what is my cashflow  ")
    complex_query = ("compare the loan and income  give me detail information  ")
    complex_query = ("what are the top stock investent and mf investmet ")
    complex_query = ("what are the top stock investent and mf investmet ")
    
    
    print(f"\n🚀 Attempting to execute complex query through ADK orchestrator...")
    
    # Execute the complex query
    result = await call_agent_async(
        query=complex_query,
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    print(f"\n✅ Query execution completed. Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())