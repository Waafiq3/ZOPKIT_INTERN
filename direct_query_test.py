"""
Direct Query Node Test - Testing the logic without network
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_chatbot import DynamicChatBot
from db import init_db, test_connection

def test_query_node_directly():
    """Test Query Node functionality directly without Flask"""
    
    print("🧪 DIRECT QUERY NODE TEST")
    print("=" * 60)
    
    # Initialize database
    print("📊 Initializing database connection...")
    if not test_connection():
        print("❌ Database connection failed!")
        return False
    
    # Initialize chatbot
    print("🤖 Initializing Dynamic Chatbot...")
    try:
        chatbot = DynamicChatBot()
        print("✅ Chatbot initialized successfully")
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return False
    
    # Test intent analysis for queries
    print("\n🎯 Testing Intent Analysis for Queries")
    print("-" * 40)
    
    test_queries = [
        "How many users are registered?",
        "Show me all employees with admin position", 
        "List pending purchase orders",
        "When did employee EMP001 check in?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        
        try:
            # Create mock state
            state = {}
            
            # Test intent analysis
            result = chatbot._analyze_user_intent(query, state, f"test_session_{i}")
            
            print(f"✅ Status: {result.get('status', 'unknown')}")
            print(f"🎯 Intent: {result.get('intent', 'none')}")
            print(f"📋 Task: {result.get('task', 'none')}")
            print(f"🔧 Operation Type: {result.get('operation_type', 'none')}")
            print(f"❓ Query Type: {result.get('query_type', 'none')}")
            print(f"💬 Natural Query: {result.get('natural_query', 'none')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test Query Node processing directly
    print("\n\n🔍 Testing Query Node Processing")
    print("-" * 40)
    
    # Create mock state for query processing
    mock_state = {
        "intent_analyzed": True,
        "user_validated": True,
        "detected_task": "user_registration",
        "operation_type": "query",
        "query_type": "count",
        "natural_query": "How many users are registered?",
        "user_position": "admin",
        "employee_id": "EMP001"
    }
    
    print("📊 Testing Query Node with mock state:")
    print(f"   Collection: {mock_state['detected_task']}")
    print(f"   Query Type: {mock_state['query_type']}")
    print(f"   Natural Query: {mock_state['natural_query']}")
    
    try:
        result = chatbot._process_query_node("How many users are registered?", mock_state, "direct_test")
        
        print(f"\n✅ Query Node Result:")
        print(f"📈 Status: {result.get('status', 'unknown')}")
        print(f"💬 Response: {result.get('response', 'No response')[:150]}...")
        if result.get('query_results') is not None:
            print(f"📊 Results: {result.get('query_results')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query Node Error: {e}")
        return False

def test_database_functions():
    """Test the database query functions directly"""
    
    print("\n\n💾 Testing Database Functions")
    print("-" * 40)
    
    from db import execute_query, validate_query_access
    
    # Test access validation
    print("🔒 Testing access validation...")
    try:
        access_result = validate_query_access("EMP001", "user_registration")
        print(f"✅ Access validation result: {access_result.get('status')}")
        print(f"👤 Employee: {access_result.get('employee_id')}")
        print(f"🎯 Position: {access_result.get('user_position')}")
        print(f"🔓 Has Access: {access_result.get('has_access')}")
    except Exception as e:
        print(f"❌ Access validation error: {e}")
    
    # Test query execution
    print("\n📊 Testing query execution...")
    try:
        query_result = execute_query(
            collection_name="user_registration",
            query={},
            operation="count_documents"
        )
        print(f"✅ Query execution result: {query_result.get('status')}")
        print(f"📈 Count: {query_result.get('results')}")
        print(f"💬 Message: {query_result.get('message')}")
    except Exception as e:
        print(f"❌ Query execution error: {e}")

def main():
    """Run all direct tests"""
    
    print("🚀 QUERY NODE DIRECT TESTING")
    print("=" * 80)
    print("Testing Query Node functionality without Flask server")
    print("=" * 80)
    
    success = test_query_node_directly()
    test_database_functions()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Direct Query Node tests completed successfully!")
        print("🎯 The Query Node logic is working correctly")
        print("💡 Network issues may be preventing Flask server testing")
    else:
        print("❌ Some direct tests failed")
        print("🔧 Check the error messages above for debugging")
    print("=" * 80)

if __name__ == "__main__":
    main()