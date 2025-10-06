"""
Test User Registration Validation Integration
Tests the complete user registration validation system within the dynamic chatbot
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from dynamic_chatbot import DynamicChatBot
from db import init_db
import json

def test_user_registration_validation():
    """Test user registration validation within the chatbot"""
    
    print("🧪 Testing User Registration Validation Integration")
    print("=" * 60)
    
    # Initialize database
    if not init_db():
        print("❌ Database initialization failed")
        return
    
    # Initialize chatbot
    chatbot = DynamicChatBot()
    
    # Test cases for validation
    test_cases = [
        {
            "name": "Valid User Registration",
            "data": {
                "email": "newuser@company.com",
                "first_name": "John",
                "last_name": "Doe",
                "mobile": "9876543210",
                "employee_id": "EMP999",
                "position": "Software Engineer",
                "department": "IT"
            },
            "should_pass": True
        },
        {
            "name": "Invalid Email Format",
            "data": {
                "email": "invalid-email",
                "first_name": "Jane",
                "last_name": "Smith",
                "mobile": "9876543210",
                "employee_id": "EMP998",
                "position": "Manager",
                "department": "HR"
            },
            "should_pass": False
        },
        {
            "name": "Invalid Mobile Number (Too Short)",
            "data": {
                "email": "user2@company.com",
                "first_name": "Bob",
                "last_name": "Johnson",
                "mobile": "98765",
                "employee_id": "EMP997",
                "position": "Analyst",
                "department": "Finance"
            },
            "should_pass": False
        },
        {
            "name": "Invalid Mobile Number (Wrong Start Digit)",
            "data": {
                "email": "user3@company.com",
                "first_name": "Alice",
                "last_name": "Wilson",
                "mobile": "1876543210",
                "employee_id": "EMP996",
                "position": "Designer",
                "department": "Marketing"
            },
            "should_pass": False
        },
        {
            "name": "Duplicate Email (assuming admin@company.com exists)",
            "data": {
                "email": "admin@company.com",
                "first_name": "Duplicate",
                "last_name": "User",
                "mobile": "9876543210",
                "employee_id": "EMP995",
                "position": "Duplicate",
                "department": "Test"
            },
            "should_pass": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Create a mock state for user registration
        state = {
            "current_task": "user_registration",
            "collected_data": test_case["data"],
            "session_id": f"test_session_{i}"
        }
        
        try:
            # Call the _save_to_database method
            result = chatbot._save_to_database(state, f"test_session_{i}", "test registration")
            
            # Check results
            is_success = result.get("status") != "error"
            
            print(f"📊 Result: {'✅ PASS' if is_success == test_case['should_pass'] else '❌ FAIL'}")
            print(f"📝 Status: {result.get('status', 'unknown')}")
            
            if result.get("status") == "error":
                print(f"🚫 Error: {result.get('response', 'No error message')}")
            else:
                print(f"✅ Success: User registered successfully")
                if result.get("inserted_id"):
                    print(f"🆔 Document ID: {result.get('inserted_id')}")
            
            # Clean up successful test registrations (if any)
            if is_success and result.get("inserted_id"):
                try:
                    from db import get_db_connection
                    db = get_db_connection()
                    if db:
                        db.user_registration.delete_one({"_id": result["inserted_id"]})
                        print("🧹 Test data cleaned up")
                except Exception as e:
                    print(f"⚠️ Cleanup warning: {e}")
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎯 User Registration Validation Test Complete!")

def test_validation_directly():
    """Test validation function directly"""
    
    print("\n🔧 Testing Validation Function Directly")
    print("=" * 50)
    
    try:
        from user_validation import validate_user_data
        
        test_data = {
            "email": "direct.test@company.com",
            "first_name": "Direct",
            "last_name": "Test",
            "mobile_number": "9876543210",
            "employee_id": "EMP888",
            "position": "Tester"
        }
        
        is_valid, errors = validate_user_data(test_data)
        
        print(f"📊 Validation Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        if errors:
            print("🚫 Errors found:")
            for error in errors:
                print(f"   • {error}")
        else:
            print("✅ No validation errors")
            
    except Exception as e:
        print(f"❌ Direct validation test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_registration_validation()
    test_validation_directly()