import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the fi_mcp_data_access import since it has dependency issues
sys.modules['src.fi_mcp_data_access'] = MagicMock()

import importlib.util

class TestCreateGoalFunctionality(unittest.TestCase):
    """
    Test suite specifically for the new create_goal functionality.
    """
    
    def setUp(self):
        """Set up test environment with mocked agent."""
        # Load the goal agent module directly to avoid import issues
        spec = importlib.util.spec_from_file_location(
            'goal_agent', 
            os.path.join(os.path.dirname(__file__), '..', 'src', 'agents', 'goal_investment_strategy_agent.py')
        )
        self.goal_module = importlib.util.module_from_spec(spec)
        
        # Mock the relative import
        with patch.dict('sys.modules', {'src.fi_mcp_data_access': MagicMock()}):
            spec.loader.exec_module(self.goal_module)
        
        # Create test user data
        self.user1_data = {
            'bank_transactions': {
                'bankTransactions': [{
                    'txns': [
                        [50000, 'SALARY', '2024-01-01', 1],  # Credit
                        [25000, 'EXPENSE', '2024-01-02', 2]   # Debit
                    ]
                }]
            },
            'goals': {}
        }
        
        self.user2_data = {
            'bank_transactions': {
                'bankTransactions': [{
                    'txns': [
                        [30000, 'SALARY', '2024-01-01', 1],  # Credit
                        [15000, 'EXPENSE', '2024-01-02', 2]   # Debit
                    ]
                }]
            },
            'goals': {}
        }
        
        # Create temporary file for goals
        self.temp_goals_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        self.temp_goals_file.write('[]')
        self.temp_goals_file.close()
        
        # Create agent instance with mocked file path
        with patch.object(self.goal_module.GoalInvestmentStrategyAgent, 'goals_file_path', self.temp_goals_file.name):
            self.agent = self.goal_module.GoalInvestmentStrategyAgent(self.user1_data, self.user2_data)
    
    def tearDown(self):
        """Clean up temporary files."""
        try:
            os.unlink(self.temp_goals_file.name)
        except:
            pass
    
    def test_create_goal_basic_functionality(self):
        """Test basic goal creation functionality."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 60, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 40, 'risk': 5}
        ]
        
        result = self.agent.create_goal('Emergency Fund', 500000, asset_ladder)
        
        # Assertions
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['goal']['name'], 'Emergency Fund')
        self.assertEqual(result['goal']['target_amount'], 500000)
        self.assertEqual(result['goal']['ta_allocation_percentage'], 100)
        self.assertTrue(result['goal']['pledged'])
        self.assertEqual(len(self.agent.goals), 1)
        self.assertEqual(self.agent.ta, 0)  # Should be zero after using entire amount
    
    def test_create_goal_validation_errors(self):
        """Test validation errors in goal creation."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 50, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 50, 'risk': 5}
        ]
        
        # Test empty goal name
        result = self.agent.create_goal('', 100000, asset_ladder)
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('Goal name cannot be empty', result['message'])
        
        # Test negative amount
        result = self.agent.create_goal('Test Goal', -1000, asset_ladder)
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('Target amount must be positive', result['message'])
        
        # Test empty asset ladder
        result = self.agent.create_goal('Test Goal', 100000, [])
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('Asset ladder must be a non-empty list', result['message'])
        
        # Test invalid percentage sum
        invalid_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 60, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 30, 'risk': 5}  # Total = 90%
        ]
        result = self.agent.create_goal('Test Goal', 100000, invalid_ladder)
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('Asset percentages must sum to 100%', result['message'])
    
    def test_zero_ta_scenario_confirmation_required(self):
        """Test scenario when ta is zero and confirmation is required."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 50, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 50, 'risk': 5}
        ]
        
        # Create first goal to consume all ta
        self.agent.create_goal('First Goal', 300000, asset_ladder)
        self.assertEqual(self.agent.ta, 0)
        
        # Try to create second goal
        result = self.agent.create_goal('Second Goal', 200000, asset_ladder)
        
        # Assertions
        self.assertEqual(result['status'], 'CONFIRMATION_REQUIRED')
        self.assertIn('redistribution_details', result)
        self.assertIn('timeline_changes', result)
        self.assertIn('new_goal', result)
        self.assertIn('question', result)
        self.assertEqual(len(result['redistribution_details']), 1)
        
        # Check redistribution details
        redistribution = result['redistribution_details'][0]
        self.assertEqual(redistribution['goal_name'], 'First Goal')
        self.assertEqual(redistribution['old_percentage'], 100)
        self.assertEqual(redistribution['new_percentage'], 50)  # Split between 2 goals
    
    def test_confirm_goal_redistribution_accept(self):
        """Test accepting goal redistribution."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 50, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 50, 'risk': 5}
        ]
        
        # Create first goal
        self.agent.create_goal('First Goal', 300000, asset_ladder)
        
        # Get confirmation request for second goal
        confirmation_result = self.agent.create_goal('Second Goal', 200000, asset_ladder)
        self.assertEqual(confirmation_result['status'], 'CONFIRMATION_REQUIRED')
        
        # Accept the redistribution
        result = self.agent.confirm_goal_redistribution(True, confirmation_result['new_goal'])
        
        # Assertions
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertIn("Goal 'Second Goal' created successfully", result['message'])
        self.assertEqual(len(self.agent.goals), 2)
        
        # Check that percentages were redistributed
        goal1 = next(g for g in self.agent.goals if g['name'] == 'First Goal')
        goal2 = next(g for g in self.agent.goals if g['name'] == 'Second Goal')
        self.assertEqual(goal1['ta_allocation_percentage'], 50)
        self.assertEqual(goal2['ta_allocation_percentage'], 50)
    
    def test_confirm_goal_redistribution_reject(self):
        """Test rejecting goal redistribution."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 50, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 50, 'risk': 5}
        ]
        
        # Create first goal
        self.agent.create_goal('First Goal', 300000, asset_ladder)
        
        # Get confirmation request for second goal
        confirmation_result = self.agent.create_goal('Second Goal', 200000, asset_ladder)
        
        # Reject the redistribution
        result = self.agent.confirm_goal_redistribution(False, confirmation_result['new_goal'])
        
        # Assertions
        self.assertEqual(result['status'], 'CANCELLED')
        self.assertIn('Goal creation cancelled', result['message'])
        self.assertEqual(len(self.agent.goals), 1)  # Only first goal should exist
    
    def test_multiple_goals_redistribution(self):
        """Test redistribution with multiple existing goals."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 50, 'risk': 1},
            {'asset_name': 'Axis Small Cap Fund', 'percentage': 50, 'risk': 5}
        ]
        
        # Create first goal
        self.agent.create_goal('Goal 1', 300000, asset_ladder)
        # Reset ta for second goal
        self.agent.ta = self.agent.ma + self.agent.fa
        self.agent.create_goal('Goal 2', 200000, asset_ladder)
        # Reset ta for third goal
        self.agent.ta = self.agent.ma + self.agent.fa
        self.agent.create_goal('Goal 3', 100000, asset_ladder)
        
        # Now ta should be 0, try to create 4th goal
        result = self.agent.create_goal('Goal 4', 150000, asset_ladder)
        
        # Should require confirmation and redistribution among 4 goals
        self.assertEqual(result['status'], 'CONFIRMATION_REQUIRED')
        self.assertEqual(len(result['redistribution_details']), 3)  # 3 existing goals
        
        # Each goal should get 25% (100/4)
        for detail in result['redistribution_details']:
            self.assertEqual(detail['new_percentage'], 25)
    
    def test_get_all_goals(self):
        """Test retrieving all goals."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 100, 'risk': 1}
        ]
        
        # Initially no goals
        result = self.agent.get_all_goals()
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['total_goals'], 0)
        
        # Add some goals
        self.agent.create_goal('House Fund', 2000000, asset_ladder)
        self.agent.ta = self.agent.ma + self.agent.fa  # Reset for second goal
        self.agent.create_goal('Car Fund', 800000, asset_ladder)
        
        # Get all goals
        result = self.agent.get_all_goals()
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['total_goals'], 2)
        self.assertEqual(result['total_target_amount'], 2800000)
        self.assertIn('formatted_total_target', result)
        
        # Check goal details
        goal_names = [goal['name'] for goal in result['goals']]
        self.assertIn('House Fund', goal_names)
        self.assertIn('Car Fund', goal_names)
    
    def test_asset_ladder_structure_validation(self):
        """Test validation of asset ladder structure."""
        # Test missing required fields
        invalid_ladder = [
            {'asset_name': 'HDFC Bank FD', 'risk': 1},  # Missing percentage
            {'percentage': 50, 'risk': 5}  # Missing asset_name
        ]
        
        result = self.agent.create_goal('Test Goal', 100000, invalid_ladder)
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('asset_name', result['message'])
        self.assertIn('percentage', result['message'])
        
        # Test negative percentage
        invalid_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': -10, 'risk': 1},
            {'asset_name': 'Axis Fund', 'percentage': 110, 'risk': 5}
        ]
        
        result = self.agent.create_goal('Test Goal', 100000, invalid_ladder)
        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('must be positive', result['message'])
    
    def test_edge_case_single_goal_percentage(self):
        """Test edge case with single goal getting 100% allocation."""
        asset_ladder = [
            {'asset_name': 'HDFC Bank FD', 'percentage': 100, 'risk': 1}
        ]
        
        result = self.agent.create_goal('Single Goal', 100000, asset_ladder)
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['goal']['ta_allocation_percentage'], 100)
        
        # Try to create second goal
        second_result = self.agent.create_goal('Second Goal', 50000, asset_ladder)
        self.assertEqual(second_result['status'], 'CONFIRMATION_REQUIRED')
        
        # Accept redistribution
        final_result = self.agent.confirm_goal_redistribution(True, second_result['new_goal'])
        self.assertEqual(final_result['status'], 'SUCCESS')
        
        # Both goals should have 50% allocation
        for goal in self.agent.goals:
            self.assertEqual(goal['ta_allocation_percentage'], 50)


if __name__ == '__main__':
    unittest.main(verbosity=2)