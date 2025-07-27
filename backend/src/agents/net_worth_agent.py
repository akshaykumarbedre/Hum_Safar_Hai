"""
Net Worth & Financial Health Agent

This agent is responsible for analyzing and reporting on a user's
net worth, assets, and liabilities.
"""
from typing import Optional, Dict, Any, List
from ..fi_mcp_data_access import FIMCPDataAccess


class NetWorthAndHealthAgent:
    """
    Agent for analyzing and reporting user's net worth and financial health.
    """
    
    def __init__(self, dal: FIMCPDataAccess):
        """
        Initializes the agent with a Data Access Layer instance.
        
        Args:
            dal (FIMCPDataAccess): Instance of the data access layer
        """
        self.dal = dal


    def get_core_net_worth_snapshot(self) -> dict:
        """
        Get core net worth snapshot in a pre-processed, token-efficient format.
        
        Returns:
            dict: Pre-processed net worth data with minimal token usage
        """
        try:
            # Fetch net worth and EPF data
            net_worth_data = self.dal.get_net_worth()
            epf_data = self.dal.get_epf_details()
            
            if not net_worth_data:
                return {"total_net_worth": 0, "assets": {}, "liabilities": {}}
            
            net_worth_response = net_worth_data.get("netWorthResponse", {})
            
            result = {
                "total_net_worth": 0,
                "snapshot_date": "",
                "assets": {},
                "liabilities": {}
            }
            
            # Extract total net worth
            total_net_worth_data = net_worth_response.get("totalNetWorthValue", {})
            if total_net_worth_data:
                try:
                    units = total_net_worth_data.get("units", "0")
                    result["total_net_worth"] = float(units)
                except (ValueError, TypeError):
                    result["total_net_worth"] = 0
            
            # Set snapshot date (simplified)
            from datetime import datetime
            result["snapshot_date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Process assets with cleaned up names
            asset_values = net_worth_response.get("assetValues", [])
            asset_name_mapping = {
                "ASSET_TYPE_SAVINGS_ACCOUNTS": "Savings Accounts",
                "ASSET_TYPE_MUTUAL_FUND": "Mutual Funds",
                "ASSET_TYPE_INDIAN_SECURITIES": "Indian Securities",
                "ASSET_TYPE_US_SECURITIES": "US Securities",
                "ASSET_TYPE_EPF": "EPF",
                "ASSET_TYPE_FIXED_DEPOSITS": "Fixed Deposits",
                "ASSET_TYPE_GOLD": "Gold"
            }
            
            for asset in asset_values:
                try:
                    asset_type = asset.get("netWorthAttribute", "")
                    asset_value = asset.get("value", {})
                    units = asset_value.get("units", "0")
                    
                    amount = float(units)
                    if amount > 0:
                        # Clean up asset name
                        clean_name = asset_name_mapping.get(asset_type, 
                                     asset_type.replace("ASSET_TYPE_", "").replace("_", " ").title())
                        result["assets"][clean_name] = amount
                        
                except (ValueError, TypeError):
                    continue
            
            # Add EPF from separate EPF data if available and not already included
            if epf_data and "EPF" not in result["assets"]:
                uan_accounts = epf_data.get("uanAccounts", [])
                total_epf = 0
                
                for account in uan_accounts:
                    try:
                        raw_details = account.get("rawDetails", {})
                        current_pf_balance = raw_details.get("current_pf_balance", "0")
                        balance_amount = float(current_pf_balance.replace(",", ""))
                        total_epf += balance_amount
                    except (ValueError, AttributeError, TypeError):
                        continue
                
                if total_epf > 0:
                    result["assets"]["EPF"] = total_epf
            
            # Process liabilities with cleaned up names
            liability_values = net_worth_response.get("liabilityValues", [])
            liability_name_mapping = {
                "LIABILITY_TYPE_HOME_LOAN": "Home Loan",
                "LIABILITY_TYPE_VEHICLE_LOAN": "Vehicle Loan",
                "LIABILITY_TYPE_PERSONAL_LOAN": "Personal Loan",
                "LIABILITY_TYPE_CREDIT_CARD": "Credit Card Outstanding",
                "LIABILITY_TYPE_OTHER_LOAN": "Other Loans",
                "LIABILITY_TYPE_EDUCATION_LOAN": "Education Loan"
            }
            
            for liability in liability_values:
                try:
                    liability_type = liability.get("netWorthAttribute", "")
                    liability_value = liability.get("value", {})
                    units = liability_value.get("units", "0")
                    
                    amount = float(units)
                    if amount > 0:
                        # Clean up liability name
                        clean_name = liability_name_mapping.get(liability_type,
                                    liability_type.replace("LIABILITY_TYPE_", "").replace("_", " ").title())
                        result["liabilities"][clean_name] = amount
                        
                except (ValueError, TypeError):
                    continue
            
            return result
            
        except Exception as e:
            return {
                "total_net_worth": 0,
                "snapshot_date": "",
                "assets": {},
                "liabilities": {},
                "error": str(e)
            }

    def get_net_worth_summary(self) -> Dict[str, Any]:

        """
        Provides a concise summary of the user's total net worth.
        
        Returns:
            Dict[str, Any]: Structured net worth summary with total value and currency
        """
        try:
            # Fetch net worth data from DAL
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return {
                    "status": "ERROR",
                    "message": "Net worth data not available.",
                    "total_net_worth": None,
                    "currency": None
                }
            
            # Extract total net worth value
            net_worth_response = net_worth_data.get("netWorthResponse", {})
            total_net_worth = net_worth_response.get("totalNetWorthValue", {})
            
            if not total_net_worth:
                return {
                    "status": "ERROR", 
                    "message": "Net worth data not available.",
                    "total_net_worth": None,
                    "currency": None
                }
            
            # Get the currency and amount
            currency = total_net_worth.get("currencyCode", "INR")
            units = total_net_worth.get("units", "0")
            
            # Convert to float and format
            try:
                amount = float(units)
                return {
                    "status": "SUCCESS",
                    "total_net_worth": amount,
                    "currency": currency,
                    "currency_symbol": "₹" if currency == "INR" else currency,
                    "formatted_value": f"₹{amount:,.2f}" if currency == "INR" else f"{currency} {amount:,.2f}"
                }
            except (ValueError, TypeError):
                return {
                    "status": "ERROR",
                    "message": "Net worth data not properly formatted.",
                    "total_net_worth": None,
                    "currency": currency,
                    "raw_value": units
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error retrieving net worth data: {str(e)}",
                "total_net_worth": None,
                "currency": None
            }

    def get_asset_breakdown(self) -> List[Dict[str, Any]]:
        """
        Provides a structured list detailing the user's asset allocation.
        
        Returns:
            List[Dict[str, Any]]: List of asset objects with type, value, and metadata
        """
        try:
            # Fetch net worth data from DAL
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return []
            
            # Extract asset values
            net_worth_response = net_worth_data.get("netWorthResponse", {})
            asset_values = net_worth_response.get("assetValues", [])
            
            if not asset_values:
                return []
            
            # Map asset type names to more readable format
            asset_type_mapping = {
                "ASSET_TYPE_SAVINGS_ACCOUNTS": "Savings Accounts",
                "ASSET_TYPE_MUTUAL_FUND": "Mutual Funds",
                "ASSET_TYPE_INDIAN_SECURITIES": "Indian Securities",
                "ASSET_TYPE_US_SECURITIES": "US Securities",
                "ASSET_TYPE_EPF": "Employee Provident Fund (EPF)",
                "ASSET_TYPE_FIXED_DEPOSITS": "Fixed Deposits",
                "ASSET_TYPE_GOLD": "Gold Investments"
            }
            
            asset_breakdown = []
            
            for asset in asset_values:
                asset_type = asset.get("netWorthAttribute", "Unknown Asset")
                asset_value = asset.get("value", {})
                
                # Get currency and amount
                currency = asset_value.get("currencyCode", "INR")
                units = asset_value.get("units", "0")
                
                try:
                    amount = float(units)
                    currency_symbol = "₹" if currency == "INR" else currency
                    
                    # Use readable name if available, otherwise use original
                    readable_name = asset_type_mapping.get(asset_type, asset_type.replace("_", " ").title())
                    
                    asset_breakdown.append({
                        "asset_type": asset_type,
                        "asset_name": readable_name,
                        "value": amount,
                        "currency": currency,
                        "currency_symbol": currency_symbol,
                        "formatted_value": f"{currency_symbol}{amount:,.2f}"
                    })
                except (ValueError, TypeError):
                    # Include invalid entries with error status
                    asset_breakdown.append({
                        "asset_type": asset_type,
                        "asset_name": asset_type_mapping.get(asset_type, asset_type),
                        "value": None,
                        "currency": currency,
                        "currency_symbol": currency,
                        "formatted_value": "Invalid data",
                        "error": f"Invalid amount: {units}"
                    })
            
            return asset_breakdown
            
        except Exception as e:
            return [{"error": f"Error retrieving asset data: {str(e)}"}]

    def get_liability_breakdown(self) -> List[Dict[str, Any]]:
        """
        Provides a structured list detailing the user's liabilities.
        
        Returns:
            List[Dict[str, Any]]: List of liability objects with type, value, and metadata
        """
        try:
            # Fetch net worth data from DAL
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return []
            
            # Extract liability values
            net_worth_response = net_worth_data.get("netWorthResponse", {})
            liability_values = net_worth_response.get("liabilityValues", [])
            
            if not liability_values:
                return []
            
            # Map liability type names to more readable format
            liability_type_mapping = {
                "LIABILITY_TYPE_HOME_LOAN": "Home Loan",
                "LIABILITY_TYPE_VEHICLE_LOAN": "Vehicle Loan",
                "LIABILITY_TYPE_PERSONAL_LOAN": "Personal Loan",
                "LIABILITY_TYPE_CREDIT_CARD": "Credit Card Outstanding",
                "LIABILITY_TYPE_OTHER_LOAN": "Other Loans",
                "LIABILITY_TYPE_EDUCATION_LOAN": "Education Loan"
            }
            
            liability_breakdown = []
            
            for liability in liability_values:
                liability_type = liability.get("netWorthAttribute", "Unknown Liability")
                liability_value = liability.get("value", {})
                
                # Get currency and amount
                currency = liability_value.get("currencyCode", "INR")
                units = liability_value.get("units", "0")
                
                try:
                    amount = float(units)
                    currency_symbol = "₹" if currency == "INR" else currency
                    
                    # Use readable name if available, otherwise use original
                    readable_name = liability_type_mapping.get(liability_type, liability_type.replace("_", " ").title())
                    
                    liability_breakdown.append({
                        "liability_type": liability_type,
                        "liability_name": readable_name,
                        "value": amount,
                        "currency": currency,
                        "currency_symbol": currency_symbol,
                        "formatted_value": f"{currency_symbol}{amount:,.2f}"
                    })
                except (ValueError, TypeError):
                    # Include invalid entries with error status
                    liability_breakdown.append({
                        "liability_type": liability_type,
                        "liability_name": liability_type_mapping.get(liability_type, liability_type),
                        "value": None,
                        "currency": currency,
                        "currency_symbol": currency,
                        "formatted_value": "Invalid data",
                        "error": f"Invalid amount: {units}"
                    })
            
            return liability_breakdown
            
        except Exception as e:
            return [{"error": f"Error retrieving liability data: {str(e)}"}]

    def get_epf_summary(self) -> Dict[str, Any]:
        """
        Provides a summary of the user's Employee Provident Fund.
        
        Returns:
            Dict[str, Any]: Structured EPF summary with balance, employer, and contributions
        """
        try:
            # Fetch EPF data from DAL
            epf_data = self.dal.get_epf_details()
            
            if not epf_data:
                return {
                    "status": "ERROR",
                    "message": "EPF data not available.",
                    "accounts": [],
                    "total_balance": 0,
                    "total_employee_contribution": 0
                }
            
            # Extract UAN accounts
            uan_accounts = epf_data.get("uanAccounts", [])
            
            if not uan_accounts:
                return {
                    "status": "ERROR",
                    "message": "No EPF accounts found.",
                    "accounts": [],
                    "total_balance": 0,
                    "total_employee_contribution": 0
                }
            
            # Process EPF summary
            accounts_summary = []
            total_pf_balance = 0
            total_employee_contribution = 0
            
            for account in uan_accounts:
                try:
                    raw_details = account.get("rawDetails", {})
                    
                    # Extract employer information
                    est_name = raw_details.get("est_name", "Unknown Employer")
                    member_id = raw_details.get("member_id", "N/A")
                    
                    # Extract balance information
                    current_pf_balance = raw_details.get("current_pf_balance", "0")
                    employee_share_total = raw_details.get("employee_share_total", "0")
                    
                    try:
                        balance_amount = float(current_pf_balance.replace(",", ""))
                        employee_total = float(employee_share_total.replace(",", ""))
                        
                        total_pf_balance += balance_amount
                        total_employee_contribution += employee_total
                        
                        accounts_summary.append({
                            "employer_name": est_name,
                            "member_id": member_id,
                            "current_balance": balance_amount,
                            "employee_contribution": employee_total,
                            "formatted_balance": f"₹{balance_amount:,.0f}",
                            "formatted_contribution": f"₹{employee_total:,.0f}"
                        })
                        
                    except (ValueError, AttributeError):
                        # Skip accounts with invalid balance data
                        accounts_summary.append({
                            "employer_name": est_name,
                            "member_id": member_id,
                            "current_balance": None,
                            "employee_contribution": None,
                            "error": "Invalid balance data",
                            "raw_balance": current_pf_balance,
                            "raw_contribution": employee_share_total
                        })
                        
                except (KeyError, TypeError):
                    # Skip accounts with missing data
                    continue
            
            return {
                "status": "SUCCESS",
                "accounts": accounts_summary,
                "total_balance": total_pf_balance,
                "total_employee_contribution": total_employee_contribution,
                "formatted_total_balance": f"₹{total_pf_balance:,.0f}" if total_pf_balance > 0 else "₹0",
                "formatted_total_contribution": f"₹{total_employee_contribution:,.0f}" if total_employee_contribution > 0 else "₹0",
                "accounts_count": len(accounts_summary)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error retrieving EPF data: {str(e)}",
                "accounts": [],
                "total_balance": 0,
                "total_employee_contribution": 0
            }

    def get_portfolio_diversification(self) -> Dict[str, Any]:
        """
        Analyzes the user's asset allocation across different classes like Equity, Debt, and Gold.
        
        Returns:
            Dict[str, Any]: Structured portfolio diversification analysis
        """
        try:
            # Fetch net worth data from DAL
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return {
                    "status": "ERROR",
                    "message": "Portfolio data not available.",
                    "total_portfolio_value": 0,
                    "asset_allocation": [],
                    "mf_allocation": [],
                    "diversification_score": None
                }
            
            # Extract MF scheme analytics for asset class analysis
            mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
            scheme_analytics = mf_analytics.get("schemeAnalytics", [])
            
            # Extract asset values for overall allocation
            net_worth_response = net_worth_data.get("netWorthResponse", {})
            asset_values = net_worth_response.get("assetValues", [])
            
            if not asset_values:
                return {
                    "status": "ERROR",
                    "message": "No portfolio data found.",
                    "total_portfolio_value": 0,
                    "asset_allocation": [],
                    "mf_allocation": [],
                    "diversification_score": None
                }
            
            # Calculate total portfolio value
            total_portfolio = 0
            asset_allocation = {}
            
            # Map asset types to readable categories
            asset_category_mapping = {
                "ASSET_TYPE_MUTUAL_FUND": "Mutual Funds",
                "ASSET_TYPE_INDIAN_SECURITIES": "Indian Stocks",
                "ASSET_TYPE_US_SECURITIES": "US Stocks",
                "ASSET_TYPE_EPF": "EPF",
                "ASSET_TYPE_SAVINGS_ACCOUNTS": "Cash & Bank",
                "ASSET_TYPE_FIXED_DEPOSITS": "Fixed Deposits",
                "ASSET_TYPE_GOLD": "Gold",
                "ASSET_TYPE_REAL_ESTATE": "Real Estate"
            }
            
            # Calculate allocation by asset type
            for asset in asset_values:
                try:
                    asset_type = asset.get("netWorthAttribute", "")
                    asset_value = asset.get("value", {})
                    units = asset_value.get("units", "0")
                    
                    amount = float(units)
                    if amount > 0:
                        category = asset_category_mapping.get(asset_type, "Others")
                        asset_allocation[category] = asset_allocation.get(category, 0) + amount
                        total_portfolio += amount
                        
                except (ValueError, TypeError):
                    continue
            
            if total_portfolio == 0:
                return {
                    "status": "ERROR",
                    "message": "No valid portfolio data found.",
                    "total_portfolio_value": 0,
                    "asset_allocation": [],
                    "mf_allocation": [],
                    "diversification_score": None
                }
            
            # Analyze MF allocation by asset class if available
            mf_allocation = {}
            if scheme_analytics:
                for fund_data in scheme_analytics:
                    try:
                        scheme_detail = fund_data.get("schemeDetail", {})
                        asset_class = scheme_detail.get("assetClass", "Unknown")
                        
                        # Get current value
                        enriched_analytics = fund_data.get("enrichedAnalytics", {})
                        analytics = enriched_analytics.get("analytics", {})
                        scheme_details = analytics.get("schemeDetails", {})
                        current_value = scheme_details.get("currentValue", 0)
                        
                        if current_value > 0:
                            mf_allocation[asset_class] = mf_allocation.get(asset_class, 0) + current_value
                            
                    except (KeyError, TypeError):
                        continue
            
            # Format asset allocation data
            asset_allocation_list = []
            sorted_assets = sorted(asset_allocation.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_assets:
                percentage = (amount / total_portfolio) * 100
                asset_allocation_list.append({
                    "category": category,
                    "amount": amount,
                    "percentage": percentage,
                    "formatted_amount": f"₹{amount:,.0f}",
                    "formatted_percentage": f"{percentage:.1f}%"
                })
            
            # Format MF allocation data
            mf_allocation_list = []
            if mf_allocation:
                total_mf = sum(mf_allocation.values())
                if total_mf > 0:
                    sorted_mf = sorted(mf_allocation.items(), key=lambda x: x[1], reverse=True)
                    
                    for asset_class, amount in sorted_mf:
                        percentage = (amount / total_mf) * 100
                        mf_allocation_list.append({
                            "asset_class": asset_class,
                            "amount": amount,
                            "percentage": percentage,
                            "formatted_amount": f"₹{amount:,.0f}",
                            "formatted_percentage": f"{percentage:.1f}%"
                        })
            
            # Calculate diversification assessment
            largest_allocation = max(asset_allocation.values()) / total_portfolio * 100 if asset_allocation else 0
            
            if largest_allocation > 70:
                diversification_status = "POOR"
                diversification_message = "Portfolio is heavily concentrated in one asset class. Consider diversifying."
            elif largest_allocation < 40:
                diversification_status = "GOOD"
                diversification_message = "Portfolio shows good diversification across asset classes."
            else:
                diversification_status = "MODERATE"
                diversification_message = "Portfolio has moderate diversification."
            
            return {
                "status": "SUCCESS",
                "total_portfolio_value": total_portfolio,
                "formatted_total_value": f"₹{total_portfolio:,.0f}",
                "asset_allocation": asset_allocation_list,
                "mf_allocation": mf_allocation_list,
                "diversification_score": {
                    "status": diversification_status,
                    "largest_allocation_percentage": largest_allocation,
                    "message": diversification_message
                },
                "total_mf_value": sum(mf_allocation.values()) if mf_allocation else 0,
                "asset_categories_count": len(asset_allocation)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error analyzing portfolio diversification: {str(e)}",
                "total_portfolio_value": 0,
                "asset_allocation": [],
                "mf_allocation": [],
                "diversification_score": None
            }


    def get_processed_net_worth_data(self) -> Dict[str, Any]:
        """Processes and returns a structured JSON summary of all net worth and EPF data."""
        try:
            # Get net worth data
            net_worth_summary = self.get_net_worth_summary()
            asset_breakdown = self.get_asset_breakdown()
            liability_breakdown = self.get_liability_breakdown()
            epf_summary = self.get_epf_summary()
            portfolio_diversification = self.get_portfolio_diversification()
            
            # Calculate summary metrics
            total_assets = sum(asset.get("value", 0) for asset in asset_breakdown if isinstance(asset.get("value"), (int, float)))
            total_liabilities = sum(liability.get("value", 0) for liability in liability_breakdown if isinstance(liability.get("value"), (int, float)))
            
            # Asset category percentages
            asset_allocation_summary = {}
            if total_assets > 0:
                for asset in asset_breakdown:
                    if isinstance(asset.get("value"), (int, float)) and asset.get("value") > 0:
                        category = asset.get("asset_name", "Unknown")
                        value = asset.get("value", 0)
                        percentage = (value / total_assets) * 100
                        asset_allocation_summary[category] = {
                            "amount": value,
                            "percentage": percentage
                        }
            
            # Liability category percentages  
            liability_allocation_summary = {}
            if total_liabilities > 0:
                for liability in liability_breakdown:
                    if isinstance(liability.get("value"), (int, float)) and liability.get("value") > 0:
                        category = liability.get("liability_name", "Unknown")
                        value = liability.get("value", 0)
                        percentage = (value / total_liabilities) * 100
                        liability_allocation_summary[category] = {
                            "amount": value,
                            "percentage": percentage
                        }
            
            return {
                "assets_summary": {
                    "total_assets": total_assets,
                    "formatted_total_assets": f"₹{total_assets:,.2f}",
                    "asset_count": len([a for a in asset_breakdown if not a.get("error")]),
                    "asset_allocation_percentages": asset_allocation_summary,
                    "detailed_holdings": asset_breakdown
                },
                "liabilities_summary": {
                    "total_liabilities": total_liabilities,
                    "formatted_total_liabilities": f"₹{total_liabilities:,.2f}",
                    "liability_count": len([l for l in liability_breakdown if not l.get("error")]),
                    "liability_allocation_percentages": liability_allocation_summary,
                    "detailed_liabilities": liability_breakdown
                },
                "epf_summary": epf_summary,
                "portfolio_analysis": portfolio_diversification,
                "net_worth_overview": {
                    "net_worth_data": net_worth_summary,
                    "calculated_net_worth": total_assets - total_liabilities,
                    "debt_to_asset_ratio": total_liabilities / total_assets if total_assets > 0 else 0,
                    "financial_health_indicators": {
                        "positive_net_worth": (total_assets - total_liabilities) > 0,
                        "low_debt_ratio": (total_liabilities / total_assets) < 0.3 if total_assets > 0 else True,
                        "diversified_portfolio": portfolio_diversification.get("diversification_score", {}).get("status") in ["GOOD", "MODERATE"]
                    }
                },
                "data_completeness": {
                    "net_worth_available": net_worth_summary.get("status") == "SUCCESS",
                    "assets_available": len(asset_breakdown) > 0,
                    "liabilities_available": len(liability_breakdown) > 0, 
                    "epf_available": epf_summary.get("status") == "SUCCESS",
                    "portfolio_analysis_available": portfolio_diversification.get("status") == "SUCCESS"
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error processing net worth data: {str(e)}",
                "assets_summary": {},
                "liabilities_summary": {},
                "epf_summary": {},
                "portfolio_analysis": {},
                "net_worth_overview": {},
                "data_completeness": {}
            }


# Import for ADK Agent factory function
from google.adk.agents import Agent


def create_net_worth_adk_agent(dal, model: str) -> Agent:
    """Factory function to create the NetWorth ADK Agent."""
    networth_agent_instance = NetWorthAndHealthAgent(dal)

    networth_tools = [
        networth_agent_instance.get_core_net_worth_snapshot,  # NEW CORE TOOL - First and most prominent
        networth_agent_instance.get_asset_breakdown,
        networth_agent_instance.get_liability_breakdown,
        networth_agent_instance.get_net_worth_summary,
        networth_agent_instance.get_epf_summary,
        networth_agent_instance.get_portfolio_diversification,
        networth_agent_instance.get_processed_net_worth_data
    ]

    return Agent(
        name="NetWorth_Agent",
        model=model,
        description = (
            "Computes a user's total net worth by analyzing assets and liabilities across categories such as savings, mutual funds, EPF, and loans. "
            "Returns a clean, structured financial snapshot usable for dashboards, planning, and audits."
        ),
        instruction = """
You are a Net Worth Analysis Agent. Your job is to provide an accurate snapshot of a user's financial position,
based on structured financial data (from MCP).

Capabilities:
- Compute total net worth using assets and liabilities
- Parse categories such as:
    - Savings accounts
    - Mutual funds
    - EPF balances
    - Indian and US stocks
    - Loans and credit liabilities
- Format results in a structured and compact form, optimized for token efficiency

You should highlight:
- Net worth value
- Breakdown of assets and liabilities
- Date of computation
Do not speculate or interpret trends—focus on clean numeric analysis and categorization.
""",
        tools=networth_tools,
    )