# Humsafar - Multi-Agent Financial AI Assistant

Humsafar is a sophisticated, multi-agent financial AI assistant designed to provide users with a holistic and conversational interface to their personal financial data. Built using Python and Google's Agent Development Kit (ADK), it can answer complex questions about net worth, expenses, investments, and loans by delegating tasks to a team of specialized AI agents.

## ✨ Features

* **Multi-Agent Architecture**: A central orchestrator agent intelligently routes queries to specialist agents for Net Worth, Expenses, Investments, and Loans.
* **Conversational Interface**: Ask complex, natural language questions about your complete financial picture.
* **Comprehensive Analysis**: Get insights into spending patterns, portfolio performance, credit health, and more.
* **Modular & Extensible**: The architecture is designed to be easily maintained and extended with new tools and agent capabilities.

---

## 🏛️ Architecture

The system uses a hierarchical, orchestrated multi-agent approach. A main `Orchestrator Agent` receives the user query and delegates tasks to the appropriate specialist agent.

```
+----------------+      +---------------------------------+
|   User Query   |----->|     Financial_Orchestrator_Agent    |
+----------------+      +---------------------------------+
                            |           |           |           |
                            |           |           |           |
          +-----------------+-----------+-----------+-----------------+
          |                 |           |           |                 |
          v                 v           v           v                 v
+------------------+  +--------------+  +-----------+  +-----------------+
|  NetWorth_Agent  |  | Expense_Agent|  | Loan_Agent|  | Investment_Agent|
+------------------+  +--------------+  +-----------+  +-----------------+
          |                 |           |           |                 |
          +-----------------+-----------+-----------+-----------------+
                            |
                            v
+--------------------------------------------------------------------+
|                      FIMCPDataAccess (Data Layer)                  |
+--------------------------------------------------------------------+
|          (fetch_net_worth.json, fetch_bank_transactions.json, ...)     |
+--------------------------------------------------------------------+
```

---

## 📂 Project Structure

```
humsafar-financial-ai-assistant/
├── .env.example                     # Environment variables template
├── .env                            # Environment variables (git-ignored)
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
├── setup.sh                       # Automated setup script
├── main.py                        # Main application entry point
├── src/
│   ├── __init__.py
│   ├── fi_mcp_data_access.py      # Data access layer
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── net_worth_agent.py     # Net worth & health analysis
│   │   ├── expense_agent.py       # Expense & cash flow analysis
│   │   ├── investment_agent.py    # Investment & portfolio analysis
│   │   └── loan_agent.py          # Loan & credit analysis
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── adk_orchestrator.py    # Main orchestrator agent
│   └── tools/
│       ├── __init__.py
│       └── financial_tools.py     # EMI & SIP calculators
├── tests/
│   ├── test_all_agents.py               # Master test runner (30 tools)
│   ├── test_json_structures.py          # CI-friendly JSON validation
│   ├── test_financial_health_auditor_agent.py  # 12 audit tools
│   ├── test_net_worth_agent.py          # 6 net worth tools
│   ├── test_expense_agent.py            # 4 expense tools
│   ├── test_investment_agent.py         # 4 investment tools
│   ├── test_loan_agent.py               # 4 loan/credit tools
│   ├── test_phase1.py                   # Legacy core tests
│   ├── test_phase2.py                   # Legacy expense/investment tests
│   ├── test_phase3.py                   # Legacy loan tests
│   └── test_evaluation_framework.py     # Original evaluation framework
└── FI money dummy data/
    └── test_data_dir/             # User persona test data
        ├── 1111111111/            # User data directories
        ├── 2222222222/
        └── ...
```

---

## ⚙️ Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/akshaykumarbedre/humsafar-financial-ai-assistant.git
cd humsafar-financial-ai-assistant
```

### 2. Quick Setup (Automated)
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all required dependencies
- Create a `.env` file from the template
- Provide next steps for configuration

### 3. Configure Your API Key
Open the newly created `.env` file and replace `"YOUR_API_KEY_HERE"` with your actual Google API Key.

### 4. Manual Setup (Alternative)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

**📋 For detailed setup instructions, see [instructions.md](instructions.md)**

---

## ▶️ Usage

1.  Activate the virtual environment (if not already active):
    ```bash
    source venv/bin/activate
    ```

2.  Run the main application script:
    ```bash
    python main.py
    ```

The script will initialize the agent system and execute a pre-defined complex query to demonstrate its capabilities. You can modify the `complex_query` variable in `main.py` to ask your own questions.

### Example Queries

* "What's my current net worth and how has it changed over the last quarter?"
* "Show me my spending patterns for the last 90 days and identify any unusual expenses."
* "Which of my mutual funds are underperforming and what should I do about them?"
* "Analyze my credit score and suggest ways to improve it."
* "Should I prepay any of my loans based on my current financial situation?"

---

## 🌐 Testing with ADK Web Interface

For an interactive testing experience, you can use Google's Agent Development Kit (ADK) web interface to test the financial assistant agents in real-time.

### 1. Start the ADK Web Server

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the ADK web interface
adk web
```

### 2. Access the Web Interface

1. Open your web browser and navigate to `http://localhost:8080` (or the URL shown in the terminal)
2. The ADK web interface will load with your Humsafar financial agents available for testing

### 3. Interactive Testing

- **Agent Selection**: Choose from the available agents (Orchestrator, NetWorth, Expense, Investment, Loan agents)
- **Real-time Chat**: Test queries in a conversational interface
- **Agent Switching**: Seamlessly switch between different specialist agents
- **Query History**: Review previous interactions and responses

### 4. Useful Testing Scenarios

Try these scenarios in the web interface:

**Financial Health Check:**
```
"Give me a complete financial health analysis for user 1313131313"
```

**Investment Analysis:**
```
"Analyze the mutual fund portfolio performance for user 2222222222 and suggest optimizations"
```

**Expense Insights:**
```
"Show spending patterns and identify areas to reduce expenses for user 2525252525"
```

**Credit & Loan Analysis:**
```
"Evaluate credit health and loan prepayment opportunities for user 7777777777"
```

### 5. Advanced Testing Features

- **Multi-turn Conversations**: Test complex, follow-up questions
- **Agent Handoffs**: Observe how the orchestrator routes queries between agents
- **Real-time Debugging**: Monitor agent reasoning and decision-making processes
- **Performance Metrics**: Track response times and accuracy

### 6. Stopping the Web Server

To stop the ADK web server, press `Ctrl+C` in the terminal where it's running.

---

## 🧪 Testing

The project includes comprehensive test suites for all agent tools and functionality:

### Run All Tests (Recommended)
```bash
# Run comprehensive test suite for all agents
python tests/test_all_agents.py

# Test JSON structures (CI-friendly, no ADK dependencies)
python tests/test_json_structures.py
```

### Individual Agent Tests  
Each agent has dedicated test files covering all tools:

```bash
# Test Financial Health Auditor Agent (12 tools)
python tests/test_financial_health_auditor_agent.py

# Test Net Worth Agent (6 tools)
python tests/test_net_worth_agent.py

# Test Expense Agent (4 tools)
python tests/test_expense_agent.py

# Test Investment Agent (4 tools)
python tests/test_investment_agent.py

# Test Loan Agent (4 tools)
python tests/test_loan_agent.py
```

### Legacy Phase Tests
```bash
# Test core functionality (legacy)
python tests/test_phase1.py

# Test expense and investment agents (legacy)
python tests/test_phase2.py

# Test loan and credit analysis (legacy)
python tests/test_phase3.py
```

### What Tests Validate
- ✅ **JSON Output Structures**: All tools return structured data (Dict/List) instead of strings
- ✅ **Business Logic**: Financial calculations and analysis work correctly
- ✅ **Error Handling**: Graceful handling of missing or invalid data
- ✅ **Multiple User Personas**: Tests across 8+ different financial profiles
- ✅ **Comprehensive Data Tools**: Validates all `get_processed_*_data` methods

---

## 👤 Available User Personas

The system includes 25 different user personas for testing scenarios:

| Phone Number | Persona Description |
|-------------|-------------------|
| `1111111111` | No assets connected - Only savings account |
| `2222222222` | **Sudden Wealth Receiver** - All assets connected, large MF portfolio |
| `3333333333` | All assets connected - Small MF portfolio |
| `7777777777` | **Debt-Heavy Low Performer** - High liabilities, poor credit |
| `1313131313` | **Balanced Growth Tracker** - Well-diversified, good credit (750+) |
| `1414141414` | **Salary Sinkhole** - Income consumed by EMIs |
| `1616161616` | **Early Retirement Dreamer** - Aggressive savings, frugal lifestyle |
| `2525252525` | **Live-for-Today** - High income, high spending, low savings |

*See complete list in the FIMCPDataAccess class documentation*

---

## 🔧 API Reference

### Main Components

#### Financial Orchestrator Agent
Central agent that routes queries to specialized agents based on the query content and user context.

#### Specialist Agents
- **NetWorthAndHealthAgent**: Complete financial health analysis
- **ExpenseAndCashflowAgent**: Transaction analysis and spending insights
- **InvestmentAnalystAgent**: Portfolio performance and optimization
- **LoanAndCreditAgent**: Credit analysis and debt management

#### Data Access Layer
**FIMCPDataAccess**: Unified interface for accessing all financial data types including net worth, transactions, investments, loans, and credit reports.

#### Financial Tools
- **EMI Calculator**: Loan payment calculations
- **SIP Calculator**: Investment growth projections

---

## 💡 Key Features

### 🚀 **Standardized JSON Outputs**
All agent tools now return structured JSON data instead of formatted strings:
- **Machine-readable results** for better orchestration
- **Rich metadata** and calculated metrics included
- **Consistent error handling** across all tools
- **Enhanced debugging** with clear status codes

**Example JSON Response:**
```json
{
    "status": "SUCCESS",
    "total_net_worth": 1234567.89,
    "currency": "INR",
    "formatted_value": "₹12,34,567.89",
    "breakdown": {
        "assets": 1500000.00,
        "liabilities": 265432.11
    }
}
```

### 📊 **Comprehensive Data Tools**
Each specialist agent includes a powerful "data dump" tool:
- `get_processed_financial_health_data()` - Complete health metrics
- `get_processed_net_worth_data()` - Full net worth analysis
- `get_processed_transaction_data()` - Complete cashflow insights
- `get_processed_investment_portfolio()` - Full portfolio view
- `get_processed_credit_data()` - Complete credit profile

### 🏦 Net Worth & Health Analysis
- Complete asset and liability breakdown
- Financial health scoring with 10+ specialized audits
- Trend analysis and personalized recommendations

### 💰 Expense & Cash Flow Management
- Transaction categorization and analysis  
- Spending pattern insights and anomaly detection
- Budget optimization and recurring payment tracking

### 📈 Investment Analysis
- Portfolio performance tracking across mutual funds and stocks
- Underperforming fund identification with detailed metrics
- Rebalancing recommendations and diversification analysis

### 💳 Loan & Credit Management
- Credit score analysis and improvement strategies
- Loan prepayment optimization with ROI calculations
- Debt consolidation advice and EMI management

---

## 🔒 Data Privacy & Security

- All test data represents fictional personas
- No real financial data is stored or processed
- Phone numbers are used only as test identifiers
- Modular data access follows security best practices

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation and test files for examples
- Review the comprehensive test suite for usage patterns

---

*Built with ❤️ using Google's Agent Development Kit (ADK)*
