"""
Financial Health Auditor Agent

Implements a series of expert-defined checks to audit a user's financial health
and detect strategic anomalies.
"""
import pandas as pd
from typing import Optional, List, Dict, Any

from src.fi_mcp_data_access import FIMCPDataAccess
from google.adk.agents import Agent

class FinancialHealthAuditorAgent:
    def __init__(self, dal: FIMCPDataAccess):
        """Initializes the agent with a Data Access Layer instance."""
        self.dal = dal
        # Pre-load data for efficiency
        self.net_worth_data = self.dal.get_net_worth()
        self.credit_report = self.dal.get_credit_report()
        self.bank_transactions = self.dal.get_bank_transactions()
        self.mf_transactions = self.dal.get_mutual_fund_transactions()
        self.stock_transactions = self.dal.get_stock_transactions()
        self.epf_details = self.dal.get_epf_details()

    # --- Net Worth Audits ---
    def audit_net_worth_growth(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Stagnant or Declining Net Worth.
        Logic: Checks if net worth is consistently growing. (Note: True time-series requires historical data, this will be a placeholder).
        Data Sources: `netWorthResponse.totalNetWorthValue`
        """
        # Placeholder logic: In a real app, you would compare current net worth to historical snapshots.
        # For now, we check if the net worth is positive.
        if self.net_worth_data:
            net_worth_str = self.net_worth_data.get("netWorthResponse", {}).get("totalNetWorthValue", {}).get("units", "0")
            try:
                net_worth_value = float(net_worth_str)
                if net_worth_value < 0:
                    return {
                        "anomaly_code": "NEGATIVE_NET_WORTH",
                        "anomaly_title": "Negative Net Worth",
                        "description": "Your net worth is negative, indicating that your liabilities exceed your assets.",
                        "recommendation": "A detailed review of assets and liabilities is required to address this critical financial situation.",
                        "details": {
                            "current_net_worth": net_worth_value,
                            "status": "CRITICAL"
                        }
                    }
            except (ValueError, TypeError):
                return {
                    "anomaly_code": "NET_WORTH_DATA_ERROR",
                    "anomaly_title": "Net Worth Data Error",
                    "description": "Unable to determine net worth value from available data.",
                    "recommendation": "Review and update your financial data to ensure accurate calculations.",
                    "details": {
                        "data_value": net_worth_str,
                        "status": "WARNING"
                    }
                }
        return None  # Assume growth if positive for this simplified check

    def audit_bad_debt_ratio(self, threshold: float = 0.15) -> Optional[Dict[str, Any]]:
        """
        Anomaly 2: High "Bad Debt" to Asset Ratio.
        Logic: Calculates the ratio of high-interest debt (Credit Card, Personal Loan) to total assets.
        Data Sources: `netWorthResponse.liabilityValues`, `netWorthResponse.assetValues`
        """
        if not self.net_worth_data:
            return None
            
        net_worth_response = self.net_worth_data.get("netWorthResponse", {})
        liabilities = net_worth_response.get("liabilityValues", [])
        assets = net_worth_response.get("assetValues", [])
        
        # Sum high-interest debt (Credit Card, Personal Loan)
        bad_debt_total = 0
        for liability in liabilities:
            liability_type = liability.get("netWorthAttribute", "")
            if liability_type in ["LIABILITY_TYPE_CREDIT_CARD", "LIABILITY_TYPE_PERSONAL_LOAN"]:
                try:
                    bad_debt_total += float(liability.get("value", {}).get("units", "0"))
                except (ValueError, TypeError):
                    continue
        
        # Sum all assets
        total_assets = 0
        for asset in assets:
            try:
                total_assets += float(asset.get("value", {}).get("units", "0"))
            except (ValueError, TypeError):
                continue
                
        if total_assets > 0:
            ratio = bad_debt_total / total_assets
            if ratio > threshold:
                return {
                    "anomaly_code": "HIGH_BAD_DEBT_RATIO",
                    "anomaly_title": "High 'Bad Debt' to Asset Ratio",
                    "description": f"Your high-interest debt (Credit Cards, Personal Loans) is {ratio:.1%} of your total assets, exceeding the {threshold:.0%} threshold.",
                    "recommendation": "Prioritize aggressive repayment of this debt to prevent wealth erosion.",
                    "details": {
                        "bad_debt_amount": bad_debt_total,
                        "total_assets_amount": total_assets,
                        "calculated_ratio": ratio,
                        "threshold": threshold
                    }
                }
        
        return None

    def audit_asset_allocation(self, age: int = 30, threshold: float = 0.40) -> Optional[Dict[str, Any]]:
        """
        Anomaly 3: Asset Misallocation (Over-saving or Under-investing).
        Logic: Checks if an excessive percentage of assets are in low-yield accounts for a given age profile.
        Data Sources: `netWorthResponse.assetValues`
        """
        if not self.net_worth_data:
            return None
            
        assets = self.net_worth_data.get("netWorthResponse", {}).get("assetValues", [])
        
        # Sum low-yield assets (savings accounts, fixed deposits)
        low_yield_assets = 0
        total_assets = 0
        
        for asset in assets:
            try:
                asset_value = float(asset.get("value", {}).get("units", "0"))
                total_assets += asset_value
                
                asset_type = asset.get("netWorthAttribute", "")
                if asset_type in ["ASSET_TYPE_SAVINGS_ACCOUNTS", "ASSET_TYPE_FIXED_DEPOSITS"]:
                    low_yield_assets += asset_value
            except (ValueError, TypeError):
                continue
                
        if total_assets > 0:
            low_yield_ratio = low_yield_assets / total_assets
            if age < 45 and low_yield_ratio > threshold:
                return {
                    "anomaly_code": "ASSET_MISALLOCATION",
                    "anomaly_title": "Asset Misallocation - Over-saving",
                    "description": f"Over {low_yield_ratio:.1%} of your assets are in low-growth savings/FDs, potentially losing value to inflation for someone of age {age}.",
                    "recommendation": "Consider moving some funds to growth-oriented investments like equity mutual funds or stocks for better long-term returns.",
                    "details": {
                        "low_yield_assets_amount": low_yield_assets,
                        "total_assets_amount": total_assets,
                        "low_yield_ratio": low_yield_ratio,
                        "threshold": threshold,
                        "age": age,
                        "age_threshold": 45
                    }
                }
        
        return None
        
    # --- Bank Transaction Audits ---
    def audit_lifestyle_creep(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Lifestyle Creep.
        Logic: Tracks non-essential spending over time. (Note: requires historical data).
        Data Sources: `bank_transactions.json`
        """
        if not self.bank_transactions or not self.bank_transactions.get('bankTransactions'):
            return None
            
        # Convert to DataFrame for analysis
        all_txns = []
        for bank in self.bank_transactions['bankTransactions']:
            for txn in bank['txns']:
                all_txns.append([bank['bank']] + txn)
        
        if not all_txns:
            return None
            
        df = pd.DataFrame(all_txns, columns=['bank', 'amount', 'narration', 'date', 'type', 'mode', 'balance'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['amount', 'date'], inplace=True)
        
        if df.empty:
            return None
            
        # Filter for debit transactions (non-essential spending patterns)
        debits = df[df['type'] == 2].copy()
        
        # Look for entertainment, shopping, dining patterns
        non_essential_keywords = ['SWIGGY', 'ZOMATO', 'AMAZON', 'FLIPKART', 'ENTERTAINMENT', 'MOVIE', 'RESTAURANT', 'CAFE']
        non_essential_txns = debits[debits['narration'].str.upper().str.contains('|'.join(non_essential_keywords), na=False)]
        
        if len(non_essential_txns) > 10:  # Basic threshold for lifestyle creep detection
            recent_spend = non_essential_txns['amount'].sum()
            if recent_spend > 50000:  # Threshold for concerning non-essential spending
                return {
                    "anomaly_code": "LIFESTYLE_CREEP",
                    "anomaly_title": "Lifestyle Creep Detected",
                    "description": f"Your non-essential spending appears high at ₹{recent_spend:,.0f}, which may be limiting your ability to save and invest.",
                    "recommendation": "Review and reduce discretionary spending on entertainment, dining out, and online shopping to improve your savings rate.",
                    "details": {
                        "non_essential_spending_amount": recent_spend,
                        "non_essential_transactions_count": len(non_essential_txns),
                        "spending_threshold": 50000,
                        "transaction_threshold": 10,
                        "spending_categories": non_essential_keywords
                    }
                }
        
        return None

    def audit_wealth_leaking_fees(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 2: Recurring "Wealth-Leaking" Fees.
        Logic: Scans transactions for penalty fees, interest charges, etc.
        Data Sources: `bank_transactions.json`
        """
        if not self.bank_transactions or not self.bank_transactions.get('bankTransactions'):
            return None
            
        fee_keywords = ['LATE FEE', 'PENALTY', 'INTEREST CHARGE', 'MINIMUM BALANCE', 'OVERDRAFT', 'BOUNCE', 'RETURN']
        fee_transactions = []
        
        for bank in self.bank_transactions['bankTransactions']:
            for txn in bank['txns']:
                narration = str(txn[1]).upper()
                if any(keyword in narration for keyword in fee_keywords):
                    fee_transactions.append({
                        'bank': bank['bank'],
                        'amount': txn[0],
                        'narration': txn[1],
                        'date': txn[2]
                    })
        
        if fee_transactions:
            total_fees = sum(float(txn['amount']) for txn in fee_transactions if isinstance(txn['amount'], (int, float, str)) and str(txn['amount']).replace('.', '').replace('-', '').isdigit())
            return {
                "anomaly_code": "WEALTH_LEAKING_FEES",
                "anomaly_title": "Wealth-Leaking Fees Detected",
                "description": f"₹{total_fees:,.0f} in penalties and fees were found, representing avoidable costs that impact your wealth building.",
                "recommendation": "Review these fees and set up automatic payments, maintain minimum balances, and avoid overdrafts to eliminate these recurring costs.",
                "details": {
                    "total_fees_amount": total_fees,
                    "fee_transactions_count": len(fee_transactions),
                    "fee_categories": fee_keywords,
                    "sample_transactions": fee_transactions[:5]  # Show first 5 for reference
                }
            }
        
        return None

    # --- Mutual Fund Audits ---
    def audit_regular_vs_direct_plans(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Investing in "Regular" instead of "Direct" Plans.
        Logic: Identifies mutual funds that are 'Regular' plans, which have higher fees.
        Data Sources: `mfSchemeAnalytics.schemeAnalytics`
        """
        if not self.net_worth_data:
            return None
            
        scheme_analytics = self.net_worth_data.get("mfSchemeAnalytics", {}).get("schemeAnalytics", [])
        regular_funds = []
        
        for scheme in scheme_analytics:
            plan_type = scheme.get("schemeDetail", {}).get("planType", "")
            if plan_type == "REGULAR":
                fund_name = scheme.get("schemeDetail", {}).get("nameData", {}).get("longName", "Unknown Fund")
                # Get investment amount if available
                enriched_analytics = scheme.get("enrichedAnalytics", {})
                analytics = enriched_analytics.get("analytics", {})
                scheme_details = analytics.get("schemeDetails", {})
                invested_value_data = scheme_details.get("investedValue", {})
                
                # Handle both dict format {'units': '40000'} and direct numeric format
                if isinstance(invested_value_data, dict):
                    invested_value = float(invested_value_data.get("units", 0))
                else:
                    invested_value = float(invested_value_data) if invested_value_data else 0
                
                regular_funds.append({
                    "fund_name": fund_name,
                    "invested_amount": invested_value
                })
        
        if regular_funds:
            total_regular_investment = sum(fund["invested_amount"] for fund in regular_funds)
            fund_names = [fund["fund_name"] for fund in regular_funds[:3]]  # Show first 3 funds
            
            return {
                "anomaly_code": "REGULAR_PLAN_INVESTMENT",
                "anomaly_title": "Investment in Regular Plan Mutual Funds",
                "description": f"You are invested in {len(regular_funds)} 'Regular' plan mutual funds with hidden commissions that reduce your returns.",
                "recommendation": "Switch to 'Direct' plans of the same funds to eliminate distribution commissions and significantly boost your long-term returns.",
                "details": {
                    "regular_funds_count": len(regular_funds),
                    "total_regular_investment": total_regular_investment,
                    "sample_fund_names": fund_names,
                    "all_regular_funds": regular_funds
                }
            }
        
        return None

    # --- Stock Audits ---
    def audit_stock_concentration_risk(self, threshold: float = 0.15) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Over-Concentration in a Single Stock/Sector.
        Logic: Checks if any single stock constitutes too large a portion of the equity portfolio.
        Data Sources: `accountDetailsBulkResponse`
        """
        if not self.net_worth_data:
            return None
            
        account_details = self.net_worth_data.get("accountDetailsBulkResponse", {}).get("accountDetailsMap", {})
        
        # Calculate total equity portfolio value and individual stock concentrations
        total_equity_value = 0
        stock_values = {}
        
        for account_id, account_info in account_details.items():
            if account_info.get("accountDetails", {}).get("accInstrumentType") == "ACC_INSTRUMENT_TYPE_EQUITIES":
                equity_summary = account_info.get("equitySummary", {})
                holdings = equity_summary.get("holdingsInfo", [])
                
                for holding in holdings:
                    isin = holding.get("isin", "")
                    issuer_name = holding.get("issuerName", "Unknown")
                    units = holding.get("units", 0)
                    last_price = holding.get("lastTradedPrice", {})
                    
                    try:
                        price_units = float(last_price.get("units", "0"))
                        price_nanos = float(last_price.get("nanos", "0"))
                        price = price_units + (price_nanos / 1_000_000_000)
                        
                        stock_value = units * price
                        total_equity_value += stock_value
                        
                        if issuer_name in stock_values:
                            stock_values[issuer_name] += stock_value
                        else:
                            stock_values[issuer_name] = stock_value
                    except (ValueError, TypeError):
                        continue
        
        if total_equity_value > 0:
            concentrated_stocks = []
            for stock_name, stock_value in stock_values.items():
                concentration = stock_value / total_equity_value
                if concentration > threshold:
                    concentrated_stocks.append({
                        "stock_name": stock_name,
                        "stock_value": stock_value,
                        "concentration_percentage": concentration,
                        "concentration_ratio": concentration
                    })
            
            if concentrated_stocks:
                # Sort by concentration (highest first)
                concentrated_stocks.sort(key=lambda x: x["concentration_ratio"], reverse=True)
                top_concentrated_stock = concentrated_stocks[0]
                
                return {
                    "anomaly_code": "STOCK_CONCENTRATION_RISK",
                    "anomaly_title": "Over-Concentration in Single Stock",
                    "description": f"The stock {top_concentrated_stock['stock_name']} makes up {top_concentrated_stock['concentration_percentage']:.1%} of your equity portfolio, exposing you to significant concentration risk.",
                    "recommendation": "Diversify your equity holdings to reduce risk. Consider limiting individual stock positions to less than 15% of your total equity portfolio.",
                    "details": {
                        "total_equity_portfolio_value": total_equity_value,
                        "concentration_threshold": threshold,
                        "concentrated_stocks_count": len(concentrated_stocks),
                        "concentrated_stocks": concentrated_stocks,
                        "top_concentrated_stock": top_concentrated_stock
                    }
                }
        
        return None
        
    # --- EPF Audits ---
    def audit_inoperative_epf_accounts(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Inoperative or Unclaimed PF Accounts.
        Logic: Looks for EPF accounts from previous employers that haven't been transferred.
        Data Sources: `uanAccounts.rawDetails.est_details`
        """
        if not self.epf_details:
            return None
            
        uan_accounts = self.epf_details.get("uanAccounts", [])
        old_accounts = []
        
        for uan_account in uan_accounts:
            raw_details = uan_account.get("rawDetails", {})
            est_details = raw_details.get("est_details", [])
            
            if len(est_details) > 1:  # Multiple establishments indicate potential old accounts
                for establishment in est_details:
                    doe_epf = establishment.get("doe_epf")
                    if doe_epf:  # Has exit date, indicating old account
                        est_name = establishment.get("est_name", "Unknown Company")
                        doj_epf = establishment.get("doj_epf", "Unknown")
                        old_accounts.append({
                            "company_name": est_name,
                            "date_of_joining": doj_epf,
                            "date_of_exit": doe_epf
                        })
        
        if old_accounts:
            return {
                "anomaly_code": "INOPERATIVE_EPF_ACCOUNTS",
                "anomaly_title": "Inoperative EPF Accounts Detected",
                "description": f"Found {len(old_accounts)} old EPF account(s) from previous employer(s) that may be inoperative.",
                "recommendation": "Consolidate all PF accounts under your current UAN to ensure continued interest accrual and avoid losing track of your retirement savings.",
                "details": {
                    "old_accounts_count": len(old_accounts),
                    "old_accounts": old_accounts,
                    "action_required": "Transfer or consolidate accounts"
                }
            }
        
        return None
        
    # --- Credit Report Audits ---
    def audit_negative_payment_history(self) -> Optional[Dict[str, Any]]:
        """
        Anomaly 1: Any Negative Payment History.
        Logic: Checks for any record of late payments.
        Data Sources: `creditAccount.creditAccountDetails`
        """
        if not self.credit_report:
            return None
            
        credit_reports = self.credit_report.get("creditReports", [])
        negative_accounts = []
        
        for report in credit_reports:
            credit_data = report.get("creditReportData", {})
            credit_account = credit_data.get("creditAccount", {})
            account_details = credit_account.get("creditAccountDetails", [])
            
            for account in account_details:
                payment_rating = account.get("paymentRating", "0")
                if payment_rating != "0":  # Non-zero payment rating indicates negative history
                    lender_name = account.get("subscriberName", "Unknown Lender")
                    account_type = account.get("accountType", "Unknown")
                    negative_accounts.append({
                        "lender_name": lender_name,
                        "payment_rating": payment_rating,
                        "account_type": account_type
                    })
        
        if negative_accounts:
            lender_names = [acc["lender_name"] for acc in negative_accounts[:3]]  # Show first 3 lenders
            
            return {
                "anomaly_code": "NEGATIVE_PAYMENT_HISTORY",
                "anomaly_title": "Negative Payment History Detected",
                "description": f"Negative payment history found for {len(negative_accounts)} account(s) with lenders including {', '.join(lender_names)}.",
                "recommendation": "Contact these lenders to understand and resolve any outstanding issues. Consider setting up automatic payments to avoid future delays.",
                "details": {
                    "negative_accounts_count": len(negative_accounts),
                    "affected_lenders": lender_names,
                    "all_negative_accounts": negative_accounts,
                    "severity": "CRITICAL"
                }
            }
        
        return None

    def audit_high_credit_utilization(self, threshold: float = 0.30) -> Optional[Dict[str, Any]]:
        """
        Anomaly 2: High Credit Utilization Ratio.
        Logic: Checks if credit card balances are high relative to income (as a proxy for limit).
        Data Sources: `creditAccount.creditAccountDetails`, `bank_transactions.json`
        """
        if not self.credit_report or not self.bank_transactions:
            return None
            
        # Calculate total credit card balances
        total_card_balance = 0
        credit_cards = []
        credit_reports = self.credit_report.get("creditReports", [])
        
        for report in credit_reports:
            credit_data = report.get("creditReportData", {})
            credit_account = credit_data.get("creditAccount", {})
            account_details = credit_account.get("creditAccountDetails", [])
            
            for account in account_details:
                account_type = account.get("accountType", "")
                if account_type == "01":  # Credit card account type
                    try:
                        balance = float(account.get("currentBalance", "0"))
                        lender_name = account.get("subscriberName", "Unknown")
                        total_card_balance += balance
                        credit_cards.append({
                            "lender": lender_name,
                            "balance": balance
                        })
                    except (ValueError, TypeError):
                        continue
        
        # Estimate monthly income from credit transactions
        monthly_income = 0
        if self.bank_transactions.get('bankTransactions'):
            salary_keywords = ['SALARY', 'PAY', 'WAGES', 'PAYROLL']
            
            for bank in self.bank_transactions['bankTransactions']:
                for txn in bank['txns']:
                    if txn[3] == 1:  # Credit transaction
                        narration = str(txn[1]).upper()
                        if any(keyword in narration for keyword in salary_keywords):
                            try:
                                monthly_income = max(monthly_income, float(txn[0]))
                            except (ValueError, TypeError):
                                continue
        
        if monthly_income > 0 and total_card_balance > (monthly_income * threshold):
            utilization_ratio = total_card_balance / monthly_income
            
            return {
                "anomaly_code": "HIGH_CREDIT_UTILIZATION",
                "anomaly_title": "High Credit Card Utilization",
                "description": f"Your credit card utilization appears high at {utilization_ratio:.1%} relative to your monthly income, which can negatively impact your credit score.",
                "recommendation": "Reduce credit card balances to below 30% of your monthly income. Consider paying off cards with highest interest rates first or increasing your income.",
                "details": {
                    "total_credit_card_balance": total_card_balance,
                    "estimated_monthly_income": monthly_income,
                    "utilization_ratio": utilization_ratio,
                    "threshold": threshold,
                    "credit_cards": credit_cards,
                    "cards_count": len(credit_cards)
                }
            }
        
        return None

    # --- Composite Tool ---
    def run_full_financial_audit(self) -> Dict[str, Any]:
        """Runs all audit tools and returns a consolidated JSON report."""
        audit_findings = []
        
        # List of all audit methods
        audit_methods = [
            self.audit_net_worth_growth,
            self.audit_bad_debt_ratio,
            self.audit_asset_allocation,
            self.audit_lifestyle_creep,
            self.audit_wealth_leaking_fees,
            self.audit_regular_vs_direct_plans,
            self.audit_stock_concentration_risk,
            self.audit_inoperative_epf_accounts,
            self.audit_negative_payment_history,
            self.audit_high_credit_utilization
        ]
        
        # Run each audit method
        for audit_method in audit_methods:
            try:
                result = audit_method()
                if result:  # If the result is not None, add it to findings
                    audit_findings.append(result)
            except Exception as e:
                # Log the error from a specific check without crashing the whole report
                audit_findings.append({
                    "anomaly_code": "AUDIT_ERROR",
                    "anomaly_title": f"Error in {audit_method.__name__}",
                    "description": f"An error occurred while running {audit_method.__name__}: {str(e)}",
                    "recommendation": "Review the data quality and retry the audit.",
                    "details": {
                        "error_message": str(e),
                        "audit_method": audit_method.__name__,
                        "severity": "ERROR"
                    }
                })
        
        return {
            "audit_summary": {
                "total_anomalies_found": len(audit_findings),
                "status": "ANOMALIES_DETECTED" if audit_findings else "HEALTH_CHECK_PASSED",
                "summary_message": f"Financial Health Audit Complete: Found {len(audit_findings)} potential issue(s)." if audit_findings else "Financial Health Audit Complete: No major anomalies were detected.",
                "audit_timestamp": pd.Timestamp.now().isoformat(),
                "data_sources_checked": [
                    "net_worth_data",
                    "credit_report", 
                    "bank_transactions",
                    "mf_transactions",
                    "stock_transactions",
                    "epf_details"
                ]
            },
            "detected_anomalies": audit_findings
        }

    def get_processed_financial_health_data(self) -> Dict[str, Any]:
        """Processes and returns a structured JSON summary of all key financial health indicators."""
        # Calculate bad debt ratio
        bad_debt_ratio = 0
        bad_debt_total = 0
        total_assets = 0
        
        if self.net_worth_data:
            net_worth_response = self.net_worth_data.get("netWorthResponse", {})
            liabilities = net_worth_response.get("liabilityValues", [])
            assets = net_worth_response.get("assetValues", [])
            
            # Calculate bad debt
            for liability in liabilities:
                liability_type = liability.get("netWorthAttribute", "")
                if liability_type in ["LIABILITY_TYPE_CREDIT_CARD", "LIABILITY_TYPE_PERSONAL_LOAN"]:
                    try:
                        bad_debt_total += float(liability.get("value", {}).get("units", "0"))
                    except (ValueError, TypeError):
                        continue
            
            # Calculate total assets
            for asset in assets:
                try:
                    total_assets += float(asset.get("value", {}).get("units", "0"))
                except (ValueError, TypeError):
                    continue
            
            if total_assets > 0:
                bad_debt_ratio = bad_debt_total / total_assets

        # Calculate asset allocation ratios
        savings_and_fds_percentage = 0
        equity_and_mf_percentage = 0
        
        if self.net_worth_data and total_assets > 0:
            assets = self.net_worth_data.get("netWorthResponse", {}).get("assetValues", [])
            savings_and_fds = 0
            equity_and_mf = 0
            
            for asset in assets:
                try:
                    asset_value = float(asset.get("value", {}).get("units", "0"))
                    asset_type = asset.get("netWorthAttribute", "")
                    
                    if asset_type in ["ASSET_TYPE_SAVINGS_ACCOUNTS", "ASSET_TYPE_FIXED_DEPOSITS"]:
                        savings_and_fds += asset_value
                    elif asset_type in ["ASSET_TYPE_MUTUAL_FUND", "ASSET_TYPE_INDIAN_SECURITIES", "ASSET_TYPE_US_SECURITIES"]:
                        equity_and_mf += asset_value
                except (ValueError, TypeError):
                    continue
            
            savings_and_fds_percentage = savings_and_fds / total_assets
            equity_and_mf_percentage = equity_and_mf / total_assets

        # Extract credit score
        credit_score = None
        accounts_with_negative_history = 0
        
        if self.credit_report:
            credit_reports = self.credit_report.get("creditReports", [])
            if credit_reports:
                credit_report = credit_reports[0]['creditReportData']
                score_data = credit_report.get('score', {})
                bureau_score = score_data.get('bureauScore', '0')
                try:
                    credit_score = int(bureau_score) if bureau_score != '0' else None
                except (ValueError, TypeError):
                    pass
                
                # Count negative payment history accounts
                credit_account = credit_report.get('creditAccount', {})
                account_details = credit_account.get('creditAccountDetails', [])
                for account in account_details:
                    payment_rating = account.get('paymentRating', '0')
                    if payment_rating != '0':
                        accounts_with_negative_history += 1

        # Estimate credit utilization (simplified)
        credit_utilization_ratio = None
        if self.credit_report and self.bank_transactions:
            total_card_balance = 0
            monthly_income = 0
            
            # Calculate credit card balances
            credit_reports = self.credit_report.get("creditReports", [])
            for report in credit_reports:
                credit_data = report.get("creditReportData", {})
                credit_account = credit_data.get("creditAccount", {})
                account_details = credit_account.get("creditAccountDetails", [])
                
                for account in account_details:
                    account_type = account.get("accountType", "")
                    if account_type == "01":  # Credit card
                        try:
                            balance = float(account.get("currentBalance", "0"))
                            total_card_balance += balance
                        except (ValueError, TypeError):
                            continue
            
            # Estimate monthly income
            if self.bank_transactions.get('bankTransactions'):
                salary_keywords = ['SALARY', 'PAY', 'WAGES', 'PAYROLL']
                for bank in self.bank_transactions['bankTransactions']:
                    for txn in bank['txns']:
                        if txn[3] == 1:  # Credit transaction
                            narration = str(txn[1]).upper()
                            if any(keyword in narration for keyword in salary_keywords):
                                try:
                                    monthly_income = max(monthly_income, float(txn[0]))
                                except (ValueError, TypeError):
                                    continue
            
            if monthly_income > 0:
                credit_utilization_ratio = total_card_balance / monthly_income

        # Get net worth
        total_net_worth = 0
        if self.net_worth_data:
            net_worth_str = self.net_worth_data.get("netWorthResponse", {}).get("totalNetWorthValue", {}).get("units", "0")
            try:
                total_net_worth = float(net_worth_str)
            except (ValueError, TypeError):
                pass

        return {
            "key_health_indicators": {
                "net_worth": {
                    "total_net_worth": total_net_worth,
                    "bad_debt_to_asset_ratio": bad_debt_ratio,
                    "bad_debt_amount": bad_debt_total,
                    "total_assets_amount": total_assets
                },
                "asset_allocation": {
                    "savings_and_fds_percentage": savings_and_fds_percentage,
                    "equity_and_mf_percentage": equity_and_mf_percentage,
                    "cash_heavy_allocation": savings_and_fds_percentage > 0.4
                },
                "credit_profile": {
                    "credit_score": credit_score,
                    "accounts_with_negative_history": accounts_with_negative_history,
                    "credit_utilization_ratio": credit_utilization_ratio,
                    "credit_health_status": "GOOD" if credit_score and credit_score >= 750 else "NEEDS_IMPROVEMENT" if credit_score else "UNKNOWN"
                }
            },
            "data_completeness_check": {
                "net_worth_data_available": self.net_worth_data is not None,
                "credit_report_available": self.credit_report is not None,
                "bank_transactions_available": self.bank_transactions is not None,
                "mf_transactions_available": self.mf_transactions is not None,
                "stock_transactions_available": self.stock_transactions is not None,
                "epf_details_available": self.epf_details is not None
            },
            "calculated_metrics": {
                "risk_indicators": {
                    "high_bad_debt_ratio": bad_debt_ratio > 0.15,
                    "over_saving": savings_and_fds_percentage > 0.4,
                    "negative_net_worth": total_net_worth < 0,
                    "poor_credit_history": accounts_with_negative_history > 0
                }
            }
        }


def create_financial_health_auditor_adk_agent(dal: FIMCPDataAccess, model: str) -> Agent:
    """Factory function to create the Financial Health Auditor ADK Agent."""
    auditor_instance = FinancialHealthAuditorAgent(dal)
    tools = [
        auditor_instance.run_full_financial_audit,
        auditor_instance.get_processed_financial_health_data
    ]
    return Agent(
        name="Financial_Health_Auditor_Agent",
        model=model,
        description="Performs a deep, expert-level audit of the user's finances to find strategic anomalies related to net worth, debt, investments, and credit. Use when the user asks for a 'financial health checkup', 'audit', or 'review'.",
        tools=tools,
    )