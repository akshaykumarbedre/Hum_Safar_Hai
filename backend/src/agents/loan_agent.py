"""
Loan & Credit Advisor Agent

This agent analyzes a user's credit report, outstanding loans, and provides
strategies for debt management and credit score improvement.
"""
from typing import Dict, Any, List
from ..fi_mcp_data_access import FIMCPDataAccess
from ..tools import financial_tools


class LoanAndCreditAgent:
    def __init__(self, dal: FIMCPDataAccess):
        self.dal = dal


    def get_core_credit_report_data(self) -> dict:
        """
        Get core credit report data in a pre-processed, token-efficient format.
        
        Returns:
            dict: Pre-processed credit report data with minimal token usage
        """
        try:
            # Fetch credit report from DAL
            credit_data = self.dal.get_credit_report()
            
            if not credit_data or 'creditReports' not in credit_data:
                return {"credit_summary": {}, "active_accounts": []}
            
            credit_report = credit_data['creditReports'][0]['creditReportData']
            
            result = {
                "credit_summary": {},
                "active_accounts": []
            }
            
            # Extract credit summary information
            score_data = credit_report.get('score', {})
            bureau_score = score_data.get('bureauScore', '0')
            
            # Get report date from header if available
            header = credit_report.get('creditProfileHeader', {})
            report_date = header.get('reportDate', 'Unknown')
            
            # Count active accounts and overdue accounts
            credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
            active_count = 0
            overdue_count = 0
            
            # Define account type and payment status mappings
            account_type_mapping = {
                '01': 'Credit Card',
                '10': 'Credit Card',
                '03': 'Home Loan',
                '04': 'Personal Loan',
                '05': 'Personal Loan',
                '02': 'Vehicle Loan',
                '06': 'Gold Loan',
                '07': 'Education Loan',
                '08': 'Business Loan'
            }
            
            payment_status_mapping = {
                '0': 'Current',
                '1': '30 days overdue',
                '2': '60 days overdue',
                '3': '90 days overdue',
                '4': '120 days overdue',
                '5': '150 days overdue',
                '6': '180+ days overdue'
            }
            
            # Process active accounts
            for account in credit_accounts:
                try:
                    account_status = account.get('accountStatus', '')
                    current_balance = account.get('currentBalance', '0')
                    
                    # Check if account is active with balance
                    try:
                        balance_amount = float(current_balance)
                    except (ValueError, TypeError):
                        balance_amount = 0
                    
                    # Consider active if status indicates active and has balance
                    if account_status in ['11', '83', '71'] and balance_amount > 0:
                        active_count += 1
                        
                        # Extract account details
                        subscriber_name = account.get('subscriberName', 'Unknown Lender')
                        account_type = account.get('accountType', '')
                        payment_rating = account.get('paymentRating', '0')
                        
                        # Map codes to readable text
                        readable_type = account_type_mapping.get(account_type, 'Other Loan')
                        readable_status = payment_status_mapping.get(payment_rating, 'Current')
                        
                        # Count overdue accounts
                        if payment_rating and payment_rating != '0':
                            overdue_count += 1
                        
                        # Add to active accounts list
                        account_info = {
                            "lender": subscriber_name[:30],  # Truncate long names
                            "type": readable_type,
                            "balance": balance_amount,
                            "payment_status": readable_status
                        }
                        result["active_accounts"].append(account_info)
                        
                except (KeyError, TypeError, ValueError):
                    continue
            
            # Build credit summary
            try:
                credit_score = int(bureau_score) if bureau_score and bureau_score != '0' else 0
            except (ValueError, TypeError):
                credit_score = 0
            
            result["credit_summary"] = {
                "credit_score": credit_score,
                "report_date": report_date,
                "active_accounts": active_count,
                "overdue_accounts": overdue_count
            }
            
            return result
            
        except Exception as e:
            return {
                "credit_summary": {"error": str(e)},
                "active_accounts": []
            }

    def get_credit_score_analysis(self) -> Dict[str, Any]:

        """
        Analyze user's credit score and identify potential issues from payment history.
        
        Returns:
            Dict[str, Any]: Structured analysis of credit score and payment issues
        """
        # Fetch credit report from DAL
        credit_data = self.dal.get_credit_report()
        
        # Handle cases where the report is missing
        if not credit_data or 'creditReports' not in credit_data:
            return {
                "status": "ERROR",
                "message": "Credit report data is not available for analysis.",
                "credit_score": None,
                "negative_accounts": []
            }
        
        try:
            credit_report = credit_data['creditReports'][0]['creditReportData']
            
            # Extract score
            score_data = credit_report.get('score', {})
            bureau_score = score_data.get('bureauScore', '0')
            
            if not bureau_score or bureau_score == '0':
                return {
                    "status": "ERROR",
                    "message": "Credit score information is not available.",
                    "credit_score": None,
                    "negative_accounts": []
                }
            
            credit_score = int(bureau_score)
            
            # Determine score quality
            if credit_score >= 750:
                score_quality = "EXCELLENT"
                score_message = "Excellent credit score! You qualify for the best interest rates."
            elif credit_score >= 700:
                score_quality = "GOOD"
                score_message = "Good credit score. You should get favorable loan terms."
            elif credit_score >= 650:
                score_quality = "FAIR"
                score_message = "Fair credit score. There's room for improvement."
            else:
                score_quality = "POOR"
                score_message = "Poor credit score. Focus on improving your credit health."
            
            # Look for negative indicators like poor payment ratings
            credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
            accounts_with_issues = []
            
            for account in credit_accounts:
                payment_rating = account.get('paymentRating', '0')
                if payment_rating and payment_rating != '0':
                    subscriber_name = account.get('subscriberName', 'Unknown Bank')
                    account_type = account.get('accountType', 'Unknown')
                    current_balance = account.get('currentBalance', '0')
                    
                    accounts_with_issues.append({
                        "lender_name": subscriber_name,
                        "account_type": account_type,
                        "payment_rating": payment_rating,
                        "current_balance": float(current_balance) if current_balance else 0,
                        "formatted_balance": f"₹{float(current_balance):,.0f}" if current_balance else "₹0"
                    })
            
            return {
                "status": "SUCCESS",
                "credit_score": credit_score,
                "score_quality": score_quality,
                "score_message": score_message,
                "negative_accounts": accounts_with_issues,
                "negative_accounts_count": len(accounts_with_issues),
                "payment_history_status": "GOOD" if len(accounts_with_issues) == 0 else "NEEDS_ATTENTION",
                "overall_assessment": {
                    "score_band": score_quality,
                    "has_payment_issues": len(accounts_with_issues) > 0,
                    "improvement_needed": credit_score < 750 or len(accounts_with_issues) > 0
                }
            }
            
        except (KeyError, IndexError, ValueError, TypeError) as e:
            return {
                "status": "ERROR",
                "message": "Unable to analyze credit score due to incomplete data format.",
                "credit_score": None,
                "negative_accounts": [],
                "error_details": str(e)
            }

    def suggest_loan_prepayment_strategy(self) -> Dict[str, Any]:
        """
        Suggest loan prepayment strategy based on loan types and typical interest rates.
        
        Returns:
            Dict[str, Any]: Structured recommendation for loan prepayment prioritization
        """
        # Fetch the user's liabilities from net worth to get an overview
        net_worth_data = self.dal.get_net_worth()
        
        # Fetch the detailed credit accounts from credit report
        credit_data = self.dal.get_credit_report()
        
        # Handle cases where data is missing
        if not credit_data or 'creditReports' not in credit_data:
            return {
                "status": "ERROR",
                "message": "Credit report data is not available for loan analysis.",
                "prioritized_loans": [],
                "total_outstanding": 0
            }
        
        if not net_worth_data or 'netWorthResponse' not in net_worth_data:
            return {
                "status": "ERROR",
                "message": "Net worth data is not available for liability analysis.",
                "prioritized_loans": [],
                "total_outstanding": 0
            }
        
        try:
            # Get detailed credit accounts
            credit_report = credit_data['creditReports'][0]['creditReportData']
            credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
            
            # Identify all active loans and categorize them
            account_type_priority = {
                '01': ('Credit Card', 1, 'Highest interest rates (15-30% annually)'),
                '10': ('Credit Card', 1, 'Highest interest rates (15-30% annually)'),
                '04': ('Personal Loan', 2, 'High interest rates (12-18% annually)'),
                '05': ('Personal Loan', 2, 'High interest rates (12-18% annually)'),
                '02': ('Vehicle Loan', 3, 'Moderate interest rates (8-12% annually)'),
                '06': ('Vehicle Loan', 3, 'Moderate interest rates (8-12% annually)'),
                '03': ('Home Loan', 4, 'Lower interest rates (6-10% annually)')
            }
            
            active_loans = []
            total_outstanding = 0
            
            for account in credit_accounts:
                account_type = account.get('accountType', '')
                account_status = account.get('accountStatus', '')
                current_balance = account.get('currentBalance', '0')
                subscriber_name = account.get('subscriberName', 'Unknown Bank')
                
                # Check if account is active and has outstanding balance
                if (account_status and account_status != '82' and account_status != '97' and 
                    current_balance and float(current_balance) > 0):
                    
                    loan_info = account_type_priority.get(account_type, ('Other Loan', 5, 'Interest rate varies'))
                    loan_type = loan_info[0]
                    priority = loan_info[1]
                    rate_info = loan_info[2]
                    balance = float(current_balance)
                    
                    total_outstanding += balance
                    
                    active_loans.append({
                        'loan_type': loan_type,
                        'lender': subscriber_name,
                        'outstanding_balance': balance,
                        'priority': priority,
                        'account_type_code': account_type,
                        'interest_rate_info': rate_info,
                        'formatted_balance': f'₹{balance:,.0f}',
                        'prepayment_urgency': 'HIGH' if priority <= 2 else 'MODERATE' if priority <= 3 else 'LOW'
                    })
            
            if not active_loans:
                return {
                    "status": "SUCCESS",
                    "message": "Good news! You don't appear to have any active loans requiring prepayment.",
                    "prioritized_loans": [],
                    "total_outstanding": 0,
                    "strategic_advice": "Focus on building an emergency fund and investing for long-term goals."
                }
            
            # Sort by priority (lower number = higher priority) then by balance
            active_loans.sort(key=lambda x: (x['priority'], -x['outstanding_balance']))
            
            # Generate strategic advice based on loan mix
            strategic_advice = []
            if any(loan['loan_type'] == 'Credit Card' for loan in active_loans):
                cc_total = sum(loan['outstanding_balance'] for loan in active_loans if loan['loan_type'] == 'Credit Card')
                strategic_advice.append(f"Credit Cards (₹{cc_total:,.0f}) have the highest interest rates - prioritize these first.")
            
            if any(loan['loan_type'] == 'Personal Loan' for loan in active_loans):
                strategic_advice.append("Personal Loans typically have higher rates than secured loans, making them good candidates for prepayment.")
            
            if any(loan['loan_type'] == 'Home Loan' for loan in active_loans):
                strategic_advice.append("Home Loans have lower interest rates and tax benefits - consider these last for prepayment.")
            
            return {
                "status": "SUCCESS",
                "prioritized_loans": active_loans,
                "total_outstanding": total_outstanding,
                "formatted_total_outstanding": f"₹{total_outstanding:,.0f}",
                "loans_count": len(active_loans),
                "high_priority_loans": [loan for loan in active_loans if loan['priority'] <= 2],
                "strategic_advice": strategic_advice,
                "prepayment_summary": {
                    "highest_priority": active_loans[0] if active_loans else None,
                    "total_high_interest_debt": sum(loan['outstanding_balance'] for loan in active_loans if loan['priority'] <= 2),
                    "estimated_annual_savings": sum(loan['outstanding_balance'] * 0.20 for loan in active_loans if loan['priority'] <= 2)  # Assuming 20% average interest for high priority
                }
            }
            
        except (KeyError, IndexError, ValueError, TypeError) as e:
            return {
                "status": "ERROR",
                "message": "Unable to analyze loans due to incomplete data format.",
                "prioritized_loans": [],
                "total_outstanding": 0,
                "error_details": str(e)
            }

    def list_all_active_loans(self) -> List[Dict[str, Any]]:
        """
        Lists all active loans and their outstanding balances.
        
        Returns:
            List[Dict[str, Any]]: List of active loan objects with details
        """
        try:
            # Fetch the detailed credit accounts from credit report
            credit_data = self.dal.get_credit_report()
            
            # Handle cases where data is missing
            if not credit_data or 'creditReports' not in credit_data:
                return []
            
            # Get detailed credit accounts
            credit_report = credit_data['creditReports'][0]['creditReportData']
            credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
            
            # Define account type mapping for better readability
            account_type_mapping = {
                '01': 'Credit Card',
                '10': 'Credit Card',
                '03': 'Home Loan',
                '04': 'Personal Loan',
                '05': 'Personal Loan',
                '02': 'Vehicle Loan',
                '06': 'Gold Loan',
                '53': 'Consumer Loan',
                '07': 'Education Loan',
                '08': 'Business Loan',
                '09': 'Property Loan',
                '11': 'Overdraft',
                '12': 'Term Loan'
            }
            
            # Define closed/inactive status codes to exclude
            # Status 82 = Closed, 97 = Settled, other codes may indicate active accounts
            inactive_status_codes = ['82', '97']
            
            active_loans = []
            
            # Process each credit account
            for account in credit_accounts:
                try:
                    account_type = account.get('accountType', '')
                    account_status = account.get('accountStatus', '')
                    current_balance = account.get('currentBalance', '0')
                    subscriber_name = account.get('subscriberName', 'Unknown Lender')
                    date_opened = account.get('dateOpened', '')
                    
                    # Convert balance to float
                    try:
                        balance_amount = float(current_balance)
                    except (ValueError, TypeError):
                        balance_amount = 0
                    
                    # Check if account is active (not closed/settled) and has outstanding balance
                    if (account_status and account_status not in inactive_status_codes and balance_amount > 0):
                        
                        # Get readable loan type
                        loan_type = account_type_mapping.get(account_type, f'Other Loan (Type {account_type})')
                        
                        # Add account opening date if available
                        opened_date = "Unknown"
                        if date_opened and len(date_opened) >= 8:
                            try:
                                # Convert YYYYMMDD to readable format
                                year = date_opened[:4]
                                month = date_opened[4:6]
                                day = date_opened[6:8]
                                opened_date = f"{day}/{month}/{year}"
                            except:
                                opened_date = "Unknown"
                        
                        active_loans.append({
                            'loan_type': loan_type,
                            'lender': subscriber_name,
                            'outstanding_balance': balance_amount,
                            'account_opened': opened_date,
                            'account_type_code': account_type,
                            'account_status': account_status,
                            'formatted_balance': f'₹{balance_amount:,.0f}',
                            'is_credit_card': loan_type == 'Credit Card'
                        })
                        
                except (KeyError, TypeError, ValueError):
                    # Skip accounts with invalid data
                    continue
            
            # Sort by balance (descending) then by loan type
            active_loans.sort(key=lambda x: (-x['outstanding_balance'], x['loan_type']))
            
            return active_loans
            
        except (KeyError, IndexError, ValueError, TypeError) as e:
            return [{"error": f"Unable to retrieve loan information: {str(e)}"}]


    def get_processed_credit_data(self) -> Dict[str, Any]:
        """Processes and returns a structured JSON summary of all credit and loan data."""
        try:
            # Get all credit analysis
            credit_score_analysis = self.get_credit_score_analysis()
            prepayment_strategy = self.suggest_loan_prepayment_strategy()
            active_loans = self.list_all_active_loans()
            
            # Fetch raw credit data for comprehensive analysis
            credit_data = self.dal.get_credit_report()
            
            # Process detailed credit information
            credit_summary = {
                "credit_score": None,
                "total_accounts": 0,
                "active_accounts": 0,
                "closed_accounts": 0,
                "defaulted_accounts": 0
            }
            
            detailed_accounts = {
                "credit_cards": [],
                "loans": [],
                "other_accounts": []
            }
            
            recent_inquiries = []
            
            if credit_data and credit_data.get('creditReports'):
                try:
                    credit_report = credit_data['creditReports'][0]['creditReportData']
                    
                    # Extract credit score
                    score_data = credit_report.get('score', {})
                    bureau_score = score_data.get('bureauScore', '0')
                    if bureau_score and bureau_score != '0':
                        credit_summary["credit_score"] = int(bureau_score)
                    
                    # Process all credit accounts
                    credit_accounts = credit_report.get('creditAccount', {}).get('creditAccountDetails', [])
                    credit_summary["total_accounts"] = len(credit_accounts)
                    
                    for account in credit_accounts:
                        try:
                            account_type = account.get('accountType', '')
                            account_status = account.get('accountStatus', '')
                            current_balance = float(account.get('currentBalance', '0'))
                            credit_limit = float(account.get('creditLimit', '0'))
                            subscriber_name = account.get('subscriberName', 'Unknown')
                            date_opened = account.get('dateOpened', '')
                            payment_rating = account.get('paymentRating', '0')
                            
                            # Count account statuses
                            if account_status in ['11', '83', '71']:
                                credit_summary["active_accounts"] += 1
                            elif account_status in ['82', '97']:
                                credit_summary["closed_accounts"] += 1
                            elif payment_rating != '0':
                                credit_summary["defaulted_accounts"] += 1
                            
                            # Categorize account
                            account_detail = {
                                "lender": subscriber_name,
                                "account_type_code": account_type,
                                "account_status": account_status,
                                "current_balance": current_balance,
                                "credit_limit": credit_limit,
                                "utilization": (current_balance / credit_limit * 100) if credit_limit > 0 else 0,
                                "date_opened": date_opened,
                                "payment_rating": payment_rating,
                                "has_negative_history": payment_rating != '0',
                                "formatted_balance": f"₹{current_balance:,.0f}",
                                "formatted_limit": f"₹{credit_limit:,.0f}"
                            }
                            
                            if account_type in ['01', '10']:  # Credit cards
                                detailed_accounts["credit_cards"].append(account_detail)
                            elif account_type in ['02', '03', '04', '05', '06', '07', '08']:  # Loans
                                detailed_accounts["loans"].append(account_detail)
                            else:
                                detailed_accounts["other_accounts"].append(account_detail)
                                
                        except (ValueError, TypeError, KeyError):
                            continue
                    
                    # Process recent inquiries
                    inquiries = credit_report.get('inquiry', {}).get('inquiryDetails', [])
                    for inquiry in inquiries[-5:]:  # Last 5 inquiries
                        try:
                            recent_inquiries.append({
                                "enquiry_date": inquiry.get('enquiryDate', ''),
                                "enquiry_purpose": inquiry.get('enquiryPurpose', ''),
                                "enquiring_member": inquiry.get('enquiringMember', ''),
                                "amount": float(inquiry.get('amount', '0')) if inquiry.get('amount') else 0
                            })
                        except (ValueError, TypeError, KeyError):
                            continue
                            
                except (KeyError, IndexError, TypeError):
                    pass
            
            # Calculate aggregate metrics
            total_outstanding = sum(loan.get("outstanding_balance", 0) for loan in active_loans if not loan.get("error"))
            total_credit_limit = sum(card.get("credit_limit", 0) for card in detailed_accounts["credit_cards"])
            total_credit_used = sum(card.get("current_balance", 0) for card in detailed_accounts["credit_cards"])
            overall_utilization = (total_credit_used / total_credit_limit * 100) if total_credit_limit > 0 else 0
            
            # Health indicators
            credit_health_indicators = {
                "good_credit_score": credit_summary.get("credit_score", 0) >= 750,
                "low_credit_utilization": overall_utilization < 30,
                "no_negative_history": credit_summary["defaulted_accounts"] == 0,
                "manageable_debt_load": total_outstanding < 500000,  # 5 lakhs threshold
                "recent_inquiry_activity": len(recent_inquiries) <= 2
            }
            
            return {
                "credit_score_summary": credit_score_analysis,
                "loan_strategy": prepayment_strategy,
                "active_loans_list": active_loans,
                "account_summary": credit_summary,
                "detailed_loan_accounts": detailed_accounts["loans"],
                "detailed_credit_card_accounts": detailed_accounts["credit_cards"],
                "other_credit_accounts": detailed_accounts["other_accounts"],
                "recent_inquiries": recent_inquiries,
                "aggregate_metrics": {
                    "total_outstanding_debt": total_outstanding,
                    "total_credit_limit": total_credit_limit,
                    "total_credit_used": total_credit_used,
                    "overall_credit_utilization": overall_utilization,
                    "formatted_total_debt": f"₹{total_outstanding:,.0f}",
                    "formatted_credit_limit": f"₹{total_credit_limit:,.0f}",
                    "active_loans_count": len([loan for loan in active_loans if not loan.get("error")]),
                    "credit_cards_count": len(detailed_accounts["credit_cards"])
                },
                "credit_health_indicators": credit_health_indicators,
                "overall_credit_health_score": sum(1 for indicator in credit_health_indicators.values() if indicator),
                "data_completeness": {
                    "credit_report_available": credit_data is not None,
                    "credit_score_available": credit_score_analysis.get("status") == "SUCCESS",
                    "active_loans_available": len(active_loans) > 0 and not active_loans[0].get("error"),
                    "prepayment_strategy_available": prepayment_strategy.get("status") == "SUCCESS"
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error processing credit data: {str(e)}",
                "credit_score_summary": {},
                "loan_strategy": {},
                "active_loans_list": [],
                "account_summary": {},
                "detailed_loan_accounts": [],
                "detailed_credit_card_accounts": [],
                "other_credit_accounts": [],
                "recent_inquiries": [],
                "aggregate_metrics": {},
                "credit_health_indicators": {},
                "overall_credit_health_score": 0,
                "data_completeness": {}
            }


# Import for ADK Agent factory function
from google.adk.agents import Agent


def create_loan_adk_agent(dal, model: str) -> Agent:
    """Factory function to create the Loan ADK Agent."""
    loan_agent_instance = LoanAndCreditAgent(dal)

    loan_tools = [
        loan_agent_instance.get_core_credit_report_data,  # NEW CORE TOOL - First and most prominent
        loan_agent_instance.get_credit_score_analysis,
        loan_agent_instance.suggest_loan_prepayment_strategy,
        loan_agent_instance.list_all_active_loans,
        loan_agent_instance.get_processed_credit_data
    ]

    return Agent(
        name="Loan_Agent",
        model=model,
        description="Handles questions about loans, debt, and credit score.",
        tools=loan_tools,
    )