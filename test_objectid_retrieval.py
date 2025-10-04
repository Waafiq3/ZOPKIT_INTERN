"""
Test ObjectId-based Document Retrieval
Tests retrieving specific documents using MongoDB ObjectId
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot
from db import get_database

def test_objectid_retrieval():
    """Test retrieving documents by ObjectId"""
    
    print("🔍 Testing ObjectId-based Document Retrieval")
    print("=" * 60)
    
    # First, let's find a real ObjectId from the database
    db = get_database()
    supplier_doc = db.supplier_registration.find_one()
    
    if supplier_doc:
        object_id = str(supplier_doc["_id"])
        print(f"Found supplier document with ID: {object_id}")
        print(f"Company: {supplier_doc.get('company_name', 'N/A')}")
        
        chatbot = DynamicChatBot()
        test_session = "objectid_test_001"
        
        # Step 1: User wants to retrieve their supplier details
        print(f"\n📝 Step 1: User requests supplier details with ObjectId")
        query = f"_id {object_id} this is my id i already register as supplier. i want my details"
        result1 = chatbot.process_message(query, test_session)
        print(f"Status: {result1.get('status')}")
        print(f"Response: {result1.get('response', '')[:200]}...")
        
        # Step 2: Provide authentication
        print(f"\n🔐 Step 2: Provide employee authentication")
        result2 = chatbot.process_message("EMP001", test_session)
        print(f"Status: {result2.get('status')}")
        print(f"Response: {result2.get('response', '')[:200]}...")
        
        # Step 3: Retry the document query
        print(f"\n🔍 Step 3: Retry document retrieval after authentication")
        result3 = chatbot.process_message(query, test_session)
        print(f"Status: {result3.get('status')}")
        print(f"Response: {result3.get('response', '')[:300]}...")
        
        if result3.get('status') == 'query_completed':
            print("✅ SUCCESS: Document retrieved successfully!")
        elif "Error" in result3.get('response', ''):
            print("❌ ERROR: Still having issues with document retrieval")
        else:
            print("🔄 PROCESSING: Query is being processed")
            
    else:
        print("❌ No supplier documents found in database")
    
    print("\n" + "=" * 60)
    print("🎯 ObjectId Retrieval Test Complete")

if __name__ == "__main__":
    test_objectid_retrieval()