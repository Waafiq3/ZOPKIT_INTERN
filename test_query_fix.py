"""
Test Query Node Functionality After Fix
Tests the database query error fix for "list index out of range"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot

def test_query_node_fix():
    """Test Query Node with various queries that previously caused errors"""
    
    print("🧪 Testing Query Node Fix")
    print("=" * 50)
    
    chatbot = DynamicChatBot()
    test_session = "query_fix_test_001"
    
    # Test queries that previously failed
    test_queries = [
        "I want to retrieve my details",
        "Show me user information for EMP001", 
        "How many users are registered?",
        "List all employee attendance records",
        "Find purchase orders above $1000"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 30)
        
        # First establish session with employee ID
        login_result = chatbot.process_message("I am employee EMP001", test_session)
        print(f"Login Status: {login_result.get('status', 'N/A')}")
        
        # Now test the query
        result = chatbot.process_message(query, test_session)
        
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Response Preview: {result.get('response', 'No response')[:100]}...")
        
        if result.get('status') == 'error':
            print(f"❌ ERROR: {result.get('response', 'Unknown error')}")
        else:
            print(f"✅ SUCCESS: Query processed without errors")
        
        # Reset session for next test
        chatbot.reset_session(test_session)
    
    print("\n" + "=" * 50)
    print("🎯 Query Node Fix Test Complete")

if __name__ == "__main__":
    test_query_node_fix()