"""
FastAPI Application for Humsafar Financial AI Assistant
This application provides REST API endpoints for the financial AI assistant.
"""
import os
import asyncio
import inspect
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from src.fi_mcp_data_access import FIMCPDataAccess
from src.orchestration.adk_orchestrator import create_financial_orchestrator
from src.agents.net_worth_agent import NetWorthAndHealthAgent
from src.agents.expense_agent import ExpenseAndCashflowAgent
from src.agents.investment_agent import InvestmentAnalystAgent
from src.agents.loan_agent import LoanAndCreditAgent
from src.agents.financial_health_auditor_agent import FinancialHealthAuditorAgent
from src.agents.goal_investment_strategy_agent import GoalInvestmentStrategyAgent

# Load environment variables
load_dotenv()
#os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "hum-safer-hai-produciotn")
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# FastAPI app initialization
app = FastAPI(
    title="Humsafar Financial AI Assistant",
    description="AI-powered financial assistant providing personalized financial insights and recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:3000",
        "http://localhost:9002", 
        "http://34.28.47.132:9002",
        "https://34.28.47.132:9002"
    ],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Global variables for session management
session_service = InMemorySessionService()
APP_NAME = "humsafar_financial_ai"
runners = {}  # Cache runners by user_id

# Create a new API Router for agent tools
tools_router = APIRouter(
    prefix="/tools",
    tags=["Agent Tools"],
)


async def run_all_tools(agent_instance) -> dict:
    """
    Inspects an agent instance, runs all its public tool methods,
    and returns a dictionary of the results.
    """
    results = {}
    public_methods = [
        method_name for method_name, _ in inspect.getmembers(agent_instance, inspect.ismethod)
        if not method_name.startswith('_')
    ]
    
    for tool_name in public_methods:
        try:
            method_to_call = getattr(agent_instance, tool_name)
            # This assumes all tools are async or can be run in an async context
            # If you have a mix, you might need to inspect and handle differently
            if asyncio.iscoroutinefunction(method_to_call):
                results[tool_name] = await method_to_call()
            else:
                results[tool_name] = method_to_call()
        except Exception as e:
            results[tool_name] = {"error": str(e)}
            
    return results


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    response: str
    user_id: str
    session_id: str
    status: str


class HealthResponse(BaseModel):
    status: str
    message: str


async def get_or_create_runner(user_id: str) -> Runner:
    """Get or create a runner for the specified user."""
    if user_id not in runners:
        # Instantiate DAL for the user
        dal = FIMCPDataAccess(phone_number=user_id)
        
        # Create the orchestrator using the factory function
        model = "gemini-2.5-flash"
        orchestrator_agent = create_financial_orchestrator(dal, model)
        
        # Create the runner
        runner = Runner(
            agent=orchestrator_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
        
        runners[user_id] = runner
        print(f"✅ Created new runner for user: {user_id}")
    
    return runners[user_id]


async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str) -> str:
    """Sends a query to the agent and returns the final response."""
    print(f"\n>>> Processing Query for User {user_id}: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
        
        print(f"\n<<< Agent Response for User {user_id}: {final_response_text[:100]}...")
        return final_response_text
    
    except Exception as e:
        error_msg = f"Error during agent execution: {str(e)}"
        print(f"<<< Error for User {user_id}: {error_msg}")
        return error_msg


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for health check."""
    return HealthResponse(
        status="healthy",
        message="Humsafar Financial AI Assistant is running"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Service is operational"
    )


@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a financial query for a specific user."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{request.user_id}_{os.urandom(4).hex()}"
        
        # Get or create runner for the user
        runner = await get_or_create_runner(request.user_id)
        
        # Create session if it doesn't exist
        try:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=request.user_id,
                session_id=session_id
            )
        except Exception:
            # Session might already exist, which is fine
            pass
        
        # Process the query
        response = await call_agent_async(
            query=request.query,
            runner=runner,
            user_id=request.user_id,
            session_id=session_id
        )
        
        return QueryResponse(
            response=response,
            user_id=request.user_id,
            session_id=session_id,
            status="success"
        )
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@tools_router.get("/net_worth/{user_id}")
async def get_net_worth_tools(user_id: str):
    dal = FIMCPDataAccess(phone_number=user_id)
    agent = NetWorthAndHealthAgent(dal)
    return await run_all_tools(agent)

@tools_router.get("/expense/{user_id}")
async def get_expense_tools(user_id: str):
    dal = FIMCPDataAccess(phone_number=user_id)
    agent = ExpenseAndCashflowAgent(dal)
    return await run_all_tools(agent)

@tools_router.get("/investment/{user_id}")
async def get_investment_tools(user_id: str):
    dal = FIMCPDataAccess(phone_number=user_id)
    agent = InvestmentAnalystAgent(dal)
    return await run_all_tools(agent)

@tools_router.get("/loan/{user_id}")
async def get_loan_tools(user_id: str):
    dal = FIMCPDataAccess(phone_number=user_id)
    agent = LoanAndCreditAgent(dal)
    return await run_all_tools(agent)

@tools_router.get("/financial_audit/{user_id}")
async def get_financial_audit_tools(user_id: str):
    dal = FIMCPDataAccess(phone_number=user_id)
    agent = FinancialHealthAuditorAgent(dal)
    return await run_all_tools(agent)


async def list_user_sessions(user_id: str):
    """List all sessions for a specific user."""
    # This would need to be implemented based on session service capabilities
    return {"user_id": user_id, "message": "Session listing not implemented yet"}


@app.delete("/users/{user_id}/sessions/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """Delete a specific session."""
    # This would need to be implemented based on session service capabilities
    return {"message": f"Session {session_id} deletion not implemented yet"}


@app.get("/users")
async def list_available_users():
    """List available test users (personas)."""
    # Read from the test data directory to get available user personas
    try:
        test_data_path = "FI money dummy data/test_data_dir"
        if os.path.exists(test_data_path):
            users = [d for d in os.listdir(test_data_path) 
                    if os.path.isdir(os.path.join(test_data_path, d))]
            return {"available_users": users}
        else:
            return {"available_users": ["4444444444", "1010101010", "1111111111"]}  # Default test users
    except Exception as e:
        return {"error": f"Could not list users: {str(e)}"}


@tools_router.get("/goals")
async def get_all_goals():
    """Get all investment goals for hardcoded users."""
    try:
        # Taking two  user IDs for demonstration
        user_ids = ["1212121212", "2222222222"]
        results = {}

        import json
        with open("./FI money dummy data/combined_goals.json",'r') as file:
            results = json.load(file)
        
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching goals: {str(e)}")
# Include the tools router in the main FastAPI app
app.include_router(tools_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
