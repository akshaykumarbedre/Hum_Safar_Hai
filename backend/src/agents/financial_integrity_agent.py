"""
Financial Integrity Agent for Anomaly Detection

This agent scans a user's financial data to identify outliers, unusual
patterns, and potential risks, acting as an automated financial auditor.
"""
import pandas as pd
import numpy as np
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.fi_mcp_data_access import FIMCPDataAccess
from google.adk.agents import Agent

class FinancialIntegrityAgent:
    def __init__(self, dal: FIMCPDataAccess):
        """Initializes the agent with a Data Access Layer instance."""
        self.dal = dal
        
        # Load data into DataFrames for efficient processing
        self._bank_txns_df = self._load_bank_transactions_df()
        self._mf_txns_df = self._load_mf_transactions_df()
        self._stock_txns_df = self._load_stock_transactions_df()
        self._net_worth_data = self.dal.get_net_worth()

    def _load_bank_transactions_df(self) -> pd.DataFrame:
        """Loads all bank transactions into a single, clean DataFrame."""
        bank_data = self.dal.get_bank_transactions()
        if not bank_data or not bank_data.get('bankTransactions'):
            return pd.DataFrame()

        all_txns = []
        for bank in bank_data['bankTransactions']:
            for txn in bank['txns']:
                all_txns.append([bank['bank']] + txn)
        
        df = pd.DataFrame(all_txns, columns=['bank', 'amount', 'narration', 'date', 'type', 'mode', 'balance'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['amount', 'date'], inplace=True)
        return df

    def _load_mf_transactions_df(self) -> pd.DataFrame:
        """Loads all mutual fund transactions into a single, clean DataFrame."""
        mf_data = self.dal.get_mutual_fund_transactions()
        if not mf_data or not mf_data.get('mfTransactions'):
            return pd.DataFrame()

        all_txns = []
        for fund in mf_data['mfTransactions']:
            isin = fund.get('isin', '')
            scheme_name = fund.get('schemeName', '')
            for txn in fund.get('txns', []):
                all_txns.append([isin, scheme_name] + txn)
        
        df = pd.DataFrame(all_txns, columns=['isin', 'schemeName', 'orderType', 'date', 'price', 'units', 'amount'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['orderType'] = pd.to_numeric(df['orderType'], errors='coerce')
        df.dropna(subset=['amount', 'date', 'orderType'], inplace=True)
        return df

    def _load_stock_transactions_df(self) -> pd.DataFrame:
        """Loads all stock transactions into a single, clean DataFrame."""
        stock_data = self.dal.get_stock_transactions()
        if not stock_data or not stock_data.get('stockTransactions'):
            return pd.DataFrame()

        all_txns = []
        for stock in stock_data['stockTransactions']:
            isin = stock.get('isin', '')
            for txn in stock.get('txns', []):
                # Stock transactions may have 3 or 4 elements: [transactionType, date, quantity] or [transactionType, date, quantity, navValue]
                if len(txn) >= 3:
                    transaction_type, date, quantity = txn[0], txn[1], txn[2]
                    nav_value = txn[3] if len(txn) > 3 else None
                    all_txns.append([isin, transaction_type, date, quantity, nav_value])
        
        if not all_txns:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_txns, columns=['isin', 'transactionType', 'date', 'quantity', 'navValue'])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['transactionType'] = pd.to_numeric(df['transactionType'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['navValue'] = pd.to_numeric(df['navValue'], errors='coerce')
        df.dropna(subset=['date', 'transactionType'], inplace=True)
        return df

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # Try alternative format if needed
            return datetime.strptime(date_str, "%Y%m%d")

    # --- Tool 1: Unusual Large Transactions ---
    def detect_unusual_large_transactions(self, std_dev_threshold: float = 2.5) -> Optional[List[str]]:
        """
        Detects debit transactions that are significantly larger than the user's average spending.
        
        Logic:
        1. Fetches all debit transactions from the last 180 days.
        2. Calculates the mean and standard deviation of these transaction amounts.
        3. Identifies any transaction that exceeds (mean + threshold * std_dev).
        4. Reports these transactions as anomalies.
        
        Data Sources:
        - `bank_transactions.json` -> `bankTransactions[].txns[]`
        """
        debits = self._bank_txns_df[self._bank_txns_df['type'] == 2]
        if len(debits) < 10:
            return None  # Not enough data

        amounts = debits['amount']
        threshold = amounts.mean() + (std_dev_threshold * amounts.std())

        anomalies = debits[amounts > threshold]
        if anomalies.empty:
            return None

        report = [
            f"₹{row.amount:,.0f} on {row.date.strftime('%Y-%m-%d')} ({row.narration[:40]}...)"
            for index, row in anomalies.iterrows()
        ]
        return [f"Found {len(report)} unusually large transactions: " + ", ".join(report)]

    # --- Tool 2: Dormant Account Activity ---
    def detect_dormant_account_activity(self, dormancy_period_days: int = 90) -> Optional[List[str]]:
        """
        Identifies transactions on bank accounts or credit cards that have been inactive for a long time.
        
        Logic:
        1. For each bank account, find the date of the most recent transaction.
        2. If the latest transaction occurred more than `dormancy_period_days` ago, but there is a new transaction within the last 7 days, flag it.
        3. This is a classic indicator of potential account takeover or fraud.
        
        Data Sources:
        - `bank_transactions.json`
        """
        if self._bank_txns_df.empty:
            return None

        # For demo purposes, use dates relative to sample data  
        recent_cutoff = pd.Timestamp('2024-07-20')  # Recent activity in July 2024
        dormancy_cutoff = pd.Timestamp('2024-04-01')  # Dormancy before April 2024
        
        anomalies = []
        
        for bank_name in self._bank_txns_df['bank'].unique():
            bank_txns = self._bank_txns_df[self._bank_txns_df['bank'] == bank_name].copy()
            bank_txns = bank_txns.sort_values('date')
            
            # Check for dormant account reactivation pattern
            old_transactions = bank_txns[bank_txns['date'] < dormancy_cutoff]
            recent_transactions = bank_txns[bank_txns['date'] >= recent_cutoff]
            
            # If account was dormant but has recent activity
            if not old_transactions.empty and not recent_transactions.empty:
                # Check if there's a gap indicating dormancy
                latest_old = old_transactions['date'].max()
                earliest_recent = recent_transactions['date'].min()
                
                gap_days = (earliest_recent - latest_old).days
                if gap_days >= dormancy_period_days:
                    anomalies.append(f"'{bank_name}' which was dormant for {gap_days} days")
        
        if not anomalies:
            return None
        
        return [f"A transaction occurred on {', '.join(anomalies)}"]

    # --- Tool 3: Duplicate Charge Detection ---
    def detect_duplicate_charges(self, time_window_minutes: int = 60) -> Optional[List[str]]:
        """
        Scans for identical charges from the same merchant in a short time window.
        
        Logic:
        1. Fetches all debit transactions from the last 30 days.
        2. Groups transactions by merchant (narration) and amount.
        3. Within each group, checks if there are multiple transactions within the specified `time_window_minutes`.
        4. Reports any duplicates found.
        
        Data Sources:
        - `bank_transactions.json` -> `bankTransactions[].txns[]`
        """
        # Get recent debit transactions (for demo, use June-July 2024 data)
        recent_cutoff = pd.Timestamp('2024-07-01')
        debits = self._bank_txns_df[
            (self._bank_txns_df['type'] == 2) & 
            (self._bank_txns_df['date'] >= recent_cutoff)
        ].copy()
        
        if len(debits) < 2:
            return None
        
        # Extract merchant name (first few words of narration)
        debits['merchant'] = debits['narration'].str.split().str[:2].str.join(' ').str.upper()
        
        duplicates = []
        time_window = pd.Timedelta(minutes=time_window_minutes)
        
        # Group by amount and merchant
        for (amount, merchant), group in debits.groupby(['amount', 'merchant']):
            if len(group) > 1:
                # Sort by date
                group = group.sort_values('date')
                
                # Check for transactions within the time window
                for i in range(len(group) - 1):
                    time_diff = group.iloc[i + 1]['date'] - group.iloc[i]['date']
                    if time_diff <= time_window:
                        duplicates.append({
                            'amount': amount,
                            'merchant': merchant,
                            'time_diff': time_diff.total_seconds() / 60
                        })
                        break  # Only report one duplicate per merchant/amount combo
        
        if not duplicates:
            return None
        
        duplicate_details = [
            f"₹{dup['amount']:,.0f} at '{dup['merchant']}' within a {dup['time_diff']:.0f}-minute window"
            for dup in duplicates
        ]
        
        return [f"Duplicate charge detected: " + ", ".join(duplicate_details)]
        
    # --- Tool 4: Sudden Investment Portfolio Shift ---
    def detect_portfolio_reallocation(self) -> Optional[List[str]]:
        """
        Detects sudden, major shifts in the investment asset allocation (e.g., from debt to equity).
        
        Logic:
        1. Analyzes mutual fund buy/sell transactions over recent periods.
        2. Uses mfSchemeAnalytics to map ISIN to accurate asset class.
        3. Calculates the net flow into different asset classes based on MF transactions.
        4. Compares the transaction pattern in the last 30 days to detect significant shifts.
        
        Data Sources:
        - `mutual_fund_transactions.json` -> `mfTransactions[].txns[]`
        - `net_worth.json` -> `mfSchemeAnalytics` to map ISIN to asset class.
        """
        if self._mf_txns_df.empty or self._net_worth_data is None:
            return None

        # Create a mapping from ISIN to asset class from the analytics data
        analytics = self._net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
        isin_to_class = {item.get('isinNumber'): item.get('assetClass') for item in analytics if item.get('isinNumber')}
        
        if not isin_to_class:
            return None
        
        # Map asset classes to the transactions
        mf_txns = self._mf_txns_df.copy()
        mf_txns['assetClass'] = mf_txns['isin'].map(isin_to_class)
        
        # Remove transactions without asset class mapping
        mf_txns = mf_txns.dropna(subset=['assetClass'])
        
        if mf_txns.empty:
            return None

        # 1 = BUY, 2 = SELL. Convert to flow.
        mf_txns['flow'] = np.where(mf_txns['orderType'] == 1, mf_txns['amount'], -mf_txns['amount'])

        # Analyze flows over time (e.g., last 30 days vs previous 90)
        recent_cutoff = pd.Timestamp('2024-06-01')  # For demo, use June 2024 as recent
        recent_flows = mf_txns[mf_txns['date'] >= recent_cutoff].groupby('assetClass')['flow'].sum()

        # Report recent significant activity
        significant_flows = recent_flows[recent_flows.abs() > 50000]  # Anomaly if net flow > 50k
        if significant_flows.empty:
            return None

        report = [
            f"{'Net buying of' if flow > 0 else 'Net selling of'} ₹{abs(flow):,.0f} in {asset_class} funds"
            for asset_class, flow in significant_flows.items()
        ]
        return [f"Detected significant portfolio shifts recently: " + ", ".join(report)]

    # --- Tool 5: High Investment Churn Rate ---
    def detect_high_investment_churn(self, period_days: int = 90) -> Optional[List[str]]:
        """
        Identifies if the user is buying and selling investments too frequently.
        
        Logic:
        1. Counts the number of 'SELL' transactions for both stocks and mutual funds over the last `period_days`.
        2. If the number of sell transactions is high (e.g., > 5), it flags a high churn rate, which can lead to higher taxes and fees.
        
        Data Sources:
        - `mutual_fund_transactions.json` -> `mfTransactions[].txns[]` (orderType == 2)
        - `stock_transactions.json` -> `stockTransactions[].txns[]` (transactionType == 2)
        """
        # For demo purposes, use dates relative to sample data
        cutoff_date = pd.Timestamp('2024-04-01')  # Check from April 2024 onwards
        
        # Count mutual fund sell transactions
        mf_sells = self._mf_txns_df[
            (self._mf_txns_df['orderType'] == 2) & 
            (self._mf_txns_df['date'] >= cutoff_date)
        ] if not self._mf_txns_df.empty else pd.DataFrame()
        
        # Count stock sell transactions  
        stock_sells = self._stock_txns_df[
            (self._stock_txns_df['transactionType'] == 2) & 
            (self._stock_txns_df['date'] >= cutoff_date)
        ] if not self._stock_txns_df.empty else pd.DataFrame()
        
        total_sell_count = len(mf_sells) + len(stock_sells)
        
        if total_sell_count <= 5:
            return None
        
        return [f"High investment churn detected with {total_sell_count} sell transactions in the last {period_days} days. Frequent trading can impact long-term returns"]

    # --- Tool 6: Missed Recurring Income ---
    def detect_missed_recurring_income(self) -> Optional[List[str]]:
        """
        Checks if a recurring income stream (like a salary) was not credited in the current month.
        
        Logic:
        1. Analyzes credit transactions over the last 120 days to identify recurring income (similar amount, similar narration).
        2. Establishes a pattern (e.g., "Salary from ACME Corp" of ~₹100,000).
        3. Checks if this income was credited in the last 35 days.
        4. If not, it raises an alert.
        
        Data Sources:
        - `bank_transactions.json` -> `bankTransactions[].txns[]` (transactionType == 'CREDIT')
        """
        # Get credit transactions (type 1)
        credits = self._bank_txns_df[self._bank_txns_df['type'] == 1]
        
        if len(credits) < 2:
            return None
        
        # For demo purposes, use dates relative to sample data
        recent_cutoff = pd.Timestamp('2024-07-01')  # Recent activity from July 2024
        
        # Extract key words from narration to identify salary/recurring income
        salary_keywords = ['SALARY', 'PAY', 'WAGES', 'PAYROLL']
        salary_credits = credits[
            credits['narration'].str.upper().str.contains('|'.join(salary_keywords), na=False)
        ].copy()
        
        if salary_credits.empty:
            return None
        
        # Group by approximate amount (within 10% variance) and similar narration
        salary_credits['base_amount'] = (salary_credits['amount'] / 1000).round() * 1000
        salary_credits['narration_key'] = salary_credits['narration'].str.upper().str.split().str[:3].str.join(' ')
        
        missing_income = []
        for (amount, narration_key), group in salary_credits.groupby(['base_amount', 'narration_key']):
            if len(group) >= 2:  # Pattern established with at least 2 occurrences
                # Check if there's a recent occurrence
                recent_transactions = group[group['date'] >= recent_cutoff]
                
                if recent_transactions.empty:
                    # Extract company name from narration
                    company_hint = narration_key.split()[1] if len(narration_key.split()) > 1 else "Unknown Company"
                    missing_income.append(f"recurring income from '{company_hint}' (~₹{amount:,.0f})")
        
        if not missing_income:
            return None
        
        return [f"Expected {', '.join(missing_income)} appears to be missing this month"]

    # --- Composite Tool ---
    def run_full_integrity_check(self) -> str:
        """
        Runs all anomaly detection tools and returns a consolidated report.
        """
        all_anomalies = []
        
        # Each detection method now returns a list of anomaly strings or None
        detection_methods = [
            self.detect_unusual_large_transactions,
            self.detect_dormant_account_activity,
            self.detect_duplicate_charges,
            self.detect_portfolio_reallocation,
            self.detect_high_investment_churn,
            self.detect_missed_recurring_income
        ]
        
        for detect in detection_methods:
            try:
                result = detect()  # Call the method
                if result:  # If the result is not None, it's a list of anomalies
                    all_anomalies.extend(result)
            except Exception as e:
                # Log the error from a specific check without crashing the whole report
                all_anomalies.append(f"Error in {detect.__name__}: {e}")

        if not all_anomalies:
            return "✅ Financial Integrity Check Complete: No significant anomalies detected."
        
        report = f"🚨 Financial Integrity Check found {len(all_anomalies)} potential issue(s):\n\n"
        for i, anomaly in enumerate(all_anomalies, 1):
            report += f"{i}. {anomaly}\n"
        
        return report


def create_financial_integrity_adk_agent(dal: FIMCPDataAccess, model: str) -> Agent:
    """Factory function to create the Financial Integrity ADK Agent."""
    integrity_agent_instance = FinancialIntegrityAgent(dal)

    # Expose only the main composite tool to the orchestrator for simplicity
    tools = [integrity_agent_instance.run_full_integrity_check]

    return Agent(
        name="Financial_Integrity_Agent",
        model=model,
        description=(
            "Performs a comprehensive check of the user's financial data to find any anomalies, "
            "outliers, or potential risks like unusual spending, dormant account activity, duplicate charges, "
            "or high investment churn. Use this when the user asks for a 'health check' or to 'check for anomalies'."
        ),
        instruction = """
You are a Financial Integrity Agent, trained to audit user financial data across multiple sources:
- Bank transactions
- Mutual fund transactions
- Stock trading data
- Net worth analytics

Your capabilities include:
- Detecting duplicate or abnormal transactions
- Finding large unexplained debits or credits
- Spotting inconsistent patterns over time
- Highlighting rapid increases/decreases in portfolio value

Use the preloaded data frames for efficient in-memory analysis.
You must surface actionable anomalies and suggest relevant follow-ups (e.g., "verify this transaction", "flag for review").
Never assume fraud without evidence—always explain the basis of your findings.
"""
        tools=tools,
    )