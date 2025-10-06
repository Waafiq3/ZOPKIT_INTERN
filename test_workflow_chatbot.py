"""
Test the Enhanced Chatbot with Workflow AI
Run this after starting the enhanced_api_chatbot.py server
"""

import requests
import json

BASE_URL = "http://localhost:3000"

def test_workflow_integration():
    print("🧪 Testing Enhanced Chatbot with Workflow AI")
    print("=" * 50)
    
    # Test 1: Chat message that should trigger workflow
    print("\n1. Testing purchase order trigger...")
    chat_response = requests.post(f"{BASE_URL}/chat", json={
        "message": "I want to create a purchase order",
        "session_id": "test_workflow"
    })
    
    if chat_response.status_code == 200:
        result = chat_response.json()
        print(f"✅ Chat Response: {result['response'][:100]}...")
        print(f"📊 Status: {result['status']}")
    else:
        print(f"❌ Chat failed: {chat_response.status_code}")
    
    # Test 2: Create workflow via API
    print("\n2. Testing workflow creation...")
    workflow_response = requests.post(f"{BASE_URL}/api/workflow", json={
        "type": "purchase_order",
        "action": "create"
    })
    
    if workflow_response.status_code == 200:
        result = workflow_response.json()
        print(f"✅ Workflow Created: {result['workflow']['title']}")
        print(f"📋 Steps: {len(result['workflow']['steps'])}")
        for step in result['workflow']['steps']:
            print(f"   • {step['title']} - {step['status']}")
    else:
        print(f"❌ Workflow creation failed: {workflow_response.status_code}")
    
    # Test 3: Test other workflow types
    print("\n3. Testing different triggers...")
    triggers = [
        "register a new supplier",
        "create user registration", 
        "schedule training session",
        "make a purchase order for office supplies"
    ]
    
    for trigger in triggers:
        print(f"\n   Testing: '{trigger}'")
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": trigger,
            "session_id": f"test_{hash(trigger)}"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response received: {len(result['response'])} chars")
        else:
            print(f"   ❌ Failed: {response.status_code}")

def test_api_status():
    print("\n🔍 Testing API Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api-status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ API Status: {'Online' if status.get('generic_api_online') else 'Offline'}")
            print(f"📡 Endpoints: {status.get('endpoint_count', 0)}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Chatbot Workflow Test")
    print("Make sure enhanced_api_chatbot.py is running on port 3000")
    print("\nStarting tests...")
    
    try:
        # Test API status first
        test_api_status()
        
        # Test workflow integration
        test_workflow_integration()
        
        print("\n" + "=" * 50)
        print("✅ Tests completed!")
        print("\n💡 To test manually:")
        print("1. Open http://localhost:3000/")
        print("2. Type: 'I want to create a purchase order'")
        print("3. Look for the 'Start' button in the response")
        print("4. Click the Start button to open Workflow AI panel")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        print("\nMake sure the server is running:")
        print("python enhanced_api_chatbot.py")