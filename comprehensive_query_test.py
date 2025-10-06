#!/usr/bin/env python3
"""
Comprehensive Query Testing Suite
Purpose: Test various query patterns to ensure the document ID fix works properly
"""

import requests
import json
import time
from datetime import datetime

class QueryTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session_id = None
        self.test_results = []
        
    def wait_for_server(self, max_attempts=10):
        """Wait for server to be ready"""
        print("🔄 Waiting for server to start...")
        for i in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                print(f"   Attempt {i+1}/{max_attempts}...")
                time.sleep(2)
        return False
    
    def authenticate(self):
        """Authenticate as EMP001"""
        print("\n🔐 Authenticating...")
        
        # Step 1: Start session
        response = self.send_message("hi")
        if not self._check_response(response, "Welcome to the Enterprise System"):
            return False
            
        # Step 2: Request support ticket access
        response = self.send_message("i already register as customer_support_ticket")
        if not self._check_response(response, "Authorization Required"):
            return False
            
        # Step 3: Provide employee ID
        response = self.send_message("EMP001")
        if not self._check_response(response, "Access Granted"):
            return False
            
        print("✅ Authentication successful!")
        return True
    
    def send_message(self, message):
        """Send a message to the chatbot"""
        try:
            data = {
                "message": message,
                "user_id": "test_user"
            }
            response = requests.post(f"{self.base_url}/chat", json=data, timeout=30)
            return response
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def _check_response(self, response, expected_keyword):
        """Check if response contains expected content"""
        if not response or response.status_code != 200:
            return False
        try:
            data = response.json()
            return expected_keyword.lower() in data.get('response', '').lower()
        except:
            return False
    
    def test_query(self, query_name, query_text, expected_result, should_be_single_record=False):
        """Test a specific query"""
        print(f"\n🧪 Testing: {query_name}")
        print(f"   Query: {query_text}")
        
        response = self.send_message(query_text)
        
        if not response:
            self.test_results.append({
                "name": query_name,
                "status": "FAILED",
                "reason": "No response from server"
            })
            print("   ❌ FAILED: No response")
            return False
        
        if response.status_code != 200:
            self.test_results.append({
                "name": query_name,
                "status": "FAILED", 
                "reason": f"HTTP {response.status_code}"
            })
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            return False
        
        try:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check for expected content
            if expected_result.lower() in response_text.lower():
                # Additional check for single record queries
                if should_be_single_record:
                    if "4 records" in response_text or "records)" in response_text.replace("1 record", ""):
                        self.test_results.append({
                            "name": query_name,
                            "status": "FAILED",
                            "reason": "Returned multiple records instead of single record"
                        })
                        print("   ❌ FAILED: Multiple records returned")
                        print(f"      Response: {response_text[:200]}...")
                        return False
                
                self.test_results.append({
                    "name": query_name,
                    "status": "PASSED",
                    "reason": "Expected content found"
                })
                print("   ✅ PASSED")
                return True
            else:
                self.test_results.append({
                    "name": query_name,
                    "status": "FAILED",
                    "reason": f"Expected '{expected_result}' not found"
                })
                print(f"   ❌ FAILED: Expected '{expected_result}' not found")
                print(f"      Response: {response_text[:200]}...")
                return False
                
        except Exception as e:
            self.test_results.append({
                "name": query_name,
                "status": "ERROR",
                "reason": str(e)
            })
            print(f"   ❌ ERROR: {e}")
            return False
    
    def run_tests(self):
        """Run comprehensive query tests"""
        print("🚀 Starting Comprehensive Query Tests")
        print("=" * 70)
        
        # Wait for server
        if not self.wait_for_server():
            print("❌ Server not responding. Make sure enhanced_api_chatbot.py is running.")
            return
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed")
            return
        
        # Test Cases
        test_cases = [
            {
                "name": "Original Problematic Query",
                "query": "this is my document id 68e116d1b88401b56ae6c4ca.i want my details",
                "expected": "likhith vinay",
                "single_record": True
            },
            {
                "name": "Alternative Document ID Format",
                "query": "Show me document ID 68e116d1b88401b56ae6c4ca details",
                "expected": "TCK1001",
                "single_record": True
            },
            {
                "name": "Short Document ID Query",
                "query": "Document 68e116d1b88401b56ae6c4ca information",
                "expected": "Login Issue",
                "single_record": True
            },
            {
                "name": "Ticket ID Query",
                "query": "Show me ticket TCK1001 details",
                "expected": "likhith vinay",
                "single_record": False  # May return multiple if ticket_id is not unique
            },
            {
                "name": "Customer Name Query",
                "query": "Show me all tickets for customer likhith vinay",
                "expected": "TCK1001",
                "single_record": False
            },
            {
                "name": "Status Query",
                "query": "Show me all Open tickets",
                "expected": "Open",
                "single_record": False
            },
            {
                "name": "Priority Query", 
                "query": "List all High priority tickets",
                "expected": "High",
                "single_record": False
            },
            {
                "name": "Generic List Query",
                "query": "Show me all customer support tickets",
                "expected": "records",
                "single_record": False
            }
        ]
        
        # Run each test
        for test_case in test_cases:
            success = self.test_query(
                test_case["name"],
                test_case["query"], 
                test_case["expected"],
                test_case.get("single_record", False)
            )
            time.sleep(1)  # Brief pause between tests
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = sum(1 for r in self.test_results if r["status"] == "FAILED")
        errors = sum(1 for r in self.test_results if r["status"] == "ERROR")
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"⚠️  ERRORS: {errors}/{total}")
        print()
        
        # Show failed tests
        if failed > 0 or errors > 0:
            print("🔍 FAILED/ERROR DETAILS:")
            for result in self.test_results:
                if result["status"] in ["FAILED", "ERROR"]:
                    print(f"   {result['status']}: {result['name']}")
                    print(f"      Reason: {result['reason']}")
            print()
        
        # Overall status
        if passed == total:
            print("🎉 ALL TESTS PASSED! The query system is working correctly.")
        elif passed >= total * 0.8:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("⚠️  Multiple tests failed. System needs debugging.")
        
        print("\n🎯 KEY TEST: Document ID Query")
        original_test = next((r for r in self.test_results if "Original Problematic" in r["name"]), None)
        if original_test:
            if original_test["status"] == "PASSED":
                print("✅ FIXED: Your original query now returns single record!")
            else:
                print("❌ ISSUE: Your original query still has problems")
                print(f"   Reason: {original_test['reason']}")

def main():
    tester = QueryTester()
    tester.run_tests()

if __name__ == "__main__":
    main()