"""
Exhaustive Test Runner for All Agents and Users (Enhanced)

This script systematically tests every public tool method on every specialist
agent for every available user persona. It includes enhanced diagnostics to
distinguish between data fetching/initialization errors and tool execution errors.
"""
import os
import sys
import asyncio
import inspect
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the Python path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from src.fi_mcp_data_access import FIMCPDataAccess
from src.agents.net_worth_agent import NetWorthAndHealthAgent
from src.agents.expense_agent import ExpenseAndCashflowAgent
from src.agents.investment_agent import InvestmentAnalystAgent
from src.agents.loan_agent import LoanAndCreditAgent
from src.agents.financial_health_auditor_agent import FinancialHealthAuditorAgent

# List of all specialist agent classes we want to test
AGENT_CLASSES_TO_TEST = [
    NetWorthAndHealthAgent,
    ExpenseAndCashflowAgent,
    InvestmentAnalystAgent,
    LoanAndCreditAgent,
    FinancialHealthAuditorAgent,
]

def get_public_methods(agent_instance):
    """Inspects an agent instance and returns a list of its public methods."""
    return [
        method_name for method_name, _ in inspect.getmembers(agent_instance, inspect.ismethod)
        if not method_name.startswith('_')
    ]

async def main():
    """Main function to run the exhaustive test suite."""
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    print("🚀 Starting Exhaustive Test Run with Enhanced Diagnostics...")
    
    temp_dal = FIMCPDataAccess(phone_number="0")
    all_user_ids = temp_dal.get_available_users()

    if not all_user_ids:
        print("❌ No user data found. Aborting test run.")
        return

    print(f"Found {len(all_user_ids)} user personas to test against.")

    results = {"passed": 0, "failed": 0, "failures": []}
    total_tests = 0

    for user_id in all_user_ids:
        print(f"\n--- Testing User ID: {user_id} ---")
        user_dal = FIMCPDataAccess(phone_number=user_id)
        
        for agent_class in AGENT_CLASSES_TO_TEST:
            agent_name = agent_class.__name__
            agent_instance = None
            
            # Phase 1: Test Agent Initialization (and underlying data fetching)
            try:
                agent_instance = agent_class(user_dal)
            except Exception as e:
                # If agent fails to initialize, all its tools fail by default.
                print(f"  - 🚨 FAILED to initialize {agent_name}. Error in data fetching/loading.")
                # We need to know how many tools this agent has to count failures accurately.
                # Create a dummy instance without DAL to inspect methods if needed, or estimate.
                num_tools = len([m for m in dir(agent_class) if not m.startswith('_')])
                for _ in range(num_tools):
                    total_tests += 1
                    results["failed"] += 1
                    results["failures"].append({
                        "user_id": user_id, "agent": agent_name, "tool": "N/A - Initialization Failed",
                        "stage": "Data Loading / Init", "error": str(e)
                    })
                continue # Skip to the next agent

            # Phase 2: Test each tool if initialization succeeded
            tool_methods = get_public_methods(agent_instance)
            for tool_name in tool_methods:
                total_tests += 1
                print(f"  - Testing {agent_name}.{tool_name}... ", end="")
                try:
                    method_to_call = getattr(agent_instance, tool_name)
                    # This call executes the function's logic
                    result = method_to_call()
                    print("✅ PASS")
                    results["passed"] += 1
                except Exception as e:
                    print(f"❌ FAIL")
                    results["failed"] += 1
                    results["failures"].append({
                        "user_id": user_id, "agent": agent_name, "tool": tool_name,
                        "stage": "Tool Execution", "error": str(e)
                    })

    # --- Print Final, Detailed Report ---
    print("\n\n" + "="*60)
    print("📋 EXHAUSTIVE TEST RUN COMPLETE")
    print("="*60)
    print(f"Total Tests Executed: {total_tests}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results["failed"] > 0:
        print("\n--- Failure Details ---")
        # Group failures by user for easier debugging
        failures_by_user = {}
        for f in results['failures']:
            if f['user_id'] not in failures_by_user:
                failures_by_user[f['user_id']] = []
            failures_by_user[f['user_id']].append(f)

        for user, failures in failures_by_user.items():
            print(f"\n[User: {user}]")
            for failure in failures:
                print(
                    f"  - Agent: {failure['agent']}\n"
                    f"    Tool: {failure['tool']}\n"
                    f"    Stage: {failure['stage']}\n"
                    f"    Error: {failure['error']}\n"
                )

if __name__ == "__main__":
    asyncio.run(main())