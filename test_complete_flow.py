"""
Test Complete Query Flow with Authentication
Tests the full query workflow including login and database access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot

def test_complete_query_flow():
    """Test complete query flow with authentication"""
    
    print("🔐 Testing Complete Query Flow with Authentication")
    print("=" * 60)
    
    chatbot = DynamicChatBot()
    test_session = "auth_query_test_001"
    
    # Step 1: User wants to make a query
    print("\n📝 Step 1: User requests to retrieve details")
    result1 = chatbot.process_message("I want to retrieve my details", test_session)
    print(f"Status: {result1.get('status')}")
    print(f"Response: {result1.get('response', '')[:150]}...")
    
    # Step 2: Provide employee ID
    print("\n🆔 Step 2: User provides employee ID")
    result2 = chatbot.process_message("EMP001", test_session)
    print(f"Status: {result2.get('status')}")
    print(f"Response: {result2.get('response', '')[:150]}...")
    
    # Check if session was created
    if "session" in result2.get('response', '').lower():
        print("✅ Session created successfully!")
    
    # Step 3: Try the query again (should work now with authentication)
    print("\n🔍 Step 3: Retry the query with authentication")
    result3 = chatbot.process_message("Show me how many users are registered", test_session)
    print(f"Status: {result3.get('status')}")
    print(f"Response: {result3.get('response', '')[:200]}...")
    
    if result3.get('status') != 'error':
        print("✅ Query executed without database errors!")
    else:
        print("❌ Query still has issues")
    
    print("\n" + "=" * 60)
    print("🎯 Complete Query Flow Test Complete")

if __name__ == "__main__":
    test_complete_query_flow()