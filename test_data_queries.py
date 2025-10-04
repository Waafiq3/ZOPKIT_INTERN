"""
Test Query Node with Actual Data
Tests queries against actual data in the MongoDB collections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot
from db import get_database

def test_queries_with_data():
    """Test queries against actual database data"""
    
    print("📊 Testing Query Node with Actual Database Data")
    print("=" * 60)
    
    # First, check what data we have
    db = get_database()
    print("\n📋 Database Collections Summary:")
    for collection_name in ["user_registration", "supplier_registration", "employee_management"]:
        try:
            count = db[collection_name].count_documents({})
            sample = db[collection_name].find_one()
            print(f"  • {collection_name}: {count} documents")
            if sample:
                fields = list(sample.keys())[:5]  # First 5 fields
                print(f"    Fields: {', '.join(fields)}...")
        except Exception as e:
            print(f"  • {collection_name}: Error - {e}")
    
    chatbot = DynamicChatBot()
    test_session = "data_query_test_001"
    
    # Step 1: Login as EMP001
    print(f"\n🔐 Step 1: Login as EMP001")
    login_result = chatbot.process_message("I am employee EMP001", test_session)
    auth_result = chatbot.process_message("EMP001", test_session)
    print(f"Auth Status: {auth_result.get('status')}")
    
    if auth_result.get('status') == 'success':
        # Test specific queries
        queries = [
            "How many users are registered in the system?",
            "Show me user registration details", 
            "List employee records"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 40)
            
            result = chatbot.process_message(query, test_session)
            print(f"Status: {result.get('status')}")
            
            response = result.get('response', '')
            if len(response) > 300:
                print(f"Response: {response[:300]}...")
            else:
                print(f"Response: {response}")
            
            # Check for specific result indicators
            if "Found" in response or "records" in response.lower():
                print("✅ Query returned results!")
            elif "No Results Found" in response:
                print("ℹ️  No matching data found")
            elif "Error" in response:
                print("❌ Query error detected")
            else:
                print("🔄 Query processed")
    else:
        print("❌ Authentication failed")
    
    print("\n" + "=" * 60)
    print("🎯 Data Query Test Complete")

if __name__ == "__main__":
    test_queries_with_data()