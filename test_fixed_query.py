#!/usr/bin/env python3
"""
Test Fixed Query Processing
Purpose: Test if the enhanced Query Node correctly processes document ID queries
"""

import requests
import json

def test_fixed_query():
    """Test the fixed document ID query processing"""
    
    print("🔧 Testing Fixed Document ID Query")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    document_id = "68e116d1b88401b56ae6c4ca"
    
    # Test the user's exact problematic query
    test_queries = [
        "this is my document id 68e116d1b88401b56ae6c4ca.i want my details",
        f"Show me document ID {document_id} details",
        f"Get my customer support ticket for ID {document_id}"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Simulate the complete session flow
            session_data = {
                "message": query,
                "user_id": "EMP001",
                "session_context": {
                    "employee_id": "EMP001",
                    "user_validated": True
                }
            }
            
            response = requests.post(f"{base_url}/chat", 
                                   json=session_data, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"   ✅ Status: {response.status_code}")
                
                # Check for success indicators
                if '4 records' in response_text or 'records)' in response_text:
                    print(f"   ❌ ERROR: Still returning multiple records!")
                    print(f"   📄 Response: {response_text[:200]}...")
                elif 'likhith vinay' in response_text and 'TCK1001' in response_text:
                    print(f"   ✅ SUCCESS: Single record returned!")
                    print(f"   📄 Contains: Customer name and ticket ID")
                else:
                    print(f"   ⚠️  PARTIAL: Needs verification")
                    print(f"   📄 Response: {response_text[:200]}...")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Connection Error: {e}")
            print(f"   💡 Make sure server is running on {base_url}")
    
    print(f"\n🎯 EXPECTED RESULT:")
    print("=" * 60)
    print("✅ Query should return only 1 record")
    print("✅ Should show: likhith vinay, TCK1001, Login Issue")  
    print("❌ Should NOT show: 4 records, multiple tickets")
    print()
    print("🚀 If test passes, the fix is working!")
    print("🔧 If test fails, more debugging needed")

if __name__ == "__main__":
    test_fixed_query()