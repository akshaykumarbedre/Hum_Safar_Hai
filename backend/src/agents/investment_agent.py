"""
Investment & Portfolio Analyst Agent

This agent analyzes investment performance, focusing on mutual funds and stocks.
"""
from typing import Dict, Any, List
from ..fi_mcp_data_access import FIMCPDataAccess


class InvestmentAnalystAgent:
    def __init__(self, dal: FIMCPDataAccess):
        self.dal = dal


    def get_core_investment_data(self) -> dict:
        """
        Get core investment data in a pre-processed, token-efficient format.
        
        Returns:
            dict: Pre-processed investment data with minimal token usage
        """
        try:
            # Fetch investment-related data
            net_worth_data = self.dal.get_net_worth()
            mf_transactions = self.dal.get_mutual_fund_transactions()
            stock_transactions = self.dal.get_stock_transactions()
            
            result = {
                "mutual_fund_summary": [],
                "stock_holdings_summary": [],
                "recent_transactions": []
            }
            
            # Process mutual fund data from net worth analytics
            if net_worth_data:
                mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
                scheme_analytics = mf_analytics.get("schemeAnalytics", [])
                
                for fund_data in scheme_analytics:
                    try:
                        # Extract fund details
                        scheme_detail = fund_data.get("schemeDetail", {})
                        name_data = scheme_detail.get("nameData", {})
                        fund_name = name_data.get("longName", "Unknown Fund")
                        
                        # Extract performance metrics
                        enriched_analytics = fund_data.get("enrichedAnalytics", {})
                        analytics = enriched_analytics.get("analytics", {})
                        scheme_details = analytics.get("schemeDetails", {})
                        
                        current_value = scheme_details.get("currentValue", 0)
                        invested_value = scheme_details.get("investedValue", 0)
                        xirr = scheme_details.get("XIRR", 0)
                        
                        if current_value > 0:
                            fund_summary = {
                                "fund_name": fund_name[:50],  # Truncate long names
                                "current_value": current_value,
                                "invested": invested_value,
                                "xirr_percent": round(xirr, 1)
                            }
                            result["mutual_fund_summary"].append(fund_summary)
                            
                    except (KeyError, TypeError):
                        continue
            
            # Process stock holdings (if available from net worth)
            if net_worth_data:
                # Note: Stock details might be limited in net worth data
                # This is a simplified version - in real implementation we'd need more detailed stock data
                asset_values = net_worth_data.get("netWorthResponse", {}).get("assetValues", [])
                for asset in asset_values:
                    if asset.get("netWorthAttribute") == "ASSET_TYPE_INDIAN_SECURITIES":
                        value_info = asset.get("value", {})
                        units = value_info.get("units", "0")
                        try:
                            stock_value = float(units)
                            if stock_value > 0:
                                # This is simplified - real implementation would need detailed stock data
                                result["stock_holdings_summary"].append({
                                    "stock_name": "Stock Holdings",  # Placeholder
                                    "current_value": stock_value,
                                    "quantity": 0  # Would need detailed data
                                })
                        except (ValueError, TypeError):
                            continue
            
            # Process recent transactions (MF and Stock)
            recent_txns = []
            
            # MF transactions
            if mf_transactions:
                mf_txn_data = mf_transactions.get("mfTransactions", [])
                for mf_txn in mf_txn_data[-10:]:  # Last 10 transactions
                    try:
                        scheme_name = mf_txn.get("schemeName", "Unknown Fund")
                        transactions = mf_txn.get("txns", [])
                        
                        for txn in transactions[-3:]:  # Last 3 per fund
                            if len(txn) >= 5:
                                order_type = txn[0]
                                txn_date = txn[1]
                                txn_amount = txn[4]
                                
                                type_mapping = {1: "BUY", 2: "SELL"}
                                readable_type = type_mapping.get(order_type, "UNK")
                                
                                recent_txns.append({
                                    "date": txn_date,
                                    "type": readable_type,
                                    "asset": scheme_name[:40],  # Truncate
                                    "amt": txn_amount
                                })
                    except (KeyError, TypeError, IndexError):
                        continue
            
            # Sort recent transactions by date and limit
            recent_txns.sort(key=lambda x: x["date"], reverse=True)
            result["recent_transactions"] = recent_txns[:15]  # Limit to 15 most recent
            
            return result
            
        except Exception as e:
            return {
                "mutual_fund_summary": [],
                "stock_holdings_summary": [],
                "recent_transactions": [],
                "error": str(e)
            }

    def identify_underperforming_funds(self, xirr_threshold: float = 8.0) -> List[Dict[str, Any]]:

        """
        Identify mutual funds with XIRR below the specified threshold.
        
        Args:
            xirr_threshold (float): XIRR threshold percentage (default: 8.0)
            
        Returns:
            List[Dict[str, Any]]: List of underperforming fund objects
        """
        try:
            # Fetch net worth data which contains MF analytics
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return []
            
            # Access the mfSchemeAnalytics data
            mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
            scheme_analytics = mf_analytics.get("schemeAnalytics", [])
            
            if not scheme_analytics:
                return []
            
            # List to store underperforming funds
            underperforming_funds = []
            total_funds = 0
            
            # Loop through funds and check XIRR
            for fund_data in scheme_analytics:
                try:
                    # Extract fund details
                    scheme_detail = fund_data.get("schemeDetail", {})
                    name_data = scheme_detail.get("nameData", {})
                    fund_name = name_data.get("longName", "Unknown Fund")
                    
                    # Extract performance metrics
                    enriched_analytics = fund_data.get("enrichedAnalytics", {})
                    analytics = enriched_analytics.get("analytics", {})
                    scheme_details = analytics.get("schemeDetails", {})
                    xirr = scheme_details.get("XIRR", 0)
                    invested_value = scheme_details.get("investedValue", 0)
                    current_value = scheme_details.get("currentValue", 0)
                    absolute_returns = scheme_details.get("absoluteReturns", 0)
                    
                    # Additional fund information
                    amc = scheme_detail.get("amc", "Unknown AMC")
                    asset_class = scheme_detail.get("assetClass", "Unknown")
                    category_name = scheme_detail.get("categoryName", "Unknown")
                    plan_type = scheme_detail.get("planType", "Unknown")
                    
                    total_funds += 1
                    
                    # Check if XIRR is below threshold
                    if xirr < xirr_threshold:
                        fund_info = {
                            "fund_name": fund_name,
                            "xirr": xirr,
                            "xirr_threshold": xirr_threshold,
                            "invested_value": invested_value,
                            "current_value": current_value,
                            "absolute_returns": absolute_returns,
                            "return_percentage": (absolute_returns / invested_value * 100) if invested_value > 0 else 0,
                            "amc": amc,
                            "asset_class": asset_class,
                            "category": category_name,
                            "plan_type": plan_type,
                            "formatted_invested": f"₹{invested_value:,.0f}",
                            "formatted_current": f"₹{current_value:,.0f}",
                            "formatted_returns": f"₹{absolute_returns:,.0f}",
                            "performance_gap": xirr_threshold - xirr
                        }
                        underperforming_funds.append(fund_info)
                        
                except (KeyError, TypeError):
                    # Skip funds with missing or invalid data
                    continue
            
            # Sort by performance gap (worst performers first)
            underperforming_funds.sort(key=lambda x: x["performance_gap"], reverse=True)
            
            return underperforming_funds
            
        except Exception as e:
            return [{"error": f"Error analyzing investment performance: {str(e)}"}]

    def get_portfolio_performance_summary(self) -> Dict[str, Any]:
        """
        Provides a holistic summary of the mutual fund portfolio's performance.
        
        Returns:
            Dict[str, Any]: Structured portfolio performance summary
        """
        try:
            # Fetch net worth data which contains MF analytics
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return {
                    "status": "ERROR",
                    "message": "Portfolio data not available.",
                    "total_invested": 0,
                    "current_value": 0,
                    "absolute_gain": 0,
                    "overall_xirr": 0
                }
            
            # Access the mfSchemeAnalytics data
            mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
            scheme_analytics = mf_analytics.get("schemeAnalytics", [])
            
            if not scheme_analytics:
                return {
                    "status": "ERROR",
                    "message": "No mutual fund investments found.",
                    "total_invested": 0,
                    "current_value": 0,
                    "absolute_gain": 0,
                    "overall_xirr": 0
                }
            
            # Initialize portfolio metrics
            total_invested = 0
            total_current_value = 0
            total_absolute_gains = 0
            fund_count = 0
            xirr_values = []
            fund_details = []
            
            # Process each fund
            for fund_data in scheme_analytics:
                try:
                    # Extract fund details
                    scheme_detail = fund_data.get("schemeDetail", {})
                    name_data = scheme_detail.get("nameData", {})
                    fund_name = name_data.get("longName", "Unknown Fund")
                    
                    # Extract performance metrics
                    enriched_analytics = fund_data.get("enrichedAnalytics", {})
                    analytics = enriched_analytics.get("analytics", {})
                    scheme_details = analytics.get("schemeDetails", {})
                    
                    invested_value = scheme_details.get("investedValue", 0)
                    current_value = scheme_details.get("currentValue", 0)
                    absolute_returns = scheme_details.get("absoluteReturns", 0)
                    xirr = scheme_details.get("XIRR", 0)
                    
                    # Additional fund information
                    amc = scheme_detail.get("amc", "Unknown AMC")
                    asset_class = scheme_detail.get("assetClass", "Unknown")
                    
                    # Add to totals
                    total_invested += invested_value
                    total_current_value += current_value
                    total_absolute_gains += absolute_returns
                    fund_count += 1
                    
                    # Collect XIRR values for average calculation
                    if xirr > 0:
                        xirr_values.append(xirr)
                    
                    # Store individual fund details
                    fund_details.append({
                        "fund_name": fund_name,
                        "invested_value": invested_value,
                        "current_value": current_value,
                        "absolute_returns": absolute_returns,
                        "xirr": xirr,
                        "return_percentage": (absolute_returns / invested_value * 100) if invested_value > 0 else 0,
                        "amc": amc,
                        "asset_class": asset_class,
                        "formatted_invested": f"₹{invested_value:,.0f}",
                        "formatted_current": f"₹{current_value:,.0f}",
                        "formatted_returns": f"₹{absolute_returns:,.0f}"
                    })
                        
                except (KeyError, TypeError):
                    # Skip funds with missing data
                    continue
            
            if fund_count == 0:
                return {
                    "status": "ERROR",
                    "message": "No valid mutual fund data found.",
                    "total_invested": 0,
                    "current_value": 0,
                    "absolute_gain": 0,
                    "overall_xirr": 0
                }
            
            # Calculate portfolio metrics
            portfolio_return_percentage = (total_absolute_gains / total_invested * 100) if total_invested > 0 else 0
            average_xirr = sum(xirr_values) / len(xirr_values) if xirr_values else 0
            
            # Performance assessment
            if portfolio_return_percentage > 12:
                performance_status = "EXCELLENT"
                performance_message = "Portfolio is performing well above market averages!"
            elif portfolio_return_percentage > 8:
                performance_status = "GOOD"
                performance_message = "Portfolio is showing good performance."
            elif portfolio_return_percentage > 0:
                performance_status = "MODERATE"
                performance_message = "Portfolio has positive returns but could be improved."
            else:
                performance_status = "POOR"
                performance_message = "Portfolio is currently showing negative returns."
            
            # XIRR assessment
            xirr_status = "UNKNOWN"
            xirr_message = "No XIRR data available"
            if average_xirr > 0:
                if average_xirr > 15:
                    xirr_status = "EXCELLENT"
                    xirr_message = "Excellent XIRR performance across your funds!"
                elif average_xirr > 12:
                    xirr_status = "GOOD"
                    xirr_message = "Good XIRR performance across your funds."
                elif average_xirr > 8:
                    xirr_status = "MODERATE"
                    xirr_message = "Moderate XIRR performance - consider reviewing fund selection."
                else:
                    xirr_status = "POOR"
                    xirr_message = "Low XIRR performance - funds may need review."
            
            # Sort funds by performance
            fund_details.sort(key=lambda x: x["return_percentage"], reverse=True)
            
            return {
                "status": "SUCCESS",
                "portfolio_overview": {
                    "fund_count": fund_count,
                    "total_invested": total_invested,
                    "current_value": total_current_value,
                    "absolute_gain": total_absolute_gains,
                    "overall_return_percentage": portfolio_return_percentage,
                    "average_xirr": average_xirr,
                    "formatted_invested": f"₹{total_invested:,.0f}",
                    "formatted_current": f"₹{total_current_value:,.0f}",
                    "formatted_gain": f"₹{total_absolute_gains:,.0f}"
                },
                "performance_assessment": {
                    "status": performance_status,
                    "message": performance_message,
                    "xirr_status": xirr_status,
                    "xirr_message": xirr_message
                },
                "fund_details": fund_details,
                "top_performer": fund_details[0] if fund_details else None,
                "worst_performer": fund_details[-1] if fund_details else None,
                "funds_with_positive_returns": len([f for f in fund_details if f["return_percentage"] > 0]),
                "funds_with_negative_returns": len([f for f in fund_details if f["return_percentage"] < 0])
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error analyzing portfolio performance: {str(e)}",
                "total_invested": 0,
                "current_value": 0,
                "absolute_gain": 0,
                "overall_xirr": 0
            }

    def get_fund_details(self, fund_name_query: str) -> Dict[str, Any]:
        """
        Fetches details for a specific mutual fund the user asks about.
        
        Args:
            fund_name_query (str): Name or partial name of the fund to search for
            
        Returns:
            Dict[str, Any]: Detailed information about the found fund
        """
        try:
            # Fetch net worth data which contains MF analytics
            net_worth_data = self.dal.get_net_worth()
            
            if not net_worth_data:
                return {
                    "status": "ERROR",
                    "message": "Fund data not available.",
                    "fund_found": False
                }
            
            # Access the mfSchemeAnalytics data
            mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
            scheme_analytics = mf_analytics.get("schemeAnalytics", [])
            
            if not scheme_analytics:
                return {
                    "status": "ERROR",
                    "message": "No mutual fund investments found.",
                    "fund_found": False
                }
            
            # Search for the fund by name
            fund_name_upper = fund_name_query.upper()
            matching_funds = []
            
            for fund_data in scheme_analytics:
                try:
                    # Extract fund details
                    scheme_detail = fund_data.get("schemeDetail", {})
                    name_data = scheme_detail.get("nameData", {})
                    fund_name = name_data.get("longName", "Unknown Fund")
                    
                    # Check if the query matches the fund name
                    if fund_name_upper in fund_name.upper():
                        matching_funds.append((fund_data, fund_name))
                        
                except (KeyError, TypeError):
                    continue
            
            if not matching_funds:
                return {
                    "status": "ERROR",
                    "message": f"No fund found matching '{fund_name_query}'. Please check the fund name and try again.",
                    "fund_found": False,
                    "search_query": fund_name_query
                }
            
            # If multiple matches, take the first one (could be enhanced to show all)
            fund_data, fund_name = matching_funds[0]
            
            try:
                # Extract detailed fund information
                scheme_detail = fund_data.get("schemeDetail", {})
                
                # Basic fund details
                amc = scheme_detail.get("amc", "Unknown AMC")
                plan_type = scheme_detail.get("planType", "Unknown")
                asset_class = scheme_detail.get("assetClass", "Unknown")
                category_name = scheme_detail.get("categoryName", "Unknown")
                risk_level = scheme_detail.get("fundhouseDefinedRiskLevel", "Unknown")
                
                # Performance metrics
                enriched_analytics = fund_data.get("enrichedAnalytics", {})
                analytics = enriched_analytics.get("analytics", {})
                scheme_details = analytics.get("schemeDetails", {})
                
                invested_value = scheme_details.get("investedValue", 0)
                current_value = scheme_details.get("currentValue", 0)
                absolute_returns = scheme_details.get("absoluteReturns", 0)
                xirr = scheme_details.get("XIRR", 0)
                
                # Calculate return percentage
                return_percentage = (absolute_returns / invested_value * 100) if invested_value > 0 else 0
                
                # Performance assessment
                if return_percentage > 15:
                    performance_status = "EXCELLENT"
                    performance_message = "Excellent performance!"
                elif return_percentage > 8:
                    performance_status = "GOOD"
                    performance_message = "Good performance!"
                elif return_percentage > 0:
                    performance_status = "POSITIVE"
                    performance_message = "Positive returns."
                else:
                    performance_status = "NEGATIVE"
                    performance_message = "Currently showing negative returns."
                
                # Risk assessment
                risk_assessment = "UNKNOWN"
                risk_message = "Risk level information not available."
                if "HIGH_RISK" in risk_level or "VERY_HIGH_RISK" in risk_level:
                    risk_assessment = "HIGH"
                    risk_message = "This is a high-risk fund - monitor closely."
                elif "MODERATE_RISK" in risk_level:
                    risk_assessment = "MODERATE"
                    risk_message = "Moderate risk fund - suitable for balanced portfolios."
                elif "LOW_RISK" in risk_level:
                    risk_assessment = "LOW"
                    risk_message = "Low risk fund - provides stability to your portfolio."
                
                return {
                    "status": "SUCCESS",
                    "fund_found": True,
                    "fund_details": {
                        "fund_name": fund_name,
                        "amc": amc.replace('_', ' ').title(),
                        "plan_type": plan_type,
                        "asset_class": asset_class,
                        "category": category_name.replace('_', ' ').title(),
                        "risk_level": risk_level.replace('_', ' ').title()
                    },
                    "investment_performance": {
                        "invested_value": invested_value,
                        "current_value": current_value,
                        "absolute_returns": absolute_returns,
                        "return_percentage": return_percentage,
                        "xirr": xirr,
                        "formatted_invested": f"₹{invested_value:,.0f}",
                        "formatted_current": f"₹{current_value:,.0f}",
                        "formatted_returns": f"₹{absolute_returns:,.0f}"
                    },
                    "assessments": {
                        "performance_status": performance_status,
                        "performance_message": performance_message,
                        "risk_assessment": risk_assessment,
                        "risk_message": risk_message
                    },
                    "search_query": fund_name_query,
                    "exact_match": fund_name_query.upper() == fund_name.upper()
                }
                
            except (KeyError, TypeError):
                return {
                    "status": "ERROR",
                    "message": f"Found fund '{fund_name}' but unable to retrieve detailed performance data.",
                    "fund_found": True,
                    "fund_name": fund_name
                }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error retrieving fund details: {str(e)}",
                "fund_found": False
            }


    def get_processed_investment_portfolio(self) -> Dict[str, Any]:
        """Processes and returns a structured JSON summary of all investment portfolio data."""
        try:
            # Get all investment analysis
            portfolio_performance = self.get_portfolio_performance_summary()
            underperforming_funds = self.identify_underperforming_funds()
            
            # Fetch raw data for comprehensive analysis
            net_worth_data = self.dal.get_net_worth()
            mf_transactions = self.dal.get_mutual_fund_transactions()
            stock_transactions = self.dal.get_stock_transactions()
            
            # Process mutual fund holdings
            mutual_fund_holdings = []
            if net_worth_data:
                mf_analytics = net_worth_data.get("mfSchemeAnalytics", {})
                scheme_analytics = mf_analytics.get("schemeAnalytics", [])
                
                for fund_data in scheme_analytics:
                    try:
                        scheme_detail = fund_data.get("schemeDetail", {})
                        name_data = scheme_detail.get("nameData", {})
                        fund_name = name_data.get("longName", "Unknown Fund")
                        
                        enriched_analytics = fund_data.get("enrichedAnalytics", {})
                        analytics = enriched_analytics.get("analytics", {})
                        scheme_details = analytics.get("schemeDetails", {})
                        
                        mutual_fund_holdings.append({
                            "fund_name": fund_name,
                            "amc": scheme_detail.get("amc", "Unknown"),
                            "asset_class": scheme_detail.get("assetClass", "Unknown"),
                            "plan_type": scheme_detail.get("planType", "Unknown"),
                            "invested_value": scheme_details.get("investedValue", 0),
                            "current_value": scheme_details.get("currentValue", 0),
                            "absolute_returns": scheme_details.get("absoluteReturns", 0),
                            "xirr": scheme_details.get("XIRR", 0),
                            "return_percentage": (scheme_details.get("absoluteReturns", 0) / scheme_details.get("investedValue", 1) * 100) if scheme_details.get("investedValue", 0) > 0 else 0,
                            "is_underperforming": any(uf.get("fund_name") == fund_name for uf in underperforming_funds),
                            "formatted_invested": f"₹{scheme_details.get('investedValue', 0):,.0f}",
                            "formatted_current": f"₹{scheme_details.get('currentValue', 0):,.0f}"
                        })
                    except (KeyError, TypeError):
                        continue
            
            # Process stock holdings
            stock_holdings = []
            if net_worth_data:
                account_details = net_worth_data.get("accountDetailsBulkResponse", {}).get("accountDetailsMap", {})
                
                for account_id, account_info in account_details.items():
                    if account_info.get("accountDetails", {}).get("accInstrumentType") == "ACC_INSTRUMENT_TYPE_EQUITIES":
                        equity_summary = account_info.get("equitySummary", {})
                        holdings = equity_summary.get("holdingsInfo", [])
                        
                        for holding in holdings:
                            try:
                                isin = holding.get("isin", "")
                                issuer_name = holding.get("issuerName", "Unknown")
                                units = holding.get("units", 0)
                                last_price = holding.get("lastTradedPrice", {})
                                
                                price_units = float(last_price.get("units", "0"))
                                price_nanos = float(last_price.get("nanos", "0"))
                                price = price_units + (price_nanos / 1_000_000_000)
                                
                                stock_value = units * price
                                
                                stock_holdings.append({
                                    "issuer_name": issuer_name,
                                    "isin": isin,
                                    "units": units,
                                    "last_price": price,
                                    "total_value": stock_value,
                                    "formatted_value": f"₹{stock_value:,.0f}",
                                    "formatted_price": f"₹{price:,.2f}"
                                })
                            except (ValueError, TypeError):
                                continue
            
            # Calculate summary metrics
            total_mf_invested = sum(fund.get("invested_value", 0) for fund in mutual_fund_holdings)
            total_mf_current = sum(fund.get("current_value", 0) for fund in mutual_fund_holdings)
            total_stock_value = sum(stock.get("total_value", 0) for stock in stock_holdings)
            total_portfolio_value = total_mf_current + total_stock_value
            
            # Asset class distribution
            asset_class_distribution = {}
            for fund in mutual_fund_holdings:
                asset_class = fund.get("asset_class", "Unknown")
                current_value = fund.get("current_value", 0)
                asset_class_distribution[asset_class] = asset_class_distribution.get(asset_class, 0) + current_value
            
            # Performance metrics
            top_performers = sorted(mutual_fund_holdings, key=lambda x: x.get("return_percentage", 0), reverse=True)[:3]
            worst_performers = sorted(mutual_fund_holdings, key=lambda x: x.get("return_percentage", 0))[:3]
            
            return {
                "mutual_fund_holdings": mutual_fund_holdings,
                "stock_holdings": stock_holdings,
                "portfolio_summary": {
                    "total_mutual_fund_invested": total_mf_invested,
                    "total_mutual_fund_current": total_mf_current,
                    "total_stock_value": total_stock_value,
                    "total_portfolio_value": total_portfolio_value,
                    "mutual_fund_count": len(mutual_fund_holdings),
                    "stock_count": len(stock_holdings),
                    "formatted_total_portfolio": f"₹{total_portfolio_value:,.0f}",
                    "formatted_mf_invested": f"₹{total_mf_invested:,.0f}",
                    "formatted_mf_current": f"₹{total_mf_current:,.0f}",
                    "formatted_stock_value": f"₹{total_stock_value:,.0f}"
                },
                "asset_class_distribution": {
                    asset_class: {
                        "amount": amount,
                        "percentage": (amount / total_mf_current * 100) if total_mf_current > 0 else 0,
                        "formatted_amount": f"₹{amount:,.0f}"
                    }
                    for asset_class, amount in asset_class_distribution.items()
                },
                "performance_analysis": portfolio_performance,
                "underperforming_funds": underperforming_funds,
                "top_performers": top_performers,
                "worst_performers": worst_performers,
                "portfolio_health_indicators": {
                    "diversified_across_asset_classes": len(asset_class_distribution) > 2,
                    "has_underperforming_funds": len(underperforming_funds) > 0,
                    "positive_overall_returns": portfolio_performance.get("portfolio_overview", {}).get("overall_return_percentage", 0) > 0,
                    "stock_equity_exposure": total_stock_value > 0,
                    "concentrated_in_single_asset_class": any(dist.get("percentage", 0) > 70 for dist in asset_class_distribution.values())
                },
                "data_completeness": {
                    "net_worth_data_available": net_worth_data is not None,
                    "mf_transactions_available": mf_transactions is not None,
                    "stock_transactions_available": stock_transactions is not None,
                    "portfolio_performance_available": portfolio_performance.get("status") == "SUCCESS",
                    "mutual_fund_holdings_available": len(mutual_fund_holdings) > 0,
                    "stock_holdings_available": len(stock_holdings) > 0
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error processing investment portfolio: {str(e)}",
                "mutual_fund_holdings": [],
                "stock_holdings": [],
                "portfolio_summary": {},
                "asset_class_distribution": {},
                "performance_analysis": {},
                "underperforming_funds": [],
                "top_performers": [],
                "worst_performers": [],
                "portfolio_health_indicators": {},
                "data_completeness": {}
            }


# Import for ADK Agent factory function
from google.adk.agents import Agent


def create_investment_adk_agent(dal, model: str) -> Agent:
    """Factory function to create the Investment ADK Agent."""
    inv_agent_instance = InvestmentAnalystAgent(dal)

    investment_tools = [
        inv_agent_instance.get_core_investment_data,  # NEW CORE TOOL - First and most prominent
        inv_agent_instance.identify_underperforming_funds,
        inv_agent_instance.get_portfolio_performance_summary,
        inv_agent_instance.get_fund_details,
        inv_agent_instance.get_processed_investment_portfolio
    ]

    return Agent(
        name="Investment_Agent",
        model=model,
        description="Handles questions about investment performance and portfolio analysis.",
        tools=investment_tools,
    )