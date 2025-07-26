import unittest
import sys
import os
import math
# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fi_mcp_data_access import FIMCPDataAccess
from src.agents.goal_investment_strategy_agent import GoalInvestmentStrategyAgent, create_goal_investment_strategy_adk_agent


class TestGoalInvestmentStrategyAgent(unittest.TestCase):
    """
    Test suite for the GoalInvestmentStrategyAgent.
    Tests all core calculation functions with real user data.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the agent instance once for all tests in this class."""
        # Use specific test users as defined in the requirements
        # User 1 (Male): 1313131313 (Balanced Growth Tracker)
        # User 2 (Female): 2222222222 (Wealthy Investor)
        cls.user1_phone = "1313131313"
        cls.user2_phone = "2222222222"
        
        # Create data access instances
        dal1 = FIMCPDataAccess(phone_number=cls.user1_phone)
        dal2 = FIMCPDataAccess(phone_number=cls.user2_phone)
        
        # Get complete user data
        cls.user1_data = {
            'net_worth': dal1.get_net_worth(),
            'bank_transactions': dal1.get_bank_transactions(),
            'mutual_fund_transactions': dal1.get_mutual_fund_transactions(),
            'stock_transactions': dal1.get_stock_transactions(),
            'epf_details': dal1.get_epf_details(),
            'credit_report': dal1.get_credit_report(),
            'phone_number': cls.user1_phone
        }
        
        cls.user2_data = {
            'net_worth': dal2.get_net_worth(),
            'bank_transactions': dal2.get_bank_transactions(),
            'mutual_fund_transactions': dal2.get_mutual_fund_transactions(),
            'stock_transactions': dal2.get_stock_transactions(),
            'epf_details': dal2.get_epf_details(),
            'credit_report': dal2.get_credit_report(),
            'phone_number': cls.user2_phone
        }
        
        # Create the agent instance
        cls.agent = GoalInvestmentStrategyAgent(cls.user1_data, cls.user2_data)
        
        # Expected constants for validation
        cls.EXPECTED_ASSET_CLASSES_COUNT = 20  # Should have 20 asset classes
        cls.MIN_EXPECTED_SAVINGS = 5000.0  # Minimum savings recommendation
    
    def test_asset_classes_structure(self):
        """Test that asset classes are properly defined with expected returns."""
        asset_classes = self.agent.ASSET_CLASSES
        
        # Assertion 1: Check that asset classes dictionary is not empty
        self.assertGreater(len(asset_classes), 0, "Asset classes dictionary should not be empty.")
        
        # Assertion 2: Check expected number of asset classes
        self.assertEqual(len(asset_classes), self.EXPECTED_ASSET_CLASSES_COUNT, 
                        f"Expected {self.EXPECTED_ASSET_CLASSES_COUNT} asset classes.")
        
        # Assertion 3: Check that all returns are positive and reasonable (0% to 20%)
        for asset_class, return_rate in asset_classes.items():
            self.assertIsInstance(return_rate, (int, float), 
                                f"Return rate for {asset_class} should be numeric.")
            self.assertGreaterEqual(return_rate, 0.0, 
                                  f"Return rate for {asset_class} should be non-negative.")
            self.assertLessEqual(return_rate, 0.25, 
                               f"Return rate for {asset_class} should be reasonable (<25%).")
        
        # Assertion 4: Check that specific asset classes exist
        expected_assets = ['Fixed Deposit', 'Direct Equity', 'PPF (Public Provident Fund)', 'ELSS (Tax Saving)']
        for asset in expected_assets:
            self.assertIn(asset, asset_classes, f"{asset} should be in asset classes.")
    
    def test_recommend_monthly_saving(self):
        """Test the monthly savings recommendation function."""
        result = self.agent.recommend_monthly_saving()
        
        # Assertion 1: Check return type is tuple with 3 elements
        self.assertIsInstance(result, tuple, "Result should be a tuple.")
        self.assertEqual(len(result), 3, "Result should have 3 elements: user1_saving, user2_saving, combined_saving.")
        
        user1_saving, user2_saving, combined_saving = result
        
        # Assertion 2: Check that all values are positive
        self.assertGreater(user1_saving, 0, "User 1 savings should be positive.")
        self.assertGreater(user2_saving, 0, "User 2 savings should be positive.")
        self.assertGreater(combined_saving, 0, "Combined savings should be positive.")
        
        # Assertion 3: Check that combined savings equals sum of individual savings
        self.assertAlmostEqual(combined_saving, user1_saving + user2_saving, places=2,
                              msg="Combined savings should equal sum of individual savings.")
        
        # Assertion 4: Check minimum savings threshold
        self.assertGreaterEqual(user1_saving, self.MIN_EXPECTED_SAVINGS, 
                               f"User 1 savings should be at least ₹{self.MIN_EXPECTED_SAVINGS}.")
        self.assertGreaterEqual(user2_saving, self.MIN_EXPECTED_SAVINGS, 
                               f"User 2 savings should be at least ₹{self.MIN_EXPECTED_SAVINGS}.")
    
    def test_set_financial_goal(self):
        """Test setting financial goals for users."""
        # Test valid goal setting
        result = self.agent.set_financial_goal("user1", "Dream Vacation", 500000)
        
        # Assertion 1: Check successful goal setting
        self.assertEqual(result["status"], "SUCCESS", "Goal setting should be successful.")
        self.assertEqual(result["goal_name"], "Dream Vacation", "Goal name should match.")
        self.assertEqual(result["target_amount"], 500000, "Target amount should match.")
        self.assertEqual(result["user_id"], "user1", "User ID should match.")
        
        # Assertion 2: Check that goal is stored in user data
        self.assertIn("Dream Vacation", self.agent.users["user1"]["goals"], 
                     "Goal should be stored in user1 goals.")
        self.assertEqual(self.agent.users["user1"]["goals"]["Dream Vacation"], 500000,
                        "Stored goal amount should match.")
        
        # Test invalid user ID
        result = self.agent.set_financial_goal("invalid_user", "Test Goal", 100000)
        self.assertEqual(result["status"], "ERROR", "Invalid user ID should return error.")
        
        # Test invalid target amount
        result = self.agent.set_financial_goal("user2", "Invalid Goal", -1000)
        self.assertEqual(result["status"], "ERROR", "Negative amount should return error.")
        
        # Test goal update
        result = self.agent.set_financial_goal("user1", "Dream Vacation", 600000)
        self.assertEqual(result["status"], "SUCCESS", "Goal update should be successful.")
        self.assertEqual(self.agent.users["user1"]["goals"]["Dream Vacation"], 600000,
                        "Updated goal amount should be stored.")
    
    def test_get_num_of_months_to_reach_goal(self):
        """Test the compound interest calculation for goal achievement."""
        # Test case 1: Basic calculation
        result = self.agent.get_num_of_months_to_reach_goal(10000, 120000, 0.12)
        
        # Assertion 1: Check successful calculation
        self.assertEqual(result["status"], "SUCCESS", "Calculation should be successful.")
        self.assertIn("months_needed", result, "Result should contain months_needed.")
        self.assertGreater(result["months_needed"], 0, "Months needed should be positive.")
        
        # Assertion 2: Check mathematical accuracy
        # Manual calculation: 10000 monthly, 120000 target, 12% annual (1% monthly)
        # Using compound interest formula: n = log(1 + (FV × r / PMT)) / log(1 + r)
        monthly_rate = 0.12 / 12  # 1% monthly
        expected_months = math.log(1 + (120000 * monthly_rate / 10000)) / math.log(1 + monthly_rate)
        self.assertAlmostEqual(result["months_needed"], expected_months, places=1,
                              msg="Calculated months should match mathematical formula.")
        
        # Test case 2: Zero return rate (simple savings)
        result = self.agent.get_num_of_months_to_reach_goal(5000, 60000, 0.0)
        self.assertEqual(result["status"], "SUCCESS", "Zero return calculation should succeed.")
        self.assertEqual(result["months_needed"], 12.0, "Simple savings: 60000/5000 = 12 months.")
        
        # Test case 3: Invalid inputs
        result = self.agent.get_num_of_months_to_reach_goal(-1000, 50000, 0.10)
        self.assertEqual(result["status"], "ERROR", "Negative investment should return error.")
        
        result = self.agent.get_num_of_months_to_reach_goal(1000, -50000, 0.10)
        self.assertEqual(result["status"], "ERROR", "Negative target should return error.")
        
        result = self.agent.get_num_of_months_to_reach_goal(1000, 50000, -0.05)
        self.assertEqual(result["status"], "ERROR", "Negative return rate should return error.")
        
        # Test case 4: Check additional fields in response
        result = self.agent.get_num_of_months_to_reach_goal(8000, 100000, 0.15)
        required_fields = ["years", "remaining_months", "time_description", "total_invested", 
                          "total_returns", "formatted_target", "return_percentage"]
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain {field} field.")
    
    def test_get_investment_options_sorted_by_return(self):
        """Test investment options sorting by expected returns."""
        result = self.agent.get_investment_options_sorted_by_return()
        
        # Assertion 1: Check that result is a list
        self.assertIsInstance(result, list, "Result should be a list.")
        self.assertGreater(len(result), 0, "Result should not be empty.")
        
        # Assertion 2: Check that options are sorted by return (ascending)
        returns = [option["expected_annual_return"] for option in result]
        self.assertEqual(returns, sorted(returns), "Options should be sorted by return rate (ascending).")
        
        # Assertion 3: Check structure of each option
        for option in result:
            required_fields = ["asset_class", "expected_annual_return", "expected_return_percentage", 
                             "risk_category", "description"]
            for field in required_fields:
                self.assertIn(field, option, f"Option should contain {field} field.")
        
        # Assertion 4: Check that lowest and highest returns are reasonable
        lowest_return = result[0]["expected_annual_return"]
        highest_return = result[-1]["expected_annual_return"]
        self.assertLessEqual(lowest_return, 0.06, "Lowest return should be reasonable (≤6%).")
        self.assertGreaterEqual(highest_return, 0.12, "Highest return should be reasonable (≥12%).")
        
        # Assertion 5: Check risk categorization
        risk_categories = set(option["risk_category"] for option in result)
        expected_risks = {"Low Risk", "Moderate Risk", "High Risk", "Very High Risk"}
        self.assertTrue(risk_categories.issubset(expected_risks), 
                       "All risk categories should be valid.")
    
    def test_get_user_goals(self):
        """Test retrieving user goals."""
        # Set up some test goals
        self.agent.set_financial_goal("user1", "House Down Payment", 1000000)
        self.agent.set_financial_goal("user1", "Emergency Fund", 300000)
        
        result = self.agent.get_user_goals("user1")
        
        # Assertion 1: Check successful retrieval
        self.assertEqual(result["status"], "SUCCESS", "Goal retrieval should be successful.")
        self.assertIn("goals", result, "Result should contain goals.")
        
        # Assertion 2: Check goal count and content
        self.assertGreaterEqual(result["total_goals"], 2, "Should have at least 2 goals.")
        self.assertIn("House Down Payment", result["goals"], "Should contain House Down Payment goal.")
        self.assertIn("Emergency Fund", result["goals"], "Should contain Emergency Fund goal.")
        
        # Assertion 3: Check total target amount calculation
        expected_total = 1000000 + 300000
        self.assertGreaterEqual(result["total_target_amount"], expected_total, 
                               "Total target should include all goals.")
        
        # Test invalid user ID
        result = self.agent.get_user_goals("invalid_user")
        self.assertEqual(result["status"], "ERROR", "Invalid user ID should return error.")
        
        # Test user with no goals initially (clear any existing goals first)
        self.agent.users["user2"]["goals"] = {}  # Clear goals for clean test
        result = self.agent.get_user_goals("user2")
        self.assertEqual(result["status"], "SUCCESS", "No goals should still be successful.")
        self.assertEqual(result["total_goals"], 0, "Should have 0 goals after clearing.")
    
    def test_get_savings_analysis(self):
        """Test comprehensive savings analysis."""
        # Set up some goals for testing
        self.agent.set_financial_goal("user1", "Retirement", 5000000)
        self.agent.set_financial_goal("user2", "House Purchase", 3000000)
        
        result = self.agent.get_savings_analysis()
        
        # Assertion 1: Check successful analysis
        self.assertEqual(result["status"], "SUCCESS", "Savings analysis should be successful.")
        
        # Assertion 2: Check main sections exist
        required_sections = ["savings_recommendations", "user1_analysis", "user2_analysis", "combined_analysis"]
        for section in required_sections:
            self.assertIn(section, result, f"Result should contain {section} section.")
        
        # Assertion 3: Check savings recommendations
        savings_rec = result["savings_recommendations"]
        self.assertIn("user1_monthly_saving", savings_rec, "Should contain user1 savings.")
        self.assertIn("user2_monthly_saving", savings_rec, "Should contain user2 savings.")
        self.assertIn("combined_monthly_saving", savings_rec, "Should contain combined savings.")
        
        # Assertion 4: Check that combined savings equals sum
        user1_saving = savings_rec["user1_monthly_saving"]
        user2_saving = savings_rec["user2_monthly_saving"]
        combined_saving = savings_rec["combined_monthly_saving"]
        self.assertAlmostEqual(combined_saving, user1_saving + user2_saving, places=2,
                              msg="Combined savings should equal sum of individual savings.")
        
        # Assertion 5: Check goal timelines
        user1_analysis = result["user1_analysis"]
        self.assertIn("goal_timelines", user1_analysis, "Should contain goal timelines.")
        if "Retirement" in user1_analysis["goal_timelines"]:
            retirement_timeline = user1_analysis["goal_timelines"]["Retirement"]
            self.assertIn("months_needed", retirement_timeline, "Timeline should contain months needed.")
        
        # Assertion 6: Check combined analysis metrics
        combined_analysis = result["combined_analysis"]
        self.assertIn("savings_rate", combined_analysis, "Should contain savings rate.")
        self.assertGreaterEqual(combined_analysis["savings_rate"], 0, "Savings rate should be non-negative.")
    
    def test_agent_initialization(self):
        """Test agent initialization with user data."""
        # Assertion 1: Check that agent was initialized correctly
        self.assertIsInstance(self.agent, GoalInvestmentStrategyAgent, "Agent should be correct type.")
        
        # Assertion 2: Check that user data is stored
        self.assertIn("user1", self.agent.users, "Agent should contain user1 data.")
        self.assertIn("user2", self.agent.users, "Agent should contain user2 data.")
        
        # Assertion 3: Check that goals dictionary is initialized
        self.assertIn("goals", self.agent.users["user1"], "User1 should have goals dictionary.")
        self.assertIn("goals", self.agent.users["user2"], "User2 should have goals dictionary.")
        self.assertIsInstance(self.agent.users["user1"]["goals"], dict, "Goals should be a dictionary.")
        
        # Assertion 4: Check that user data contains expected sections
        expected_sections = ["net_worth", "bank_transactions", "phone_number"]
        for user_id in ["user1", "user2"]:
            for section in expected_sections:
                self.assertIn(section, self.agent.users[user_id], 
                             f"{user_id} should contain {section} data.")
    
    def test_adk_agent_factory(self):
        """Test the ADK agent factory function."""
        try:
            # Test agent creation via factory
            adk_agent = create_goal_investment_strategy_adk_agent(
                self.user1_phone, self.user2_phone, "gemini-2.0-flash"
            )
            
            # Assertion 1: Check that agent was created
            self.assertIsNotNone(adk_agent, "ADK agent should be created successfully.")
            
            # Assertion 2: Check agent properties
            self.assertEqual(adk_agent.name, "Goal_Investment_Strategy_Agent", "Agent name should match.")
            self.assertIn("savings and investment strategy", adk_agent.description.lower(), 
                         "Agent description should mention its purpose.")
            
            # Assertion 3: Check that agent has tools
            self.assertGreater(len(adk_agent.tools), 0, "Agent should have tools.")
            
            print("✅ ADK agent factory test passed.")
            
        except Exception as e:
            self.fail(f"ADK agent factory failed: {str(e)}")
    
    def test_mathematical_accuracy(self):
        """Test mathematical accuracy of compound interest calculations."""
        # Test case: Known calculation
        # 5000 monthly, 100000 target, 10% annual return
        monthly_investment = 5000
        target_amount = 100000
        annual_return = 0.10
        
        result = self.agent.get_num_of_months_to_reach_goal(monthly_investment, target_amount, annual_return)
        
        # Manual calculation for verification
        monthly_rate = annual_return / 12
        expected_months = math.log(1 + (target_amount * monthly_rate / monthly_investment)) / math.log(1 + monthly_rate)
        
        # Assertion 1: Mathematical accuracy
        self.assertAlmostEqual(result["months_needed"], expected_months, places=1,
                              msg="Compound interest calculation should be mathematically accurate.")
        
        # Assertion 2: Total invested calculation
        expected_total_invested = monthly_investment * expected_months  # Use exact months, not rounded
        self.assertAlmostEqual(result["total_invested"], expected_total_invested, places=1,
                              msg="Total invested calculation should be accurate.")
        
        # Assertion 3: Returns calculation
        expected_returns = target_amount - expected_total_invested
        self.assertAlmostEqual(result["total_returns"], expected_returns, places=2,
                              msg="Returns calculation should be accurate.")
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test very small amounts
        result = self.agent.get_num_of_months_to_reach_goal(1, 100, 0.05)
        self.assertEqual(result["status"], "SUCCESS", "Small amounts should be handled.")
        
        # Test very large amounts
        result = self.agent.get_num_of_months_to_reach_goal(100000, 10000000, 0.12)
        self.assertEqual(result["status"], "SUCCESS", "Large amounts should be handled.")
        
        # Test zero return rate
        result = self.agent.get_num_of_months_to_reach_goal(1000, 12000, 0.0)
        self.assertEqual(result["status"], "SUCCESS", "Zero return should be handled.")
        self.assertEqual(result["months_needed"], 12.0, "Zero return should give simple division.")
        
        # Test high return rate
        result = self.agent.get_num_of_months_to_reach_goal(5000, 50000, 0.20)
        self.assertEqual(result["status"], "SUCCESS", "High return rates should be handled.")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)