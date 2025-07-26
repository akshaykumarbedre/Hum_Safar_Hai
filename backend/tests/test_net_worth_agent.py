import unittest
import sys
import os
# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fi_mcp_data_access import FIMCPDataAccess
from src.agents.net_worth_agent import NetWorthAndHealthAgent

class TestNetWorthAgent(unittest.TestCase):
    """
    Test suite for the NetWorthAndHealthAgent.
    We will test against a specific user with known net worth data.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the agent instance once for all tests in this class."""
        # Use user "2222222222" (Sudden Wealth Receiver) with predictable net worth data
        user_id_to_test = "2222222222" 
        dal = FIMCPDataAccess(phone_number=user_id_to_test)
        cls.agent = NetWorthAndHealthAgent(dal)
        
        # Manually inspected expected results for this user (based on actual data)
        cls.EXPECTED_NET_WORTH = {
            "total_net_worth": 658305.0,
            "currency": "INR",
            "status": "SUCCESS"
        }
        
        cls.EXPECTED_ASSET_TYPES = [
            "ASSET_TYPE_MUTUAL_FUND",
            "ASSET_TYPE_EPF", 
            "ASSET_TYPE_INDIAN_SECURITIES",
            "ASSET_TYPE_CRYPTO"
        ]
        
        cls.EXPECTED_ASSET_VALUES = {
            "ASSET_TYPE_MUTUAL_FUND": 84642.0,
            "ASSET_TYPE_EPF": 211111.0,
            "ASSET_TYPE_INDIAN_SECURITIES": 200642.0
        }

    def test_get_net_worth_summary(self):
        """
        Tests the get_net_worth_summary tool for correctness.
        """
        result = self.agent.get_net_worth_summary()

        # Assertion 1: Check if the output is a dictionary
        self.assertIsInstance(result, dict, "Output should be a dictionary.")

        # Assertion 2: Check for the presence of mandatory keys
        required_keys = ["status", "total_net_worth", "currency", "formatted_value"]
        for key in required_keys:
            self.assertIn(key, result, f"JSON result is missing the '{key}' key.")

        # Assertion 3: Check if the calculated values match our expected values
        self.assertEqual(result["total_net_worth"], self.EXPECTED_NET_WORTH["total_net_worth"], 
                        "Calculated total net worth is incorrect.")
        self.assertEqual(result["currency"], self.EXPECTED_NET_WORTH["currency"], 
                        "Currency should be INR.")
        self.assertEqual(result["status"], self.EXPECTED_NET_WORTH["status"], 
                        "Status should be SUCCESS.")
        
        # Assertion 4: Check formatted value format
        self.assertIn("₹", result["formatted_value"], "Formatted value should contain currency symbol.")
        self.assertIn("658,305", result["formatted_value"], "Formatted value should contain comma-separated amount.")

    def test_get_asset_breakdown(self):
        """
        Tests the get_asset_breakdown tool.
        """
        result = self.agent.get_asset_breakdown()
        
        # Assertion 1: Check output type
        self.assertIsInstance(result, list, "Output should be a list.")
        
        # Assertion 2: Check that we have assets
        self.assertGreater(len(result), 0, "Should have at least one asset.")
        
        # Assertion 3: Check structure of each asset
        for asset in result:
            self.assertIsInstance(asset, dict, "Each asset should be a dictionary.")
            required_keys = ["asset_type", "asset_name", "value", "currency", "formatted_value"]
            for key in required_keys:
                self.assertIn(key, asset, f"Asset is missing the '{key}' key.")
        
        # Assertion 4: Check for expected asset types
        asset_types = [asset["asset_type"] for asset in result]
        for expected_type in self.EXPECTED_ASSET_TYPES:
            if expected_type in ["ASSET_TYPE_MUTUAL_FUND", "ASSET_TYPE_EPF", "ASSET_TYPE_INDIAN_SECURITIES"]:
                self.assertIn(expected_type, asset_types, f"Expected asset type '{expected_type}' not found.")
        
        # Assertion 5: Check specific asset values for key assets
        asset_values = {asset["asset_type"]: asset["value"] for asset in result}
        for asset_type, expected_value in self.EXPECTED_ASSET_VALUES.items():
            if asset_type in asset_values:
                self.assertEqual(asset_values[asset_type], expected_value,
                               f"Asset value for {asset_type} is incorrect.")

    def test_get_liability_breakdown(self):
        """
        Tests the get_liability_breakdown tool.
        """
        result = self.agent.get_liability_breakdown()
        
        # Assertion 1: Check output type
        self.assertIsInstance(result, list, "Output should be a list.")
        
        # Assertion 2: Check structure if liabilities exist
        for liability in result:
            self.assertIsInstance(liability, dict, "Each liability should be a dictionary.")
            required_keys = ["liability_type", "liability_name", "value", "currency", "formatted_value"]
            for key in required_keys:
                self.assertIn(key, liability, f"Liability is missing the '{key}' key.")
        
        # Note: User 2222222222 (Sudden Wealth Receiver) typically has no debt, so liabilities may be empty

    def test_get_epf_summary(self):
        """
        Tests the get_epf_summary tool.
        """
        result = self.agent.get_epf_summary()
        
        # Assertion 1: Check output type
        self.assertIsInstance(result, dict, "Output should be a dictionary.")
        
        # Assertion 2: Check required keys
        required_keys = ["status"]
        for key in required_keys:
            self.assertIn(key, result, f"JSON result is missing the '{key}' key.")
        
        # Assertion 3: If EPF data is available, check structure (flexible for different implementations)
        if result["status"] == "SUCCESS":
            # Check for common EPF keys (flexible)
            possible_keys = ["total_epf_balance", "total_balance", "accounts", "epf_accounts"]
            has_epf_data = any(key in result for key in possible_keys)
            self.assertTrue(has_epf_data, "Should have some EPF data when status is SUCCESS.")

    def test_get_portfolio_diversification(self):
        """
        Tests the get_portfolio_diversification tool.
        """
        result = self.agent.get_portfolio_diversification()
        
        # Assertion 1: Check output type
        self.assertIsInstance(result, dict, "Output should be a dictionary.")
        
        # Assertion 2: Check required keys
        required_keys = ["status"]
        for key in required_keys:
            self.assertIn(key, result, f"JSON result is missing the '{key}' key.")
        
        # Assertion 3: If diversification data is available, check structure
        if result["status"] == "SUCCESS":
            div_keys = ["diversification_analysis", "asset_allocation"]
            for key in div_keys:
                if key in result:
                    self.assertIsInstance(result[key], (dict, list), 
                                        f"Diversification field '{key}' should be dict or list.")

    def test_get_processed_net_worth_data(self):
        """
        Tests the get_processed_net_worth_data comprehensive tool.
        """
        result = self.agent.get_processed_net_worth_data()
        
        # Assertion 1: Check output type
        self.assertIsInstance(result, dict, "Output should be a dictionary.")
        
        # Assertion 2: Check basic required keys (flexible for different implementations)
        basic_keys = ["status"]  # Only check minimal required structure
        for key in basic_keys:
            if key not in result:
                # If no status, check for other indicators of valid data
                data_indicators = ["net_worth_summary", "assets_summary", "net_worth_overview", "asset_breakdown"]
                has_data = any(indicator in result for indicator in data_indicators)
                self.assertTrue(has_data, "Should have some net worth data structure.")
                break
        
        # Assertion 3: Check that we have some kind of comprehensive data
        expected_components = ["net_worth_summary", "asset_breakdown", "liability_breakdown", 
                             "assets_summary", "liabilities_summary", "net_worth_overview"]
        has_component = any(comp in result for comp in expected_components)
        self.assertTrue(has_component, "Should have at least one comprehensive data component.")
        
        # Assertion 4: Basic consistency check if we can find net worth data
        if "net_worth_overview" in result and "net_worth_data" in result["net_worth_overview"]:
            individual_net_worth = self.agent.get_net_worth_summary()
            processed_net_worth = result["net_worth_overview"]["net_worth_data"]["total_net_worth"]
            self.assertEqual(processed_net_worth, individual_net_worth["total_net_worth"],
                           "Processed data net worth should match individual call.")

    def test_edge_cases(self):
        """
        Tests edge cases and error handling.
        """
        # Test with non-existent user
        no_data_dal = FIMCPDataAccess(phone_number="0000000000")
        no_data_agent = NetWorthAndHealthAgent(no_data_dal)
        
        # Test net worth summary with no data
        result = no_data_agent.get_net_worth_summary()
        self.assertIsInstance(result, dict, "Should return dict even with no data.")
        self.assertIn("status", result, "Should have status key.")
        
        # Status should be ERROR for no data case
        if "total_net_worth" in result and result["total_net_worth"] is None:
            self.assertEqual(result["status"], "ERROR", "Status should be ERROR when no data available.")

    def test_data_consistency(self):
        """
        Tests consistency between different methods.
        """
        # Get data from different methods
        net_worth_summary = self.agent.get_net_worth_summary()
        asset_breakdown = self.agent.get_asset_breakdown()
        liability_breakdown = self.agent.get_liability_breakdown()
        
        # Calculate total assets
        total_assets = sum(asset["value"] for asset in asset_breakdown)
        
        # Calculate total liabilities  
        total_liabilities = sum(liability["value"] for liability in liability_breakdown)
        
        # Net worth should equal assets minus liabilities
        calculated_net_worth = total_assets - total_liabilities
        reported_net_worth = net_worth_summary["total_net_worth"]
        
        # Allow for small floating point differences
        self.assertAlmostEqual(calculated_net_worth, reported_net_worth, places=0,
                              msg="Net worth should equal assets minus liabilities.")


if __name__ == '__main__':
    unittest.main()