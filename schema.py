COLLECTION_SCHEMAS = {
    "user_registration": {
        "required": ["first_name", "last_name", "email", "mobile", "department", "position", "employee_id"], 
        "optional": ["location", "address", "blood_group", "emergency_contact"]
    },
    "user_onboarding": {
        "required": ["uuid", "permissions", "applications", "system_role"], 
        "optional": ["locations", "hierarchy_of_employees"]
    },
    "user_activation": {
        "required": ["employee_id", "activation_date", "assigned_role"], 
        "optional": ["remarks", "temporary_password"]
    },
    "supplier_registration": {
        "required": ["supplier_name", "supplier_contact", "mobile", "gst_number", "cin_number"], 
        "optional": ["location", "address", "products", "supplier_rating"]
    },
    "client_registration": {
        "required": ["client_name", "email", "contact_person", "industry"], 
        "optional": ["website", "notes"]
    },
    "product_catalog": {
        "required": ["product_id", "product_name", "category", "price"], 
        "optional": ["description", "discount", "warranty"]
    },
    "inventory_management": {
        "required": ["item_id", "quantity", "warehouse_location"], 
        "optional": ["expiry_date", "batch_number"]
    },
    "order_placement": {
        "required": ["order_id", "customer_id", "product_id", "quantity"], 
        "optional": ["delivery_notes"]
    },
    "order_tracking": {
        "required": ["order_id", "current_status", "delivery_date"], 
        "optional": ["courier_service", "tracking_url"]
    },
    "payment_processing": {
        "required": ["transaction_id", "order_id", "amount", "payment_method"], 
        "optional": ["coupon_code", "payment_notes"]
    },
    "employee_leave_request": {
        "required": ["employee_id", "leave_type", "start_date", "end_date"], 
        "optional": ["reason", "backup_employee"]
    },
    "payroll_management": {
        "required": ["employee_id", "salary", "bank_account"], 
        "optional": ["tax_details", "bonus"]
    },
    "training_registration": {
        "required": ["employee_id", "training_name", "date"], 
        "optional": ["feedback_form"]
    },
    "performance_review": {
        "required": ["employee_id", "review_period", "reviewer_id", "rating"], 
        "optional": ["comments", "improvement_plan"]
    },
    "customer_support_ticket": {
        "required": ["ticket_id", "customer_id", "issue_type", "description"], 
        "optional": ["priority", "attachments"]
    },
    "project_assignment": {
        "required": ["project_id", "employee_id", "role", "start_date"], 
        "optional": ["end_date", "notes"]
    },
    "meeting_scheduler": {
        "required": ["meeting_title", "date", "time", "participants"], 
        "optional": ["agenda", "location"]
    },
    "it_asset_allocation": {
        "required": ["asset_id", "employee_id", "allocation_date"], 
        "optional": ["return_date", "notes"]
    },
    "compliance_report": {
        "required": ["report_id", "department", "report_date"], 
        "optional": ["reviewer_comments"]
    },
    "audit_log_viewer": {
        "required": ["log_id", "timestamp", "action", "user_id"], 
        "optional": ["ip_address", "device_info"]
    },
    "recruitment_portal": {
        "required": ["candidate_name", "email", "resume", "position_applied"], 
        "optional": ["referral_source", "notes"]
    },
    "interview_scheduling": {
        "required": ["candidate_id", "interviewer_id", "date", "time"], 
        "optional": ["feedback_form"]
    },
    "offer_letter_generation": {
        "required": ["candidate_id", "position", "salary", "joining_date"], 
        "optional": ["bonus", "special_clauses"]
    },
    "employee_exit_clearance": {
        "required": ["employee_id", "last_working_day", "clearance_form"], 
        "optional": ["feedback", "notes"]
    },
    "travel_request": {
        "required": ["employee_id", "destination", "start_date", "end_date"], 
        "optional": ["purpose", "budget"]
    },
    "expense_reimbursement": {
        "required": ["employee_id", "expense_type", "amount", "date"], 
        "optional": ["receipt", "notes"]
    },
    "vendor_management": {
        "required": ["vendor_name", "contact_person", "gst_number"], 
        "optional": ["products", "address", "rating"]
    },
    "invoice_management": {
        "required": ["invoice_id", "vendor_id", "amount", "due_date"], 
        "optional": ["notes"]
    },
    "shipping_management": {
        "required": ["shipment_id", "order_id", "carrier", "dispatch_date"], 
        "optional": ["tracking_url", "delivery_notes"]
    },
    "warehouse_management": {
        "required": ["warehouse_id", "location", "capacity"], 
        "optional": ["supervisor", "notes"]
    },
    "purchase_order": {
        "required": ["po_id", "vendor_id", "product", "quantity"], 
        "optional": ["notes", "delivery_date"]
    },
    "contract_management": {
        "required": ["contract_id", "vendor_id", "start_date", "end_date"], 
        "optional": ["renewal_terms", "notes"]
    },
    "knowledge_base": {
        "required": ["article_id", "title", "content", "category"], 
        "optional": ["tags", "attachments"]
    },
    "faq_management": {
        "required": ["question", "answer", "category"], 
        "optional": ["tags"]
    },
    "system_configuration": {
        "required": ["config_id", "setting_name", "value"], 
        "optional": ["notes"]
    },
    "role_management": {
        "required": ["role_id", "role_name", "permissions"], 
        "optional": ["description"]
    },
    "access_control": {
        "required": ["user_id", "role_id", "access_level"], 
        "optional": ["expiry_date"]
    },
    "notification_settings": {
        "required": ["user_id", "notification_type", "channel"], 
        "optional": ["frequency"]
    },
    "chatbot_training_data": {
        "required": ["intent", "utterance", "response"], 
        "optional": ["tags"]
    },
    "attendance_tracking": {
        "required": ["employee_id", "date", "check_in", "check_out"], 
        "optional": ["notes", "location"]
    },
    "shift_scheduling": {
        "required": ["employee_id", "shift_type", "start_date", "end_date"], 
        "optional": ["notes"]
    },
    "health_and_safety_incident_reporting": {
        "required": ["incident_id", "employee_id", "date", "description"], 
        "optional": ["attachments", "location"]
    },
    "grievance_management": {
        "required": ["ticket_id", "employee_id", "description"], 
        "optional": ["attachments", "priority"]
    },
    "knowledge_transfer_kt_handover": {
        "required": ["employee_id", "subject", "handover_to", "date"], 
        "optional": ["notes", "attachments"]
    },
    "customer_feedback_management": {
        "required": ["feedback_id", "customer_id", "rating", "comments"], 
        "optional": ["attachments", "suggestions"]
    },
    "marketing_campaign_management": {
        "required": ["campaign_id", "name", "start_date", "end_date", "target_audience"], 
        "optional": ["budget", "notes"]
    },
    "data_backup_and_restore": {
        "required": ["backup_id", "date", "type"], 
        "optional": ["notes"]
    },
    "system_audit_and_compliance_dashboard": {
        "required": ["dashboard_id", "department", "date"], 
        "optional": ["reviewer_notes"]
    },
    "announcements_notice_board": {
        "required": ["notice_id", "title", "date", "department"], 
        "optional": ["attachments", "expiry_date"]
    }
}