"""
Test API Integration for Query Node
Tests the enhanced Query Node that calls API endpoints instead of direct database access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot

def test_api_integration():
    """Test Query Node with API integration"""
    
    print("🔗 Testing API Integration for Query Node")
    print("=" * 60)
    
    chatbot = DynamicChatBot()
    test_session = "api_integration_test_001"
    
    # Test case: Supplier details retrieval
    print("\n🎯 Test Case: Supplier Details Retrieval")
    print("-" * 40)
    
    # User provides employee ID and supplier ID in one message
    test_message = "I already register as supplier 68de3a043af7466cd71bfff9 this is my id. My employee id is EMP001. I want to get my details"
    
    print(f"User Message: {test_message}")
    print("\nProcessing...")
    
    result = chatbot.process_message(test_message, test_session)
    
    print(f"\n📊 Result:")
    print(f"Status: {result.get('status')}")
    print(f"Response Preview: {result.get('response', '')[:200]}...")
    
    # Check if the query was successful
    if result.get('status') == 'query_completed':
        print("✅ SUCCESS: Query completed successfully!")
        
        # Check if we got actual data
        query_results = result.get('query_results', [])
        if query_results:
            print(f"📋 Data Retrieved: {len(query_results)} records found")
            if isinstance(query_results, list) and len(query_results) > 0:
                first_record = query_results[0]
                print(f"🏢 Sample Data: {list(first_record.keys()) if isinstance(first_record, dict) else 'N/A'}")
        else:
            print("📭 No data found")
            
    elif result.get('status') == 'error':
        print("❌ ERROR: Query failed")
        print(f"Error Details: {result.get('response', 'Unknown error')}")
    else:
        print(f"ℹ️  Status: {result.get('status')} - {result.get('response', '')[:100]}...")
    
    # Test another case: User registration query
    print(f"\n🎯 Test Case 2: User Registration Count")
    print("-" * 40)
    
    test_message2 = "How many users are registered in the system? My employee ID is EMP001"
    print(f"User Message: {test_message2}")
    
    # Reset session for clean test
    chatbot.reset_session(test_session)
    
    result2 = chatbot.process_message(test_message2, test_session)
    
    print(f"\n📊 Result:")
    print(f"Status: {result2.get('status')}")
    print(f"Response Preview: {result2.get('response', '')[:200]}...")
    
    if result2.get('status') == 'query_completed':
        print("✅ SUCCESS: Count query completed!")
    else:
        print(f"ℹ️  Status: {result2.get('status')}")
    
    print("\n" + "=" * 60)
    print("🎯 API Integration Test Complete")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"Test 1 (Supplier Details): {'✅ Success' if result.get('status') == 'query_completed' else '❌ Failed'}")
    print(f"Test 2 (User Count): {'✅ Success' if result2.get('status') == 'query_completed' else '❌ Failed'}")

if __name__ == "__main__":
    test_api_integration()