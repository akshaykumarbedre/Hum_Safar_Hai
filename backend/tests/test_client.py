"""
Test client for Humsafar Financial AI Assistant API
This script demonstrates how to interact with the FastAPI endpoints.
"""
import requests
import json
import time


class FinancialAIClient:
    """Client for interacting with the Financial AI Assistant API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_users(self):
        """Get list of available test users."""
        try:
            response = requests.get(f"{self.base_url}/users")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_query(self, query: str, user_id: str, session_id: str = None):
        """Send a financial query to the AI assistant."""
        try:
            payload = {
                "query": query,
                "user_id": user_id
            }
            if session_id:
                payload["session_id"] = session_id
            
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=120  # 2 minutes timeout for complex queries
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Demonstrate API usage with sample queries."""
    client = FinancialAIClient()
    
    print("🚀 Testing Humsafar Financial AI Assistant API")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # List users
    print("\n2. Available Users:")
    users = client.list_users()
    print(json.dumps(users, indent=2))
    
    # Test user (debt-heavy low performer for rich test case)
    test_user = "4444444444"
    
    # Sample queries to test
    test_queries = [
        "What is my total net worth?",
        "What are my top 3 spending categories in the last 90 days?",
        "Provide a summary of my expenses for the last 7 days.",
        "What are my top stock investments and mutual fund investments?",
        "Compare my loans and income. Give me detailed information."
    ]
    
    print(f"\n3. Testing Queries for User {test_user}:")
    print("-" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Query {i}: {query}")
        print("⏳ Processing...")
        
        start_time = time.time()
        result = client.send_query(query, test_user)
        end_time = time.time()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Response ({end_time - start_time:.2f}s):")
            # Print response with word wrapping
            response_text = result.get('response', 'No response')
            words = response_text.split()
            line = ""
            for word in words:
                if len(line + word) > 80:
                    print(f"   {line}")
                    line = word + " "
                else:
                    line += word + " "
            if line:
                print(f"   {line}")
        
        print("-" * 30)
        
        # Wait a bit between queries to be respectful
        if i < len(test_queries):
            time.sleep(2)


if __name__ == "__main__":
    main()
