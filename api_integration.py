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
GENERIC_API_URL = "http://localhost:5000"
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

# def api_check_supplier_eligibility(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
#     """Check supplier eligibility - simplified version"""
#     try:
#         # Basic validation
#         required = ["company_name", "contact_email"]
#         missing = [f for f in required if f not in supplier_data or not supplier_data[f]]
        
#         if missing:
#             return {
#                 'eligible': False,
#                 'reason': f'Missing required fields: {", ".join(missing)}'
#             }
        
#         # Simple eligibility check
#         return {
#             'eligible': True,
#             'reason': 'All requirements met'
#         }
        
#     except Exception as e:
#         return {
#             'eligible': False,
#             'reason': f'Error checking eligibility: {str(e)}'
#         }

if __name__ == "__main__":
    print("🚀 Starting Flask API server with chatbot integration...")
    app.run(debug=True, host='0.0.0.0', port=5000)