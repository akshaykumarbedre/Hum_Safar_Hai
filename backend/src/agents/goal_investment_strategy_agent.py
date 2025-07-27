
import math
import json
from typing import Dict, Any, List, Tuple, Optional
from src.fi_mcp_data_access import FIMCPDataAccess
from collections import Counter

class GoalInvestmentStrategyAgent:
    """
    Goal & Investment Strategy Agent that provides personalized savings and investment advice.
    
    This agent is initialized with data for two specific users and provides tools for:
    - Calculating monthly savings recommendations
    - Setting and managing financial goals
    - Computing time-to-goal with compound interest
    - Providing investment options sorted by expected returns
    """
    
    # Asset class data structure with expected annual returns
    ASSETS = [
        {
            "asset_class": "Mutual Fund",
            "asset_subtype": "Small Cap",
            "default_options": [
            "Axis Small Cap Fund - Direct Plan - Growth"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 18.5,
            "risk_rating": 5
        },
        {
            "asset_class": "Mutual Fund",
            "asset_subtype": "Mid Cap",
            "default_options": [
            "Kotak Emerging Equity Fund - Direct Plan - Growth"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 15.2,
            "risk_rating": 4
        },
        {
            "asset_class": "Mutual Fund",
            "asset_subtype": "Large Cap",
            "default_options": [
            "ICICI Prudential Bluechip Fund - Direct - Growth",
            "Nippon India Large Cap Fund - Direct - Growth"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 12.9,
            "risk_rating": 3
        },
        {
            "asset_class": "Fixed Deposit",
            "asset_subtype": "N/A",
            "default_options": [
            "HDFC Bank 5-Year FD"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 7.0,
            "risk_rating": 1
        },
        {
            "asset_class": "Savings Account",
            "asset_subtype": "N/A",
            "default_options": [
            "SBI Regular Savings Account"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 3.5,
            "risk_rating": 1
        },
        {
            "asset_class": "ETF",
            "asset_subtype": "N/A",
            "default_options": [
            "Motilal Oswal Nasdaq 100 ETF",
            "Nifty 50 ETF"
            ],
            "male_existing_options": [],
            "female_existing_options": [],
            "expected_cagr": 12.5,
            "risk_rating": 4
        }
    ]
    
    def __init__(self, male_phone: str, female_phone: str):
        """
        Initialize the Goal & Investment Strategy Agent with data for two users.
        
        Args:
            user1_data: Complete bank transactions data for User 1 (Male)
            user2_data: Complete bank transactions data for User 2 (Female)
        """
        
        # Calculate the ma and fa
        male_bank_transactions = FIMCPDataAccess(phone_number=male_phone).get_bank_transactions()
        female_bank_transactions = FIMCPDataAccess(phone_number=female_phone).get_bank_transactions()

        self.male_monthly_contribution = self._estimate_monthly_income(male_bank_transactions) - self._estimate_monthly_expenses(male_bank_transactions)
        self.female_monthly_contribution = self._estimate_monthly_income(female_bank_transactions) - self._estimate_monthly_expenses(female_bank_transactions)
        self.total_monthly_contribution = self.male_monthly_contribution + self.female_monthly_contribution
        print(self.male_monthly_contribution, self.female_monthly_contribution, self.total_monthly_contribution)

        # Initialize goals from JSON file
        self.goals_file_path = "./FI money dummy data/combined_goals.json"
        try:
            with open(self.goals_file_path, 'r') as f:
                self.goals = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.goals = []
            self._save_goals_to_file()

        goal_names = [goal['name'] for goal in self.goals]
        if("Wealth Creation (1 Cr)" not in goal_names and "Retirement Corpus (10 Cr)" not in goal_names):
            self.goals = self.create_initial_goals(male_phone,female_phone)

        print(self.goals, 'This is in this step')
        for goal in self.goals:
            # Pledged means the goals that is not yet captured in the bank expense
            if(goal['pledged']):
                self.male_monthly_contribution -= goal['male_monthly_contribution']
                self.female_monthly_contribution -= goal['female_monthly_contribution']
                self.total_monthly_contribution -= goal['total_monthly_contribution']

        self.ASSETS = self.analyze_and_structure_assets_by_category(male_phone,female_phone)
    
    def _save_goals_to_file(self):
        """Save goals to JSON file."""
        try:
            with open(self.goals_file_path, 'w') as f:
                json.dump(self.goals, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save goals to file: {str(e)}")

    def create_initial_goals(self, male_phone: str, female_phone: str):
        """
        Reads MF and EPF statements, creates initial wealth and retirement goals with a new structure
        that distinguishes between the current corpus and ongoing monthly contributions.

        Args:
            male_phone (str): The phone number of the male partner.
            female_phone (str): The phone number of the female partner.
            goals_file_path (str): The path to the JSON file to save the goals.
        """
        # --- 1. Load Data from Files ---
        try:
            male_mf_data = FIMCPDataAccess(phone_number=male_phone).get_mutual_fund_transactions()
            female_mf_data = FIMCPDataAccess(phone_number=female_phone).get_mutual_fund_transactions()

            male_epf_data = FIMCPDataAccess(phone_number=male_phone).get_epf_details()
            female_epf_data = FIMCPDataAccess(phone_number=female_phone).get_epf_details()

        except FileNotFoundError as e:
            print(f"Error: Could not find a required data file. {e}")
            return
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse a JSON file. {e}")
            return

        male_mf_transactions = male_mf_data.get('mfTransactions', [])
        female_mf_transactions = female_mf_data.get('mfTransactions', [])

        # --- 2. Process Mutual Fund Data for Wealth Goal ---
        def process_mf_transactions(transactions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float, float]:
            """
            Processes MF transactions to get total invested amount and estimate monthly contribution.

            Returns:
                Tuple containing:
                - A list of assets with their total invested amount.
                - The total corpus (sum of all investments).
                - The estimated total monthly contribution (from SIPs).
            """
            assets = {}
            total_corpus = 0.0

            for mf in transactions:
                scheme_name = mf.get('schemeName')
                if not scheme_name:
                    continue

                buy_txns = [txn[4] for txn in mf.get('txns', []) if txn[0] == 1]
                if not buy_txns:
                    continue

                # Calculate the total amount invested in this scheme (current corpus for this asset)
                total_investment_in_scheme = sum(buy_txns)
                total_corpus += total_investment_in_scheme
                
                # Heuristic to find the recurring SIP amount
                # Count the frequency of each investment amount.
                amount_counts = Counter(buy_txns)
                
                # Find the most common investment amount.
                if amount_counts:
                    # We assume the most frequent, non-trivial amount is the SIP.
                    # This helps filter out single large lump-sum investments.
                    # We can add more logic here, e.g., filter out amounts that only appear once.
                    most_common_amount, count = amount_counts.most_common(1)[0]
                    if count >= 1: # Assume it's a recurring SIP if it happened more than once
                        assets[scheme_name] = most_common_amount

            asset_list = [{"asset_name": name, "amount": amount} for name, amount in assets.items()]
            return asset_list, total_corpus, sum([asset['amount'] for asset in asset_list])

        male_mf_assets, male_corpus, male_monthly_contri = process_mf_transactions(male_mf_transactions)
        female_mf_assets, female_corpus, female_monthly_contri = process_mf_transactions(female_mf_transactions)

        wealth_goal = {
            'name': 'Wealth Creation (1 Cr)',
            'target_amount': 10000000.0,
            'male_assets': male_mf_assets,
            'female_assets': female_mf_assets,
            'current_corpus': male_corpus + female_corpus,
            'male_monthly_contribution': male_monthly_contri,
            'female_monthly_contribution': female_monthly_contri,
            'total_monthly_contribution': male_monthly_contri + female_monthly_contri,
            'pledged': False
        }

        # --- 3. Process EPF Data for Retirement Goal ---
        def process_epf_data(epf_data: Dict[str, Any]) -> float:
            total_epf_corpus = 0.0
            contribution_amount = 0.0
            for account in epf_data.get('uanAccounts', []):
                raw_details = account.get('rawDetails', {})
                overall_balance = raw_details.get('overall_pf_balance', {})
                if overall_balance:
                    pf_balance = float(overall_balance.get('current_pf_balance', '0'))
                    pension_balance = float(overall_balance.get('pension_balance', '0'))
                    total_epf_corpus += pf_balance + pension_balance
                
                contribution_amount = float(raw_details.get('overall_pf_balance',{}).get('employee_share_total',{}).get('credit',0)) + float(raw_details.get('overall_pf_balance',{}).get('employer_share_total',{}).get('credit',0))
            return total_epf_corpus, contribution_amount

        male_epf_corpus, male_contribution = process_epf_data(male_epf_data)
        female_epf_corpus, female_contribution = process_epf_data(female_epf_data)

        retirement_goal = {
            'name': 'Retirement Corpus (10 Cr)',
            'target_amount': 100000000.0,
            'male_assets': [{"asset_name": "EPF & Pension", "amount": male_contribution}],
            'female_assets': [{"asset_name": "EPF & Pension", "amount": female_contribution}],
            'current_corpus': male_epf_corpus + female_epf_corpus,
            'male_monthly_contribution': male_contribution,  # Cannot be determined from EPF data snapshot
            'female_monthly_contribution': female_contribution, # Cannot be determined from EPF data snapshot
            'total_monthly_contribution': male_contribution + female_contribution,
            'pledged': False
        }

        # --- 4. Combine Goals and Save to File ---
        return [wealth_goal, retirement_goal]

    def _extract_user_holdings(self, net_worth_data: Dict[str, Any], all_products: List[Dict[str, Any]],male=True):
        """
        Parses a user's net worth JSON to find which of the master products they hold.

        Returns:
            A set of asset names from the master product list that the user owns.
        """

        # --- Match Mutual Funds ---
        mf_schemes = net_worth_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
        for scheme in mf_schemes:
            user_mf_name = scheme.get('nameData', {}).get('longName', '').lower()
            asset_fund = scheme.get('assetClass','')
            category = scheme.get('categoryName','')
            risk_category = scheme.get('fundhouseDefinedRiskLevel','')
            for product in all_products:
                if(asset_fund=='EQUITY' and product["asset_class"]== "Mutual Fund" and product['risk_rating']>=4 and risk_category == 'VERY_HIGH_RISK'):
                    if(male):
                        product['male_existing_options'].append(user_mf_name)
                    else:
                        product['female_existing_options'].append(user_mf_name)
                elif(asset_fund=='EQUITY' and product["asset_class"]== "Mutual Fund" and product['risk_rating']==4 and risk_category == 'MODERATE_RISK'):
                    if(male):
                        product['male_existing_options'].append(user_mf_name)
                    else:
                        product['female_existing_options'].append(user_mf_name)
                elif(asset_fund=='EQUITY' and product["asset_class"]== "Mutual Fund" and product['risk_rating']==4 and risk_category == 'MODERATE_RISK'):
                    pass

        return all_products


    def analyze_and_structure_assets_by_category(self, male_phone: str, female_phone: str) -> List[Dict[str, Any]]:
        """
        Analyzes couple's assets and structures them by category, showing existing and default options.

        Args:
            male_phone: Phone number of the male partner.
            female_phone: Phone number of the female partner.

        Returns:
            A list of dictionaries, where each dict represents an asset category
            with detailed options.
        """
        try:
            # Load user net worth data
            male_net_worth = FIMCPDataAccess(phone_number=male_phone).get_net_worth()
            female_net_worth = FIMCPDataAccess(phone_number=female_phone).get_net_worth()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading or parsing net worth files: {e}")
            return [{"error": str(e)}]

        # 1. Get the set of products each user holds
        male_holdings = self._extract_user_holdings(male_net_worth, self.ASSETS)
        female_holdings = self._extract_user_holdings(female_net_worth, male_holdings)

        return female_holdings
    
    def create_goal(self, target_amount: float):
        """
        Creates a new financial goal based on previously calculated asset allocation strategy.
        
        This tool finalizes the goal creation process after the user has reviewed and approved 
        the investment timeline and asset allocation through calculate_months_to_reach_goal_with_asset_ladder.
        
        IMPORTANT: This tool should only be called AFTER the user has:
        1. Used calculate_months_to_reach_goal_with_asset_ladder to see timeline with safe assets (Savings Account)
        2. Optionally explored faster timelines with mixed asset allocations (Large Cap + Small Cap)
        3. Confirmed they want to create the goal with the discussed asset allocation
        
        Args:
            target_amount (float): The target amount for the financial goal (e.g., 500000 for ₹5 lakhs)
        
        Returns:
            str: A detailed summary of the created goal including:
                - Asset allocation for both partners
                - Monthly SIP recommendations
                - Existing investments that can be topped up
                - New investments that need to be started
        
        Note: This tool uses the asset allocation from the last call to calculate_months_to_reach_goal_with_asset_ladder
        and creates specific investment recommendations for both partners based on their existing portfolios.
        """

        male_assets = []
        female_assets = []

        print('I am in the create goal agent',self.final_discussion)
        if(not self.final_discussion or 'asset_ladder' not in self.final_discussion):
            return "First finalise the asset ladder for this goal before creating the goal"

        output_string = ["Created the goal successfully:\n"]
        for asset_class, asset_subtype, asset_percentage in self.final_discussion['asset_ladder']:
            for product in self.ASSETS:
                if(product['asset_class']==asset_class and product['asset_subtype']==asset_subtype):
                    male_options = product['male_existing_options']
                    if(male_options):
                        output_string.append(f"Yay Rohan, you already have an existing mutual fund of {male_options[0]} under the {asset_class}, top up the SIP with {self.final_discussion['male_monthly_contribution']* asset_percentage} ")
                        male_assets.append({"asset_name": male_options[0], "amount": self.final_discussion['male_monthly_contribution']* asset_percentage })
                    else:
                        output_string.append(f"Rohan, from next month you need to invest in mutual fund of {product['default_options'][0]} under the {asset_class}, top up the SIP with {self.final_discussion['male_monthly_contribution']* asset_percentage} ")
                        male_assets.append({"asset_name": product['default_options'][0], "amount": self.final_discussion['male_monthly_contribution']* asset_percentage })
                    
                    female_options = product['female_existing_options']
                    if(female_options):
                        output_string.append(f"Yay Priya, you already have an existing mutual fund of {female_options[0]} under the {asset_class}, top up the SIP with {self.final_discussion['female_monthly_contribution']* asset_percentage} ")
                        female_assets.append({"asset_name": female_options[0], "amount": self.final_discussion['female_monthly_contribution']* asset_percentage })
                    else:
                        output_string.append(f"Priya, from next month you need to invest in mutual fund of {product['default_options'][0]} under the {asset_class}, top up the SIP with {self.final_discussion['female_monthly_contribution']* asset_percentage} ")
                        female_assets.append({"asset_name": product['default_options'][0], "amount": self.final_discussion['female_monthly_contribution']* asset_percentage })

        goali = {
            'name': self.final_discussion['name'],
            'target_amount': target_amount,
            'male_assets': male_assets,
            'female_assets': female_assets,
            'current_corpus': 0,
            'male_monthly_contribution': self.final_discussion['male_monthly_contribution'],  # Cannot be determined from EPF data snapshot
            'female_monthly_contribution': self.final_discussion['female_monthly_contribution'], # Cannot be determined from EPF data snapshot
            'total_monthly_contribution': self.final_discussion['male_monthly_contribution'] + self.final_discussion['female_monthly_contribution'],
            'pledged': True
        }

        self.goals.append(goali)
        self.male_monthly_contribution -= self.final_discussion['male_monthly_contribution']
        self.female_monthly_contribution -= self.final_discussion['female_monthly_contribution']
        self.total_monthly_contribution -= self.final_discussion['male_monthly_contribution'] + self.final_discussion['female_monthly_contribution']
        print(json.dumps(self.goals,indent=2))

        self._save_goals_to_file()
        return '\n'.join(output_string)
    
    def _estimate_monthly_income(self, user_data: Dict[str, Any]) -> float:
        """Estimate monthly income from bank transactions."""
        try:
            bank_transactions = user_data.get('bank_transactions', {})
            if not bank_transactions or 'bankTransactions' not in bank_transactions:
                return 50000.0  # Default assumption
            
            total_credits = 0
            transaction_count = 0
            
            for bank_account in bank_transactions['bankTransactions']:
                for txn in bank_account.get('txns', []):
                    if len(txn) >= 4:
                        amount = float(txn[0])
                        txn_type = int(txn[3])
                        narration = str(txn[1]).upper()
                        
                        # Credit transactions (type = 1) that look like income
                        if txn_type == 1 and amount > 10000:  # Significant credits
                            # Filter for likely income sources
                            if any(keyword in narration for keyword in ['SALARY', 'SAL', 'PAYROLL', 'WAGES', 'COMPANY']):
                                total_credits += amount
                                transaction_count += 1
            
            if transaction_count > 0:
                # Assume data covers 3 months, so divide by 3
                return total_credits / max(3, transaction_count * 0.5)
            
            return 50000.0  # Default if no income detected
            
        except Exception:
            return 50000.0
    
    def _estimate_monthly_expenses(self, user_data: Dict[str, Any]) -> float:
        """Estimate monthly expenses from bank transactions."""
        try:
            bank_transactions = user_data.get('bank_transactions', {})
            if not bank_transactions or 'bankTransactions' not in bank_transactions:
                return 30000.0  # Default assumption
            
            total_debits = 0
            transaction_count = 0
            
            for bank_account in bank_transactions['bankTransactions']:
                for txn in bank_account.get('txns', []):
                    if len(txn) >= 4:
                        amount = float(txn[0])
                        txn_type = int(txn[3])
                        
                        # Debit transactions (type = 2)
                        if txn_type == 2:
                            total_debits += amount
                            transaction_count += 1
            
            if transaction_count > 0:
                # Assume data covers 3 months, so divide by 3
                return total_debits / 3
            
            return 30000.0  # Default if no expenses detected
            
        except Exception:
            return 30000.0
    
    def get_num_of_months_to_reach_goal(
        self,
        monthly_investment: float, 
        target_amount: float, 
        annual_return_rate: float,
        current_corpus: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate the number of months needed to reach a financial goal using compound interest,
        starting with an existing corpus amount.
        """
        try:
            if monthly_investment <= 0:
                return {"status": "ERROR", "message": "Monthly investment must be positive."}
            
            if target_amount <= 0:
                return {"status": "ERROR", "message": "Target amount must be positive."}
            
            if annual_return_rate < 0:
                return {"status": "ERROR", "message": "Annual return rate cannot be negative."}
            
            if current_corpus < 0:
                return {"status": "ERROR", "message": "Current corpus cannot be negative."}
            
            # Check if goal is already achieved
            if current_corpus >= target_amount:
                return {"status": "SUCCESS", "months_needed": 0}
            
            # Convert annual rate to monthly rate
            monthly_rate = annual_return_rate / 12
            
            if monthly_rate == 0:
                months_needed = (target_amount - current_corpus) / monthly_investment
            else:
                numerator = target_amount * monthly_rate + monthly_investment
                denominator = current_corpus * monthly_rate + monthly_investment
                
                if denominator <= 0:
                    return {"status": "ERROR", "message": "Mathematical error in calculation."}
                
                try:
                    months_needed = math.log(numerator / denominator) / math.log(1 + monthly_rate)
                except (ValueError, ZeroDivisionError):
                    return {"status": "ERROR", "message": "Mathematical error in calculation."}
            
            if months_needed <= 0:
                return {"status": "ERROR", "message": "Invalid calculation result."}
            
            return {"status": "SUCCESS", "months_needed": months_needed}
            
        except Exception as e:
            return {"status": "ERROR", "message": f"Error in calculation: {str(e)}"}


    def calculate_goal_impact_with_contribution_change(
        self,
        contribution_percentage_change: float,
        gender: str,
        time_period_months: int,
        annual_return_rate: float
    ) -> str:
        """
        Analyzes the impact of income changes on existing financial goals timeline.
        
        Use this tool when users ask questions like:
        - "What if my wife gets a 15% increment, how does it affect our goals?"
        - "If my husband's salary increases by 20%, how much faster can we achieve our targets?"
        - "What happens to our timeline if one of us gets a bonus/promotion?"
        - "How do our goals change if income decreases due to job change?"
        
        This tool calculates how changes in monthly contributions affect the timeline 
        to achieve all existing financial goals.
        
        Args:
            contribution_percentage_change (float): The percentage change in contribution 
                (e.g., 0.15 for 15% increase, -0.10 for 10% decrease)
            gender (str): Whose contribution is changing - "male" or "female"
            time_period_months (Optional[int]): Duration of the change in months. 
                Use None for permanent changes (default: None)
            annual_return_rate (float): Expected annual return rate for calculations (default: 12%)
        
        Returns:
            str: Detailed analysis showing:
                - Original timeline for each goal
                - New timeline after the contribution change
                - Time saved or added for each goal
                - Whether the change is permanent or temporary
        
        Example Usage:
            - For "Wife gets 15% increment": contribution_percentage_change=0.15, gender="female"
            - For "Husband takes 6-month unpaid leave": contribution_percentage_change=-1.0, gender="male", time_period_months=6
        """
        
        if gender.lower() not in ["male", "female"]:
            return "Error: Gender must be 'male' or 'female'"
        
        results = []
        monthly_rate = annual_return_rate / 12
        
        for goal in self.goals:
            goal_name = goal.get("name", "Unnamed Goal")
            target_amount = goal.get("target_amount", 0)
            current_corpus = goal.get("current_corpus", 0)
            male_contribution = goal.get("male_monthly_contribution", 0)
            female_contribution = goal.get("female_monthly_contribution", 0)
            total_contribution = goal.get("total_monthly_contribution", male_contribution + female_contribution)
            
            # Calculate original timeline
            original_result = self.get_num_of_months_to_reach_goal(
                total_contribution, target_amount, annual_return_rate, current_corpus
            )
            
            if original_result["status"] != "SUCCESS":
                results.append(f"{goal_name}: Error in original calculation - {original_result['message']}")
                continue
                
            original_months = original_result["months_needed"]
            
            # Calculate new timeline with changes
            if time_period_months is None:
                # Permanent change
                if gender.lower() == "male":
                    new_male_contribution = male_contribution * (1 + contribution_percentage_change)
                    new_total_contribution = new_male_contribution + female_contribution
                else:
                    new_female_contribution = female_contribution * (1 + contribution_percentage_change)
                    new_total_contribution = male_contribution + new_female_contribution
                
                new_result = self.get_num_of_months_to_reach_goal(
                    new_total_contribution, target_amount, annual_return_rate, current_corpus
                )
                
                if new_result["status"] != "SUCCESS":
                    results.append(f"{goal_name}: Error in new calculation - {new_result['message']}")
                    continue
                    
                new_months = new_result["months_needed"]
                
            else:
                # Temporary change
                if gender.lower() == "male":
                    temp_male_contribution = male_contribution * (1 + contribution_percentage_change)
                    temp_total_contribution = temp_male_contribution + female_contribution
                else:
                    temp_female_contribution = female_contribution * (1 + contribution_percentage_change)
                    temp_total_contribution = male_contribution + temp_female_contribution
                
                # Phase 1: Calculate corpus growth during temporary period
                if temp_total_contribution <= 0:
                    # If total contribution becomes 0 or negative, only corpus grows
                    corpus_after_temp_period = current_corpus * ((1 + monthly_rate) ** time_period_months)
                    additional_invested_temp = 0
                else:
                    # Corpus grows and contributions are added
                    corpus_after_temp_period = current_corpus * ((1 + monthly_rate) ** time_period_months)
                    if monthly_rate > 0:
                        additional_invested_temp = temp_total_contribution * (((1 + monthly_rate) ** time_period_months - 1) / monthly_rate)
                        corpus_after_temp_period += additional_invested_temp
                    else:
                        corpus_after_temp_period += temp_total_contribution * time_period_months
                
                # Check if goal is achieved during temporary period
                if corpus_after_temp_period >= target_amount:
                    new_months = time_period_months
                else:
                    # Phase 2: Calculate remaining time with normal contributions
                    remaining_target = target_amount
                    remaining_result = self.get_num_of_months_to_reach_goal(
                        total_contribution, remaining_target, annual_return_rate, corpus_after_temp_period
                    )
                    
                    if remaining_result["status"] != "SUCCESS":
                        results.append(f"{goal_name}: Error in remaining calculation - {remaining_result['message']}")
                        continue
                        
                    new_months = time_period_months + remaining_result["months_needed"]
            
            # Format the result
            difference = original_months - new_months
            original_years = int(original_months // 12)
            original_remaining = int(original_months % 12)
            new_years = int(new_months // 12)
            new_remaining = int(new_months % 12)
            
            original_time_str = f"{original_years} years {original_remaining} months" if original_years > 0 else f"{original_remaining} months"
            new_time_str = f"{new_years} years {new_remaining} months" if new_years > 0 else f"{new_remaining} months"
            
            # More precise difference calculation
            if abs(difference) < 0.1:  # Less than 0.1 month difference
                impact_str = "no significant change"
            elif difference > 0:
                if difference >= 1:
                    diff_months = int(round(difference))
                    impact_str = f"{diff_months} months faster"
                else:
                    impact_str = f"{difference:.1f} months faster"
            else:
                if abs(difference) >= 1:
                    diff_months = int(round(abs(difference)))
                    impact_str = f"{diff_months} months slower"
                else:
                    impact_str = f"{abs(difference):.1f} months slower"
            
            results.append(f"{goal_name}: Previously {original_time_str}, now {new_time_str} ({impact_str})")
        
        # Create summary
        change_type = "permanent" if time_period_months is None else f"{time_period_months}-month temporary"
        change_desc = f"{contribution_percentage_change*100:+.0f}%" if contribution_percentage_change != 0 else "0%"
        
        summary = f"Impact of {change_desc} change in {gender} contribution ({change_type}):\n\n"
        summary += "\n".join(results)
        
        return summary

            
    def get_all_goals(self) -> Dict[str, Any]:
        """
        Retrieves all existing financial goals with comprehensive details.
        
        Use this tool when users want to:
        - See their current financial goals and progress
        - Review existing investment plans
        - Check goal status before creating new goals
        - Understand their current financial commitments
        
        This tool provides complete information about all goals including both
        the default goals (Wealth Creation and Retirement) and any custom goals
        created by the users.
        
        Returns:
            Dict[str, Any]: Complete list of all financial goals containing:
                - Goal name and target amount
                - Current corpus and monthly contributions by each partner
                - Asset allocation details for both partners
                - Pledge status (whether goal is actively being funded)
                - Investment timeline and expected returns
        
        Each goal includes:
            - name: Goal description (e.g., "Emergency Fund", "House Down Payment")
            - target_amount: Target amount to achieve
            - current_corpus: Current savings towards this goal
            - male_monthly_contribution: Male partner's monthly investment
            - female_monthly_contribution: Female partner's monthly investment
            - male_assets: Specific investments/funds for male partner
            - female_assets: Specific investments/funds for female partner
            - pledged: Whether this goal is actively being funded
        """
        return self.goals
    
    def get_expected_cagr(self,asset_class: str, asset_subtype: str) -> Optional[float]:
        """
        Get expected CAGR for a given asset class and subtype from the ASSETS list.
        
        Args:
            asset_class: Asset class (e.g., "Mutual Fund", "Fixed Deposit")
            asset_subtype: Asset subtype (e.g., "Large Cap", "Mid Cap", "N/A")
            
        Returns:
            Expected CAGR as decimal (e.g., 12.9 for 12.9%) or None if not found
        """
        for asset in self.ASSETS:
            if (asset["asset_class"] == asset_class and 
                asset["asset_subtype"] == asset_subtype):
                return asset["expected_cagr"]
        return None


    def calculate_weighted_portfolio_return(self,asset_ladder: List) -> Dict[str, Any]:
        """
        Calculate weighted average return for the portfolio based on asset allocation.
        
        Args:
            asset_ladder: List of [asset_class, asset_subtype, allocation_percentage]
            
        Returns:
            Dictionary with portfolio return details
        """
        total_allocation = 0
        weighted_return = 0
        allocation_details = []
        
        for allocation in asset_ladder:
            if len(allocation) != 3:
                return {
                    "status": "ERROR",
                    "message": f"Invalid allocation format: {allocation}. Expected [asset_class, asset_subtype, percentage]"
                }
            
            asset_class, asset_subtype, percentage = allocation
            
            # Validate allocation percentage
            if not (0 <= percentage <= 1):
                return {
                    "status": "ERROR",
                    "message": f"Allocation percentage must be between 0 and 1, got {percentage}"
                }
            
            # Get expected CAGR for this asset
            expected_cagr = self.get_expected_cagr(asset_class, asset_subtype)
            if expected_cagr is None:
                return {
                    "status": "ERROR",
                    "message": f"Asset not found: {asset_class} - {asset_subtype}"
                }
            
            # Calculate weighted contribution
            weighted_contribution = percentage * expected_cagr
            weighted_return += weighted_contribution
            total_allocation += percentage
            
            allocation_details.append({
                "asset_class": asset_class,
                "asset_subtype": asset_subtype,
                "allocation_percentage": percentage * 100,  # Convert to percentage for display
                "expected_cagr": expected_cagr,
                "weighted_contribution": weighted_contribution
            })
        
        # Validate total allocation
        if abs(total_allocation - 1.0) > 0.001:  # Allow small floating point errors
            return {
                "status": "ERROR",
                "message": f"Total allocation must equal 100%, got {total_allocation * 100:.1f}%"
            }
        
        return {
            "status": "SUCCESS",
            "portfolio_expected_cagr": weighted_return,
            "total_allocation": total_allocation * 100,
            "allocation_details": allocation_details
        }


    def calculate_months_to_reach_goal_with_asset_ladder(
        self,
        goal_name: str,
        asset_ladder: List[list[str,str,int]],
        target_amount: float,
    ) -> Dict[str, Any]:
        """
        Calculates timeline to achieve a financial goal using specific asset allocation strategy.
        
        This is the PRIMARY tool for goal planning and should be used in this sequence:
        
        1. FIRST CALL: Always start with the safest option to show conservative timeline:
           asset_ladder = [["Savings Account", "N/A", 1.0]]
           This shows how long it would take with just savings (3.5% returns)
        
        2. SECOND CALL: If user wants faster achievement, suggest aggressive allocation:
           asset_ladder = [["Mutual Fund", "Large Cap", 0.7], ["Mutual Fund", "Small Cap", 0.3]]
           This shows reduced timeline with mixed equity exposure
        
        3. GOAL CREATION: Once user approves the timeline and allocation, use create_goal()
        
        Available Asset Classes and Subtypes (use exactly as shown):
        - ["Mutual Fund", "Small Cap"] - 18.5% CAGR, High Risk
        - ["Mutual Fund", "Mid Cap"] - 15.2% CAGR, Medium-High Risk  
        - ["Mutual Fund", "Large Cap"] - 12.9% CAGR, Medium Risk
        - ["ETF", "N/A"] - 12.5% CAGR, Medium Risk
        - ["Fixed Deposit", "N/A"] - 7.0% CAGR, Low Risk
        - ["Savings Account", "N/A"] - 3.5% CAGR, Lowest Risk
        
        Args:
            goal_name (str): Name/description of the financial goal (e.g., "Emergency Fund", "Vacation Fund")
            asset_ladder (List[List]): Asset allocation as list of [asset_class, asset_subtype, percentage]
                Example: [["Mutual Fund", "Large Cap", 0.6], ["Mutual Fund", "Small Cap", 0.4]]
                Note: Percentages must sum to 1.0
            target_amount (float): Target amount for the goal (e.g., 500000 for ₹5 lakhs)
        
        Returns:
            Dict[str, Any]: Comprehensive analysis including:
                - Timeline in months and years
                - Total investment required vs returns generated
                - Portfolio expected CAGR
                - Monthly contribution breakdown by partner
                - Detailed asset allocation with individual returns
                - Formatted currency displays
        
        Example Usage:
            # Start with safe option
            calculate_months_to_reach_goal_with_asset_ladder(
                "Emergency Fund", 
                [["Savings Account", "N/A", 1.0]], 
                500000
            )
            
            # Then show faster option
            calculate_months_to_reach_goal_with_asset_ladder(
                "Emergency Fund", 
                [["Mutual Fund", "Large Cap", 0.7], ["Mutual Fund", "Small Cap", 0.3]], 
                500000
            )
        """
        try:
            starting_corpus = 0
            # Validate inputs
            if target_amount <= 0:
                return {"status": "ERROR", "message": "Target amount must be positive."}
            
            if(self.male_monthly_contribution == 0 and self.female_monthly_contribution == 0):
                print('HERE Bro')
                no_of_pledged,pledged_male_contribution,pledged_female_contribution = 0,0,0
                for goal in self.goals:
                    male_contribution, female_contribution = goal['male_monthly_contribution'], goal['female_monthly_contribution']
                    if(goal['pledged']):
                        no_of_pledged = no_of_pledged + 1
                        pledged_male_contribution = male_contribution + pledged_male_contribution
                        pledged_female_contribution = female_contribution + pledged_female_contribution

                if(no_of_pledged == 0):
                    return {"status": "ERROR", "message": "You don't have any amount to invest"}
            
                no_of_pledged+=1

                for i,goal in enumerate(self.goals):
                    if(goal['pledged']):
                        self.goals[i]['male_monthly_contribution'] /= no_of_pledged
                        self.goals[i]['female_monthly_contribution'] /= no_of_pledged
                        self.goals[i]['total_monthly_contribution'] /= no_of_pledged

                        for j,asset in enumerate(goal['male_assets']):
                            self.goals[i]['male_assets'][j]['amount'] /= no_of_pledged
                        
                        for j,asset in enumerate(goal['female_assets']):
                            self.goals[i]['female_assets'][j]['amount'] /= no_of_pledged

                self.male_monthly_contribution = pledged_male_contribution/no_of_pledged
                self.female_monthly_contribution = pledged_female_contribution/no_of_pledged

            total_monthly_contribution = self.male_monthly_contribution + self.female_monthly_contribution
            
            if total_monthly_contribution <= 0:
                return {"status": "ERROR", "message": "Total monthly contribution must be positive."}
            
            if starting_corpus < 0:
                return {"status": "ERROR", "message": "Starting corpus cannot be negative."}
            
            # Check if goal is already achieved
            if starting_corpus >= target_amount:
                return {
                    "status": "SUCCESS",
                    "goal_already_achieved": True,
                    "months_needed": 0,
                    "years": 0,
                    "remaining_months": 0,
                    "message": "Goal already achieved with starting corpus!"
                }
            
            # Calculate portfolio weighted return
            portfolio_result = self.calculate_weighted_portfolio_return(asset_ladder)
            if portfolio_result["status"] != "SUCCESS":
                return portfolio_result
            
            portfolio_cagr = portfolio_result["portfolio_expected_cagr"]
            annual_return_rate = portfolio_cagr / 100  # Convert percentage to decimal
            monthly_rate = annual_return_rate / 12
            
            # Calculate months needed using compound interest formula
            if monthly_rate == 0:
                # Simple case: no returns, just savings
                months_needed = (target_amount - starting_corpus) / total_monthly_contribution
            else:
                # Compound interest formula: FV = PV(1+r)^n + PMT × (((1 + r)^n - 1) / r)
                # Solving for n: n = log((FV × r + PMT) / (PV × r + PMT)) / log(1 + r)
                numerator = target_amount * monthly_rate + total_monthly_contribution
                denominator = starting_corpus * monthly_rate + total_monthly_contribution
                
                if denominator <= 0:
                    return {"status": "ERROR", "message": "Mathematical error in calculation."}
                
                try:
                    months_needed = math.log(numerator / denominator) / math.log(1 + monthly_rate)
                except (ValueError, ZeroDivisionError):
                    return {"status": "ERROR", "message": "Mathematical error in calculation."}
            
            if months_needed <= 0:
                return {"status": "ERROR", "message": "Invalid calculation result."}
            
            # Calculate additional details
            total_invested = starting_corpus + (total_monthly_contribution * months_needed)
            total_returns = target_amount - total_invested
            
            # Convert to years and months
            years = int(months_needed // 12)
            remaining_months = int(months_needed % 12)
            
            self.final_discussion = {
                'name' : goal_name,
                'male_monthly_contribution': self.male_monthly_contribution,
                'female_monthly_contribution': self.female_monthly_contribution,
                'asset_ladder': asset_ladder
            }

            return {
                "status": "SUCCESS",
                "goal_already_achieved": False,
                "months_needed": round(months_needed, 1),
                "years": years,
                "remaining_months": remaining_months,
                "time_description": f"{years} years and {remaining_months} months" if years > 0 else f"{remaining_months} months",
                
                # Investment details
                "target_amount": target_amount,
                "starting_corpus": starting_corpus,
                "male_monthly_contribution": self.male_monthly_contribution,
                "female_monthly_contribution": self.female_monthly_contribution,
                "total_monthly_contribution": total_monthly_contribution,
                "total_invested": total_invested,
                "total_returns": total_returns,
                
                # Portfolio details
                "portfolio_expected_cagr": portfolio_cagr,
                "annual_return_rate": annual_return_rate,
                "monthly_return_rate": monthly_rate,
                "allocation_details": portfolio_result["allocation_details"],
                
                # Formatted values
                "formatted_target": f"₹{target_amount:,.0f}",
                "formatted_starting_corpus": f"₹{starting_corpus:,.0f}",
                "formatted_total_invested": f"₹{total_invested:,.0f}",
                "formatted_total_returns": f"₹{total_returns:,.0f}",
                "formatted_monthly_contribution": f"₹{total_monthly_contribution:,.0f}",
                "portfolio_cagr_display": f"{portfolio_cagr:.2f}%"
            }
            
        except Exception as e:
            return {"status": "ERROR", "message": f"Error in calculation: {str(e)}"}

# Import for ADK Agent factory function
from google.adk.agents import Agent


def create_goal_investment_strategy_adk_agent(user1_phone: str, user2_phone: str, model: str) -> Agent:
    """
    Factory function to create the Goal & Investment Strategy ADK Agent.
    
    Args:
        user1_phone: Phone number for User 1 (Male)
        user2_phone: Phone number for User 2 (Female)
        model: AI model to use for the agent
        
    Returns:
        Agent: Configured ADK agent for goal and investment strategy
    """

    # Create the agent instance
    goal_agent_instance = GoalInvestmentStrategyAgent(user1_phone, user2_phone)
    
    # Define tools for the agent
    goal_strategy_tools = [
        goal_agent_instance.create_goal,
        goal_agent_instance.calculate_goal_impact_with_contribution_change,
        goal_agent_instance.get_all_goals,
        goal_agent_instance.calculate_months_to_reach_goal_with_asset_ladder,
    ]
    
    agent_description = f"""
You are a Goal & Investment Strategy Agent for a couple - Rohan (male) and Priya (female). Your expertise lies in helping them create, track, and optimize their financial goals through strategic asset allocation.

## Your Core Responsibilities:
1. **Goal Creation & Planning**: Help users define clear financial targets with realistic timelines
2. **Asset Allocation Strategy**: Recommend optimal investment mix based on risk tolerance and timeline
3. **Impact Analysis**: Analyze how income changes affect existing goals
4. **Portfolio Optimization**: Balance safety vs growth based on user preferences

## Available Asset Classes & Expected Returns:
{chr(10).join([f"- {asset['asset_class']} ({asset['asset_subtype']}): {asset['expected_cagr']}% CAGR, Risk Level {asset['risk_rating']}" for asset in goal_agent_instance.ASSETS])}

## Tool Usage Workflow:

### For New Goal Creation:
1. **ALWAYS START SAFE**: First call `calculate_months_to_reach_goal_with_asset_ladder` with:
   - asset_ladder = [["Savings Account", "N/A", 1.0]]
   - This shows conservative timeline (3.5% returns)

2. **OFFER FASTER OPTIONS**: If user wants quicker achievement, suggest:
   - Mixed allocation like [["Mutual Fund", "Large Cap", 0.7], ["Mutual Fund", "Small Cap", 0.3]]
   - Show reduced timeline with higher returns but more risk

3. **FINALIZE GOAL**: Once user approves timeline and allocation, call `create_goal(target_amount)`

### For Impact Analysis:
Use `calculate_goal_impact_with_contribution_change` for questions like:
- "What if my wife gets 15% increment?" → (0.15, "female")
- "If my husband's salary decreases by 10%?" → (-0.10, "male")
- "What if bonus for 6 months?" → (0.20, "male", 6)

### For Goal Review:
Use `get_all_goals()` when users want to see current goals and progress.

## Communication Style:
- Be encouraging and realistic about financial goals
- Explain risk-return tradeoffs clearly
- Use specific fund names from their existing portfolios when possible
- Always present options from conservative to aggressive
- Celebrate existing investments and suggest optimizations

Remember: Always start with safe options, then progressively show how aggressive allocations can accelerate goal achievement. Your job is to guide them to make informed decisions about their financial future.
"""
    
    return Agent(
        name="Goal_Investment_Strategy_Agent",
        model=model,
        instruction=agent_description,
        description = "Provides personalized goal-based investment and savings strategies for couples, based on asset types, expected returns, and timelines.",
        tools=goal_strategy_tools,
    )