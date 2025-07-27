
import os
import asyncio
from dotenv import load_dotenv


from src.fi_mcp_data_access import FIMCPDataAccess
from src.orchestration.adk_orchestrator import create_financial_orchestrator

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# Define user context
USER_ID = "4444444444"  # Using the "Debt-Heavy Low Performer" for a rich test case

# Instantiate DAL
dal = FIMCPDataAccess(phone_number=USER_ID)

# --- 2. Create the orchestrator using the factory function ---
model = "gemini-2.5-flash"
orchestrator_agent = create_financial_orchestrator(dal, model)

root_agent = orchestrator_agent
