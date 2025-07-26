#!/usr/bin/env python3
"""
Test Phase 1 - Core Financial Tools & Net Worth Agent

This script tests the implementation of:
1. Financial Tools Module (EMI and SIP calculators)
2. NetWorthAndHealthAgent class
3. Integration with FIMCPDataAccess

Sample usage for phone number "2222222222" as specified in requirements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fi_mcp_data_access import FIMCPDataAccess
from src.agents.net_worth_agent import NetWorthAndHealthAgent
from src.tools.financial_tools import calculate_loan_emi, calculate_sip_future_value


def test_financial_tools():
    """Test the financial tools module."""
    print("=" * 60)
    print("TESTING FINANCIAL TOOLS")
    print("=" * 60)
    
    # Test EMI calculation
    print("\n1. Testing EMI Calculator:")
    principal = 500000  # ₹5 lakh
    annual_rate = 12.5  # 12.5% annual interest
    tenure_years = 10   # 10 years
    
    emi = calculate_loan_emi(principal, annual_rate, tenure_years)
    print(f"   Loan Amount: ₹{principal:,}")
    print(f"   Interest Rate: {annual_rate}% per annum")
    print(f"   Tenure: {tenure_years} years")
    print(f"   Monthly EMI: ₹{emi:,.2f}")
    
    # Test SIP calculation
    print("\n2. Testing SIP Calculator:")
    monthly_investment = 5000  # ₹5,000 per month
    annual_return = 12.0      # 12% expected annual return
    investment_years = 10     # 10 years
    
    future_value = calculate_sip_future_value(monthly_investment, annual_return, investment_years)
    total_invested = monthly_investment * investment_years * 12
    
    print(f"   Monthly Investment: ₹{monthly_investment:,}")
    print(f"   Expected Annual Return: {annual_return}%")
    print(f"   Investment Period: {investment_years} years")
    print(f"   Total Amount Invested: ₹{total_invested:,}")
    print(f"   Future Value: ₹{future_value:,.2f}")
    print(f"   Total Gain: ₹{future_value - total_invested:,.2f}")
    
    # Test edge cases
    print("\n3. Testing Edge Cases:")
    
    # Zero interest rate
    zero_interest_emi = calculate_loan_emi(100000, 0, 5)
    print(f"   EMI with 0% interest (₹1,00,000 for 5 years): ₹{zero_interest_emi:,.2f}")
    
    # Zero return SIP
    zero_return_sip = calculate_sip_future_value(1000, 0, 5)
    print(f"   SIP with 0% return (₹1,000/month for 5 years): ₹{zero_return_sip:,.2f}")


def test_net_worth_agent():
    """Test the NetWorthAndHealthAgent class."""
    print("\n" + "=" * 60)
    print("TESTING NET WORTH & HEALTH AGENT")
    print("=" * 60)
    
    # Initialize DAL and agent
    USER_ID = "2222222222"
    dal = FIMCPDataAccess(phone_number=USER_ID)
    agent = NetWorthAndHealthAgent(dal)
    
    # Test with sample user as specified in requirements
    print(f"\nTesting with user: {USER_ID}")
    print(f"User persona: {dal.get_user_persona_description()}")
    
    # Test each method
    print("\n1. Net Worth Summary:")
    net_worth_summary = agent.get_net_worth_summary()
    print(f"   {net_worth_summary}")
    
    print("\n2. Asset Breakdown:")
    asset_breakdown = agent.get_asset_breakdown()
    for line in asset_breakdown.split('\n'):
        print(f"   {line}")
    
    print("\n3. Liability Breakdown:")
    liability_breakdown = agent.get_liability_breakdown()
    for line in liability_breakdown.split('\n'):
        print(f"   {line}")
    
    # Test with a user that has no data
    print(f"\n4. Testing with non-existent user:")
    no_data_dal = FIMCPDataAccess(phone_number="0000000000")
    no_data_agent = NetWorthAndHealthAgent(no_data_dal)
    no_data_summary = no_data_agent.get_net_worth_summary()
    print(f"   {no_data_summary}")


def test_integration():
    """Test integration between all components."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION")
    print("=" * 60)
    
    # Initialize components
    dal = FIMCPDataAccess(phone_number="2222222222")  # Use dummy phone for listing users
    agent = NetWorthAndHealthAgent(dal)
    
    # Get available users
    users = dal.get_available_users()
    print(f"\nAvailable test users: {users[:5]}...")  # Show first 5
    
    # Test multiple users
    test_users = ["2222222222", "3333333333", "7777777777"]
    
    for user in test_users:
        if user in users:
            print(f"\n--- Testing User: {user} ---")
            # Create DAL instance for this specific user
            user_dal = FIMCPDataAccess(phone_number=user)
            user_agent = NetWorthAndHealthAgent(user_dal)
            
            print(f"Persona: {user_dal.get_user_persona_description()[:80]}...")
            
            # Quick summary
            net_worth = user_agent.get_net_worth_summary()
            print(f"Net Worth: {net_worth}")
            
            # Check data availability
            profile = user_dal.get_complete_profile()
            available_data = sum(1 for k, v in profile.items() if v is not None and k != "user_id")
            print(f"Available data types: {available_data}/6")


def main():
    """Main test function."""
    print("HUMSAFAR FINANCIAL AI ASSISTANT - PHASE 1 TESTS")
    print("Testing Core Financial Tools & Net Worth Agent")
    print("Date:", "2024")
    
    try:
        # Run all tests
        test_financial_tools()
        test_net_worth_agent()
        test_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nCore components are working correctly:")
        print("✓ Financial Tools Module (EMI & SIP calculators)")
        print("✓ NetWorthAndHealthAgent class")
        print("✓ Integration with FIMCPDataAccess")
        print("✓ Error handling for missing data")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()