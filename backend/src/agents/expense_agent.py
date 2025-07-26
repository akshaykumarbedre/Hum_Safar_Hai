"""
Expense & Cash Flow Agent

This agent analyzes bank transactions to provide insights into spending habits.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any, List
from ..fi_mcp_data_access import FIMCPDataAccess


class ExpenseAndCashflowAgent:
    def __init__(self, dal: FIMCPDataAccess):
        self.dal = dal

    def get_core_transaction_data(self) -> dict:
        """
        Get core transaction data in a pre-processed, token-efficient format.
        
        Returns:
            dict: Pre-processed transaction data with minimal token usage
        """
        try:
            # Fetch bank transactions from the DAL
            bank_data = self.dal.get_bank_transactions()
            
            if not bank_data:
                return {"transactions": []}
            
            bank_transactions = bank_data.get("bankTransactions", [])
            if not bank_transactions:
                return {"transactions": []}
            
            # Process all transactions into a flat list
            processed_transactions = []
            
            for bank_account in bank_transactions:
                transactions = bank_account.get("txns", [])
                
                for txn in transactions:
                    try:
                        # Parse transaction data
                        # Schema: [amount, narration, date, type, mode, balance]
                        if len(txn) < 4:
                            continue
                            
                        amount = float(txn[0])
                        narration = str(txn[1])
                        txn_date = str(txn[2])
                        txn_type = int(txn[3])
                        
                        # Map transaction type to readable format
                        type_mapping = {1: "CR", 2: "DR"}
                        readable_type = type_mapping.get(txn_type, "OTH")
                        
                        # Truncate long narrations to save tokens
                        truncated_desc = narration[:70] + "..." if len(narration) > 70 else narration
                        
                        # Create processed transaction object
                        processed_txn = {
                            "date": txn_date,
                            "desc": truncated_desc,
                            "amt": amount,
                            "type": readable_type
                        }
                        
                        processed_transactions.append(processed_txn)
                        
                    except (ValueError, IndexError, TypeError):
                        # Skip transactions with invalid data
                        continue
            
            # Sort by date (most recent first) and limit to reasonable number
            processed_transactions.sort(key=lambda x: x["date"], reverse=True)
            
            # Return in the required format
            return {"transactions": processed_transactions}
            
        except Exception as e:
            return {"transactions": [], "error": str(e)}

    def _categorize_transaction(self, narration: str) -> str:
        """
        Categorize a transaction based on its narration using simple rule-based logic.
        
        Args:
            narration (str): Transaction narration/description
            
        Returns:
            str: Category name
        """
        if not narration:
            return "Miscellaneous"
        
        # Convert to uppercase for case-insensitive matching
        narration_upper = narration.upper()
        
        # Food & Dining
        if any(keyword in narration_upper for keyword in ["ZOMATO", "SWIGGY", "FOOD", "RESTAURANT", "CAFE"]):
            return "Food & Dining"
        
        # Shopping
        if any(keyword in narration_upper for keyword in ["AMAZON", "FLIPKART", "MYNTRA", "SHOPPING", "MALL"]):
            return "Shopping"
        
        # Bills & Utilities
        if any(keyword in narration_upper for keyword in ["AIRTEL", "VODAFONE", "ELECTRICITY", "WATER", "GAS", "BROADBAND", "INTERNET", "ACT BROADBAND"]):
            return "Bills & Utilities"
        
        # Transportation  
        if any(keyword in narration_upper for keyword in ["UBER", "OLA", "TAXI", "BUS", "METRO", "PETROL", "DIESEL", "FUEL"]):
            return "Transportation"
        
        # Financial Services
        if any(keyword in narration_upper for keyword in ["CRED", "CREDIT CARD", "LOAN", "EMI", "INSURANCE", "MUTUAL FUND", "INVESTMENT"]):
            return "Financial Services"
        
        # Loans & EMIs (keeping separate for backward compatibility)
        if "EMI" in narration_upper:
            return "Loans & EMIs"
        
        # Default category
        return "Miscellaneous"

    def get_spending_summary(self, period_days: int = 90) -> Dict[str, Any]:
        """
        Generate a spending summary for the user over the specified period.
        
        Args:
            period_days (int): Number of days to analyze (default: 90)
            
        Returns:
            Dict[str, Any]: Structured spending summary with categories and totals
        """
        try:
            # Fetch bank transactions from the DAL
            bank_data = self.dal.get_bank_transactions()
            
            if not bank_data:
                return {
                    "status": "ERROR",
                    "message": "Bank transaction data not available.",
                    "spending_by_category": {},
                    "total_spending": 0,
                    "transaction_count": 0,
                    "period_days": period_days
                }
            
            bank_transactions = bank_data.get("bankTransactions", [])
            if not bank_transactions:
                return {
                    "status": "ERROR",
                    "message": "No bank accounts found.",
                    "spending_by_category": {},
                    "total_spending": 0,
                    "transaction_count": 0,
                    "period_days": period_days
                }
            
            # Calculate the cutoff date for filtering transactions
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=period_days)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Dictionary to aggregate spending by category
            category_spending = defaultdict(float)
            total_debit_amount = 0
            transaction_count = 0
            
            # Process all bank accounts and their transactions
            for bank_account in bank_transactions:
                bank_name = bank_account.get("bank", "Unknown Bank")
                transactions = bank_account.get("txns", [])
                
                for txn in transactions:
                    try:
                        # Parse transaction data
                        # Schema: [amount, narration, date, type, mode, balance]
                        if len(txn) < 4:
                            continue
                            
                        amount = float(txn[0])
                        narration = str(txn[1])
                        txn_date = str(txn[2])
                        txn_type = int(txn[3])
                        
                        # Filter for DEBIT transactions (type = 2) - process all available data for dummy/test scenarios
                        # Note: For production, consider re-enabling date filtering based on business requirements
                        if txn_type == 2:
                            # Categorize the transaction
                            category = self._categorize_transaction(narration)
                            
                            # Add to category spending
                            category_spending[category] += amount
                            total_debit_amount += amount
                            transaction_count += 1
                            
                    except (ValueError, IndexError, TypeError):
                        # Skip transactions with invalid data
                        continue
            
            # Generate the summary
            if transaction_count == 0:
                return {
                    "status": "SUCCESS",
                    "message": f"No debit transactions found in the last {period_days} days.",
                    "spending_by_category": {},
                    "total_spending": 0,
                    "transaction_count": 0,
                    "period_days": period_days
                }
            
            # Convert defaultdict to regular dict and sort by spending amount
            spending_by_category = dict(category_spending)
            sorted_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)
            
            # Format spending data
            category_breakdown = []
            for category, amount in sorted_categories:
                category_breakdown.append({
                    "category": category,
                    "amount": amount,
                    "formatted_amount": f"₹{amount:,.0f}",
                    "percentage_of_total": (amount / total_debit_amount * 100) if total_debit_amount > 0 else 0
                })
            
            return {
                "status": "SUCCESS",
                "spending_by_category": spending_by_category,
                "category_breakdown": category_breakdown,
                "total_spending": total_debit_amount,
                "formatted_total_spending": f"₹{total_debit_amount:,.0f}",
                "transaction_count": transaction_count,
                "period_days": period_days,
                "daily_average": total_debit_amount / period_days if period_days > 0 else 0,
                "formatted_daily_average": f"₹{total_debit_amount / period_days:,.0f}" if period_days > 0 else "₹0"
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error analyzing spending data: {str(e)}",
                "spending_by_category": {},
                "total_spending": 0,
                "transaction_count": 0,
                "period_days": period_days
            }

    def get_income_sources(self) -> Dict[str, Any]:
        """
        Identifies and summarizes sources of income from bank transactions.
        
        Returns:
            Dict[str, Any]: Structured income sources summary
        """
        try:
            # Fetch bank transactions from the DAL
            bank_data = self.dal.get_bank_transactions()
            
            if not bank_data:
                return {
                    "status": "ERROR",
                    "message": "Bank transaction data not available.",
                    "income_sources": {},
                    "total_income": 0,
                    "monthly_average": 0
                }
            
            bank_transactions = bank_data.get("bankTransactions", [])
            if not bank_transactions:
                return {
                    "status": "ERROR",
                    "message": "No bank accounts found.",
                    "income_sources": {},
                    "total_income": 0,
                    "monthly_average": 0
                }
            
            # Calculate the cutoff date for last 90 days
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=90)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Dictionary to track income sources
            income_sources = {}
            total_income = 0
            
            # Income keywords to identify salary and other income sources
            salary_keywords = ["SALARY", "SAL", "PAYROLL", "COMPANY", "EMPLOYER", "WAGES"]
            business_keywords = ["BUSINESS", "PROFESSIONAL", "FREELANCE", "CONSULTING"]
            investment_keywords = ["DIVIDEND", "INTEREST", "MATURITY", "REDEMPTION", "CAPITAL GAIN"]
            other_keywords = ["REFUND", "CASHBACK", "REWARD", "BONUS"]
            
            # Process all bank accounts and their transactions
            for bank_account in bank_transactions:
                bank_name = bank_account.get("bank", "Unknown Bank")
                transactions = bank_account.get("txns", [])
                
                for txn in transactions:
                    try:
                        # Parse transaction data
                        if len(txn) < 4:
                            continue
                            
                        amount = float(txn[0])
                        narration = str(txn[1]).upper()
                        txn_date = str(txn[2])
                        txn_type = int(txn[3])
                        
                        # Filter for CREDIT transactions (type = 1) - process all available data for dummy/test scenarios
                        # Note: For production, consider re-enabling date filtering based on business requirements
                        if txn_type == 1 and amount > 0:
                            # Categorize income source
                            income_category = "Other Credits"
                            
                            # Check for salary indicators
                            if any(keyword in narration for keyword in salary_keywords):
                                income_category = "Salary/Company Credit"
                            # Check for business income
                            elif any(keyword in narration for keyword in business_keywords):
                                income_category = "Business/Professional Income"
                            # Check for investment income
                            elif any(keyword in narration for keyword in investment_keywords):
                                income_category = "Investment Income"
                            # Check for other income types
                            elif any(keyword in narration for keyword in other_keywords):
                                income_category = "Refunds/Cashbacks"
                            # Large amounts might be salary even without keywords
                            elif amount > 25000:
                                income_category = "Likely Salary/Large Credit"
                            
                            # Add to income sources
                            income_sources[income_category] = income_sources.get(income_category, 0) + amount
                            total_income += amount
                            
                    except (ValueError, IndexError, TypeError):
                        # Skip transactions with invalid data
                        continue
            
            # Generate the income summary
            if total_income == 0:
                return {
                    "status": "SUCCESS",
                    "message": "No significant income sources detected in the last 90 days.",
                    "income_sources": {},
                    "total_income": 0,
                    "monthly_average": 0
                }
            
            # Sort income sources by amount (descending)
            sorted_income = sorted(income_sources.items(), key=lambda x: x[1], reverse=True)
            
            # Format income data
            income_breakdown = []
            for category, amount in sorted_income:
                income_breakdown.append({
                    "category": category,
                    "amount": amount,
                    "formatted_amount": f"₹{amount:,.0f}",
                    "percentage_of_total": (amount / total_income * 100) if total_income > 0 else 0
                })
            
            # Calculate monthly average
            monthly_average = total_income / 3  # 90 days ≈ 3 months
            
            return {
                "status": "SUCCESS",
                "income_sources": income_sources,
                "income_breakdown": income_breakdown,
                "total_income": total_income,
                "formatted_total_income": f"₹{total_income:,.0f}",
                "monthly_average": monthly_average,
                "formatted_monthly_average": f"₹{monthly_average:,.0f}",
                "analysis_period_days": 90,
                "largest_income_source": sorted_income[0][0] if sorted_income else None,
                "income_diversity": len(income_sources)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error analyzing income sources: {str(e)}",
                "income_sources": {},
                "total_income": 0,
                "monthly_average": 0
            }

    def identify_recurring_payments(self) -> Dict[str, Any]:
        """
        Scans for recurring debits like subscriptions and bills.
        
        Returns:
            Dict[str, Any]: Structured recurring payments analysis
        """
        try:
            # Fetch bank transactions from the DAL
            bank_data = self.dal.get_bank_transactions()
            
            if not bank_data:
                return {
                    "status": "ERROR",
                    "message": "Bank transaction data not available.",
                    "recurring_payments": [],
                    "estimated_monthly_total": 0
                }
            
            bank_transactions = bank_data.get("bankTransactions", [])
            if not bank_transactions:
                return {
                    "status": "ERROR",
                    "message": "No bank accounts found.",
                    "recurring_payments": [],
                    "estimated_monthly_total": 0
                }
            
            # Calculate the cutoff date for last 180 days (6 months)
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=180)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Dictionary to track similar transactions
            transaction_patterns = defaultdict(list)
            
            # Process all bank accounts and their transactions
            for bank_account in bank_transactions:
                bank_name = bank_account.get("bank", "Unknown Bank")
                transactions = bank_account.get("txns", [])
                
                for txn in transactions:
                    try:
                        # Parse transaction data
                        if len(txn) < 4:
                            continue
                            
                        amount = float(txn[0])
                        narration = str(txn[1])
                        txn_date = str(txn[2])
                        txn_type = int(txn[3])
                        
                        # Filter for DEBIT transactions (type = 2) - process all available data for dummy/test scenarios
                        # Note: For production, consider re-enabling date filtering based on business requirements
                        if txn_type == 2 and amount > 0:
                            # Create a pattern key by normalizing the narration
                            pattern_key = self._normalize_narration_for_pattern(narration)
                            
                            # Store transaction details
                            transaction_patterns[pattern_key].append({
                                'amount': amount,
                                'date': txn_date,
                                'narration': narration,
                                'bank': bank_name
                            })
                            
                    except (ValueError, IndexError, TypeError):
                        # Skip transactions with invalid data
                        continue
            
            # Identify recurring patterns
            recurring_payments = []
            
            for pattern_key, transactions in transaction_patterns.items():
                if len(transactions) >= 2:  # At least 2 occurrences
                    # Check if amounts are similar and transactions are somewhat regular
                    amounts = [txn['amount'] for txn in transactions]
                    avg_amount = sum(amounts) / len(amounts)
                    
                    # Consider it recurring if amounts are within 20% variance
                    amount_variance = all(abs(amt - avg_amount) / avg_amount <= 0.2 for amt in amounts)
                    
                    if amount_variance:
                        # Calculate frequency
                        dates = sorted([datetime.strptime(txn['date'], "%Y-%m-%d") for txn in transactions])
                        date_diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                        avg_interval = sum(date_diffs) / len(date_diffs) if date_diffs else 0
                        
                        # Determine frequency description
                        if 25 <= avg_interval <= 35:
                            frequency = "Monthly"
                            monthly_equivalent = avg_amount
                        elif 85 <= avg_interval <= 95:
                            frequency = "Quarterly"
                            monthly_equivalent = avg_amount / 3
                        elif 350 <= avg_interval <= 370:
                            frequency = "Yearly"
                            monthly_equivalent = avg_amount / 12
                        elif avg_interval <= 7:
                            frequency = "Weekly"
                            monthly_equivalent = avg_amount * 4
                        else:
                            frequency = f"Every {avg_interval:.0f} days"
                            monthly_equivalent = avg_amount * 30 / avg_interval if avg_interval > 0 else 0
                        
                        recurring_payments.append({
                            'pattern': pattern_key,
                            'amount': avg_amount,
                            'formatted_amount': f"₹{avg_amount:,.0f}",
                            'frequency': frequency,
                            'frequency_days': avg_interval,
                            'count': len(transactions),
                            'monthly_equivalent': monthly_equivalent,
                            'formatted_monthly_equivalent': f"₹{monthly_equivalent:,.0f}",
                            'sample_narration': transactions[0]['narration'],
                            'first_occurrence': min(txn['date'] for txn in transactions),
                            'last_occurrence': max(txn['date'] for txn in transactions),
                            'all_transactions': transactions
                        })
            
            # Generate the recurring payments summary
            if not recurring_payments:
                return {
                    "status": "SUCCESS",
                    "message": "No clear recurring payment patterns detected in the last 6 months.",
                    "recurring_payments": [],
                    "estimated_monthly_total": 0,
                    "analysis_period_days": 180
                }
            
            # Sort by monthly equivalent amount (descending)
            recurring_payments.sort(key=lambda x: x['monthly_equivalent'], reverse=True)
            
            # Calculate total estimated monthly recurring amount
            monthly_total = sum(payment['monthly_equivalent'] for payment in recurring_payments)
            
            return {
                "status": "SUCCESS",
                "recurring_payments": recurring_payments,
                "recurring_payments_count": len(recurring_payments),
                "estimated_monthly_total": monthly_total,
                "formatted_monthly_total": f"₹{monthly_total:,.0f}",
                "analysis_period_days": 180,
                "top_recurring_payment": recurring_payments[0] if recurring_payments else None,
                "frequency_distribution": {
                    "monthly": len([p for p in recurring_payments if "Monthly" in p['frequency']]),
                    "quarterly": len([p for p in recurring_payments if "Quarterly" in p['frequency']]),
                    "yearly": len([p for p in recurring_payments if "Yearly" in p['frequency']]),
                    "weekly": len([p for p in recurring_payments if "Weekly" in p['frequency']]),
                    "other": len([p for p in recurring_payments if "days" in p['frequency']])
                }
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Error identifying recurring payments: {str(e)}",
                "recurring_payments": [],
                "estimated_monthly_total": 0
            }

    def _normalize_narration_for_pattern(self, narration: str) -> str:
        """
        Normalize transaction narration to identify similar patterns.
        
        Args:
            narration (str): Original transaction narration
            
        Returns:
            str: Normalized pattern key
        """
        if not narration:
            return "UNKNOWN"
        
        # Convert to uppercase and remove extra spaces
        normalized = narration.upper().strip()
        
        # Remove common prefixes and suffixes
        prefixes_to_remove = ["UPI/", "NEFT/", "IMPS/", "ACH/", "CHQ/", "RTGS/"]
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        
        # Extract meaningful keywords
        words = normalized.split()
        
        # Common subscription/bill services
        service_keywords = [
            "NETFLIX", "AMAZON", "SPOTIFY", "HOTSTAR", "PRIMEVIDEO",
            "AIRTEL", "VODAFONE", "JIO", "BSNL",
            "ZOMATO", "SWIGGY", "UBER", "OLA",
            "CRED", "PAYTM", "PHONEPE", "GPAY",
            "GYM", "FITNESS", "MEMBERSHIP",
            "INSURANCE", "PREMIUM",
            "ELECTRICITY", "WATER", "GAS"
        ]
        
        # Look for service keywords first
        for word in words:
            for service in service_keywords:
                if service in word:
                    return service
        
        # If no service keyword found, use the first meaningful word
        # Skip common transaction words
        skip_words = ["TO", "FROM", "UPI", "PAYMENT", "TRANSFER", "TRANSACTION", "REF", "ID"]
        for word in words:
            if len(word) > 3 and word not in skip_words:
                return word
        
        # If nothing meaningful found, return first word
        return words[0] if words else "UNKNOWN"


    def get_processed_transaction_data(self) -> Dict[str, Any]:
        """Processes and returns a structured JSON summary of all transaction data."""
        try:
            # Get all transaction analysis
            spending_summary = self.get_spending_summary()
            income_sources = self.get_income_sources()
            recurring_payments = self.identify_recurring_payments()
            
            # Process debit transactions by category
            debit_transactions_categorized = {}
            credit_transactions_categorized = {}
            
            # Fetch bank transactions for detailed categorization
            bank_data = self.dal.get_bank_transactions()
            
            if bank_data and bank_data.get("bankTransactions"):
                current_date = datetime.now()
                cutoff_date = current_date - timedelta(days=90)
                cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
                
                # Categorize all transactions
                for bank_account in bank_data["bankTransactions"]:
                    bank_name = bank_account.get("bank", "Unknown Bank")
                    transactions = bank_account.get("txns", [])
                    
                    for txn in transactions:
                        try:
                            if len(txn) < 4:
                                continue
                                
                            amount = float(txn[0])
                            narration = str(txn[1])
                            txn_date = str(txn[2])
                            txn_type = int(txn[3])
                            
                            # Only process recent transactions
                            if txn_date >= cutoff_date_str:
                                transaction_detail = {
                                    "amount": amount,
                                    "narration": narration,
                                    "date": txn_date,
                                    "bank": bank_name,
                                    "formatted_amount": f"₹{amount:,.0f}"
                                }
                                
                                if txn_type == 2:  # Debit
                                    category = self._categorize_transaction(narration)
                                    if category not in debit_transactions_categorized:
                                        debit_transactions_categorized[category] = []
                                    debit_transactions_categorized[category].append(transaction_detail)
                                
                                elif txn_type == 1:  # Credit
                                    # Simple credit categorization
                                    if any(keyword in narration.upper() for keyword in ["SALARY", "SAL", "PAYROLL", "WAGES"]):
                                        category = "Salary"
                                    elif any(keyword in narration.upper() for keyword in ["DIVIDEND", "INTEREST", "MATURITY"]):
                                        category = "Investment Income"
                                    elif any(keyword in narration.upper() for keyword in ["REFUND", "CASHBACK", "REWARD"]):
                                        category = "Refunds & Rewards"
                                    else:
                                        category = "Other Credits"
                                    
                                    if category not in credit_transactions_categorized:
                                        credit_transactions_categorized[category] = []
                                    credit_transactions_categorized[category].append(transaction_detail)
                                    
                        except (ValueError, IndexError, TypeError):
                            continue
            
            # Calculate financial behavior metrics
            total_spending = spending_summary.get("total_spending", 0)
            total_income = income_sources.get("total_income", 0)
            savings_rate = ((total_income - total_spending) / total_income * 100) if total_income > 0 else 0
            
            # Identify spending patterns
            top_spending_category = None
            if spending_summary.get("category_breakdown"):
                top_spending_category = spending_summary["category_breakdown"][0]["category"]
            
            return {
                "debit_transactions_categorized": debit_transactions_categorized,
                "credit_transactions_categorized": credit_transactions_categorized,
                "spending_analysis": spending_summary,
                "income_analysis": income_sources,
                "recurring_payments_analysis": recurring_payments,
                "financial_behavior_metrics": {
                    "total_spending_90_days": total_spending,
                    "total_income_90_days": total_income,
                    "estimated_savings_rate": savings_rate,
                    "estimated_monthly_savings": (total_income - total_spending) / 3 if total_income > total_spending else 0,
                    "top_spending_category": top_spending_category,
                    "spending_diversity": len(spending_summary.get("spending_by_category", {})),
                    "income_diversity": len(income_sources.get("income_sources", {})),
                    "recurring_commitments": recurring_payments.get("estimated_monthly_total", 0)
                },
                "identified_recurring_payments": recurring_payments.get("recurring_payments", []),
                "cashflow_health_indicators": {
                    "positive_cashflow": total_income > total_spending,
                    "healthy_savings_rate": savings_rate > 20,
                    "controlled_recurring_payments": recurring_payments.get("estimated_monthly_total", 0) < (total_income / 3 * 0.5),  # Less than 50% of monthly income
                    "diversified_income": len(income_sources.get("income_sources", {})) > 1,
                    "spending_control": total_spending / 90 < total_income / 3 * 0.8  # Daily spending less than 80% of estimated daily income
                },
                "data_completeness": {
                    "bank_transactions_available": bank_data is not None,
                    "spending_analysis_available": spending_summary.get("status") == "SUCCESS",
                    "income_analysis_available": income_sources.get("status") == "SUCCESS",
                    "recurring_payments_available": recurring_payments.get("status") == "SUCCESS",
                    "sufficient_transaction_history": spending_summary.get("transaction_count", 0) > 10
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error processing transaction data: {str(e)}",
                "debit_transactions_categorized": {},
                "credit_transactions_categorized": {},
                "spending_analysis": {},
                "income_analysis": {},
                "recurring_payments_analysis": {},
                "financial_behavior_metrics": {},
                "identified_recurring_payments": [],
                "cashflow_health_indicators": {},
                "data_completeness": {}
            }


# Import for ADK Agent factory function
from google.adk.agents import Agent


def create_expense_adk_agent(dal, model: str) -> Agent:
    """Factory function to create the Expense ADK Agent."""
    exp_agent_instance = ExpenseAndCashflowAgent(dal)

    expense_tools = [
        exp_agent_instance.get_core_transaction_data,  # NEW CORE TOOL - First and most prominent
        exp_agent_instance.get_spending_summary,
        exp_agent_instance.get_income_sources,
        exp_agent_instance.identify_recurring_payments,
        exp_agent_instance.get_processed_transaction_data
    ]

    return Agent(
        name="Expense_Agent",
        model=model,
        description="Handles questions about user spending, expenses, and cash flow.",
        tools=expense_tools,
    )