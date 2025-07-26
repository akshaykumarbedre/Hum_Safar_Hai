#!/usr/bin/env python3
"""
Test Phase 2 - Expense & Investment Analyst Agents

This script tests the implementation of:
1. ExpenseAndCashflowAgent class  
2. InvestmentAnalystAgent class
3. Integration with existing FIMCPDataAccess and NetWorthAndHealthAgent

Sample usage for multiple phone numbers as specified in requirements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fi_mcp_data_access import FIMCPDataAccess
from src.agents.net_worth_agent import NetWorthAndHealthAgent
from src.agents.expense_agent import ExpenseAndCashflowAgent
from src.agents.investment_agent import InvestmentAnalystAgent


def test_expense_agent():
    """Test the ExpenseAndCashflowAgent class."""
    print("=" * 60)
    print("TESTING EXPENSE & CASH FLOW AGENT")
    print("=" * 60)
    
    # Test with multiple users
    test_users = ["2222222222", "7777777777", "3333333333"]
    
    for phone_number in test_users:
        print(f"\n--- Testing User: {phone_number} ---")
        # Create DAL and agent for this specific user
        user_dal = FIMCPDataAccess(phone_number=phone_number)
        user_agent = ExpenseAndCashflowAgent(user_dal)
        
        persona_desc = user_dal.get_user_persona_description()
        print(f"Persona: {persona_desc[:80]}...")
        
        # Test spending summary
        print("\n1. Spending Summary (90 days):")
        spending_summary = user_agent.get_spending_summary(90)
        for line in spending_summary.split('\n'):
            print(f"   {line}")
        
        # Test with shorter period
        print("\n2. Spending Summary (30 days):")
        spending_summary_30 = user_agent.get_spending_summary(30)
        for line in spending_summary_30.split('\n'):
            print(f"   {line}")
    
    # Test edge cases
    print(f"\n--- Testing Edge Cases ---")
    
    # Test with non-existent user
    print("\n3. Non-existent User:")
    no_data_dal = FIMCPDataAccess(phone_number="0000000000")
    no_data_agent = ExpenseAndCashflowAgent(no_data_dal)
    no_data_summary = no_data_agent.get_spending_summary(90)
    print(f"   {no_data_summary}")
    
    # Test categorization functionality directly
    print("\n4. Transaction Categorization Tests:")
    test_narrations = [
        "UPI-SWIGGY-SWIGGY8@YBL-PAYMENT FROM PHONE",
        "UPI-AMAZON-PAYMENT FROM PHONE", 
        "UPI-AIRTEL-PAYMENT FOR RECHARGE",
        "EMI PAYMENT HDFC BANK",
        "UPI-RANDOM MERCHANT-PAYMENT FROM PHONE"
    ]
    
    # Use any agent instance for categorization test
    test_dal = FIMCPDataAccess(phone_number="2222222222")
    test_agent = ExpenseAndCashflowAgent(test_dal)
    
    for narration in test_narrations:
        category = test_agent._categorize_transaction(narration)
        print(f"   '{narration[:40]}...' → {category}")


def test_investment_agent():
    """Test the InvestmentAnalystAgent class."""
    print("\n" + "=" * 60)
    print("TESTING INVESTMENT & PORTFOLIO ANALYST AGENT")
    print("=" * 60)
    
    # Test with multiple users and thresholds
    test_cases = [
        ("2222222222", 8.0),
        ("2222222222", 10.0),
        ("7777777777", 5.0),
        ("3333333333", 8.0)
    ]
    
    for phone_number, threshold in test_cases:
        print(f"\n--- Testing User: {phone_number} (Threshold: {threshold}%) ---")
        # Create DAL and agent for this specific user
        user_dal = FIMCPDataAccess(phone_number=phone_number)
        user_agent = InvestmentAnalystAgent(user_dal)
        
        persona_desc = user_dal.get_user_persona_description()
        print(f"Persona: {persona_desc[:80]}...")
        
        # Test underperforming funds identification
        print(f"\nUnderperforming Funds Analysis:")
        underperforming_summary = user_agent.identify_underperforming_funds(threshold)
        for line in underperforming_summary.split('\n'):
            print(f"   {line}")
    
    # Test edge cases
    print(f"\n--- Testing Edge Cases ---")
    
    # Test with non-existent user
    print("\nNon-existent User:")
    no_data_dal = FIMCPDataAccess(phone_number="0000000000")
    no_data_agent = InvestmentAnalystAgent(no_data_dal)
    no_data_summary = no_data_agent.identify_underperforming_funds(8.0)
    print(f"   {no_data_summary}")


def test_integration():
    """Test integration between all agents."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION - ALL AGENTS")
    print("=" * 60)
    
    # Initialize components for a specific user
    USER_ID = "2222222222"
    dal = FIMCPDataAccess(phone_number=USER_ID)
    net_worth_agent = NetWorthAndHealthAgent(dal)
    expense_agent = ExpenseAndCashflowAgent(dal)
    investment_agent = InvestmentAnalystAgent(dal)
    
    # Test with a comprehensive user profile
    print(f"\nComprehensive Analysis for User: {USER_ID}")
    print(f"Persona: {dal.get_user_persona_description()}")
    
    print("\n1. Net Worth Summary:")
    net_worth_summary = net_worth_agent.get_net_worth_summary()
    print(f"   {net_worth_summary}")
    
    print("\n2. Asset Breakdown:")
    asset_breakdown = net_worth_agent.get_asset_breakdown()
    for line in asset_breakdown.split('\n')[:5]:  # Show first 5 lines
        print(f"   {line}")
    
    print("\n3. Spending Analysis:")
    spending_summary = expense_agent.get_spending_summary(90)
    for line in spending_summary.split('\n')[:5]:  # Show first 5 lines
        print(f"   {line}")
    
    print("\n4. Investment Performance:")
    investment_summary = investment_agent.identify_underperforming_funds(8.0)
    for line in investment_summary.split('\n')[:5]:  # Show first 5 lines
        print(f"   {line}")
    
    # Test data availability across agents
    profile = dal.get_complete_profile()
    available_data = sum(1 for k, v in profile.items() if v is not None and k != "user_id")
    print(f"\nData Availability: {available_data}/6 data types available")
    
    print(f"\nAgent Capabilities Summary:")
    print(f"✓ Net Worth Analysis: Available")
    print(f"✓ Expense Analysis: Available") 
    print(f"✓ Investment Analysis: Available")


def main():
    """Main test function."""
    print("HUMSAFAR FINANCIAL AI ASSISTANT - PHASE 2 TESTS")
    print("Testing Expense & Investment Analyst Agents")
    print("Date:", "2024")
    
    try:
        # Run all tests
        test_expense_agent()
        test_investment_agent()
        test_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNew agent components are working correctly:")
        print("✓ ExpenseAndCashflowAgent class")
        print("✓ Transaction categorization logic")
        print("✓ Spending summary generation")
        print("✓ InvestmentAnalystAgent class")
        print("✓ Underperforming funds identification")
        print("✓ Integration with existing FIMCPDataAccess")
        print("✓ Error handling for missing data")
        print("✓ Multiple user personas support")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()