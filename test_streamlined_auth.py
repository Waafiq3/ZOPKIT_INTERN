"""
Test Enhanced Authentication Workflow
Tests the new streamlined authentication where users can provide Employee ID and request together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot

def test_streamlined_authentication():
    """Test streamlined authentication workflow"""
    
    print("🚀 Testing Enhanced Authentication Workflow")
    print("=" * 60)
    
    chatbot = DynamicChatBot()
    test_session = "streamlined_auth_test_001"
    
    # Test Case 1: User provides Employee ID and supplier query in same message
    print("\n📋 Test Case 1: Combined Employee ID + Supplier Query")
    print("-" * 50)
    
    combined_message = "EMP001._id 68de3a043af7466cd71bfff9 this is my id i already register as supplier. I want my details"
    
    print(f"User Message: {combined_message}")
    result = chatbot.process_message(combined_message, test_session)
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Response Preview: {result.get('response', '')[:200]}...")
    
    if result.get('status') in ['query_completed', 'authenticated_proceed']:
        print("✅ SUCCESS: User authenticated and request processed in one step!")
    elif result.get('status') == 'authorization_required':
        print("⚠️  Still requiring separate authorization (old behavior)")
    else:
        print(f"❓ Unexpected status: {result.get('status')}")
    
    # Reset session for next test
    chatbot.reset_session(test_session)
    
    # Test Case 2: Different format - Employee ID at start
    print("\n📋 Test Case 2: Employee ID at Message Start")
    print("-" * 50)
    
    alt_message = "EMP001 - I want to retrieve my supplier registration details for _id 68de3a043af7466cd71bfff9"
    
    print(f"User Message: {alt_message}")
    result2 = chatbot.process_message(alt_message, test_session)
    
    print(f"\nStatus: {result2.get('status')}")
    print(f"Response Preview: {result2.get('response', '')[:200]}...")
    
    if result2.get('status') in ['query_completed', 'authenticated_proceed']:
        print("✅ SUCCESS: Alternative format also works!")
    else:
        print(f"❓ Status: {result2.get('status')}")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Authentication Test Complete")

if __name__ == "__main__":
    test_streamlined_authentication()