"""
Test Purchase Order Button Visibility Logic
Tests authorization, showing, hiding, and navigation scenarios
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_purchase_order_button_logic():
    """Test the complete Purchase Order button visibility workflow"""
    
    print("🧪 Testing Purchase Order Button Visibility Logic")
    print("=" * 60)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "❌ Unauthorized Employee ID",
            "message": "I am employee EMP002 and I want to create a purchase order",
            "expected": "should not show button - unauthorized"
        },
        {
            "name": "✅ Authorized Employee ID (EMP001)",
            "message": "I am employee EMP001",
            "expected": "should authenticate user"
        },
        {
            "name": "📦 Purchase Order Request by Authorized User",
            "message": "I want to create a purchase order", 
            "expected": "should show button if authorized"
        },
        {
            "name": "📝 User Registration (Should Hide Button)",
            "message": "I want to register a new user",
            "expected": "should hide purchase order button"
        },
        {
            "name": "🏢 Supplier Registration (Should Hide Button)",
            "message": "I want to register a supplier",
            "expected": "should hide purchase order button"
        },
        {
            "name": "🔍 Query Operation (Should Hide Button)",
            "message": "Show me all user registrations",
            "expected": "should hide purchase order button"
        },
        {
            "name": "✅ Authorized Employee ID (EMP003 - Procurement)",
            "message": "I am employee EMP003 and I need to create a purchase order",
            "expected": "should show button for procurement manager"
        },
        {
            "name": "✅ Authorized Employee ID (EMP004 - Finance)",
            "message": "EMP004 - I want to create a purchase order",
            "expected": "should show button for finance manager"
        },
        {
            "name": "✅ Authorized Employee ID (EMP005 - Director)",
            "message": "My employee ID is EMP005, I need to make a purchase",
            "expected": "should show button for director"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Test {i}: {scenario['name']}")
        print("-" * 50)
        print(f"💬 Message: {scenario['message']}")
        print(f"📋 Expected: {scenario['expected']}")
        
        try:
            # Send message to chatbot
            response = requests.post(f"{BASE_URL}/chat", json={
                "message": scenario["message"]
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', 'No response')
                
                print(f"🤖 Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                
                # Analyze response for authorization patterns
                if 'access granted' in response_text.lower():
                    print("✅ Authorization detected in response")
                elif 'access denied' in response_text.lower():
                    print("❌ Access denied detected in response")
                elif 'unauthorized' in response_text.lower():
                    print("🚫 Unauthorized access detected")
                
                # Check for registration context
                if any(word in response_text.lower() for word in ['register', 'registration', 'create user', 'create supplier']):
                    print("📝 Registration context detected - button should be hidden")
                
                # Check for query context
                if any(word in response_text.lower() for word in ['documents found', 'query result', 'collection:', 'database:']):
                    print("🔍 Query context detected - button should be hidden")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(1)  # Brief delay between tests
    
    print(f"\n{'='*60}")
    print("🎯 Purchase Order Button Logic Test Complete!")
    print("\n📋 Manual Testing Steps:")
    print("1. Open browser to http://localhost:5001")
    print("2. Check that Purchase Order button is hidden by default")
    print("3. Try clicking unauthorized employee ID - button should stay hidden")
    print("4. Try authorized employee ID (EMP001/EMP003/EMP004/EMP005) - button should appear after authorization")
    print("5. Switch to other registrations - button should disappear")
    print("6. Return to purchase order context - button should reappear if authorized")

def test_button_edge_cases():
    """Test edge cases and boundary conditions"""
    
    print("\n🔬 Testing Edge Cases")
    print("=" * 40)
    
    edge_cases = [
        {
            "name": "Mixed Case Employee ID",
            "message": "I am employee emp001",
            "expected": "should handle case insensitive"
        },
        {
            "name": "Employee ID with Spaces",
            "message": "My ID is EMP 001",
            "expected": "should not match due to space"
        },
        {
            "name": "Invalid Employee ID Format",
            "message": "I am employee E001",
            "expected": "should not match invalid format"
        },
        {
            "name": "Multiple Employee IDs",
            "message": "EMP001 and EMP003 working together",
            "expected": "should match first valid ID"
        }
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n🧪 Edge Case {i}: {case['name']}")
        print(f"💬 Message: {case['message']}")
        print(f"📋 Expected: {case['expected']}")
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json={
                "message": case["message"]
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"🤖 Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    test_purchase_order_button_logic()
    test_button_edge_cases()