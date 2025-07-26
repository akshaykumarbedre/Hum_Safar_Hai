# FI Money User Data Documentation

## Overview

This document provides a comprehensive analysis of the FI Money financial data structure accessible via the `get_complete_profile` function. The data represents complete financial profiles for various user personas, including assets, liabilities, transactions, and credit information.

## Data Structure Overview

The complete user profile consists of 6 main data categories:

1. **Net Worth** (`net_worth`): Asset and liability breakdown with valuations
2. **Bank Transactions** (`bank_transactions`): Banking transaction history
3. **Mutual Fund Transactions** (`mutual_fund_transactions`): MF investment records
4. **Stock Transactions** (`stock_transactions`): Equity trading history
5. **EPF Details** (`epf_details`): Employee Provident Fund information
6. **Credit Report** (`credit_report`): Credit score and account details

## 1. Net Worth Data (`fetch_net_worth.json`)

### Structure
```json
{
  "netWorthResponse": { ... },
  "mfSchemeAnalytics": { ... },
  "accountDetailsBulkResponse": { ... }
}
```

### 1.1 Net Worth Response

#### Asset Values
- **Field**: `netWorthResponse.assetValues[]`
- **Description**: Array of different asset types and their values

**Asset Types (`netWorthAttribute`)**:
- `ASSET_TYPE_MUTUAL_FUND`: Mutual fund investments
- `ASSET_TYPE_EPF`: Employee Provident Fund balance
- `ASSET_TYPE_INDIAN_SECURITIES`: Indian stock investments
- `ASSET_TYPE_SAVINGS_ACCOUNTS`: Bank savings account balances
- `ASSET_TYPE_US_SECURITIES`: US stock investments
- `ASSET_TYPE_FIXED_DEPOSITS`: Fixed deposit investments
- `ASSET_TYPE_REAL_ESTATE`: Real estate valuations
- `ASSET_TYPE_GOLD`: Gold investments

**Value Structure**:
```json
{
  "currencyCode": "INR",  // Always "INR"
  "units": "amount"       // String representation of amount
}
```

#### Liability Values
- **Field**: `netWorthResponse.liabilityValues[]`
- **Description**: Array of different liability types and amounts owed

**Liability Types (`netWorthAttribute`)**:
- `LIABILITY_TYPE_VEHICLE_LOAN`: Vehicle loan outstanding
- `LIABILITY_TYPE_HOME_LOAN`: Home loan outstanding
- `LIABILITY_TYPE_OTHER_LOAN`: Other loans (personal, education, etc.)
- `LIABILITY_TYPE_CREDIT_CARD`: Credit card outstanding
- `LIABILITY_TYPE_PERSONAL_LOAN`: Personal loan outstanding

#### Total Net Worth
- **Field**: `netWorthResponse.totalNetWorthValue`
- **Description**: Total net worth calculation (assets - liabilities)
- **Structure**: Same as value structure above

### 1.2 Mutual Fund Scheme Analytics

#### Scheme Details
- **Field**: `mfSchemeAnalytics.schemeAnalytics[]`
- **Description**: Detailed analytics for each mutual fund scheme

**Scheme Detail Fields**:
- `amc`: Asset Management Company (e.g., "CANARA_ROBECO", "ICICI_PRUDENTIAL")
- `nameData.longName`: Full scheme name
- `planType`: "DIRECT" or "REGULAR"
- `investmentType`: "OPEN" (open-ended funds)
- `optionType`: "GROWTH" or "DIVIDEND"
- `divReinvOptionType`: "REINVESTMENT_ONY" (for dividend schemes)
- `assetClass`: "EQUITY", "DEBT", "HYBRID", "CASH"
- `isinNumber`: ISIN identifier
- `categoryName`: Fund category (e.g., "GOVERNMENT_BOND", "INDEX_FUNDS")
- `fundhouseDefinedRiskLevel`: "LOW_RISK", "MODERATE_RISK", "HIGH_RISK", "VERY_HIGH_RISK"

**NAV Structure**:
```json
{
  "currencyCode": "INR",
  "units": "whole_number",
  "nanos": nanoseconds_component  // For precision
}
```

**Analytics Fields**:
- `currentValue`: Current investment value
- `investedValue`: Total amount invested
- `XIRR`: Extended Internal Rate of Return (percentage)
- `absoluteReturns`: Absolute gain/loss amount
- `unrealisedReturns`: Unrealized gains/losses
- `navValue`: Current NAV
- `units`: Number of units held

### 1.3 Account Details Bulk Response

#### Account Types
The system supports multiple account types identified by `accInstrumentType`:

1. **`ACC_INSTRUMENT_TYPE_DEPOSIT`**: Bank accounts
2. **`ACC_INSTRUMENT_TYPE_EQUITIES`**: Equity/stock accounts
3. **`ACC_INSTRUMENT_TYPE_ETF`**: ETF holdings
4. **`ACC_INSTRUMENT_TYPE_REIT`**: REIT investments
5. **`ACC_INSTRUMENT_TYPE_INVIT`**: InvIT investments
6. **`ACC_INSTRUMENT_TYPE_RECURRING_DEPOSIT`**: Recurring deposits

#### Deposit Accounts
**Account Type Values**:
- `DEPOSIT_ACCOUNT_TYPE_SAVINGS`: Savings accounts
- `DEPOSIT_ACCOUNT_TYPE_CURRENT`: Current accounts

**Status Values**:
- `DEPOSIT_ACCOUNT_STATUS_ACTIVE`: Active account

**Fields**:
- `currentBalance`: Current account balance
- `balanceDate`: Balance as of date (ISO 8601)
- `branch`: Branch name
- `ifscCode`: IFSC code
- `micrCode`: MICR code
- `openingDate`: Account opening date

#### Equity Accounts
**Holdings Structure**:
```json
{
  "isin": "stock_isin_code",
  "issuerName": "company_name",
  "type": "EQUITY_HOLDING_TYPE_DEMAT",
  "units": number_of_shares,
  "lastTradedPrice": {
    "currencyCode": "INR",
    "units": "price_whole",
    "nanos": price_fractional
  },
  "isinDescription": "stock_description"
}
```

#### ETF Accounts
**Holdings Structure**:
```json
{
  "isin": "etf_isin_code",
  "units": number_of_units,
  "nav": nav_structure,
  "lastNavDate": "date_iso8601",
  "isinDescription": "etf_description"
}
```

#### REIT/InvIT Accounts
**Holdings Structure**:
```json
{
  "isin": "reit_isin_code",
  "totalNumberUnits": number_of_units,
  "isinDescription": "reit_description",
  "nominee": "NOMINEE_TYPE_REGISTERED",
  "lastClosingRate": price_structure
}
```

## 2. Bank Transactions (`fetch_bank_transactions.json`)

### Structure
```json
{
  "schemaDescription": "transaction_schema_explanation",
  "bankTransactions": [
    {
      "bank": "bank_name",
      "txns": [ ... ]
    }
  ]
}
```

### Transaction Schema
Each transaction is an array with the following structure:
```
[transactionAmount, transactionNarration, transactionDate, transactionType, transactionMode, currentBalance]
```

**Transaction Types**:
1. `CREDIT`: Money credited to account
2. `DEBIT`: Money debited from account
3. `OPENING`: Opening balance
4. `INTEREST`: Interest credited
5. `TDS`: Tax deducted at source
6. `INSTALLMENT`: EMI or installment payment
7. `CLOSING`: Closing balance
8. `OTHERS`: Other transaction types

**Transaction Modes**:
- `UPI`: UPI transactions
- `CARD_PAYMENT`: Card payments
- `FT`: Fund transfer
- `CASH`: Cash transactions
- `ATM`: ATM transactions
- `OTHERS`: Other modes

**Bank Names**: Various banks like "HDFC Bank", "ICICI Bank", "SBI", etc.

## 3. Mutual Fund Transactions (`fetch_mf_transactions.json`)

### Structure
```json
{
  "mfTransactions": [
    {
      "isin": "fund_isin",
      "schemeName": "fund_name",
      "folioId": "folio_number",
      "txns": [ ... ]
    }
  ],
  "schemaDescription": "transaction_schema_explanation"
}
```

### Transaction Schema
Each transaction is an array:
```
[orderType, transactionDate, purchasePrice, purchaseUnits, transactionAmount]
```

**Order Types**:
1. `BUY`: Purchase transaction
2. `SELL`: Redemption transaction

**Fields**:
- `orderType`: 1 for BUY, 2 for SELL
- `transactionDate`: Date in YYYY-MM-DD format
- `purchasePrice`: NAV at transaction
- `purchaseUnits`: Number of units
- `transactionAmount`: Transaction value

## 4. Stock Transactions (`fetch_stock_transactions.json`)

### Structure
```json
{
  "schemaDescription": "transaction_schema_explanation",
  "stockTransactions": [
    {
      "isin": "stock_isin",
      "txns": [ ... ]
    }
  ]
}
```

### Transaction Schema
Each transaction is an array:
```
[transactionType, transactionDate, quantity, navValue?]
```

**Transaction Types**:
1. `BUY`: Purchase of stocks
2. `SELL`: Sale of stocks
3. `BONUS`: Bonus shares
4. `SPLIT`: Stock split

**Fields**:
- `transactionType`: 1-4 as above
- `transactionDate`: Date in YYYY-MM-DD format
- `quantity`: Number of shares
- `navValue`: Price per share (optional)

## 5. EPF Details (`fetch_epf_details.json`)

### Structure
```json
{
  "uanAccounts": [
    {
      "phoneNumber": { },
      "rawDetails": {
        "est_details": [ ... ],
        "overall_pf_balance": { ... }
      }
    }
  ]
}
```

### Establishment Details
**Fields per establishment**:
- `est_name`: Employer name
- `member_id`: EPF member ID (masked)
- `office`: EPF office handling the account
- `doj_epf`: Date of joining EPF (DD-MM-YYYY)
- `doe_epf`: Date of exit from EPF (DD-MM-YYYY)
- `doe_eps`: Date of exit from EPS (DD-MM-YYYY)

### PF Balance Structure
```json
{
  "net_balance": "total_balance",
  "employee_share": {
    "credit": "employee_contribution",
    "balance": "employee_balance"
  },
  "employer_share": {
    "credit": "employer_contribution",
    "balance": "employer_balance"
  }
}
```

### Overall PF Balance
- `pension_balance`: EPS pension balance
- `current_pf_balance`: Current total PF balance
- `employee_share_total`: Total employee contributions

## 6. Credit Report (`fetch_credit_report.json`)

### Structure
```json
{
  "creditReports": [
    {
      "creditReportData": {
        "userMessage": { ... },
        "creditProfileHeader": { ... },
        "currentApplication": { ... },
        "creditAccount": { ... },
        "score": { ... },
        "caps": { ... }
      },
      "vendor": "EXPERIAN"
    }
  ]
}
```

### Credit Profile Header
- `reportDate`: Report generation date (YYYYMMDD)
- `reportTime`: Report generation time (HHMMSS)

### Credit Account Summary
**Account Counts**:
- `creditAccountTotal`: Total credit accounts
- `creditAccountActive`: Active accounts
- `creditAccountDefault`: Defaulted accounts
- `creditAccountClosed`: Closed accounts

**Outstanding Balance**:
- `outstandingBalanceSecured`: Secured loan outstanding
- `outstandingBalanceUnSecured`: Unsecured loan outstanding
- `outstandingBalanceAll`: Total outstanding

### Credit Account Details
**Account Types**:
- `01`: Credit Card
- `03`: Home Loan
- `04`: Personal Loan
- `06`: Gold Loan
- `10`: Credit Line
- `53`: Consumer Loan

**Account Status Codes**:
- `11`: Active
- `71`: Closed
- `78`: Written Off
- `82`: Settled
- `83`: Active with dues

**Payment Ratings**:
- `0`: Current (no dues)
- `1`: 1-30 days overdue
- `2`: 31-60 days overdue
- `3`: 61-90 days overdue
- `4`: 91-120 days overdue
- `5`: 120+ days overdue

### Credit Score
- `bureauScore`: Credit score (300-900 range)
- `bureauScoreConfidenceLevel`: "H" (High), "M" (Medium), "L" (Low)

### CAPS (Credit Application Processing Service)
**Enquiry Reasons**:
- `1`: Auto Loan
- `2`: Personal Loan
- `6`: Credit Card
- `8`: Home Loan
- `10`: Consumer Loan

## Data Relationships and Dependencies

### Net Worth Calculation
Total Net Worth = Sum of all asset values - Sum of all liability values

### MF Analytics Dependencies
- Current value depends on NAV and units held
- XIRR calculation requires investment dates and amounts
- Returns calculation: Current Value - Invested Value

### Transaction Dependencies
- Bank balance updates with each transaction
- MF units accumulate/reduce with each transaction
- Stock quantities change with buy/sell/bonus/split events

### EPF Balance Calculation
Net Balance = Employee Share + Employer Share + Interest

### Credit Score Factors
- Payment history (most important)
- Outstanding balances
- Account types and mix
- Recent credit inquiries
- Account age

## Business Logic and Validation Rules

### Amount Validations
- All monetary values are in INR
- Negative values for liabilities are represented as negative strings
- Zero balances may be omitted from arrays

### Date Formats
- Bank transactions: "YYYY-MM-DD"
- EPF: "DD-MM-YYYY"
- Credit report: "YYYYMMDD"

### ISIN Code Format
- Mutual Funds: Start with "INF"
- Stocks: Start with "INE"
- ETFs: Start with "INF"

### Account Status Logic
- Active accounts contribute to net worth
- Closed accounts may show zero balances
- Defaulted accounts show in credit report

## Error Handling and Edge Cases

### Missing Data
- Empty arrays for users with no transactions
- Null/empty objects for unavailable data categories
- Default values: 0 for balances, empty arrays for transactions

### Data Consistency
- Net worth totals should match sum of individual assets/liabilities
- Transaction dates should be chronological
- Account balances should reflect transaction history

### Validation Constraints
- Credit scores: 300-900 range
- Interest rates: 0-100% range
- Dates: Valid date formats and logical sequences
- ISINs: Valid format and check digits

This documentation provides the foundation for implementing granular accessor functions for every data point in the FI Money user profile system.