"""
Simple Query Node Test
"""

import requests
import json
import time

def test_single_query():
    """Test a single query to verify Query Node is working"""
    
    print("🔍 Testing Query Node Integration")
    print("=" * 50)
    
    url = "http://localhost:5001/api/query"
    
    test_data = {
        "query": "How many users are registered?",
        "collection": "user_registration",
        "employee_id": "EMP001",
        "session_id": "test_session_1"
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"🧪 Query: {test_data['query']}")
    print(f"📊 Collection: {test_data['collection']}")
    print(f"👤 Employee: {test_data['employee_id']}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\n📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"🤖 Response: {result.get('response', '')}")
            print(f"📊 Query Results: {result.get('query_results')}")
            print(f"👤 Employee: {result.get('employee_id')}")
            print(f"🎯 User Position: {result.get('user_position')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not running on http://localhost:5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_query():
    """Test query through chat endpoint"""
    
    print("\n\n💬 Testing Query Through Chat Endpoint")
    print("=" * 50)
    
    url = "http://localhost:5001/chat"
    
    test_data = {
        "message": "How many users are registered in the system?",
        "session_id": "chat_test_1"
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"💬 Message: {test_data['message']}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\n📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"🤖 Response: {result.get('response', '')[:200]}...")
            if result.get('intent'):
                print(f"🎯 Intent: {result.get('intent')}")
            if result.get('task'):
                print(f"📋 Task: {result.get('task')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not running on http://localhost:5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SIMPLE QUERY NODE TEST")
    print("=" * 80)
    
    # Wait a moment for server to be fully ready
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success1 = test_single_query()
    success2 = test_chat_query()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("✅ All tests passed! Query Node is working.")
    elif success1 or success2:
        print("⚠️ Some tests passed. Check the results above.")
    else:
        print("❌ Tests failed. Check server status and try again.")
    print("=" * 80)