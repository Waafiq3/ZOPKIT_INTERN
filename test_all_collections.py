"""
Comprehensive Test Script for All 49 Collections
Tests both POST (storage) and GET (retrieval) operations
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
ENHANCED_CHATBOT_URL = "http://localhost:5001"
API_SERVER_URL = "http://localhost:5000"
TEST_SESSION_ID = "test_all_collections_session"
TEST_EMPLOYEE_ID = "EMP005"  # Using existing test employee

# All 49 collections with test data
COLLECTION_TEST_DATA = {
    "user_registration": {
        "post_message": "Register user: John Doe, email john.test@company.com, password secure123, phone 555-0123",
        "get_message": "Show me user details for john.test@company.com",
        "expected_endpoint": "/api/user_registration"
    },
    "supplier_registration": {
        "post_message": "Register supplier: TestCorp Inc, email contact@testcorp.com, business type corporation, tax ID 123456789",
        "get_message": "Show me supplier details for TestCorp Inc",
        "expected_endpoint": "/api/supplier_registration"
    },
    "role_management": {
        "post_message": "Create role: Test Admin role with permissions create_user, delete_user, view_reports",
        "get_message": "Show me role details for Test Admin",
        "expected_endpoint": "/api/role_management"
    },
    "performance_review": {
        "post_message": "Create performance review for employee EMP001, reviewer EMP005, rating excellent",
        "get_message": "Show me performance review for employee EMP001",
        "expected_endpoint": "/api/performance_review"
    },
    "audit_log_viewer": {
        "post_message": "Log audit entry: user EMP005 performed action login_attempt",
        "get_message": "Show me audit logs for user EMP005",
        "expected_endpoint": "/api/audit_log_viewer"
    },
    "health_and_safety_incident_reporting": {
        "post_message": "Report incident: slip and fall on 2025-10-04 at main office, minor injury",
        "get_message": "Show me incident reports for 2025-10-04",
        "expected_endpoint": "/api/health_and_safety_incident_reporting"
    },
    "grievance_management": {
        "post_message": "File grievance: employee EMP001 workplace harassment complaint, status pending",
        "get_message": "Show me grievances for employee EMP001",
        "expected_endpoint": "/api/grievance_management"
    },
    "travel_request": {
        "post_message": "Create travel request: employee EMP001 to New York for conference, status pending",
        "get_message": "Show me travel requests for employee EMP001",
        "expected_endpoint": "/api/travel_request"
    },
    "payment_processing": {
        "post_message": "Process payment: amount 5000, currency USD, customer CUST001",
        "get_message": "Show me payments for customer CUST001",
        "expected_endpoint": "/api/payment_processing"
    },
    "purchase_order": {
        "post_message": "Create purchase order: supplier SUP001, order date 2025-10-04, items laptops x5, total 7500",
        "get_message": "Show me purchase orders for supplier SUP001",
        "expected_endpoint": "/api/purchase_order"
    },
    "customer_feedback_management": {
        "post_message": "Record feedback: customer CUST001, type complaint, rating 2, issue with product quality",
        "get_message": "Show me feedback from customer CUST001",
        "expected_endpoint": "/api/customer_feedback_management"
    },
    "training_registration": {
        "post_message": "Register training: employee EMP001 for Python programming course, location online",
        "get_message": "Show me training registrations for employee EMP001",
        "expected_endpoint": "/api/training_registration"
    },
    "interview_scheduling": {
        "post_message": "Schedule interview: candidate CAND001 for software engineer position, type technical",
        "get_message": "Show me interviews for candidate CAND001",
        "expected_endpoint": "/api/interview_scheduling"
    },
    "chatbot_training_data": {
        "post_message": "Add training data: question 'How to reset password?', answer 'Contact IT support', category support",
        "get_message": "Show me training data for category support",
        "expected_endpoint": "/api/chatbot_training_data"
    },
    "expense_reimbursement": {
        "post_message": "Submit expense: employee EMP001, type travel, amount 250, description conference travel",
        "get_message": "Show me expenses for employee EMP001",
        "expected_endpoint": "/api/expense_reimbursement"
    },
    "user_onboarding": {
        "post_message": "Update onboarding: user EMP006, stage documentation_complete, progress 75%",
        "get_message": "Show me onboarding status for user EMP006",
        "expected_endpoint": "/api/user_onboarding"
    },
    "data_backup_and_restore": {
        "post_message": "Create backup: type full_backup, timestamp 2025-10-04T10:00:00Z, status completed",
        "get_message": "Show me backup records for 2025-10-04",
        "expected_endpoint": "/api/data_backup_and_restore"
    },
    "order_tracking": {
        "post_message": "Track order: order ID ORD001, customer CUST001, status shipped",
        "get_message": "Show me tracking for order ORD001",
        "expected_endpoint": "/api/order_tracking"
    },
    "knowledge_base": {
        "post_message": "Add knowledge: title 'Password Reset Guide', content 'Step by step instructions', category IT",
        "get_message": "Show me knowledge base articles for category IT",
        "expected_endpoint": "/api/knowledge_base"
    },
    "employee_exit_clearance": {
        "post_message": "Process exit: employee EMP007, last working day 2025-10-15, status pending_clearance",
        "get_message": "Show me exit clearance for employee EMP007",
        "expected_endpoint": "/api/employee_exit_clearance"
    },
    "invoice_management": {
        "post_message": "Create invoice: number INV001, customer CUST001, amount 3500, due date 2025-11-04",
        "get_message": "Show me invoices for customer CUST001",
        "expected_endpoint": "/api/invoice_management"
    },
    "shipping_management": {
        "post_message": "Create shipment: ID SHIP001, origin New York, destination California, status in_transit",
        "get_message": "Show me shipment details for SHIP001",
        "expected_endpoint": "/api/shipping_management"
    },
    "knowledge_transfer_kt_handover": {
        "post_message": "Create handover: project PROJ001, from employee EMP008, to employee EMP009, status in_progress",
        "get_message": "Show me handover details for project PROJ001",
        "expected_endpoint": "/api/knowledge_transfer_kt_handover"
    },
    "faq_management": {
        "post_message": "Add FAQ: question 'How to request time off?', answer 'Use the HR portal', category HR",
        "get_message": "Show me FAQs for category HR",
        "expected_endpoint": "/api/faq_management"
    },
    "shift_scheduling": {
        "post_message": "Schedule shift: employee EMP001, date 2025-10-05, time 9AM-5PM, location main office",
        "get_message": "Show me shifts for employee EMP001",
        "expected_endpoint": "/api/shift_scheduling"
    },
    "it_asset_allocation": {
        "post_message": "Allocate asset: laptop LAPTOP001 to employee EMP001, type computer equipment",
        "get_message": "Show me assets allocated to employee EMP001",
        "expected_endpoint": "/api/it_asset_allocation"
    },
    "contract_management": {
        "post_message": "Create contract: ID CONT001, vendor VendorCorp, value 50000, status active",
        "get_message": "Show me contracts with vendor VendorCorp",
        "expected_endpoint": "/api/contract_management"
    },
    "customer_support_ticket": {
        "post_message": "Create ticket: ID TICK001, customer CUST001, issue login problems, priority high",
        "get_message": "Show me tickets for customer CUST001",
        "expected_endpoint": "/api/customer_support_ticket"
    },
    "attendance_tracking": {
        "post_message": "Record attendance: employee EMP001, date 2025-10-04, check-in 9:00 AM, check-out 5:00 PM",
        "get_message": "Show me attendance for employee EMP001",
        "expected_endpoint": "/api/attendance_tracking"
    },
    "vendor_management": {
        "post_message": "Add vendor: ID VEND001, company TechSuppliers Inc, rating 4.5, contact vendor@techsuppliers.com",
        "get_message": "Show me vendor details for TechSuppliers Inc",
        "expected_endpoint": "/api/vendor_management"
    },
    "notification_settings": {
        "post_message": "Update notifications: user EMP001, type email_alerts, enabled true",
        "get_message": "Show me notification settings for user EMP001",
        "expected_endpoint": "/api/notification_settings"
    },
    "client_registration": {
        "post_message": "Register client: company ClientCorp, contact person John Smith, email john@clientcorp.com",
        "get_message": "Show me client details for ClientCorp",
        "expected_endpoint": "/api/client_registration"
    },
    "budget_planning": {
        "post_message": "Create budget: department IT, year 2025, amount 100000, category equipment",
        "get_message": "Show me budget for IT department",
        "expected_endpoint": "/api/budget_planning"
    },
    "recruitment_management": {
        "post_message": "Create position: title Software Engineer, department IT, status open, salary range 80k-120k",
        "get_message": "Show me open positions in IT department",
        "expected_endpoint": "/api/recruitment_management"
    },
    "equipment_maintenance": {
        "post_message": "Schedule maintenance: equipment EQUIP001, date 2025-10-10, type routine_check, technician TECH001",
        "get_message": "Show me maintenance schedule for equipment EQUIP001",
        "expected_endpoint": "/api/equipment_maintenance"
    },
    "quality_assurance": {
        "post_message": "Record QA check: product PROD001, inspector EMP005, result passed, date 2025-10-04",
        "get_message": "Show me QA records for product PROD001",
        "expected_endpoint": "/api/quality_assurance"
    },
    "compliance_monitoring": {
        "post_message": "Log compliance: regulation GDPR, status compliant, last_audit 2025-09-01, next_review 2025-12-01",
        "get_message": "Show me compliance status for GDPR",
        "expected_endpoint": "/api/compliance_monitoring"
    },
    "document_management": {
        "post_message": "Upload document: title 'Employee Handbook', type policy, version 1.2, author EMP005",
        "get_message": "Show me documents of type policy",
        "expected_endpoint": "/api/document_management"
    },
    "project_management": {
        "post_message": "Create project: name 'Website Redesign', manager EMP005, start_date 2025-10-01, status active",
        "get_message": "Show me projects managed by EMP005",
        "expected_endpoint": "/api/project_management"
    },
    "inventory_management": {
        "post_message": "Update inventory: item ITEM001, quantity 150, location warehouse_A, category electronics",
        "get_message": "Show me inventory in warehouse_A",
        "expected_endpoint": "/api/inventory_management"
    },
    "time_tracking": {
        "post_message": "Log time: employee EMP001, project PROJ001, hours 8, date 2025-10-04, activity development",
        "get_message": "Show me time logs for employee EMP001",
        "expected_endpoint": "/api/time_tracking"
    },
    "security_incident_response": {
        "post_message": "Report incident: type data_breach, severity high, reported_by EMP005, date 2025-10-04",
        "get_message": "Show me security incidents reported by EMP005",
        "expected_endpoint": "/api/security_incident_response"
    },
    "facility_management": {
        "post_message": "Schedule facility: room CONF001, date 2025-10-05, time 10:00-12:00, purpose team meeting",
        "get_message": "Show me facility bookings for room CONF001",
        "expected_endpoint": "/api/facility_management"
    },
    "communication_logs": {
        "post_message": "Log communication: from EMP005, to CUST001, type email, subject 'Project Update', date 2025-10-04",
        "get_message": "Show me communications from EMP005",
        "expected_endpoint": "/api/communication_logs"
    },
    "workflow_automation": {
        "post_message": "Create workflow: name 'Invoice Approval', trigger new_invoice, steps approve,process,notify",
        "get_message": "Show me workflow details for Invoice Approval",
        "expected_endpoint": "/api/workflow_automation"
    },
    "resource_allocation": {
        "post_message": "Allocate resource: resource DEV_SERVER, project PROJ001, allocated_by EMP005, duration 30_days",
        "get_message": "Show me resource allocations for project PROJ001",
        "expected_endpoint": "/api/resource_allocation"
    },
    "survey_management": {
        "post_message": "Create survey: title 'Employee Satisfaction', type feedback, created_by EMP005, active true",
        "get_message": "Show me surveys created by EMP005",
        "expected_endpoint": "/api/survey_management"
    },
    "license_management": {
        "post_message": "Track license: software Office365, quantity 100, expiry 2026-01-01, assigned_to IT_DEPT",
        "get_message": "Show me licenses for IT department",
        "expected_endpoint": "/api/license_management"
    },
    "event_management": {
        "post_message": "Plan event: name 'Annual Conference', date 2025-12-15, location main_auditorium, organizer EMP005",
        "get_message": "Show me events organized by EMP005",
        "expected_endpoint": "/api/event_management"
    }
}

def test_collection(collection_name: str, test_data: Dict[str, str]) -> Dict[str, Any]:
    """Test a single collection for both POST and GET operations"""
    print(f"\n{'='*60}")
    print(f"Testing Collection: {collection_name}")
    print(f"{'='*60}")
    
    results = {
        "collection": collection_name,
        "post_test": {"success": False, "api_called": False, "stored": False, "error": None},
        "get_test": {"success": False, "api_called": False, "retrieved": False, "error": None}
    }
    
    try:
        # Test POST operation (data storage)
        print(f"\n1. Testing POST operation...")
        print(f"Message: {test_data['post_message']}")
        
        post_response = requests.post(
            f"{ENHANCED_CHATBOT_URL}/chat",
            json={
                "message": test_data['post_message'],
                "session_id": f"{TEST_SESSION_ID}_{collection_name}_post"
            },
            timeout=30
        )
        
        if post_response.status_code == 200:
            post_result = post_response.json()
            print(f"✅ POST Response Status: {post_result.get('status', 'unknown')}")
            
            # Check if API was called or database was used
            response_text = post_result.get('response', '').lower()
            if 'api endpoint' in response_text or 'calling api' in response_text:
                results["post_test"]["api_called"] = True
                print(f"🌐 API endpoint was called")
            
            if 'saved' in response_text or 'success' in response_text or 'document id' in response_text:
                results["post_test"]["stored"] = True
                results["post_test"]["success"] = True
                print(f"💾 Data stored successfully")
        
        time.sleep(2)  # Brief pause between requests
        
        # Test GET operation (data retrieval)
        print(f"\n2. Testing GET operation...")
        print(f"Message: {test_data['get_message']}")
        
        get_response = requests.post(
            f"{ENHANCED_CHATBOT_URL}/chat",
            json={
                "message": test_data['get_message'],
                "session_id": f"{TEST_SESSION_ID}_{collection_name}_get"
            },
            timeout=30
        )
        
        if get_response.status_code == 200:
            get_result = get_response.json()
            print(f"✅ GET Response Status: {get_result.get('status', 'unknown')}")
            
            # Check if API was called or database was used
            response_text = get_result.get('response', '').lower()
            if 'api endpoint' in response_text or 'calling api' in response_text:
                results["get_test"]["api_called"] = True
                print(f"🌐 API endpoint was called")
            
            if 'found' in response_text or 'results' in response_text or 'details' in response_text:
                results["get_test"]["retrieved"] = True
                results["get_test"]["success"] = True
                print(f"📊 Data retrieved successfully")
    
    except Exception as e:
        print(f"❌ Error testing {collection_name}: {str(e)}")
        results["post_test"]["error"] = str(e)
        results["get_test"]["error"] = str(e)
    
    return results

def run_all_tests():
    """Run tests for all 49 collections"""
    print("🚀 Starting Comprehensive Test for All 49 Collections")
    print("="*80)
    
    # First authenticate with EMP005
    auth_response = requests.post(
        f"{ENHANCED_CHATBOT_URL}/chat",
        json={
            "message": "EMP005",
            "session_id": f"{TEST_SESSION_ID}_auth"
        },
        timeout=10
    )
    
    if auth_response.status_code == 200:
        print("✅ Authenticated as EMP005")
    else:
        print("⚠️ Authentication may have failed, continuing anyway...")
    
    time.sleep(2)
    
    all_results = []
    successful_collections = 0
    api_called_count = 0
    
    for collection_name, test_data in COLLECTION_TEST_DATA.items():
        try:
            result = test_collection(collection_name, test_data)
            all_results.append(result)
            
            if result["post_test"]["success"] or result["get_test"]["success"]:
                successful_collections += 1
            
            if result["post_test"]["api_called"] or result["get_test"]["api_called"]:
                api_called_count += 1
                
            time.sleep(1)  # Brief pause between collections
            
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Critical error testing {collection_name}: {e}")
            continue
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY REPORT")
    print("="*80)
    print(f"Total Collections Tested: {len(all_results)}")
    print(f"Successfully Processed: {successful_collections}")
    print(f"API Calls Attempted: {api_called_count}")
    print(f"Success Rate: {(successful_collections/len(all_results)*100):.1f}%")
    
    print(f"\n📋 Detailed Results:")
    print("-" * 80)
    for result in all_results:
        collection = result["collection"]
        post_status = "✅" if result["post_test"]["success"] else "❌"
        get_status = "✅" if result["get_test"]["success"] else "❌"
        api_status = "🌐" if (result["post_test"]["api_called"] or result["get_test"]["api_called"]) else "🔗"
        
        print(f"{collection:35} | POST:{post_status} GET:{get_status} API:{api_status}")
    
    # Save detailed results to file
    with open('test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to 'test_results.json'")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()