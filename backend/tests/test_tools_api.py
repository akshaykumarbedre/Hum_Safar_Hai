"""
Test suite for the Financial Tools API

This module contains tests for all the individual tool endpoints.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from tools_api import app

# Create test client
client = TestClient(app)

# Test user for all tests
TEST_USER = "4444444444"

class TestHealthEndpoints:
    """Test health check and utility endpoints."""
    
    def test_root_endpoint(self):
        """Test root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_list_tools_endpoint(self):
        """Test tools list endpoint."""
        response = client.get("/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "expense_tools" in data["tools"]
        assert "networth_tools" in data["tools"]
    
    def test_list_users_endpoint(self):
        """Test list available users endpoint."""
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert "available_users" in data or "error" in data


class TestExpenseTools:
    """Test expense and cash flow tool endpoints."""
    
    def test_core_transaction_data(self):
        """Test core transaction data endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/expense/core_transaction_data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
        assert "data" in data
    
    def test_spending_summary(self):
        """Test spending summary endpoint."""
        payload = {"user_name": TEST_USER, "period_days": 30}
        response = client.post("/tools/expense/spending_summary", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_income_sources(self):
        """Test income sources endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/expense/income_sources", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_processed_transaction_data(self):
        """Test processed transaction data endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/expense/processed_transaction_data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestNetWorthTools:
    """Test net worth tool endpoints."""
    
    def test_core_snapshot(self):
        """Test core net worth snapshot endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/networth/core_snapshot", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_summary(self):
        """Test net worth summary endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/networth/summary", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_asset_breakdown(self):
        """Test asset breakdown endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/networth/asset_breakdown", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_liability_breakdown(self):
        """Test liability breakdown endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/networth/liability_breakdown", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_epf_summary(self):
        """Test EPF summary endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/networth/epf_summary", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestInvestmentTools:
    """Test investment tool endpoints."""
    
    def test_core_data(self):
        """Test core investment data endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/investment/core_data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_portfolio_performance(self):
        """Test portfolio performance endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/investment/portfolio_performance", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_fund_details(self):
        """Test fund details endpoint."""
        payload = {"user_name": TEST_USER, "fund_name_query": "HDFC"}
        response = client.post("/tools/investment/fund_details", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestLoanTools:
    """Test loan and credit tool endpoints."""
    
    def test_core_credit_data(self):
        """Test core credit data endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/loan/core_credit_data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_credit_score_analysis(self):
        """Test credit score analysis endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/loan/credit_score_analysis", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestGoalTools:
    """Test goal and investment strategy tool endpoints."""
    
    def test_all_goals(self):
        """Test get all goals endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/goals/all_goals", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_create_goal(self):
        """Test create goal endpoint."""
        payload = {
            "user_name": TEST_USER,
            "goal_name": "Test Emergency Fund",
            "target_amount": 100000,
            "target_date": "2025-12-31",
            "risk_tolerance": "low"
        }
        response = client.post("/tools/goals/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_suggested_assets(self):
        """Test suggested assets endpoint."""
        payload = {
            "user_name": TEST_USER,
            "goal_name": "Emergency Fund",
            "target_amount": 100000
        }
        response = client.post("/tools/goals/suggested_assets", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_months_to_reach(self):
        """Test months to reach goal endpoint."""
        payload = {
            "user_name": TEST_USER,
            "monthly_investment": 10000,
            "target_amount": 100000,
            "annual_return_rate": 12.0
        }
        response = client.post("/tools/goals/months_to_reach", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_investment_options(self):
        """Test investment options endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/goals/investment_options", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_savings_analysis(self):
        """Test savings analysis endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/goals/savings_analysis", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestIntegrityTools:
    """Test financial integrity tool endpoints."""
    
    def test_unusual_transactions(self):
        """Test unusual transactions detection endpoint."""
        payload = {"user_name": TEST_USER, "std_dev_threshold": 2.5}
        response = client.post("/tools/integrity/unusual_transactions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_dormant_activity(self):
        """Test dormant activity detection endpoint."""
        payload = {"user_name": TEST_USER, "dormancy_period_days": 90}
        response = client.post("/tools/integrity/dormant_activity", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_duplicate_charges(self):
        """Test duplicate charges detection endpoint."""
        payload = {"user_name": TEST_USER, "time_window_minutes": 60}
        response = client.post("/tools/integrity/duplicate_charges", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_portfolio_reallocation(self):
        """Test portfolio reallocation detection endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/integrity/portfolio_reallocation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_investment_churn(self):
        """Test investment churn detection endpoint."""
        payload = {"user_name": TEST_USER, "period_days": 90}
        response = client.post("/tools/integrity/investment_churn", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_missed_income(self):
        """Test missed income detection endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/integrity/missed_income", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER
    
    def test_full_check(self):
        """Test full integrity check endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/integrity/full_check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestHealthTools:
    """Test financial health tool endpoints."""
    
    def test_processed_data(self):
        """Test processed financial health data endpoint."""
        payload = {"user_name": TEST_USER}
        response = client.post("/tools/health/processed_data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_name"] == TEST_USER


class TestErrorHandling:
    """Test error handling in the API."""
    
    def test_invalid_user(self):
        """Test handling of invalid user names."""
        payload = {"user_name": "invalid_user"}
        response = client.post("/tools/expense/core_transaction_data", json=payload)
        # Should handle gracefully, might return empty data or error
        assert response.status_code in [200, 500]
    
    def test_missing_required_field(self):
        """Test handling of missing required fields."""
        payload = {}  # Missing user_name
        response = client.post("/tools/expense/core_transaction_data", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_period_days(self):
        """Test handling of invalid period days."""
        payload = {"user_name": TEST_USER, "period_days": -1}
        response = client.post("/tools/expense/spending_summary", json=payload)
        # Should handle gracefully
        assert response.status_code in [200, 422, 500]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
