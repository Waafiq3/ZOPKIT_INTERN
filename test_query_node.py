"""
Test Script for Query Node Integration
Tests the complete natural language query workflow
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5001"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
QUERY_ENDPOINT = f"{BASE_URL}/api/query"

def test_query_endpoint_direct():
    """Test the direct query API endpoint"""
    print("🔍 Testing Direct Query API Endpoint")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        {
            "query": "How many users are registered?",
            "collection": "user_registration",
            "employee_id": "EMP001",
            "expected": "count operation"
        },
        {
            "query": "Show all users with admin position",
            "collection": "user_registration", 
            "employee_id": "EMP001",
            "expected": "find operation with filter"
        },
        {
            "query": "List all purchase orders",
            "collection": "purchase_order",
            "employee_id": "EMP001",
            "expected": "find operation"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test['query']}")
        print(f"Collection: {test['collection']}")
        print(f"Employee: {test['employee_id']}")
        
        try:
            response = requests.post(QUERY_ENDPOINT, json={
                "query": test["query"],
                "collection": test["collection"],
                "employee_id": test["employee_id"],
                "session_id": f"test_session_{i}"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result.get('status')}")
                print(f"🤖 Response: {result.get('response', '')[:100]}...")
                if result.get('query_results') is not None:
                    print(f"📊 Results: {len(result['query_results']) if isinstance(result['query_results'], list) else result['query_results']}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_chat_endpoint_queries():
    """Test natural language queries through the chat endpoint"""
    print("\n\n💬 Testing Queries Through Chat Endpoint")
    print("=" * 50)
    
    # Test natural language queries
    test_messages = [
        "How many users are registered in the system?",
        "Show me all employees with admin position",
        "List pending purchase orders",
        "When did employee EMP001 last check in?",
        "How many training sessions were scheduled this month?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 Chat Test {i}: {message}")
        
        try:
            response = requests.post(CHAT_ENDPOINT, json={
                "message": message,
                "session_id": f"chat_test_session_{i}"
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result.get('status')}")
                print(f"🤖 Response: {result.get('response', '')[:150]}...")
                if result.get('intent'):
                    print(f"🎯 Intent: {result.get('intent')}")
                if result.get('task'):
                    print(f"📋 Task: {result.get('task')}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_access_control():
    """Test access control for different employee roles"""
    print("\n\n🔒 Testing Access Control")
    print("=" * 50)
    
    # Test different employee roles
    access_tests = [
        {
            "employee_id": "EMP001",
            "expected_access": "admin - should have access to all",
            "query": "Show all users",
            "collection": "user_registration"
        },
        {
            "employee_id": "EMP002", 
            "expected_access": "hr_manager - should have HR access",
            "query": "List employee leave requests",
            "collection": "employee_leave_request"
        },
        {
            "employee_id": "INVALID123",
            "expected_access": "invalid employee - should be denied",
            "query": "Show anything",
            "collection": "user_registration"
        }
    ]
    
    for i, test in enumerate(access_tests, 1):
        print(f"\n🧪 Access Test {i}: {test['employee_id']}")
        print(f"Expected: {test['expected_access']}")
        
        try:
            response = requests.post(QUERY_ENDPOINT, json={
                "query": test["query"],
                "collection": test["collection"],
                "employee_id": test["employee_id"],
                "session_id": f"access_test_{i}"
            })
            
            print(f"📊 HTTP Status: {response.status_code}")
            result = response.json()
            print(f"🎯 Result Status: {result.get('status')}")
            print(f"💬 Message: {result.get('response', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 QUERY NODE INTEGRATION TESTS")
    print("=" * 80)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Run tests
    try:
        test_query_endpoint_direct()
        test_chat_endpoint_queries()
        test_access_control()
        
        print("\n\n" + "=" * 80)
        print("✅ All tests completed!")
        print("🎯 Check the results above for any issues")
        print("💡 Make sure the server is running on http://localhost:5001")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")

if __name__ == "__main__":
    main()