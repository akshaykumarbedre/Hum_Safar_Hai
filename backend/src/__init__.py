"""
Humsafar Financial AI Assistant

A comprehensive suite of financial calculators and tools designed for 
AI-powered financial decision making and MCP tool integration.
"""

__version__ = "1.0.0"
__author__ = "Akshay Kumar Bedre"
__email__ = "your.email@example.com"

from .fi_mcp_data_access import *

__all__ = [
    # FI-MCP Data Access
    "FIMCPDataAccess",
    "get_net_worth",
    "get_bank_transactions",
    "get_mutual_fund_transactions",
    "get_stock_transactions",
    "get_epf_details",
    "get_credit_report",
    "get_complete_profile",
    "analyze_user_financial_health",
    "get_available_users"
]