#!/usr/bin/env python3
"""
Direct Query Node Test
Purpose: Test the query processing logic directly without web interface
"""

import sys
sys.path.append('.')

def test_query_processing():
    """Test the query processing logic directly"""
    
    print("🔧 Direct Query Node Testing")
    print("=" * 50)
    
    try:
        # Import the chatbot
        from dynamic_chatbot import DynamicChatBot
        
        # Create instance
        bot = DynamicChatBot()
        print("✅ Chatbot initialized")
        
        # Test the problematic query directly
        user_input = "this is my document id 68e116d1b88401b56ae6c4ca.i want my details"
        
        # Set up state as if user is authenticated
        state = {
            'user_validated': True,
            'employee_id': 'EMP001',
            'detected_task': 'customer_support_ticket',
            'operation_type': 'query',
            'query_type': 'find',
            'natural_query': user_input
        }
        
        print(f"\n🧪 Testing Query: {user_input}")
        print("-" * 50)
        
        # Test query processing
        result = bot._process_query_node(user_input, state, 'test_session')
        
        print(f"Status: {result.get('status')}")
        response = result.get('response', '')
        
        # Check the response
        if '4 records' in response:
            print("❌ FAILED: Still returning 4 records")
            print("   Issue: MongoDB query not properly filtering by document ID")
        elif 'likhith vinay' in response and 'TCK1001' in response and ('1 record' in response or '**1.**' in response):
            print("✅ SUCCESS: Single record returned with correct data")
            print("   Contains: likhith vinay, TCK1001")
        elif 'likhith vinay' in response and 'TCK1001' in response:
            print("✅ PARTIAL SUCCESS: Correct data found")
            print("   Note: Check if it's truly single record")
        else:
            print("⚠️  UNKNOWN RESULT")
            print(f"   Response preview: {response[:200]}...")
        
        # Additional diagnostic info
        print(f"\nDiagnostic Info:")
        print(f"- Response length: {len(response)} characters")
        print(f"- Contains 'records': {'records' in response}")
        print(f"- Contains 'likhith': {'likhith' in response}")
        print(f"- Contains 'TCK1001': {'TCK1001' in response}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("💡 Make sure MongoDB is running and all dependencies are installed")

def test_mongodb_query_directly():
    """Test MongoDB query directly to verify data exists"""
    
    print("\n🔍 Direct MongoDB Test")
    print("-" * 30)
    
    try:
        from db import init_db, get_database
        from bson import ObjectId
        
        # Initialize and get database
        init_db()
        db = get_database()
        collection = db['customer_support_ticket']
        
        # Test the specific document ID
        doc_id = "68e116d1b88401b56ae6c4ca"
        obj_id = ObjectId(doc_id)
        
        # Query the specific document
        result = collection.find_one({"_id": obj_id})
        
        if result:
            print("✅ Document found in database")
            print(f"   Customer: {result.get('customer_name')}")
            print(f"   Ticket: {result.get('ticket_id')}")
            print(f"   Issue: {result.get('issue_type')}")
        else:
            print("❌ Document not found in database")
            print("   This could explain why the query isn't working")
        
        # Also check total count
        total = collection.count_documents({})
        print(f"   Total documents in collection: {total}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_query_processing()
    test_mongodb_query_directly()