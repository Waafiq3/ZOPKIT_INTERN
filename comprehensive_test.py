"""
Comprehensive Query Node Testing Guide
Tests all aspects of the Query Node integration
"""

import requests
import json
import time
from datetime import datetime

class QueryNodeTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.chat_url = f"{base_url}/chat"
        self.query_url = f"{base_url}/api/query"
        self.health_url = f"{base_url}/health"
        
    def test_server_health(self):
        """Test if the server is running and healthy"""
        print("🏥 Testing Server Health")
        print("-" * 30)
        
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and healthy")
                return True
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running or not accessible")
            print(f"💡 Make sure to run: python enhanced_api_chatbot.py")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_direct_query_api(self):
        """Test the direct /api/query endpoint"""
        print("\n🔍 Testing Direct Query API")
        print("-" * 30)
        
        test_cases = [
            {
                "name": "Count Query - User Registration",
                "data": {
                    "query": "How many users are registered?",
                    "collection": "user_registration",
                    "employee_id": "EMP001"
                },
                "expected_status": 200
            },
            {
                "name": "Find Query - Admin Users",
                "data": {
                    "query": "Show me all users with admin position",
                    "collection": "user_registration", 
                    "employee_id": "EMP001"
                },
                "expected_status": 200
            },
            {
                "name": "Access Denied Test - Invalid Employee",
                "data": {
                    "query": "Show all data",
                    "collection": "user_registration",
                    "employee_id": "INVALID123"
                },
                "expected_status": 403
            }
        ]
        
        results = []
        for test in test_cases:
            print(f"\n🧪 {test['name']}")
            try:
                response = requests.post(self.query_url, json=test['data'], timeout=30)
                
                if response.status_code == test['expected_status']:
                    print(f"✅ Status Code: {response.status_code} (Expected)")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"📊 Status: {result.get('status')}")
                        print(f"👤 Employee: {result.get('employee_id')}")
                        print(f"🎯 Position: {result.get('user_position')}")
                        if result.get('query_results') is not None:
                            print(f"📈 Results: {result.get('query_results')}")
                        print(f"💬 Response: {result.get('response', '')[:100]}...")
                    else:
                        result = response.json()  
                        print(f"🔒 Access Control: {result.get('response', '')[:100]}...")
                    
                    results.append({"test": test['name'], "status": "PASS"})
                else:
                    print(f"❌ Status Code: {response.status_code} (Expected: {test['expected_status']})")
                    print(f"📝 Response: {response.text[:200]}...")
                    results.append({"test": test['name'], "status": "FAIL"})
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({"test": test['name'], "status": "ERROR", "error": str(e)})
        
        return results
    
    def test_chat_integration(self):
        """Test Query Node through the chat interface"""
        print("\n💬 Testing Chat Integration")
        print("-" * 30)
        
        test_queries = [
            "How many users are registered in the system?",
            "Show me all employees",
            "List purchase orders",
            "When did employee EMP001 check in?",
            "How many training sessions are scheduled?"
        ]
        
        results = []
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Chat Test {i}: {query}")
            
            try:
                response = requests.post(self.chat_url, json={
                    "message": query,
                    "session_id": f"test_chat_{i}"
                }, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Status: {result.get('status')}")
                    print(f"🎯 Intent: {result.get('intent', 'None')}")
                    print(f"📋 Task: {result.get('task', 'None')}")
                    print(f"💬 Response: {result.get('response', '')[:150]}...")
                    
                    # Check if it detected query operation
                    if 'query' in str(result.get('operation_type', '')).lower():
                        print("🔍 ✅ Query operation detected correctly")
                    elif 'authorization' in result.get('status', ''):
                        print("🔐 ✅ Authorization flow triggered (expected for queries)")
                    
                    results.append({"query": query, "status": "PASS"})
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text[:100]}...")
                    results.append({"query": query, "status": "FAIL"})
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({"query": query, "status": "ERROR", "error": str(e)})
        
        return results
    
    def test_access_control(self):
        """Test role-based access control"""
        print("\n🔒 Testing Access Control")
        print("-" * 30)
        
        access_tests = [
            {
                "employee_id": "EMP001",
                "expected": "Admin - Full Access",
                "collection": "user_registration"
            },
            {
                "employee_id": "EMP002", 
                "expected": "HR Manager - HR Access",
                "collection": "employee_leave_request"
            },
            {
                "employee_id": "INVALID999",
                "expected": "Invalid Employee - Access Denied", 
                "collection": "user_registration"
            }
        ]
        
        results = []
        for test in access_tests:
            print(f"\n🧪 Testing {test['employee_id']} - {test['expected']}")
            
            try:
                response = requests.post(self.query_url, json={
                    "query": "Test access query",
                    "collection": test['collection'],
                    "employee_id": test['employee_id']
                }, timeout=30)
                
                print(f"📊 HTTP Status: {response.status_code}")
                result = response.json()
                print(f"🎯 Result: {result.get('status')}")
                print(f"💬 Message: {result.get('response', '')[:100]}...")
                
                if test['employee_id'] == "INVALID999":
                    if response.status_code == 403 or 'not found' in result.get('response', '').lower():
                        print("✅ Access correctly denied for invalid employee")
                        results.append({"test": test['expected'], "status": "PASS"})
                    else:
                        print("❌ Should have denied access")
                        results.append({"test": test['expected'], "status": "FAIL"})
                else:
                    if response.status_code == 200:
                        print("✅ Access granted for valid employee")
                        results.append({"test": test['expected'], "status": "PASS"})
                    else:
                        print("❌ Access should have been granted")
                        results.append({"test": test['expected'], "status": "FAIL"})
                        
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({"test": test['expected'], "status": "ERROR", "error": str(e)})
        
        return results
    
    def test_database_operations(self):
        """Test database operations directly"""
        print("\n💾 Testing Database Operations")
        print("-" * 30)
        
        try:
            # Import and test database functions directly
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            from db import execute_query, validate_query_access
            
            # Test query execution
            print("📊 Testing execute_query function...")
            result = execute_query("user_registration", {}, "count_documents")
            print(f"✅ Count query result: {result.get('results')} documents")
            
            # Test access validation  
            print("\n🔒 Testing validate_query_access function...")
            access = validate_query_access("EMP001", "user_registration")
            print(f"✅ Access validation: {access.get('has_access')} for {access.get('employee_id')}")
            print(f"🎯 Position: {access.get('user_position')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database test error: {e}")
            return False
    
    def run_complete_test_suite(self):
        """Run all tests and provide summary"""
        print("🚀 QUERY NODE COMPLETE TEST SUITE")
        print("=" * 80)
        print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test server health first
        if not self.test_server_health():
            print("\n❌ Server is not running. Please start the server first:")
            print("   python enhanced_api_chatbot.py")
            return False
        
        # Run all test suites
        api_results = self.test_direct_query_api()
        chat_results = self.test_chat_integration()
        access_results = self.test_access_control()
        db_working = self.test_database_operations()
        
        # Print summary
        print("\n\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # API Tests Summary
        api_pass = sum(1 for r in api_results if r['status'] == 'PASS')
        print(f"🔍 Direct API Tests: {api_pass}/{len(api_results)} passed")
        for result in api_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['test']}")
        
        # Chat Tests Summary  
        chat_pass = sum(1 for r in chat_results if r['status'] == 'PASS')
        print(f"\n💬 Chat Integration Tests: {chat_pass}/{len(chat_results)} passed")
        for result in chat_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['query'][:50]}...")
        
        # Access Control Summary
        access_pass = sum(1 for r in access_results if r['status'] == 'PASS')
        print(f"\n🔒 Access Control Tests: {access_pass}/{len(access_results)} passed")
        for result in access_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"  
            print(f"   {status_icon} {result['test']}")
        
        # Database Tests
        db_icon = "✅" if db_working else "❌"
        print(f"\n💾 Database Operations: {db_icon} {'Working' if db_working else 'Failed'}")
        
        # Overall Assessment
        total_tests = len(api_results) + len(chat_results) + len(access_results) + (1 if db_working else 0)
        total_passed = api_pass + chat_pass + access_pass + (1 if db_working else 0)
        
        print(f"\n🎯 OVERALL RESULT: {total_passed}/{total_tests} tests passed")
        
        if total_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Query Node is working perfectly!")
            print("✅ Your system is ready for production and interviews!")
        elif total_passed >= total_tests * 0.8:
            print("⚠️ Most tests passed! Minor issues detected.")
            print("🔧 Check failed tests above for debugging.")
        else:
            print("❌ Multiple test failures detected.")
            print("🛠️ System needs debugging before production use.")
        
        print("=" * 80)
        return total_passed == total_tests

def main():
    tester = QueryNodeTester()
    success = tester.run_complete_test_suite()
    
    if not success:
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Make sure MongoDB is running")
        print("2. Start the server: python enhanced_api_chatbot.py") 
        print("3. Check for any error messages in the server console")
        print("4. Ensure all dependencies are installed")

if __name__ == "__main__":
    main()