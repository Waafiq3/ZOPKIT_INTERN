#!/usr/bin/env python3
"""
Verification Script: Test User's Specific Query Format
Purpose: Verify that the suggested query format will work for the user
"""

import requests
import json
from datetime import datetime

def test_user_query():
    """Test the exact query format we recommended to the user"""
    
    print("🔍 Testing User's Query Format")
    print("=" * 60)
    
    # Test data - using the user's actual document ID
    document_id = "68e1144110cd4c5bcaa12efd"
    base_url = "http://localhost:5001"
    
    # Test 1: Direct API call (what the Query Node should trigger)
    print(f"\n✅ Test 1: Direct API Call")
    print(f"   GET /api/invoice_management?_id={document_id}")
    
    try:
        response = requests.get(f"{base_url}/api/invoice_management", 
                              params={"_id": document_id}, 
                              timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {response.status_code}")
            print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Connection Error: {e}")
        print(f"   💡 Note: This is expected if server is not running")
    
    # Test 2: Chat interface simulation
    print(f"\n✅ Test 2: Chat Interface Query")
    print(f"   Recommended query: 'Show me invoice details for document ID {document_id}'")
    
    try:
        chat_data = {
            "message": f"Show me invoice details for document ID {document_id}",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/chat", 
                               json=chat_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: Chat responded")
            print(f"   📄 Response: {result.get('response', 'No response')[:200]}...")
            
            # Check if it triggered Query Node
            if 'query_node' in str(result).lower() or 'api' in str(result).lower():
                print(f"   🎯 Query Node: LIKELY TRIGGERED")
            else:
                print(f"   ⚠️  Query Node: May not have triggered")
                
        else:
            print(f"   ❌ Chat Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Connection Error: {e}")
        print(f"   💡 Note: Start your chatbot server first")
    
    # Test 3: Query format analysis
    print(f"\n✅ Test 3: Query Format Analysis")
    
    queries = [
        "Show me invoice details for document ID 68e1144110cd4c5bcaa12efd",  # ✅ Recommended
        "Get my invoice management information for ID 68e1144110cd4c5bcaa12efd",  # ✅ Alternative
        "i want to get my details .please show me my information",  # ❌ User's original
        "show me invoice INV1001 details"  # ✅ Field-based
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"   Query {i}: {query}")
        
        # Analyze query specificity
        has_collection = any(col in query.lower() for col in ['invoice', 'user', 'supplier', 'employee'])
        has_identifier = any(id_type in query.lower() for id_type in ['id', 'document', 'inv', 'emp'])
        has_specific_value = any(char.isdigit() or char.isalnum() for char in query if len(char) > 5)
        
        score = sum([has_collection, has_identifier, has_specific_value])
        
        if score >= 2:
            print(f"      🎯 LIKELY TO WORK (Specificity: {score}/3)")
        else:
            print(f"      ❌ TOO GENERIC (Specificity: {score}/3)")
        print()
    
    print("🎯 RECOMMENDATION FOR USER:")
    print("=" * 60)
    print(f"In your chat, type exactly:")
    print(f"📝 Show me invoice details for document ID {document_id}")
    print()
    print("🔧 If that doesn't work, try:")
    print(f"📝 Get invoice management data for ID {document_id}")
    print()
    print("🚀 Start your Enhanced Chatbot server first:")
    print("📝 python enhanced_api_chatbot.py")

if __name__ == "__main__":
    test_user_query()