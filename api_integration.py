"""
API Integration Layer for Dynamic Chatbot
Replaces direct database calls with API endpoint calls
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# API configuration
GENERIC_API_URL = "http://localhost:8000"
API_TIMEOUT = 10

# Collection schemas - defines required and optional fields for each collection
COLLECTION_SCHEMAS = {
    "user_registration": {"required": ["email", "first_name", "last_name"], "optional": ["phone", "position", "employee_id"]},
    "supplier_registration": {"required": ["company_name", "contact_email", "requesting_user_id"], "optional": ["phone", "business_type"]},
    "performance_review": {"required": ["employee_id", "reviewer_id"], "optional": ["rating"]},
    "audit_log_viewer": {"required": ["user_id", "action"], "optional": ["timestamp"]},
    "health_and_safety_incident_reporting": {"required": ["incident_date", "location"], "optional": ["description"]},
    "grievance_management": {"required": ["employee_id", "grievance_type"], "optional": ["status"]},
    "travel_request": {"required": ["employee_id", "destination"], "optional": ["status"]},
    "payment_processing": {"required": ["amount", "currency"], "optional": ["customer_id"]},
    "purchase_order": {"required": ["supplier_id", "order_date"], "optional": ["status"]},
    "customer_feedback_management": {"required": ["customer_id", "feedback_type"], "optional": ["rating"]},
    "training_registration": {"required": ["employee_id", "training_program"], "optional": ["location"]},
    "interview_scheduling": {"required": ["candidate_id", "position"], "optional": ["interview_type"]},
    "chatbot_training_data": {"required": ["question", "answer"], "optional": ["category"]},
    "expense_reimbursement": {"required": ["employee_id", "expense_type"], "optional": ["amount"]},
    "user_onboarding": {"required": ["user_id", "onboarding_stage"], "optional": ["progress"]},
    "data_backup_and_restore": {"required": ["backup_type", "timestamp"], "optional": ["status"]},
    "order_tracking": {"required": ["order_id", "customer_id"], "optional": ["status"]},
    "knowledge_base": {"required": ["title", "content"], "optional": ["category"]},
    "role_management": {"required": ["role_name", "permissions"], "optional": ["description"]},
    "employee_exit_clearance": {"required": ["employee_id", "last_working_day"], "optional": ["status"]},
    "invoice_management": {"required": ["invoice_number", "customer_id"], "optional": ["amount"]},
    "shipping_management": {"required": ["shipment_id", "origin"], "optional": ["destination"]},
    "knowledge_transfer_kt_handover": {"required": ["project_id", "from_employee"], "optional": ["status"]},
    "faq_management": {"required": ["question", "answer"], "optional": ["category"]},
    "shift_scheduling": {"required": ["employee_id", "shift_date"], "optional": ["location"]},
    "it_asset_allocation": {"required": ["asset_id", "employee_id"], "optional": ["asset_type"]},
    "contract_management": {"required": ["contract_id", "vendor_name"], "optional": ["status"]},
    "customer_support_ticket": {"required": ["ticket_id", "customer_id"], "optional": ["status"]},
    "attendance_tracking": {"required": ["employee_id", "date"], "optional": ["check_in_time"]},
    "vendor_management": {"required": ["vendor_id", "company_name"], "optional": ["rating"]},
    "notification_settings": {"required": ["user_id", "notification_type"], "optional": ["enabled"]},
    "client_registration": {"required": ["company_name", "contact_person"], "optional": ["email"]},
    "product_catalog": {"required": ["product_id", "name"], "optional": ["price"]},
    "inventory_management": {"required": ["item_id", "item_name"], "optional": ["current_stock"]},
    "access_control": {"required": ["user_id", "resource"], "optional": ["permission_level"]},
    "employee_leave_request": {"required": ["employee_id", "leave_type"], "optional": ["start_date"]},
    "project_assignment": {"required": ["project_id", "employee_id"], "optional": ["role"]},
    "order_placement": {"required": ["customer_id", "items"], "optional": ["total_amount"]},
    "marketing_campaign_management": {"required": ["campaign_name", "start_date"], "optional": ["budget"]},
    "meeting_scheduler": {"required": ["meeting_title", "organizer_id"], "optional": ["start_time"]},
    "payroll_management": {"required": ["employee_id", "pay_period"], "optional": ["gross_salary"]},
    "user_activation": {"required": ["user_id", "activation_token"], "optional": ["status"]},
    "compliance_report": {"required": ["report_type", "reporting_period"], "optional": ["compliance_status"]},
    "warehouse_management": {"required": ["warehouse_id", "operation_type"], "optional": ["item_id"]},
    "recruitment_portal": {"required": ["job_id", "candidate_id"], "optional": ["application_date"]},
    "system_audit_and_compliance_dashboard": {"required": ["audit_type", "timestamp"], "optional": ["system_component"]},
    "offer_letter_generation": {"required": ["candidate_id", "position"], "optional": ["salary"]},
    "announcements_notice_board": {"required": ["title", "content"], "optional": ["posted_by"]},
    "system_configuration": {"required": ["config_key", "config_value"], "optional": ["module"]}
}

# Field mappings - Maps schema field names to display collection field names  
FIELD_MAPPINGS = {
    # Commented out for now - using SIMPLE_FIELD_MAPPINGS instead
}
#     "user_registration": {
#         "email": "Email",
#         "first_name": "First Name", 
#         "last_name": "Last Name",
#         "phone": "Phone",
#         "position": "Position",
#         "employee_id": "Employee ID"
#     },
#     "supplier_registration": {
#         "company_name": "Company Name",
#         "contact_email": "Contact Email",
#         "phone": "Phone",
#         "business_type": "Business Type",
#         "requesting_user_id": "Requesting User ID"
#     },
#     "performance_review": {
#         "employee_id": "Employee ID",
#         "reviewer_id": "Reviewer ID", 
#         "rating": "Rating"
#     },
#     "purchase_order": {
#         "supplier_id": "Vendor ID",
#         "order_date": "Order Date",
#         "status": "Status",
#         "items": "Product",
#         "quantity": "Quantity",
#         "po_id": "PO ID"
#     },
#     "training_registration": {
#         "employee_id": "Employee ID",
#         "training_program": "Training Name",
#         "start_date": "Date",
#         "location": "Location"
#     },
#     "employee_leave_request": {
#         "employee_id": "Employee ID",
#         "leave_type": "Leave Type",
#         "start_date": "Start Date",
#         "end_date": "End Date",
#         "reason": "Reason"
#     },
#     "payroll_management": {
#         "employee_id": "Employee ID",
#         "pay_period": "Pay Period",
#         "gross_salary": "Gross Salary",
#         "net_salary": "Net Salary"
#     },
#     "inventory_management": { 
#         "item_id": "Item ID",
#         "item_name": "Item Name",
#         "current_stock": "Current Stock",
#         "location": "Location"
#     },
#     "customer_support_ticket": {
#         "ticket_id": "Ticket ID",
#         "customer_id": "Customer ID",
#         "status": "Status",
#         "description": "Description"
#     },
#     "meeting_scheduler": {
#         "meeting_title": "Meeting Title",
#         "organizer_id": "Organizer ID",
#         "start_time": "Start Time",
#         "participants": "Participants"
#     },
#     "project_assignment": {
#         "project_id": "Project ID",
#         "employee_id": "Employee ID",
#         "role": "Role",
#         "start_date": "Start Date"
#     },
#     "expense_reimbursement": {
#         "employee_id": "Employee ID",
#         "expense_type": "Expense Type",
#         "amount": "Amount",
#         "description": "Description"
#     },
#     "access_control": {
#         "user_id": "User ID",
#         "resource": "Resource",
#         "permission_level": "Permission Level"
#     },
#     "vendor_management": {
#         "vendor_id": "Vendor ID",
#         "company_name": "Company Name",
#         "rating": "Rating",
#         "contact_info": "Contact Info"
#     },
#     "invoice_management": {
#         "invoice_number": "Invoice Number",
#         "customer_id": "Customer ID",
#         "amount": "Amount",
#         "due_date": "Due Date"
#     },
#     "attendance_tracking": {
#         "employee_id": "Employee ID",
#         "date": "Date",
#         "check_in_time": "Check In Time",
#         "check_out_time": "Check Out Time"
#     },
#     "interview_scheduling": {
#         "candidate_id": "Candidate ID",
#         "position": "Position",
#         "interview_type": "Interview Type",
#         "interview_date": "Interview Date"
#     },
#     "contract_management": {
#         "contract_id": "Contract ID",
#         "vendor_name": "Vendor Name",
#         "status": "Status",
#         "start_date": "Start Date"
#     },
#     "shift_scheduling": {
#         "employee_id": "Employee ID",
#         "shift_date": "Shift Date",
#         "location": "Location",
#         "shift_type": "Shift Type"
#     },
#     "travel_request": {
#         "employee_id": "Employee ID",
#         "destination": "Destination",
#         "status": "Status",
#         "travel_date": "Travel Date"
#     },
#     "order_tracking": {
#         "order_id": "Order ID",
#         "customer_id": "Customer ID",
#         "status": "Status",
#         "tracking_number": "Tracking Number"
#     },
#     "warehouse_management": {
#         "warehouse_id": "Warehouse ID",
#         "operation_type": "Operation Type",
#         "item_id": "Item ID",
#         "quantity": "Quantity"
#     },
#     "client_registration": {
#         "company_name": "Company Name",
#         "contact_person": "Contact Person",
#         "email": "Email",
#         "phone": "Phone"
#     },
#     "product_catalog": {
#         "product_id": "Product ID",
#         "name": "Name",
#         "price": "Price",
#         "category": "Category"
#     },
#     "notification_settings": {
#         "user_id": "User ID",
#         "notification_type": "Notification Type",
#         "enabled": "Enabled"
#     },
#     "knowledge_base": {
#         "title": "Title",
#         "content": "Content",
#         "category": "Category",
#         "author": "Author"
#     },
#     "role_management": {
#         "role_name": "Role Name",
#         "permissions": "Permissions",
#         "description": "Description"
#     },
#     "system_configuration": {
#         "config_key": "Config Key",
#         "config_value": "Config Value",
#         "module": "Module"
#     },
#     # Additional mappings for remaining collections
#     "audit_log_viewer": {
#         "user_id": "User ID",
#         "action": "Action",
#         "timestamp": "Timestamp"
#     },
#     "health_and_safety_incident_reporting": {
#         "incident_date": "Incident Date",
#         "location": "Location",
#         "description": "Description"
#     },
#     "grievance_management": {
#         "employee_id": "Employee ID",
#         "grievance_type": "Grievance Type",
#         "status": "Status"
#     },
#     "payment_processing": {
#         "amount": "Amount",
#         "currency": "Currency",
#         "customer_id": "Customer ID"
#     },
#     "customer_feedback_management": {
#         "customer_id": "Customer ID",
#         "feedback_type": "Feedback Type",
#         "rating": "Rating"
#     },
#     "chatbot_training_data": {
#         "question": "Question",
#         "answer": "Answer",
#         "category": "Category"
#     },
#     "user_onboarding": {
#         "user_id": "User ID",
#         "onboarding_stage": "Onboarding Stage",
#         "progress": "Progress"
#     },
#     "data_backup_and_restore": {
#         "backup_type": "Backup Type",
#         "timestamp": "Timestamp",
#         "status": "Status"
#     },
#     "employee_exit_clearance": {
#         "employee_id": "Employee ID",
#         "last_working_day": "Last Working Day",
#         "status": "Status"
#     },
#     "shipping_management": {
#         "shipment_id": "Shipment ID",
#         "origin": "Origin",
#         "destination": "Destination"
#     },
#     "knowledge_transfer_kt_handover": {
#         "project_id": "Project ID",
#         "from_employee": "From Employee",
#         "status": "Status"
#     },
#     "faq_management": {
#         "question": "Question",
#         "answer": "Answer",
#         "category": "Category"
#     },
#     "it_asset_allocation": {
#         "asset_id": "Asset ID",
#         "employee_id": "Employee ID",
#         "asset_type": "Asset Type"
#     },
#     "order_placement": {
#         "customer_id": "Customer ID",
#         "items": "Items",
#         "total_amount": "Total Amount"
#     },
#     "marketing_campaign_management": {
#         "campaign_name": "Campaign Name",
#         "start_date": "Start Date",
#         "budget": "Budget"
#     },
#     "user_activation": {
#         "user_id": "User ID",
#         "activation_token": "Activation Token",
#         "status": "Status"
#     },
#     "compliance_report": {
#         "report_type": "Report Type",
#         "reporting_period": "Reporting Period",
#         "compliance_status": "Compliance Status"
#     },
#     "recruitment_portal": {
#         "job_id": "Job ID",
#         "candidate_id": "Candidate ID",
#         "application_date": "Application Date"
#     },
#     "system_audit_and_compliance_dashboard": {
#         "audit_type": "Audit Type",
#         "timestamp": "Timestamp",
#         "system_component": "System Component"
#     },
#     "offer_letter_generation": {
#         "candidate_id": "Candidate ID",
#         "position": "Position",
#         "salary": "Salary"
#     },
#     "announcements_notice_board": {
#         "title": "Title",
#         "content": "Content",
#         "posted_by": "Posted By"
#     }
# }

# # Display collection name mappings
# DISPLAY_COLLECTION_NAMES = {
#     "user_registration": "User Registration",
#     "supplier_registration": "Supplier Registration", 
#     "performance_review": "Performance Review",
#     "audit_log_viewer": "Audit Log Viewer",
#     "health_and_safety_incident_reporting": "Health & Safety Incident Reporting",
#     "grievance_management": "Grievance Management",
#     "travel_request": "Travel Request",
#     "payment_processing": "Payment Processing",
#     "purchase_order": "Purchase Order",
#     "customer_feedback_management": "Customer Feedback Management",
#     "training_registration": "Training Registration",
#     "interview_scheduling": "Interview Scheduling",
#     "chatbot_training_data": "Chatbot Training Data",
#     "expense_reimbursement": "Expense Reimbursement",
#     "user_onboarding": "User Onboarding",
#     "data_backup_and_restore": "Data Backup & Restore",
#     "order_tracking": "Order Tracking",
#     "knowledge_base": "Knowledge Base",
#     "role_management": "Role Management",
#     "employee_exit_clearance": "Employee Exit Clearance",
#     "invoice_management": "Invoice Management",
#     "shipping_management": "Shipping Management",
#     "knowledge_transfer_kt_handover": "Knowledge Transfer (KT) Handover",
#     "faq_management": "FAQ Management",
#     "shift_scheduling": "Shift Scheduling",
#     "it_asset_allocation": "IT Asset Allocation",
#     "contract_management": "Contract Management",
#     "customer_support_ticket": "Customer Support Ticket",
#     "attendance_tracking": "Attendance Tracking",
#     "vendor_management": "Vendor Management",
#     "notification_settings": "Notification Settings",
#     "client_registration": "Client Registration",
#     "product_catalog": "Product Catalog",
#     "inventory_management": "Inventory Management",
#     "access_control": "Access Control",
#     "employee_leave_request": "Employee Leave Request",
#     "project_assignment": "Project Assignment",
#     "order_placement": "Order Placement",
#     "marketing_campaign_management": "Marketing Campaign Management",
#     "meeting_scheduler": "Meeting Scheduler",
#     "payroll_management": "Payroll Management",
#     "user_activation": "User Activation",
#     "compliance_report": "Compliance Report",
#     "warehouse_management": "Warehouse Management",
#     "recruitment_portal": "Recruitment Portal",
#     "system_audit_and_compliance_dashboard": "System Audit & Compliance Dashboard",
#     "offer_letter_generation": "Offer Letter Generation",
#     "announcements_notice_board": "Announcements/Notice Board",
#     "system_configuration": "System Configuration"
# }

# def transform_fields_to_display_format(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Transform document fields from schema format to display collection format
    
#     Args:
#         collection_name: Schema collection name
#         document: Document with schema field names
        
#     Returns:
#         Document with display collection field names
#     """
#     field_mapping = FIELD_MAPPINGS.get(collection_name, {})
    
#     if not field_mapping:
#         logger.debug(f"⚠️ No field mapping found for {collection_name}, using original fields")
#         return document
    
#     transformed = {}
#     for key, value in document.items():
#         # Transform field name if mapping exists, otherwise keep original
#         display_key = field_mapping.get(key, key)
#         transformed[display_key] = value
        
#         if display_key != key:
#             logger.debug(f"🔄 Field transformed: {key} → {display_key}")
    
#     # Add standard fields that display collections expect
#     if "Who Can Access" not in transformed:
#         transformed["Who Can Access"] = "Admin, HR Manager"
    
#     if "created_at" not in transformed and "Created At" not in transformed:
#         transformed["Created At"] = datetime.utcnow().isoformat()
    
#     if "updated_at" not in transformed and "Updated At" not in transformed:
#         transformed["Updated At"] = datetime.utcnow().isoformat()
    
#     logger.info(f"✅ Transformed {len(document)} fields to display format for {collection_name}")
#     return transformed

# def direct_db_insert(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Direct database insert using display collection names with field transformation
#     """
#     try:
#         from pymongo import MongoClient
#         from bson import ObjectId
        
#         # Get display collection name
#         display_collection_name = DISPLAY_COLLECTION_NAMES.get(collection_name, collection_name)
        
#         # Transform fields to display format
#         display_document = transform_fields_to_display_format(collection_name, document)
        
#         # Connect to MongoDB
#         client = MongoClient("mongodb://localhost:27017")
#         db = client.enterprise_db
        
#         logger.info(f"🔌 Using display collection: {display_collection_name} for schema: {collection_name}")
        
#         try:
#             # Try display collection first
#             collection = db[display_collection_name]
#             result = collection.insert_one(display_document)
            
#             logger.info(f"✅ Document inserted in {display_collection_name}: {result.inserted_id}")
#             return {
#                 "success": True,
#                 "inserted_id": str(result.inserted_id),
#                 "message": f"Document created successfully in {display_collection_name}",
#                 "collection_used": display_collection_name
#             }
            
#         except Exception as display_error:
#             logger.error(f"❌ Display collection insert failed: {display_error}")
            
#             # Fallback to original collection name with original fields
#             if display_collection_name != collection_name:
#                 logger.info(f"🔄 Falling back to original collection name")
#                 fallback_collection = db[collection_name]
#                 fallback_result = fallback_collection.insert_one(document)
                
#                 logger.info(f"✅ Document inserted in {collection_name}: {fallback_result.inserted_id}")
#                 return {
#                     "success": True,
#                     "inserted_id": str(fallback_result.inserted_id),
#                     "message": f"Document created successfully in {collection_name} (fallback)",
#                     "collection_used": collection_name
#                 }
#             else:
#                 raise display_error
                
#     except Exception as e:
#         logger.error(f"❌ Database insert failed: {e}")
#         return {
#             "success": False,
#             "message": f"Database error: {str(e)}",
#             "error": str(e)
#         }

# class APIIntegrationError(Exception):
#     """Custom exception for API integration errors"""
#     pass

# def call_api_endpoint(endpoint: str, data: dict) -> dict:
#     """
#     Call generic API endpoint and return result
    
#     Args:
#         endpoint: API endpoint path (e.g., 'user_registration')
#         data: Dictionary containing the data to send
        
#     Returns:
#         Dictionary with success status and result data
#     """
#     try:
#         url = f"{GENERIC_API_URL}/api/{endpoint}"
#         logger.info(f"🔌 Calling API: {url}")
#         logger.debug(f"📤 Request data: {data}")
        
#         response = requests.post(url, json=data, timeout=API_TIMEOUT)
        
#         logger.info(f"📥 API Response Status: {response.status_code}")
        
#         if response.status_code in [200, 201]:
#             api_result = response.json()
#             logger.info(f"✅ API call successful: {api_result}")
#             return {
#                 "success": True,
#                 "inserted_id": api_result.get("document_id") or api_result.get("id") or api_result.get("_id"),
#                 "message": api_result.get("message", "Document created successfully via API"),
#                 "api_response": api_result
#             }
#         else:
#             error_msg = f"API call failed: {response.status_code}"
#             try:
#                 error_detail = response.json()
#                 logger.error(f"❌ API Error: {error_detail}")
#                 error_msg = error_detail.get("detail", error_detail.get("message", response.text))
#             except:
#                 logger.error(f"❌ API Error: {response.text}")
#                 error_msg = response.text
                
#             return {
#                 "success": False,
#                 "message": error_msg,
#                 "error": error_msg,
#                 "status_code": response.status_code
#             }
            
#     except requests.exceptions.Timeout:
#         error_msg = f"API call timeout after {API_TIMEOUT} seconds"
#         logger.error(f"⏱️ {error_msg}")
#         return {
#             "success": False,
#             "message": error_msg,
#             "error": "timeout"
#         }
#     except requests.exceptions.ConnectionError as e:
#         error_msg = f"Cannot connect to API server at {GENERIC_API_URL}"
#         logger.error(f"🔌 {error_msg}: {e}")
#         return {
#             "success": False,
#             "message": error_msg,
#             "error": str(e)
#         }
#     except Exception as e:
#         logger.error(f"❌ Unexpected API call error: {e}", exc_info=True)
#         return {
#             "success": False,
#             "message": f"API connection error: {str(e)}",
#             "error": str(e)
#         }

# def validate_required_fields(collection_name: str, data: Dict[str, Any]) -> tuple:
#     """
#     Validate that required fields are present for the collection
    
#     Args:
#         collection_name: Name of the collection
#         data: Document data to validate
        
#     Returns:
#         Tuple of (is_valid, error_message, missing_fields)
#     """
#     schema = COLLECTION_SCHEMAS.get(collection_name)
    
#     if not schema:
#         logger.warning(f"⚠️ No schema defined for collection: {collection_name}")
#         return True, None, []
    
#     required_fields = schema.get("required", [])
#     missing_fields = []
    
#     for field in required_fields:
#         if field not in data or data[field] is None or data[field] == "":
#             missing_fields.append(field)
    
#     if missing_fields:
#         error_msg = f"Missing required fields for {collection_name}: {', '.join(missing_fields)}"
#         logger.error(f"❌ Validation failed: {error_msg}")
#         return False, error_msg, missing_fields
    
#     logger.info(f"✅ All required fields present for {collection_name}")
#     return True, None, []

# def get_collection_info(collection_name: str) -> Dict[str, Any]:
#     """
#     Get schema information for a collection
    
#     Args:
#         collection_name: Name of the collection
        
#     Returns:
#         Dictionary with schema info
#     """
#     schema = COLLECTION_SCHEMAS.get(collection_name)
#     if not schema:
#         return {
#             "exists": False,
#             "message": f"No schema found for {collection_name}"
#         }
    
#     return {
#         "exists": True,
#         "collection_name": collection_name,
#         "required_fields": schema.get("required", []),
#         "optional_fields": schema.get("optional", []),
#         "total_fields": len(schema.get("required", [])) + len(schema.get("optional", []))
#     }

# def clean_document_data(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Clean and prepare document data based on schema
#     Removes None values and validates field types
    
#     Args:
#         collection_name: Name of the collection
#         document: Document to clean
        
#     Returns:
#         Cleaned document
#     """
#     schema = COLLECTION_SCHEMAS.get(collection_name)
#     if not schema:
#         return document
    
#     allowed_fields = schema.get("required", []) + schema.get("optional", [])
#     cleaned = {}
    
#     for key, value in document.items():
#         # Keep the field if it's in the schema or if we don't have a schema
#         if key in allowed_fields or not schema:
#             # Skip None values and empty strings for optional fields
#             if value is not None and value != "":
#                 cleaned[key] = value
#             # Keep None/empty for required fields to catch validation errors
#             elif key in schema.get("required", []):
#                 cleaned[key] = value
    
#     logger.debug(f"🧹 Cleaned document: {len(document)} -> {len(cleaned)} fields")
#     return cleaned

# def auto_generate_missing_fields(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Auto-generate missing required fields for specific collections
    
#     Args:
#         collection_name: Schema collection name  
#         document: Original document data
        
#     Returns:
#         Document with auto-generated fields
#     """
#     import uuid
#     from datetime import datetime
    
#     # Create a copy to avoid modifying original
#     enhanced_doc = document.copy()
    
#     # Collection-specific field generation
#     if collection_name == "purchase_order":
#         # Generate PO ID if missing
#         if "po_id" not in enhanced_doc or not enhanced_doc["po_id"]:
#             enhanced_doc["po_id"] = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
#         # Extract items and quantity from existing fields or user message
#         if "items" not in enhanced_doc and "item" in enhanced_doc:
#             enhanced_doc["items"] = enhanced_doc["item"]
        
#         # Try to extract quantity from items string (e.g., "laptops x10" -> quantity: 10)
#         if "quantity" not in enhanced_doc and "items" in enhanced_doc:
#             import re
#             items_text = str(enhanced_doc.get("items", ""))
#             qty_match = re.search(r'x(\d+)', items_text, re.IGNORECASE)
#             if qty_match:
#                 enhanced_doc["quantity"] = int(qty_match.group(1))
#                 # Clean up items text (remove quantity part)
#                 enhanced_doc["items"] = re.sub(r'\s*x\d+', '', items_text).strip()
#             else:
#                 enhanced_doc["quantity"] = 1  # Default quantity
                
#         # Generate total amount if missing
#         if "total_amount" not in enhanced_doc:
#             # Try to extract from user message context if available
#             enhanced_doc["total_amount"] = 0.0
    
#     elif collection_name == "user_registration":
#         # Generate user ID if missing
#         if "user_id" not in enhanced_doc:
#             enhanced_doc["user_id"] = f"USER{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
#     # Add timestamps if missing
#     current_time = datetime.utcnow().isoformat()
#     if "created_at" not in enhanced_doc:
#         enhanced_doc["created_at"] = current_time
#     if "updated_at" not in enhanced_doc:
#         enhanced_doc["updated_at"] = current_time
    
#     logger.debug(f"🔧 Auto-generated fields for {collection_name}: {set(enhanced_doc.keys()) - set(document.keys())}")
#     return enhanced_doc

# def api_insert_document(collection_name: str, document: Dict[str, Any], 
#                         validate: bool = True) -> Dict[str, Any]:
#     """
#     Insert document using display collection with field transformation
    
#     Args:
#         collection_name: Schema/collection name (e.g., 'user_registration')
#         document: Document data to insert
#         validate: Whether to validate required fields (default: True)
        
#     Returns:
#         Dictionary with success status and result
#     """
    
#     logger.info(f"📝 Inserting document to collection: {collection_name}")
#     logger.debug(f"📄 Original document: {document}")
    
#     # Auto-generate missing required fields
#     document = auto_generate_missing_fields(collection_name, document)
    
#     # Clean document data
#     document = clean_document_data(collection_name, document)
    
#     # Validate required fields if requested
#     if validate:
#         is_valid, error_msg, missing = validate_required_fields(collection_name, document)
#         if not is_valid:
#             return {
#                 "success": False,
#                 "message": f"Validation error: {error_msg}",
#                 "error": error_msg,
#                 "missing_fields": missing
#             }
    
#     # Add metadata if not present
#     if "created_at" not in document:
#         document["created_at"] = datetime.utcnow().isoformat()
#     if "updated_at" not in document:
#         document["updated_at"] = datetime.utcnow().isoformat()
    
#     # First try direct database insert with display collection and field transformation
#     logger.info(f"🎯 Attempting direct insert with display collection for: {collection_name}")
#     db_result = direct_db_insert(collection_name, document)
    
#     if db_result["success"]:
#         logger.info(f"✅ Direct database insert successful: {db_result['inserted_id']}")
#         return db_result
    
#     # Fallback to API endpoint if direct insert fails
#     logger.warning(f"⚠️ Direct insert failed, falling back to API endpoint")
#     logger.debug(f"Direct insert error: {db_result.get('message', 'Unknown error')}")
    
#     # Use collection_name as endpoint
#     endpoint = collection_name
    
#     # Call API endpoint with original document
#     result = call_api_endpoint(endpoint, document)
    
#     if result["success"]:
#         logger.info(f"✅ API fallback successful - ID: {result.get('inserted_id')}")
#     else:
#         logger.error(f"❌ Both direct insert and API fallback failed: {result['message']}")
    
#     return result

# def api_check_supplier_eligibility(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Check supplier eligibility using API or fallback logic
    
#     Args:
#         supplier_data: Supplier information to check
        
#     Returns:
#         Dictionary with eligibility status
#     """
#     try:
#         # First validate required fields for supplier
#         required = ["company_name", "contact_email"]
#         missing = [f for f in required if f not in supplier_data or not supplier_data[f]]
        
#         if missing:
#             return {
#                 'eligible': False,
#                 'checks': {'missing_fields': missing},
#                 'reason': f'Missing required fields: {", ".join(missing)}'
#             }
        
#         # Try API endpoint
#         endpoint = "supplier_eligibility_check"
#         logger.info(f"🔍 Checking supplier eligibility")
        
#         url = f"{GENERIC_API_URL}/api/{endpoint}"
#         response = requests.post(url, json=supplier_data, timeout=API_TIMEOUT)
        
#         if response.status_code == 200:
#             result = response.json()
#             logger.info(f"✅ Eligibility check result: {result}")
#             return result
#         else:
#             logger.warning(f"⚠️ Eligibility API returned {response.status_code}, using fallback")
#             return _fallback_eligibility_check(supplier_data)
            
#     except requests.exceptions.ConnectionError:
#         logger.warning("⚠️ Cannot connect to eligibility API, using fallback")
#         return _fallback_eligibility_check(supplier_data)
#     except Exception as e:
#         logger.error(f"❌ Eligibility check error: {e}", exc_info=True)
#         return {
#             'eligible': False,
#             'checks': {},
#             'reason': f'Error during eligibility check: {str(e)}'
#         }

# def _fallback_eligibility_check(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
#     """Fallback eligibility check with basic validation"""
#     checks = {
#         "has_company_name": bool(supplier_data.get("company_name")),
#         "has_contact_email": bool(supplier_data.get("contact_email")),
#         "has_requesting_user": bool(supplier_data.get("requesting_user_id")),
#         "valid_email": "@" in str(supplier_data.get("contact_email", ""))
#     }
    
#     eligible = all(checks.values())
    
#     if not eligible:
#         failed = [k.replace("_", " ").title() for k, v in checks.items() if not v]
#         reason = f"Failed checks: {', '.join(failed)}"
#     else:
#         reason = "Supplier meets basic eligibility criteria"
    
#     return {
#         'eligible': eligible,
#         'checks': checks,
#         'reason': reason
#     }

# def api_query_documents(collection_name: str, query: Dict[str, Any] = None, 
#                         limit: int = 10) -> Dict[str, Any]:
#     """
#     Query documents from API
    
#     Args:
#         collection_name: Collection to query
#         query: Query filters (MongoDB-style query)
#         limit: Maximum number of results
        
#     Returns:
#         Dictionary with query results
#     """
#     try:
#         endpoint = f"{collection_name}/query"
#         data = {
#             "query": query or {},
#             "limit": limit
#         }
        
#         logger.info(f"🔍 Querying collection: {collection_name} with limit: {limit}")
#         logger.debug(f"Query filters: {query}")
        
#         result = call_api_endpoint(endpoint, data)
#         return result
        
#     except Exception as e:
#         logger.error(f"❌ Query error: {e}", exc_info=True)
#         return {
#             "success": False,
#             "message": f"Query error: {str(e)}",
#             "error": str(e)
#         }

# def api_update_document(collection_name: str, document_id: str, 
#                         updates: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Update document via API
    
#     Args:
#         collection_name: Collection name
#         document_id: Document ID to update
#         updates: Fields to update
        
#     Returns:
#         Dictionary with update result
#     """
#     try:
#         endpoint = f"{collection_name}/{document_id}"
#         updates["updated_at"] = datetime.utcnow().isoformat()
        
#         url = f"{GENERIC_API_URL}/api/{endpoint}"
#         logger.info(f"📝 Updating document {document_id} in {collection_name}")
#         logger.debug(f"Update fields: {list(updates.keys())}")
        
#         response = requests.put(url, json=updates, timeout=API_TIMEOUT)
        
#         if response.status_code in [200, 204]:
#             logger.info(f"✅ Document updated successfully")
#             return {
#                 "success": True,
#                 "message": "Document updated successfully",
#                 "updated_id": document_id
#             }
#         else:
#             logger.error(f"❌ Update failed: {response.status_code}")
#             return {
#                 "success": False,
#                 "message": f"Update failed: {response.status_code}",
#                 "error": response.text
#             }
            
#     except Exception as e:
#         logger.error(f"❌ Update error: {e}", exc_info=True)
#         return {
#             "success": False,
#             "message": f"Update error: {str(e)}",
#             "error": str(e)
#         }

# def test_api_connection() -> bool:
#     """Test if API server is reachable"""
#     try:
#         response = requests.get(f"{GENERIC_API_URL}/health", timeout=5)
#         if response.status_code == 200:
#             logger.info("✅ API server is reachable")
#             return True
#         else:
#             logger.warning(f"⚠️ API server returned status {response.status_code}")
#             return False
#     except Exception as e:
#         logger.error(f"❌ Cannot reach API server: {e}")
#         return False

# def list_available_collections() -> List[str]:
#     """Get list of all available collection names"""
#     return sorted(COLLECTION_SCHEMAS.keys())

# if __name__ == "__main__":
#     # Configure logging for testing
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )
    
#     print("=" * 60)
#     print("API Integration Layer - Test Suite")
#     print("=" * 60)
    
#     # Test 1: API connection
#     print("\n1️⃣ Testing API connection...")
#     if test_api_connection():
#         print("   ✅ API server is online")
#     else:
#         print("   ❌ API server is offline")
    
#     # Test 2: List collections
#     print(f"\n2️⃣ Available collections: {len(list_available_collections())}")
    
#     # Test 3: Get collection info
#     print("\n3️⃣ Collection Info Examples:")
#     for col in ["user_registration", "purchase_order", "training_registration"]:
#         info = get_collection_info(col)
#         print(f"   • {col}: {len(info.get('required_fields', []))} required, "
#               f"{len(info.get('optional_fields', []))} optional")
    
#     # Test 4: Validate document
#     print("\n4️⃣ Testing validation...")
#     test_doc = {
#         "email": "test@example.com",
#         "first_name": "John",
#         "last_name": "Doe"
#     }
#     is_valid, msg, missing = validate_required_fields("user_registration", test_doc)
#     print(f"   Valid: {is_valid}, Missing: {missing}")
    
#     # Test 5: Insert document (will fail if API is down)
#     print("\n5️⃣ Testing document insertion...")
#     result = api_insert_document("user_registration", test_doc)
#     print(f"   Success: {result['success']}")
#     print(f"   Message: {result['message']}")
    
#     print("\n" + "=" * 60)
#     print("Test suite completed!")
#     print("=" * 60)


from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import re
from typing import Dict, List, Any
import json

app = Flask(__name__)

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "enterprise_db"
client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

# API Endpoints Configuration
API_ENDPOINTS = {
    "user_registration": {
        "collection": "user_registration",
        "required": ["email", "first_name", "last_name", "password"],
        "keywords": ["user registration", "register user", "sign up", "create account", "new user"]
    },
    "supplier_registration": {
        "collection": "supplier_registration",
        "required": ["company_name", "contact_email", "business_type", "tax_id"],
        "keywords": ["supplier registration", "register supplier", "add supplier", "vendor signup"]
    },
    "performance_review": {
        "collection": "performance_review",
        "required": ["employee_id", "reviewer_id", "review_period", "overall_rating"],
        "keywords": ["performance review", "employee review", "appraisal", "performance evaluation"]
    },
    "audit_log_viewer": {
        "collection": "audit_log_viewer",
        "required": ["user_id", "action", "timestamp", "resource"],
        "keywords": ["audit log", "view audit", "system logs", "activity log"]
    },
    "health_and_safety_incident_reporting": {
        "collection": "health_and_safety_incident_reporting",
        "required": ["incident_date", "location", "incident_type", "reporter_id"],
        "keywords": ["safety incident", "health incident", "report incident", "accident report"]
    },
    "grievance_management": {
        "collection": "grievance_management",
        "required": ["employee_id", "grievance_type", "description", "submission_date"],
        "keywords": ["grievance", "complaint", "employee complaint", "raise grievance"]
    },
    "travel_request": {
        "collection": "travel_request",
        "required": ["employee_id", "destination", "start_date", "end_date", "purpose"],
        "keywords": ["travel request", "business travel", "trip request", "travel booking"]
    },
    "payment_processing": {
        "collection": "payment_processing",
        "required": ["amount", "currency", "payment_method", "transaction_id"],
        "keywords": ["payment", "process payment", "transaction", "make payment"]
    },
    "purchase_order": {
        "collection": "purchase_order",
        "required": ["supplier_id", "order_date", "total_amount", "items"],
        "keywords": ["purchase order", "po", "create order", "buy items"]
    },
    "customer_feedback_management": {
        "collection": "customer_feedback_management",
        "required": ["customer_id", "feedback_type", "rating", "comments"],
        "keywords": ["customer feedback", "feedback", "customer review", "submit feedback"]
    },
    "training_registration": {
        "collection": "training_registration",
        "required": ["employee_id", "training_program", "start_date", "trainer_id"],
        "keywords": ["training registration", "register training", "enroll training", "training program"]
    },
    "interview_scheduling": {
        "collection": "interview_scheduling",
        "required": ["candidate_id", "position", "interview_date", "interviewer_id"],
        "keywords": ["interview schedule", "schedule interview", "book interview", "interview appointment"]
    },
    "chatbot_training_data": {
        "collection": "chatbot_training_data",
        "required": ["question", "answer", "category", "confidence_score"],
        "keywords": ["chatbot training", "train bot", "bot data", "chatbot learning"]
    },
    "expense_reimbursement": {
        "collection": "expense_reimbursement",
        "required": ["employee_id", "expense_type", "amount", "expense_date"],
        "keywords": ["expense reimbursement", "claim expense", "reimbursement", "expense claim"]
    },
    "user_onboarding": {
        "collection": "user_onboarding",
        "required": ["user_id", "onboarding_stage", "start_date", "assigned_mentor"],
        "keywords": ["user onboarding", "onboard user", "new employee onboarding", "onboarding process"]
    },
    "data_backup_and_restore": {
        "collection": "data_backup_and_restore",
        "required": ["backup_type", "timestamp", "status", "data_size"],
        "keywords": ["data backup", "backup", "restore data", "backup system"]
    },
    "order_tracking": {
        "collection": "order_tracking",
        "required": ["order_id", "customer_id", "status", "last_updated"],
        "keywords": ["order tracking", "track order", "order status", "check order"]
    },
    "knowledge_base": {
        "collection": "knowledge_base",
        "required": ["title", "content", "category", "author_id"],
        "keywords": ["knowledge base", "add article", "kb", "documentation"]
    },
    "role_management": {
        "collection": "role_management",
        "required": ["role_name", "permissions", "description", "created_by"],
        "keywords": ["role management", "manage roles", "create role", "user roles"]
    },
    "employee_exit_clearance": {
        "collection": "employee_exit_clearance",
        "required": ["employee_id", "last_working_day", "clearance_status", "hr_approval"],
        "keywords": ["exit clearance", "employee exit", "resignation clearance", "full and final"]
    },
    "invoice_management": {
        "collection": "invoice_management",
        "required": ["invoice_number", "customer_id", "amount", "due_date"],
        "keywords": ["invoice", "create invoice", "billing", "invoice management"]
    },
    "shipping_management": {
        "collection": "shipping_management",
        "required": ["shipment_id", "origin", "destination", "carrier"],
        "keywords": ["shipping", "shipment", "delivery", "shipping management"]
    },
    "knowledge_transfer_kt_handover": {
        "collection": "knowledge_transfer_kt_handover",
        "required": ["project_id", "from_employee", "to_employee", "handover_date"],
        "keywords": ["knowledge transfer", "kt", "handover", "transfer knowledge"]
    },
    "faq_management": {
        "collection": "faq_management",
        "required": ["question", "answer", "category", "created_by"],
        "keywords": ["faq", "frequently asked questions", "add faq", "manage faq"]
    },
    "shift_scheduling": {
        "collection": "shift_scheduling",
        "required": ["employee_id", "shift_date", "start_time", "end_time"],
        "keywords": ["shift schedule", "schedule shift", "shift management", "work shift"]
    },
    "it_asset_allocation": {
        "collection": "it_asset_allocation",
        "required": ["asset_id", "employee_id", "asset_type", "allocation_date"],
        "keywords": ["asset allocation", "allocate asset", "it asset", "assign equipment"]
    },
    "contract_management": {
        "collection": "contract_management",
        "required": ["contract_id", "vendor_name", "contract_type", "start_date", "end_date"],
        "keywords": ["contract", "manage contract", "contract management", "vendor contract"]
    },
    "customer_support_ticket": {
        "collection": "customer_support_ticket",
        "required": ["ticket_id", "customer_id", "issue_type", "priority"],
        "keywords": ["support ticket", "create ticket", "customer support", "help ticket"]
    },
    "attendance_tracking": {
        "collection": "attendance_tracking",
        "required": ["employee_id", "date", "check_in_time", "check_out_time"],
        "keywords": ["attendance", "mark attendance", "check in", "check out"]
    },
    "vendor_management": {
        "collection": "vendor_management",
        "required": ["vendor_id", "company_name", "contact_email", "service_category"],
        "keywords": ["vendor management", "manage vendor", "add vendor", "vendor details"]
    },
    "notification_settings": {
        "collection": "notification_settings",
        "required": ["user_id", "notification_type", "enabled", "delivery_method"],
        "keywords": ["notification settings", "notifications", "alert settings", "notification preferences"]
    },
    "client_registration": {
        "collection": "client_registration",
        "required": ["company_name", "contact_person", "email", "industry"],
        "keywords": ["client registration", "register client", "add client", "new client"]
    },
    "product_catalog": {
        "collection": "product_catalog",
        "required": ["product_id", "name", "category", "price"],
        "keywords": ["product catalog", "add product", "product list", "manage products"]
    },
    "inventory_management": {
        "collection": "inventory_management",
        "required": ["item_id", "item_name", "current_stock", "minimum_stock"],
        "keywords": ["inventory", "stock management", "inventory management", "manage stock"]
    },
    "access_control": {
        "collection": "access_control",
        "required": ["user_id", "resource", "permission_level", "granted_by"],
        "keywords": ["access control", "permissions", "grant access", "manage access"]
    },
    "employee_leave_request": {
        "collection": "employee_leave_request",
        "required": ["employee_id", "leave_type", "start_date", "end_date"],
        "keywords": ["leave request", "apply leave", "request leave", "vacation request"]
    },
    "project_assignment": {
        "collection": "project_assignment",
        "required": ["project_id", "employee_id", "role", "start_date"],
        "keywords": ["project assignment", "assign project", "project allocation", "assign employee"]
    },
    "order_placement": {
        "collection": "order_placement",
        "required": ["customer_id", "items", "total_amount", "order_date"],
        "keywords": ["order placement", "place order", "create order", "new order"]
    },
    "marketing_campaign_management": {
        "collection": "marketing_campaign_management",
        "required": ["campaign_name", "start_date", "end_date", "budget"],
        "keywords": ["marketing campaign", "campaign", "marketing", "create campaign"]
    },
    "meeting_scheduler": {
        "collection": "meeting_scheduler",
        "required": ["meeting_title", "organizer_id", "start_time", "end_time"],
        "keywords": ["meeting schedule", "schedule meeting", "book meeting", "meeting scheduler"]
    },
    "payroll_management": {
        "collection": "payroll_management",
        "required": ["employee_id", "pay_period", "gross_salary", "deductions"],
        "keywords": ["payroll", "salary processing", "payroll management", "process salary"]
    },
    "user_activation": {
        "collection": "user_activation",
        "required": ["user_id", "activation_token", "status", "created_date"],
        "keywords": ["user activation", "activate user", "account activation", "activate account"]
    },
    "compliance_report": {
        "collection": "compliance_report",
        "required": ["report_type", "reporting_period", "compliance_status", "created_by"],
        "keywords": ["compliance report", "compliance", "generate report", "compliance status"]
    },
    "warehouse_management": {
        "collection": "warehouse_management",
        "required": ["warehouse_id", "operation_type", "item_id", "quantity"],
        "keywords": ["warehouse", "warehouse management", "warehouse operations", "manage warehouse"]
    },
    "recruitment_portal": {
        "collection": "recruitment_portal",
        "required": ["job_id", "candidate_id", "application_date", "status"],
        "keywords": ["recruitment", "job application", "recruitment portal", "apply job"]
    },
    "system_audit_and_compliance_dashboard": {
        "collection": "system_audit_and_compliance_dashboard",
        "required": ["audit_type", "timestamp", "system_component", "compliance_score"],
        "keywords": ["system audit", "compliance dashboard", "audit dashboard", "system compliance"]
    },
    "offer_letter_generation": {
        "collection": "offer_letter_generation",
        "required": ["candidate_id", "position", "salary", "start_date"],
        "keywords": ["offer letter", "generate offer", "job offer", "offer letter generation"]
    },
    "announcements_notice_board": {
        "collection": "announcements_notice_board",
        "required": ["title", "content", "posted_by", "post_date"],
        "keywords": ["announcement", "notice board", "post announcement", "company announcement"]
    },
    "system_configuration": {
        "collection": "system_configuration",
        "required": ["config_key", "config_value", "module", "updated_by"],
        "keywords": ["system configuration", "system settings", "configure system", "system config"]
    }
}


class ChatbotNLP:
    """Simple NLP for intent detection"""
    
    @staticmethod
    def detect_intent(message: str) -> Dict[str, Any]:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check for GET operations
        get_keywords = ["get", "show", "display", "list", "view", "see", "fetch", "retrieve", "find"]
        is_get = any(keyword in message_lower for keyword in get_keywords)
        
        # Check for POST operations
        post_keywords = ["create", "add", "register", "submit", "post", "insert", "new", "apply"]
        is_post = any(keyword in message_lower for keyword in post_keywords)
        
        # Detect which endpoint
        matched_endpoint = None
        max_matches = 0
        
        for endpoint, config in API_ENDPOINTS.items():
            matches = sum(1 for keyword in config["keywords"] if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                matched_endpoint = endpoint
        
        # Default to POST if ambiguous
        if not is_get and not is_post:
            is_post = True
        
        return {
            "endpoint": matched_endpoint,
            "operation": "GET" if is_get and not is_post else "POST",
            "confidence": max_matches
        }
    
    @staticmethod
    def extract_filters(message: str) -> Dict[str, Any]:
        """Extract filters from message for GET requests"""
        filters = {}
        
        # Extract common patterns
        patterns = {
            "employee_id": r"employee[_\s]id[:\s]+(\w+)",
            "user_id": r"user[_\s]id[:\s]+(\w+)",
            "customer_id": r"customer[_\s]id[:\s]+(\w+)",
            "order_id": r"order[_\s]id[:\s]+(\w+)",
            "email": r"email[:\s]+([\w\.-]+@[\w\.-]+\.\w+)"
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, message.lower())
            if match:
                filters[field] = match.group(1)
        
        return filters


# Chatbot endpoint
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Main chatbot endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                "status": "error",
                "message": "Please provide a message"
            }), 400
        
        # Detect intent
        intent = ChatbotNLP.detect_intent(user_message)
        
        if not intent['endpoint']:
            return jsonify({
                "status": "error",
                "message": "I couldn't understand what you're looking for. Please be more specific.",
                "suggestions": [
                    "Try: 'I want to register a new user'",
                    "Try: 'Show me all employees'",
                    "Try: 'Create a leave request'"
                ]
            }), 200
        
        endpoint_config = API_ENDPOINTS[intent['endpoint']]
        collection_name = endpoint_config['collection']
        
        # Handle GET operation
        if intent['operation'] == 'GET':
            filters = ChatbotNLP.extract_filters(user_message)
            result = get_data(collection_name, filters)
            return result
        
        # Handle POST operation
        else:
            return jsonify({
                "status": "info",
                "message": f"I can help you with {intent['endpoint'].replace('_', ' ')}.",
                "endpoint": f"/api/{intent['endpoint']}",
                "required_fields": endpoint_config['required'],
                "action": "Please provide the required information to proceed."
            }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500


def get_data(collection_name: str, filters: Dict[str, Any] = None):
    """Get data from collection"""
    try:
        collection = db[collection_name]
        
        if filters:
            data = list(collection.find(filters).limit(50))
        else:
            data = list(collection.find().limit(50))
        
        # Convert ObjectId to string
        for item in data:
            item['_id'] = str(item['_id'])
        
        return jsonify({
            "status": "success",
            "collection": collection_name,
            "count": len(data),
            "data": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error fetching data: {str(e)}"
        }), 500


# Generic POST endpoints for all 49 collections
@app.route('/api/<endpoint_name>', methods=['POST'])
def handle_post(endpoint_name):
    """Generic POST handler for all endpoints"""
    try:
        if endpoint_name not in API_ENDPOINTS:
            return jsonify({
                "status": "error",
                "message": f"Endpoint '{endpoint_name}' not found"
            }), 404
        
        config = API_ENDPOINTS[endpoint_name]
        data = request.json
        
        # Validate required fields
        missing_fields = [field for field in config['required'] if field not in data]
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }), 400
        
        # Add metadata
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        # Insert into database
        collection = db[config['collection']]
        result = collection.insert_one(data)
        
        return jsonify({
            "status": "success",
            "message": f"Data added to {endpoint_name} successfully",
            "id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        }), 500


# Generic GET endpoints for all 49 collections
@app.route('/api/<endpoint_name>', methods=['GET'])
def handle_get(endpoint_name):
    """Generic GET handler for all endpoints"""
    try:
        if endpoint_name not in API_ENDPOINTS:
            return jsonify({
                "status": "error",
                "message": f"Endpoint '{endpoint_name}' not found"
            }), 404
        
        config = API_ENDPOINTS[endpoint_name]
        collection_name = config['collection']
        
        # Get query parameters as filters
        filters = {k: v for k, v in request.args.items()}
        
        return get_data(collection_name, filters)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error fetching data: {str(e)}"
        }), 500


# Get all available endpoints
@app.route('/api/endpoints', methods=['GET'])
def list_endpoints():
    """List all available endpoints"""
    endpoints = []
    for name, config in API_ENDPOINTS.items():
        endpoints.append({
            "name": name,
            "post_url": f"/api/{name}",
            "get_url": f"/api/{name}",
            "collection": config['collection'],
            "required_fields": config['required']
        })
    
    return jsonify({
        "status": "success",
        "total_endpoints": len(endpoints),
        "endpoints": endpoints
    }), 200


# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        client.server_info()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503


if __name__ == '__main__':
    print("=" * 60)
    print("Enterprise Chatbot API Server")
    print("=" * 60)
    print(f"Database: {DATABASE_NAME}")
    print(f"Total Endpoints: {len(API_ENDPOINTS)}")
    print("\nChatbot Endpoint: POST /api/chatbot")
    print("Available Endpoints: GET /api/endpoints")
    print("Health Check: GET /health")
    print("\nExample Usage:")
    print("  POST /api/chatbot")
    print('  Body: {"message": "I want to register a new user"}')
    print("\n  POST /api/user_registration")
    print('  Body: {"email": "user@example.com", "first_name": "John", ...}')
    print("\n  GET /api/user_registration?email=user@example.com")
    print("=" * 60)


# =============================================================================
# CHATBOT INTEGRATION FUNCTIONS (Required by dynamic_chatbot.py)
# =============================================================================

from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection for direct integration
try:
    mongo_client = MongoClient("mongodb://localhost:27017")
    mongo_db = mongo_client["enterprise_db"]
    print("✅ MongoDB connected for integration functions")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    mongo_db = None

# Simplified field mappings for key collections
SIMPLE_FIELD_MAPPINGS = {
    "purchase_order": {
        "supplier_id": "Vendor ID",
        "order_date": "Order Date", 
        "status": "Status",
        "items": "Product",
        "quantity": "Quantity",
        "po_id": "PO ID"
    },
    "user_registration": {
        "email": "Email",
        "first_name": "First Name",
        "last_name": "Last Name",
        "phone": "Phone"
    },
    "training_registration": {
        "employee_id": "Employee ID",
        "training_program": "Training Name",
        "location": "Location"
    }
}

# Display collection names
SIMPLE_DISPLAY_NAMES = {
    "user_registration": "User Registration",
    "supplier_registration": "Supplier Registration", 
    "purchase_order": "Purchase Order",
    "training_registration": "Training Registration",
    "faq_management": "FAQ Management"
}

def api_insert_document(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert document by calling API endpoint first, then fallback to direct database insertion
    """
    try:
        # Auto-generate missing fields
        document = auto_generate_missing_fields(collection_name, document)
        
        # First try to call the actual API endpoint
        try:
            url = f"{GENERIC_API_URL}/api/{collection_name}"
            print(f"🌐 Calling API endpoint: {url}")
            
            response = requests.post(url, json=document, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                api_result = response.json()
                print(f"✅ API endpoint call successful")
                print(f"📄 API Response: {api_result}")
                
                # Extract document ID from API response
                document_id = "unknown"
                if "data" in api_result and "_id" in api_result["data"]:
                    document_id = api_result["data"]["_id"]
                elif "inserted_id" in api_result:
                    document_id = api_result["inserted_id"]
                
                return {
                    "success": True,
                    "inserted_id": document_id,
                    "collection": collection_name,
                    "method": "api_endpoint",
                    "validation": "api_validated"
                }
            else:
                print(f"⚠️ API endpoint returned {response.status_code}, falling back to direct DB")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API endpoint failed: {e}, falling back to direct DB")
        
        # Fallback to direct database insertion
        if mongo_db is None:
            return {"success": False, "error": "Database not connected and API unavailable"}
        
        print(f"🔄 Using direct database insertion for {collection_name}")
        
        # Add timestamps
        current_time = datetime.utcnow().isoformat()
        if "created_at" not in document:
            document["created_at"] = current_time
        if "updated_at" not in document:
            document["updated_at"] = current_time
            
        # Try display collection first
        display_name = SIMPLE_DISPLAY_NAMES.get(collection_name)
        if display_name:
            try:
                # Transform fields for display collection
                display_doc = transform_fields_to_display_format(collection_name, document)
                result = mongo_db[display_name].insert_one(display_doc)
                return {
                    "success": True,
                    "inserted_id": str(result.inserted_id),
                    "collection": display_name,
                    "method": "direct_db_display"
                }
            except Exception as e:
                print(f"Display collection failed: {e}")
        
        # Fallback to underscore collection
        result = mongo_db[collection_name].insert_one(document)
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "collection": collection_name,
            "method": "direct_db_fallback"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def auto_generate_missing_fields(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-generate missing required fields"""
    enhanced_doc = document.copy()
    
    if collection_name == "purchase_order":
        # Generate PO ID if missing
        if "po_id" not in enhanced_doc:
            enhanced_doc["po_id"] = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract quantity from items (e.g., "laptops x10")
        if "quantity" not in enhanced_doc and "items" in enhanced_doc:
            import re
            items_text = str(enhanced_doc.get("items", ""))
            qty_match = re.search(r'x(\d+)', items_text, re.IGNORECASE)
            if qty_match:
                enhanced_doc["quantity"] = int(qty_match.group(1))
                enhanced_doc["items"] = re.sub(r'\s*x\d+', '', items_text).strip()
            else:
                enhanced_doc["quantity"] = 1
    
    return enhanced_doc

def transform_fields_to_display_format(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """Transform schema field names to display collection field names"""
    if collection_name not in SIMPLE_FIELD_MAPPINGS:
        return document
    
    field_mapping = SIMPLE_FIELD_MAPPINGS[collection_name]
    transformed = {}
    
    for original_field, value in document.items():
        display_field = field_mapping.get(original_field, original_field)
        transformed[display_field] = value
    
    return transformed

def api_check_supplier_eligibility(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check supplier eligibility - simplified version"""
    try:
        # Basic validation
        required = ["company_name", "contact_email"]
        missing = [f for f in required if f not in supplier_data or not supplier_data[f]]
        
        if missing:
            return {
                'eligible': False,
                'reason': f'Missing required fields: {", ".join(missing)}'
            }
        
        # Simple eligibility check
        return {
            'eligible': True,
            'reason': 'All requirements met'
        }
        
    except Exception as e:
        return {
            'eligible': False,
            'reason': f'Error checking eligibility: {str(e)}'
        }

if __name__ == "__main__":
    print("🚀 Starting Flask API server with chatbot integration...")
    app.run(debug=True, host='0.0.0.0', port=5000)