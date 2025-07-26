# FI-MCP: Financial Intelligence - Model Context Protocol Data

## Overview

The FI-MCP module provides comprehensive dummy financial data designed for AI agent training and testing. It contains detailed financial profiles for 25 different user personas, each representing distinct financial behaviors and situations commonly found in real-world scenarios.

## 🎯 Purpose

This module is designed to:
- Enable AI agents to understand diverse financial profiles
- Provide realistic test data for financial analysis and planning
- Support MCP (Model Context Protocol) integration for structured data access
- Facilitate development of personalized financial advisory systems

## 📊 Data Structure

Each user persona is identified by a unique phone number and contains the following data types:

### Data Categories

1. **📊 Net Worth Data** (`fetch_net_worth.json`)
   - Total asset valuation
   - Asset breakdown by category
   - Account details and balances

2. **🏦 Bank Transactions** (`fetch_bank_transactions.json`)
   - Transaction history across multiple bank accounts
   - Credit/debit transaction details
   - Account balance information

3. **📈 Mutual Fund Transactions** (`fetch_mf_transactions.json`)
   - MF investment portfolio
   - SIP and lumpsum transactions
   - Fund performance data

4. **📊 Stock Transactions** (`fetch_stock_transactions.json`)
   - Equity investment portfolio
   - Buy/sell transaction history
   - Stock holding details

5. **🏛️ EPF Details** (`fetch_epf_details.json`)
   - Employee Provident Fund balances
   - Employer-wise EPF history
   - UAN account details

6. **💳 Credit Report** (`fetch_credit_report.json`)
   - Credit score and history
   - Loan and credit card details
   - Payment behavior analysis

## 🧑‍💼 User Personas

| Phone Number | Persona Type | Description |
|--------------|--------------|-------------|
| 1111111111 | **Minimal Assets** | No assets connected. Only saving account balance present |
| 2222222222 | **Wealthy Investor** | All assets connected. Large mutual fund portfolio with 9 funds |
| 3333333333 | **Moderate Investor** | All assets connected. Small mutual fund portfolio with 1 fund |
| 4444444444 | **Multi-Bank User** | Multiple bank accounts and EPF UANs, partial transaction coverage |
| 5555555555 | **No Credit History** | All assets except credit score. Multiple bank accounts |
| 6666666666 | **Investment Only** | All assets except bank account. Large MF portfolio |
| 7777777777 | **Debt-Heavy Low Performer** | High liabilities, poor returns, low credit score |
| 8888888888 | **SIP Samurai** | Consistent SIP investments, moderate returns (8-12% XIRR) |
| 9999999999 | **Fixed Income Fanatic** | Debt MF preference, conservative growth (8-10% XIRR) |
| 1010101010 | **Precious Metal Believer** | 50% gold allocation, minimal equity exposure |
| 1212121212 | **Dormant EPF Earner** | Stagnant EPF, no private investments |
| 1313131313 | **Balanced Growth Tracker** | Well-diversified, good credit score (750+) |
| 1414141414 | **Salary Sinkhole** | 70% salary goes to EMIs, low investment |
| 1515151515 | **Ghost Portfolio** | Old investments, no recent activity |
| 1616161616 | **Early Retirement Dreamer** | Aggressive equity (80-90%), high savings rate |
| 1717171717 | **The Swinger** | High churn, short-term trading focus |
| 1818181818 | **Passive Contributor** | Joint accounts, old EPF, no active investments |
| 1919191919 | **Section 80C Strategist** | Tax-saving focus (ELSS, EPF, NPS) |
| 2020202020 | **Starter Saver** | New investor, low amounts, minimal debt |
| 2121212121 | **Dual Income Dynamo** | Freelance + salary, irregular but growing investments |
| 2222222222 | **Sudden Wealth Receiver** | Recently inherited wealth, learning to manage |
| 2323232323 | **Overseas Optimizer** | NRI managing Indian investments |
| 2424242424 | **Mattress Money Mindset** | 95% in FDs/savings, market averse |
| 2525252525 | **Live-for-Today** | High income, high spending, minimal savings |

## 🔧 Data Schema

### Net Worth Schema
```json
{
  "netWorthResponse": {
    "assetValues": [
      {
        "netWorthAttribute": "ASSET_TYPE_SAVINGS_ACCOUNTS",
        "value": {
          "currencyCode": "INR",
          "units": "186726"
        }
      }
    ],

    

}
```

### Bank Transaction Schema
```json
{
  "bankTransactions": [
    {
      "bank": "HDFC Bank",
      "txns": [
        [
          "transactionAmount",
          "transactionNarration", 
          "transactionDate",
          "transactionType", // 1:CREDIT, 2:DEBIT, 3:OPENING, 4:INTEREST, 5:TDS, 6:INSTALLMENT, 7:CLOSING, 8:OTHERS
          "transactionMode",
          "currentBalance"
        ]
      ]
    }
  ]
}
```

### Mutual Fund Transaction Schema
```json
{
  "mfTransactions": [
    {
      "isin": "INF760K01FC4",
      "schemeName": "Fund Name",
      "folioId": "55557777",
      "txns": [
        [
          "orderType", // 1:BUY, 2:SELL
          "transactionDate",
          "purchasePrice",
          "purchaseUnits",
          "transactionAmount"
        ]
      ]
    }
  ]
}
```

### Stock Transaction Schema
```json
{
  "stockTransactions": [
    {
      "isin": "INE0BWS23018",
      "txns": [
        [
          "transactionType", // 1:BUY, 2:SELL, 3:BONUS, 4:SPLIT
          "transactionDate",
          "quantity",
          "navValue" // optional
        ]
      ]
    }
  ]
}
```

### EPF Details Schema
```json
{
  "uanAccounts": [
    {
      "rawDetails": {
        "est_details": [
          {
            "est_name": "Company Name",
            "member_id": "Member ID",
            "office": "EPF Office",
            "doj_epf": "Date of Joining",
            "doe_epf": "Date of Exit",
            "pf_balance": {
              "net_balance": "Total Balance",
              "employee_share": {"credit": "Amount", "balance": "Balance"},
              "employer_share": {"credit": "Amount", "balance": "Balance"}
            }
          }
        ]
      }
    }
  ]
}
```

### Credit Report Schema
```json
{
  "creditReports": [
    {
      "creditReportData": {
        "score": {
          "bureauScore": "746",
          "bureauScoreConfidenceLevel": "H"
        },
        "creditAccount": {
          "creditAccountSummary": {
            "account": {
              "creditAccountTotal": "6",
              "creditAccountActive": "6"
            },
            "totalOutstandingBalance": {
              "outstandingBalanceAll": "75000"
            }
          },
          "creditAccountDetails": [
            {
              "subscriberName": "Bank Name",
              "accountType": "Account Type Code",
              "currentBalance": "Outstanding Amount",
              "paymentRating": "Payment Score"
            }
          ]
        }
      }
    }
  ]
}
```

## 💻 Usage with Python API

### Basic Usage

```python
from humsafar_financial_ai import FIMCPDataAccess

# Initialize data access
fi_data = FIMCPDataAccess()

# Get all available users
users = fi_data.get_available_users()
print(f"Available personas: {len(users)}")

# Get specific data for a user
net_worth = fi_data.get_net_worth("2222222222")
bank_txns = fi_data.get_bank_transactions("2222222222")
mf_txns = fi_data.get_mutual_fund_transactions("2222222222")

# Get complete profile
profile = fi_data.get_complete_profile("2222222222")

# Analyze financial health
analysis = fi_data.analyze_user_financial_health("2222222222")
print(f"Net Worth: ₹{analysis.get('total_net_worth', 0)}")
print(f"Credit Score: {analysis.get('credit_score', 'N/A')}")
```

### Convenience Functions

```python
from humsafar_financial_ai import (
    get_net_worth,
    get_bank_transactions,
    get_mutual_fund_transactions,
    get_stock_transactions,
    get_epf_details,
    get_credit_report,
    analyze_user_financial_health
)

# Direct function calls
net_worth = get_net_worth("1111111111")
credit_report = get_credit_report("7777777777") 
health_analysis = analyze_user_financial_health("1313131313")
```

### AI Agent Integration

```python
def financial_advisory_agent(user_id: str):
    """Example AI agent using FI-MCP data"""
    
    # Get complete financial profile
    profile = get_complete_profile(user_id)
    analysis = analyze_user_financial_health(user_id)
    
    # Generate insights based on data
    insights = []
    
    if analysis["credit_score"] and analysis["credit_score"] < 650:
        insights.append("🚨 Credit score needs improvement")
    
    if analysis["total_net_worth"] < 500000:
        insights.append("💰 Focus on wealth building")
    
    # Check investment patterns
    mf_data = profile.get("mutual_fund_transactions")
    if mf_data and len(mf_data.get("mfTransactions", [])) > 5:
        insights.append("📈 Diversified MF portfolio")
    
    return {
        "user_persona": analysis["persona_description"],
        "key_insights": insights,
        "data_completeness": f"{analysis['profile_completeness']:.1f}%"
    }
```

## 🎯 Use Cases

### 1. Financial Health Assessment
- Analyze net worth composition
- Evaluate investment portfolio diversification  
- Assess debt-to-income ratios
- Credit score improvement recommendations

### 2. Investment Pattern Analysis
- SIP vs lumpsum investment behavior
- Asset allocation preferences
- Risk tolerance assessment
- Return analysis (XIRR calculations)

### 3. Spending Behavior Analysis
- Transaction categorization
- Monthly expense patterns
- EMI vs discretionary spending
- Cash flow analysis

### 4. Retirement Planning
- EPF corpus evaluation
- Private investment adequacy
- Retirement readiness assessment
- Goal-based planning

### 5. Tax Optimization
- Section 80C utilization analysis
- Tax-saving investment patterns
- ELSS vs EPF vs NPS allocation
- Tax liability optimization

## 🔗 Integration with Finance Calculators

The FI-MCP data can be seamlessly integrated with the finance calculator functions:

```python
from humsafar_financial_ai import (
    get_net_worth,
    get_epf_details,
    retirement_corpus_calculator,
    net_worth_calculator
)

def comprehensive_analysis(user_id: str):
    # Get user data
    net_worth_data = get_net_worth(user_id)
    epf_data = get_epf_details(user_id)
    
    # Use calculators with real data
    assets = {"savings": 500000, "investments": 200000}
    liabilities = {"loans": 300000}
    
    net_worth_analysis = net_worth_calculator(assets, liabilities)
    retirement_plan = retirement_corpus_calculator(
        current_age=30,
        retirement_age=60,
        monthly_expenses=50000,
        inflation_rate=6.0,
        expected_return=12.0
    )
    
    return {
        "current_analysis": net_worth_analysis,
        "retirement_planning": retirement_plan
    }
```

## 📚 Best Practices

1. **Data Privacy**: This is dummy data for testing only. Never use with real user information.

2. **Error Handling**: Always check for None returns when accessing data:
   ```python
   data = get_net_worth(user_id)
   if data:
       # Process data
       pass
   else:
       # Handle missing data
       pass
   ```

3. **Performance**: Use the class-based approach for multiple operations on the same dataset:
   ```python
   fi_data = FIMCPDataAccess()
   for user in users:
       profile = fi_data.get_complete_profile(user)
   ```

4. **Validation**: Always validate data structure before processing:
   ```python
   def safe_get_credit_score(user_id):
       credit_data = get_credit_report(user_id)
       try:
           return int(credit_data["creditReports"][0]["creditReportData"]["score"]["bureauScore"])
       except (KeyError, IndexError, ValueError):
           return None
   ```

---

**Note**: This module is part of the Humsafar Financial AI Assistant and is designed for demonstration, testing, and AI agent training purposes. The data represents realistic but fictional financial scenarios.