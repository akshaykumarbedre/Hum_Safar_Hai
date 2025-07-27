# Hum Safar Hai - Intelligent Financial Companion

> **"Your trusted financial journey partner"**

A comprehensive full-stack financial management platform combining AI-powered financial analysis with an intuitive web interface. Hum Safar Hai features a sophisticated multi-agent AI system for personalized financial insights and a modern React-based dashboard for seamless user experience.

## 🎥 Demo Video

Watch the complete demonstration of Hum Safar Hai in action:
[**📺 View Demo Video**](https://dl.dropboxusercontent.com/scl/fi/7sey7g2thmfzjn0enz6c0/opera_C2gJCM4NAY.mp4?rlkey=put2yua0i5dv2wkyzyzj9rnbx&dl=0)

## 🌟 Overview

Hum Safar Hai is a next-generation financial management platform designed to provide users with comprehensive financial insights through AI-powered analysis and an elegant web interface. The platform combines:

- **AI-Powered Financial Analysis**: Multi-agent system using Google's Agent Development Kit (ADK)
- **Modern Web Interface**: React/Next.js dashboard with real-time financial visualizations
- **Couple-Friendly Design**: Shared financial planning and goal tracking
- **Intelligent Insights**: Natural language queries for complex financial analysis

## ✨ Key Features

### 🤖 AI-Powered Financial Assistant
- **Multi-Agent Architecture**: Specialized AI agents for different financial domains
- **Natural Language Interface**: Ask complex financial questions in plain English
- **Comprehensive Analysis**: Net worth, expenses, investments, loans, and credit analysis
- **Intelligent Orchestration**: Automatic routing of queries to appropriate specialist agents

### 💼 Financial Management Dashboard
- **Real-time Overview**: Integrated dashboard with key financial metrics
- **Goal Tracking**: Interactive goal setting and progress monitoring
- **Couples Dashboard**: Joint financial planning and visibility for partners
- **Simulation Tools**: Financial scenario planning and modeling

### 📊 Advanced Analytics
- **Net Worth Analysis**: Complete asset and liability breakdown with trends
- **Expense Intelligence**: Smart categorization and spending pattern analysis
- **Investment Insights**: Portfolio performance tracking and optimization recommendations
- **Credit Management**: Score analysis and improvement strategies

## 🏗️ Architecture

### Backend Architecture
```
                    User Query
                         |
                         v
            ┌─────────────────────────┐
            │  Financial Orchestrator │
            │      Agent (ADK)        │
            └─────────────────────────┘
                         |
        ┌────────────────┼────────────────┐
        |                |                |
        v                v                v
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ NetWorth     │  │ Expense      │  │ Investment   │
│ Agent        │  │ Agent        │  │ Agent        │
└──────────────┘  └──────────────┘  └──────────────┘
        |                |                |
        └────────────────┼────────────────┘
                         |
                         v
            ┌─────────────────────────┐
            │   FI MCP Data Access    │
            │      (Data Layer)       │
            └─────────────────────────┘
```

### Frontend Architecture
```
                    Next.js Application
                         |
        ┌────────────────┼────────────────┐
        |                |                |
        v                v                v
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Dashboard    │  │ Chat         │  │ Goals        │
│ Components   │  │ Interface    │  │ Tracker      │
└──────────────┘  └──────────────┘  └──────────────┘
        |                |                |
        └────────────────┼────────────────┘
                         |
                         v
            ┌─────────────────────────┐
            │     Backend API         │
            │   (Agent System)        │
            └─────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Google API Key** (for ADK agents)
- **Firebase Project** (for frontend features)

### 1. Clone the Repository
```bash
git clone https://github.com/akshaykumarbedre/Hum_Safar_Hai.git
cd Hum_Safar_Hai
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Google API key and configuration
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Running the Application

#### Start Backend Services
```bash
cd backend
source venv/bin/activate
python main.py

# For ADK web interface
adk web
```

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:9002
- **ADK Interface**: http://localhost:8080

## 📁 Project Structure

```
Hum_Safar_Hai/
├── README.md                    # Main project documentation
├── pyproject.toml              # Python project configuration
├── combined_goals.json         # Shared financial goals data
│
├── backend/                    # Python AI Backend
│   ├── src/
│   │   ├── agents/            # Specialist AI agents
│   │   │   ├── net_worth_agent.py
│   │   │   ├── expense_agent.py
│   │   │   ├── investment_agent.py
│   │   │   ├── loan_agent.py
│   │   │   └── financial_health_auditor_agent.py
│   │   ├── orchestration/     # Main orchestrator
│   │   │   └── adk_orchestrator.py
│   │   ├── tools/            # Financial calculation tools
│   │   └── fi_mcp_data_access.py  # Data access layer
│   ├── tests/                # Comprehensive test suite
│   ├── evaluation/           # Performance evaluation tools
│   ├── FI money dummy data/  # Test financial data
│   ├── main.py              # Backend entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/                 # Next.js React Frontend
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   ├── components/      # React components
│   │   ├── ai/             # AI integration
│   │   └── lib/            # Utility libraries
│   ├── docs/               # Frontend documentation
│   ├── package.json        # Node.js dependencies
│   └── next.config.ts      # Next.js configuration
│
└── fi-mcp-dev/             # Development utilities
```

## 🎯 Usage Examples

### AI Financial Queries
The backend supports natural language financial analysis:

```python
# Example queries you can ask the AI system
queries = [
    "What's my current net worth and how has it changed over the last quarter?",
    "Show me my spending patterns for the last 90 days and identify any unusual expenses.",
    "Which of my mutual funds are underperforming and what should I do about them?",
    "Analyze my credit score and suggest ways to improve it.",
    "Should I prepay any of my loans based on my current financial situation?"
]
```

### Web Dashboard Features
- **Financial Overview**: Real-time financial metrics and trends
- **Goal Planning**: Set and track financial goals with progress visualization
- **Couples Mode**: Shared financial planning for partners
- **Chat Interface**: Natural language queries with AI responses
- **Simulation Tools**: Model different financial scenarios

## 🧪 Testing

### Backend Testing
```bash
cd backend
source venv/bin/activate

# Run all tests
python tests/test_all_agents.py

# Test individual agents
python tests/test_net_worth_agent.py
python tests/test_expense_agent.py
python tests/test_investment_agent.py
python tests/test_loan_agent.py
```

### Frontend Testing
```bash
cd frontend

# Type checking
npm run typecheck

# Linting
npm run lint

# Build test
npm run build
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Frontend Configuration (.env.local)
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
# Additional Firebase configuration...
```

## 🤖 AI Agents Overview

### Core Specialist Agents
1. **Financial Orchestrator**: Routes queries to appropriate agents
2. **Net Worth Agent**: Asset/liability analysis and financial health scoring
3. **Expense Agent**: Transaction analysis and spending insights
4. **Investment Agent**: Portfolio performance and optimization
5. **Loan Agent**: Credit analysis and debt management
6. **Financial Health Auditor**: Comprehensive financial health assessment
7. **Goal Strategy Agent**: Investment strategy for financial goals

### Available User Personas (Testing)
The system includes 25+ test personas for comprehensive testing:
- **1111111111**: Basic savings account holder
- **2222222222**: Wealthy investor with large portfolio
- **7777777777**: Debt-heavy low performer
- **1313131313**: Balanced growth tracker
- And many more...

## 🎨 Design System

### Color Palette
- **Primary**: Soft lavender (#D1B0FF) - Calming and sophisticated
- **Background**: Very light gray (#F5F4F7) - Clean and unobtrusive
- **Accent**: Muted blue-purple (#7957D4) - Interactive elements
- **Typography**: Inter (body), Space Grotesk (headings)

### UI Components
- Radix UI primitives for accessibility
- Tailwind CSS for styling
- Responsive design optimized for all devices
- Subtle animations and transitions

## 📊 Dependencies

### Backend
- **google-adk**: Agent Development Kit for AI agents
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **fastapi**: Modern web framework
- **pydantic**: Data validation

### Frontend
- **Next.js 15**: React framework with app router
- **React 18**: Frontend library
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Firebase**: Backend services
- **Recharts**: Data visualization
- **Genkit**: AI integration toolkit

## 🔒 Security & Privacy

- All test data represents fictional personas
- No real financial data is stored or processed
- Environment variables for API key management
- Secure Firebase authentication
- Data validation with Pydantic and Zod

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure both frontend and backend tests pass

## 📚 Documentation

- **Backend**: See [backend/README.md](backend/README.md) for detailed backend documentation
- **Frontend**: See [frontend/docs/blueprint.md](frontend/docs/blueprint.md) for design specifications
- **API Reference**: Available in the ADK web interface at http://localhost:8080

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your Google API key is properly set in the backend .env file
2. **Port Conflicts**: Default ports are 9002 (frontend) and 8080 (ADK interface)
3. **Python Version**: Requires Python 3.11 or higher
4. **Node Version**: Requires Node.js 18 or higher

### Getting Help
- Check the documentation in respective directories
- Review test files for usage examples
- Create an issue for bugs or feature requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **Created by**: Akshay Kumar Bedre
- **Contributors**: Kirushikesh and team

---

**Hum Safar Hai** - *Your intelligent financial journey companion* 🚀

Built with ❤️ using Google's Agent Development Kit, Next.js, and modern web technologies.