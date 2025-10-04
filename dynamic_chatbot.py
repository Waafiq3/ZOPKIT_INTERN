"""
Truly Dynamic ChatBot - Zero Hardcoding
Adapts to any conversation flow using AI intelligence
"""

import logging
import re
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from db import init_db, get_collections_info, validate_user_position, get_endpoint_access_requirements, create_dummy_users
from schema import COLLECTION_SCHEMAS

# Import API integration layer
try:
    from api_integration import api_insert_document, api_check_supplier_eligibility
    USE_API_INTEGRATION = True
    logger = logging.getLogger(__name__)
    logger.info("✅ API Integration layer loaded - will use API endpoints")
except ImportError:
    from db import insert_document, check_supplier_eligibility
    USE_API_INTEGRATION = False
    logger = logging.getLogger(__name__)
    logger.info("⚠️ API Integration not available - using direct database access")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Install google-generativeai: pip install google-generativeai")

class DynamicChatBot:
    """Fully dynamic chatbot with zero hardcoded patterns"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.conversation_state = {}
        self.use_gemini = False
        
        if GEMINI_AVAILABLE:
            try:
                api_key = "AIzaSyC75gcuuklMxi8RyCWa_Ss5waRevWtKtEk"
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment variables")
                
                genai.configure(api_key=api_key)
                
                # Try Gemini 2.5 Flash first, fallback to 1.5
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                    logger.info("✅ Using Gemini 2.5 Flash")
                except:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("✅ Using Gemini 1.5 Flash")
                
                self.use_gemini = True
            except Exception as e:
                logger.error(f"❌ Gemini initialization failed: {e}")
                logger.info("Set GEMINI_API_KEY environment variable")
        
        if not self.use_gemini:
            logger.warning("⚠️ Running in LIMITED mode without AI")
    
    def process_message(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """Process any user message dynamically"""
        logger.info(f"💬 [{session_id}] User: {user_input}")
        
        # Initialize session
        if session_id not in self.conversation_state:
            self.conversation_state[session_id] = {
                "history": [],
                "current_task": None,
                "collected_data": {},
                "context": {}
            }
        
        state = self.conversation_state[session_id]
        state["history"].append({"role": "user", "content": user_input})
        
        # Process with AI or fallback
        if self.use_gemini:
            result = self._process_with_ai(user_input, state, session_id)
        else:
            result = self._process_without_ai(user_input, state, session_id)
        
        state["history"].append({"role": "assistant", "content": result["response"]})
        
        logger.info(f"🤖 [{session_id}] Bot: {result['response'][:100]}...")
        return result
    
    def _process_with_ai(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """AI-powered dynamic processing"""
        
        # First, let the AI determine what the user wants to do
        if not state.get("intent_analyzed", False) and not state.get("user_validated", False):
            return self._analyze_user_intent(user_input, state, session_id)
        
        # Handle user validation if needed (after intent is known)
        if not state.get("user_validated", False):
            return self._handle_user_validation(user_input, state, session_id)
        
        # Build dynamic context
        context = self._build_context(state)
        
        prompt = f"""You are an intelligent assistant helping users with various tasks. 

{context}

User's message: "{user_input}"

Analyze the message and respond with JSON:
{{
    "intent": "description of what user wants",
    "action": "continue_conversation|collect_data|save_data|provide_info|clarify",
    "task_type": "detected task/collection name or null",
    "extracted_fields": {{"field_name": "value"}},
    "missing_fields": ["list", "of", "missing", "required", "fields"],
    "is_confirmation": true/false,
    "confidence": 0.0-1.0,
    "response": "natural conversational response to user",
    "next_step": "what should happen next"
}}

CRITICAL Rules:
1. Extract ALL possible data from the user's message
2. Be conversational and natural - never robotic
3. If user provides data, acknowledge it warmly
4. If data is incomplete, ask for missing fields naturally
5. When ALL REQUIRED fields are collected, use action "save_data" to call API endpoint
6. Handle confirmations (yes/confirm/save) by setting is_confirmation=true and action="save_data"
7. If user mentions wanting to do a task but provides no data, use action="collect_data" and ask for required fields
8. Adapt to the user's communication style
9. Don't repeat questions if data was already provided

Task Detection Examples:
- "register supplier" -> task_type: "supplier_registration"  
- "purchase order" -> task_type: "purchase_order"
- "employee leave" -> task_type: "employee_leave_request"
- "schedule training" -> task_type: "training_registration"

Action Logic:
- User mentions task but no data -> action: "collect_data" (ask for required fields)
- User provides some data -> action: "collect_data" (ask for missing fields)
- User provides all required data -> action: "save_data" (call API)
- User confirms (yes/confirm) -> is_confirmation: true, action: "save_data"

Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            
            analysis = json.loads(result_text)
            
            # Process based on AI analysis
            return self._handle_ai_response(analysis, state, session_id, user_input)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._create_fallback_response(user_input, state)
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return self._create_fallback_response(user_input, state)
    
    def _handle_ai_response(self, analysis: Dict, state: Dict, session_id: str, user_input: str) -> Dict[str, Any]:
        """Handle AI analysis and execute appropriate actions"""
        
        action = analysis.get("action", "continue_conversation")
        task_type = analysis.get("task_type")
        extracted = analysis.get("extracted_fields", {})
        is_confirmation = analysis.get("is_confirmation", False)
        
        # Update task if detected  
        if task_type and task_type != state["current_task"]:
            # If we have a new task but user is already validated, proceed
            if state.get("user_validated", False):
                # User already validated, check if they have access to this new task
                access_requirements = get_endpoint_access_requirements()
                required_positions = access_requirements.get(task_type, ['admin'])
                user_position = state.get("user_details", {}).get("position", "")
                
                if user_position in required_positions or "admin" in user_position:
                    # User has access, proceed
                    pass
                else:
                    return {
                        "status": "error", 
                        "response": f"""🚫 **Access Denied**

Your position ({user_position}) is not authorized for **{task_type.replace('_', ' ').title()}**.

**Required Positions:** {', '.join(required_positions)}

Please contact your administrator if you believe this is an error.""",
                        "intent": "access_denied",
                        "session_id": session_id
                    }
            else:
                # User not validated yet - this shouldn't happen with new flow
                # but keeping as fallback
                return {
                    "status": "awaiting_user_validation",
                    "response": f"""🔐 **Access Validation Required**

To proceed with **{task_type.replace('_', ' ').title()}**, I need to validate your authorization.

Please provide your **Employee ID** (e.g., EMP001, EMP002, etc.)""",
                    "intent": "user_validation_required",
                    "action": "request_employee_id",
                    "task": task_type,
                    "session_id": session_id
                }
            
            state["current_task"] = task_type
            state["collected_data"] = {}
        
        # Merge extracted data
        if extracted:
            state["collected_data"].update(extracted)
        
        # Handle field validation and collection for any task
        if task_type and (action in ["collect_data", "save_data"] or is_confirmation):
            return self._validate_and_collect_fields(user_input, task_type, state, session_id)
        
        # If user is continuing an existing task, validate fields
        if state.get("current_task") and action == "collect_data":
            current_task = state["current_task"]
            return self._validate_and_collect_fields(user_input, current_task, state, session_id)
        
        # Return AI's response
        return {
            "status": "success",
            "response": analysis["response"],
            "intent": analysis.get("intent"),
            "action": action,
            "task": state["current_task"],
            "data": state["collected_data"],
            "session_id": session_id,
            "confidence": analysis.get("confidence", 0.5)
        }
    
    def _process_without_ai(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Fallback processing without AI"""
        
        user_lower = user_input.lower()
        
        # Basic intent detection
        if any(word in user_lower for word in ["yes", "confirm", "correct", "save"]):
            if state["collected_data"]:
                return self._save_to_database(state, session_id, "Saving your data...")
        
        # Extract any data from message
        extracted = self._extract_data_universal(user_input)
        
        if extracted:
            state["collected_data"].update(extracted)
            
            response = f"Got it! "
            for k, v in extracted.items():
                response += f"{k.replace('_', ' ').title()}: {v}. "
            
            response += "\n\nWhat else would you like to provide?"
            
            return {
                "status": "success",
                "response": response,
                "data": state["collected_data"],
                "session_id": session_id
            }
        
        # Default helpful response
        return {
            "status": "success",
            "response": """I'm here to help! I can assist with various registrations and tasks.

Please tell me:
• What would you like to do?
• What information can you provide?

I'll adapt to whatever you need!""",
            "session_id": session_id
        }
    
    def _build_context(self, state: Dict) -> str:
        """Build dynamic context from current state"""
        
        context_parts = []
        
        # Available collections
        context_parts.append("Available collections/tasks:")
        for collection, schema in COLLECTION_SCHEMAS.items():
            fields = ", ".join(schema.get("required", []))
            context_parts.append(f"  • {collection}: requires {fields}")
        
        # Current conversation state
        if state["current_task"]:
            context_parts.append(f"\nCurrent task: {state['current_task']}")
        
        if state["collected_data"]:
            context_parts.append(f"Data collected so far: {json.dumps(state['collected_data'])}")
        
        # Recent conversation
        if len(state["history"]) > 0:
            recent = state["history"][-4:]  # Last 2 exchanges
            context_parts.append("\nRecent conversation:")
            for msg in recent:
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg["content"][:100]
                context_parts.append(f"  {role}: {content}")
        
        return "\n".join(context_parts)
    
    def _extract_data_universal(self, text: str) -> Dict[str, Any]:
        """Universal data extraction without hardcoded patterns"""
        
        extracted = {}
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            extracted["email"] = email_match.group(0)
        
        # Phone
        phone_match = re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
        if phone_match:
            extracted["phone"] = phone_match.group(0)
        
        # Names (simple extraction)
        name_match = re.search(r'(?:name is|i am|call me)\s+([A-Z][a-z]+)(?:\s+([A-Z][a-z]+))?', text, re.IGNORECASE)
        if name_match:
            extracted["first_name"] = name_match.group(1)
            if name_match.group(2):
                extracted["last_name"] = name_match.group(2)
        
        # Supplier IDs (SUP001, SUP123, etc.)
        supplier_match = re.search(r'\bSUP\d+\b', text, re.IGNORECASE)
        if supplier_match:
            extracted["supplier_id"] = supplier_match.group(0)
        
        # Items with quantities (laptops x10, chairs x5, etc.)
        items_match = re.search(r'items?:\s*([^,]+(?:\s+x\d+)?)', text, re.IGNORECASE)
        if items_match:
            extracted["items"] = items_match.group(1).strip()
        
        # Total amounts ($15000, $1,500, etc.)
        amount_match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
        if amount_match:
            amount_str = amount_match.group(0).replace('$', '').replace(',', '')
            try:
                extracted["total_amount"] = float(amount_str)
            except ValueError:
                pass
        
        # Dates (various formats)
        date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', text)
        if date_match:
            extracted["order_date"] = date_match.group(0)
        
        # Employee IDs (EMP001, EMP123, etc.)
        emp_match = re.search(r'\bEMP\d+\b', text, re.IGNORECASE)
        if emp_match:
            extracted["employee_id"] = emp_match.group(0)
        
        # Customer IDs (CUST001, CUST123, etc.)
        cust_match = re.search(r'\bCUST\d+\b', text, re.IGNORECASE)
        if cust_match:
            extracted["customer_id"] = cust_match.group(0)
        
        return extracted
    
    def _get_missing_fields(self, collection: str, data: Dict) -> List[str]:
        """Get missing required fields"""
        
        if collection not in COLLECTION_SCHEMAS:
            return []
        
        required = COLLECTION_SCHEMAS[collection].get("required", [])
        return [f for f in required if f not in data or not data[f]]
    
    def _request_confirmation(self, state: Dict, ai_response: str) -> Dict[str, Any]:
        """Request confirmation before saving"""
        
        data_summary = "\n".join([f"  • {k.replace('_', ' ').title()}: {v}" 
                                  for k, v in state["collected_data"].items()])
        
        response = f"""{ai_response}

📋 **Summary of collected data:**
{data_summary}

✅ Reply with 'yes' or 'confirm' to save
❌ Reply with 'no' to cancel or make changes"""
        
        return {
            "status": "awaiting_confirmation",
            "response": response,
            "data": state["collected_data"],
            "task": state["current_task"]
        }
    
    def _save_to_database(self, state: Dict, session_id: str, message: str) -> Dict[str, Any]:
        """Save collected data to database"""
        
        if not state["current_task"] or not state["collected_data"]:
            return {
                "status": "error",
                "response": "No data to save. What would you like to do?"
            }
        
        try:
            if not init_db():
                raise Exception("Database connection failed")
            
            # Check supplier eligibility before registration
            if "supplier" in state["current_task"].lower():
                if USE_API_INTEGRATION:
                    eligibility_result = api_check_supplier_eligibility(state["collected_data"])
                else:
                    eligibility_result = check_supplier_eligibility(state["collected_data"])
                
                if not eligibility_result.get("eligible", False):
                    failed_checks = []
                    checks = eligibility_result.get("checks", {})
                    
                    for check, passed in checks.items():
                        if not passed:
                            check_name = check.replace("_", " ").title()
                            failed_checks.append(f"❌ {check_name}")
                    
                    return {
                        "status": "error",
                        "response": f"""🚫 **Supplier Registration Not Eligible**

**Reason:** {eligibility_result.get('reason', 'Unknown reason')}

**Failed Requirements:**
{chr(10).join(failed_checks) if failed_checks else '• All checks failed'}

**To become eligible, please ensure you have:**
• ✅ Valid company name
• ✅ Recognized business type (corporation, llc, partnership, sole_proprietorship, non_profit)
• ✅ Valid contact email address
• ✅ Tax ID number
• ✅ Company name not already registered

Please provide the missing information and try again.""",
                        "intent": "supplier_eligibility_failed",
                        "action": "eligibility_check_failed",
                        "eligibility_result": eligibility_result
                    }
            
            # Use API integration or direct database
            if USE_API_INTEGRATION:
                result = api_insert_document(state["current_task"], state["collected_data"])
            else:
                result = insert_document(state["current_task"], state["collected_data"])
            
            if result["success"]:
                task_name = state["current_task"].replace("_", " ").title()
                
                # Special success message for supplier registration
                if "supplier" in state["current_task"].lower():
                    response_message = f"""🎉 **Supplier Registration Successful!**

✅ **Eligibility Verified:** All requirements met
📝 **Document ID:** {result.get('inserted_id')}
🏢 **Company:** {state["collected_data"].get('company_name', 'N/A')}
📧 **Contact:** {state["collected_data"].get('contact_email', 'N/A')}

**Your supplier account is now active and ready to use!**

How else can I help you today?"""
                else:
                    response_message = f"""🎉 Success! Your {task_name} has been saved.

📝 Document ID: {result.get('inserted_id')}

How else can I help you today?"""
                
                # Store current task before clearing state
                current_task = state["current_task"]
                
                # Clear state
                state["current_task"] = None
                state["collected_data"] = {}
                
                return {
                    "status": "success",
                    "response": response_message,
                    "document_id": result.get('inserted_id'),
                    "task": current_task,
                    "api_endpoint_used": current_task if USE_API_INTEGRATION else None
                }
            else:
                raise Exception(result.get("message", "Save failed"))
        
        except Exception as e:
            logger.error(f"Save error: {e}")
            return {
                "status": "error",
                "response": f"❌ Error saving data: {str(e)}\n\nPlease try again or let me know if you need help."
            }
    
    def _create_fallback_response(self, user_input: str, state: Dict) -> Dict[str, Any]:
        """Create fallback response when AI fails"""
        
        return {
            "status": "success",
            "response": "I'm processing your message. Could you please rephrase or provide more details?",
            "session_id": state.get("session_id")
        }
    
    def reset_session(self, session_id: str):
        """Reset a conversation session"""
        if session_id in self.conversation_state:
            del self.conversation_state[session_id]
            logger.info(f"🔄 Session {session_id} reset")

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from AI, handling common formatting issues"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Try to parse JSON
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Response text: {response_text[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return None

    def _validate_and_collect_fields(self, user_input: str, task_type: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Validate collected fields and identify missing required fields"""
        try:
            # Get schema for this collection
            from schema import COLLECTION_SCHEMAS
            schema = COLLECTION_SCHEMAS.get(task_type, {})
            required_fields = schema.get("required", [])
            optional_fields = schema.get("optional", [])
            
            # Get currently collected data
            collected_data = state.get("collected_data", {})
            
            # Use AI to extract any new fields from user input
            extraction_prompt = f"""Extract field values from this user message for {task_type}:

User message: "{user_input}"

Available fields:
Required: {required_fields}
Optional: {optional_fields}

Current data: {collected_data}

Extract any new field values and respond with JSON:
{{
    "extracted_fields": {{"field_name": "value"}},
    "updated_data": {{"field_name": "value"}},
    "missing_required": ["field1", "field2"],
    "completion_percentage": 0.0-1.0
}}

Rules:
1. Only extract fields that are explicitly mentioned
2. Don't make assumptions about missing data
3. Include all current + new data in updated_data
4. List only genuinely missing required fields
"""

            response = self.model.generate_content(extraction_prompt)
            ai_result = self._parse_json_response(response.text)
            
            if not ai_result:
                return {"status": "error", "response": "Unable to process field extraction"}
            
            # Update collected data
            updated_data = ai_result.get("updated_data", collected_data)
            missing_required = ai_result.get("missing_required", [])
            completion_percentage = ai_result.get("completion_percentage", 0.0)
            
            # Update state
            state["collected_data"] = updated_data
            
            # Check if we have all required fields
            if not missing_required:
                # All required fields collected - make API call
                return self._make_api_call(task_type, updated_data, state, session_id)
            else:
                # Still missing required fields - ask for them
                return self._request_missing_fields(task_type, missing_required, updated_data, optional_fields)
                
        except Exception as e:
            logger.error(f"Field validation error: {e}")
            return {"status": "error", "response": f"Error processing fields: {e}"}

    def _request_missing_fields(self, task_type: str, missing_fields: List[str], collected_data: Dict, optional_fields: List[str]) -> Dict[str, Any]:
        """Generate a helpful request for missing fields"""
        
        # Create a friendly field name mapping
        field_display_names = {
            # User Management
            "employee_id": "Employee ID",
            "first_name": "First Name", 
            "last_name": "Last Name",
            "email": "Email Address",
            "mobile": "Mobile Number",
            "department": "Department",
            "position": "Position/Role",
            "location": "Location",
            "address": "Address",
            "blood_group": "Blood Group",
            "emergency_contact": "Emergency Contact",
            
            # User Onboarding & Activation
            "uuid": "User UUID",
            "permissions": "Permissions",
            "applications": "Applications",
            "system_role": "System Role",
            "activation_date": "Activation Date",
            "assigned_role": "Assigned Role",
            "remarks": "Remarks",
            "temporary_password": "Temporary Password",
            
            # Supplier & Client Management
            "supplier_name": "Supplier Name",
            "supplier_contact": "Supplier Contact",
            "gst_number": "GST Number",
            "cin_number": "CIN Number",
            "supplier_rating": "Supplier Rating",
            "client_name": "Client Name",
            "contact_person": "Contact Person",
            "industry": "Industry",
            "website": "Website",
            "notes": "Notes",
            
            # Product & Inventory
            "product_id": "Product ID",
            "product_name": "Product Name",
            "category": "Category",
            "price": "Price",
            "description": "Description",
            "discount": "Discount",
            "warranty": "Warranty",
            "item_id": "Item ID",
            "quantity": "Quantity",
            "warehouse_location": "Warehouse Location",
            "expiry_date": "Expiry Date",
            "batch_number": "Batch Number",
            
            # Orders & Payments
            "order_id": "Order ID",
            "customer_id": "Customer ID",
            "delivery_notes": "Delivery Notes",
            "current_status": "Current Status",
            "delivery_date": "Delivery Date",
            "courier_service": "Courier Service",
            "tracking_url": "Tracking URL",
            "transaction_id": "Transaction ID",
            "amount": "Amount",
            "payment_method": "Payment Method",
            "coupon_code": "Coupon Code",
            "payment_notes": "Payment Notes",
            
            # Employee Services
            "leave_type": "Leave Type",
            "start_date": "Start Date",
            "end_date": "End Date",
            "reason": "Reason",
            "backup_employee": "Backup Employee",
            "salary": "Salary",
            "bank_account": "Bank Account",
            "tax_details": "Tax Details",
            "bonus": "Bonus",
            "training_name": "Training Name",
            "date": "Date",
            "feedback_form": "Feedback Form",
            
            # Travel & Expenses
            "destination": "Travel Destination",
            "purpose": "Purpose of Travel",
            "budget": "Budget",
            "expense_type": "Expense Type",
            "receipt": "Receipt",
            
            # Reviews & Performance
            "review_period": "Review Period",
            "reviewer_id": "Reviewer ID",
            "rating": "Rating",
            "comments": "Comments",
            "improvement_plan": "Improvement Plan",
            
            # Support & Projects
            "ticket_id": "Ticket ID",
            "issue_type": "Issue Type",
            "priority": "Priority",
            "attachments": "Attachments",
            "project_id": "Project ID",
            "role": "Role",
            
            # Meetings & Assets
            "meeting_title": "Meeting Title",
            "time": "Time",
            "participants": "Participants",
            "agenda": "Agenda",
            "asset_id": "Asset ID",
            "allocation_date": "Allocation Date",
            "return_date": "Return Date"
        }
        
        # Generate friendly field requests
        missing_display = []
        for field in missing_fields:
            display_name = field_display_names.get(field, field.replace('_', ' ').title())
            missing_display.append(f"• **{display_name}**")
        
        # Show what we already have
        collected_display = []
        for field, value in collected_data.items():
            display_name = field_display_names.get(field, field.replace('_', ' ').title())
            collected_display.append(f"✅ **{display_name}**: {value}")
        
        # Optional fields info
        optional_display = []
        for field in optional_fields[:3]:  # Show first 3 optional fields
            display_name = field_display_names.get(field, field.replace('_', ' ').title())
            optional_display.append(f"• {display_name}")
        
        response = f"""📝 **Almost There! Just Need a Few More Details**

**What I have so far:**
{chr(10).join(collected_display) if collected_display else "• No information collected yet"}

**Still Need:**
{chr(10).join(missing_display)}

**Optional (you can provide these too):**
{chr(10).join(optional_display) if optional_display else "• None"}

💡 **Tip**: You can provide multiple fields at once, like:
"My employee ID is EMP001 and I want to travel to New York on 2025-10-15"
"""

        return {
            "status": "field_collection",
            "response": response,
            "task_type": task_type,
            "missing_fields": missing_fields,
            "collected_data": collected_data
        }

    def _make_api_call(self, task_type: str, data: Dict, state: Dict, session_id: str) -> Dict[str, Any]:
        """Make API call with complete data"""
        try:
            if USE_API_INTEGRATION:
                from api_integration import api_insert_document
                result = api_insert_document(task_type, data)
                
                if result.get("success") == True or result.get("status") == "success":
                    document_id = result.get("inserted_id") or result.get("data", {}).get("_id", "Unknown")
                    
                    # Clear collected data after successful submission
                    state["collected_data"] = {}
                    
                    return {
                        "status": "success",
                        "response": f"""🎉 **Success! Your {task_type.replace('_', ' ').title()} has been saved.**

📝 **Document ID**: {document_id}

How else can I help you today?""",
                        "task_type": task_type,
                        "api_called": task_type,
                        "document_id": document_id
                    }
                else:
                    error_msg = result.get("message", "Unknown error")
                    return {
                        "status": "error",
                        "response": f"❌ **Error saving data**: {error_msg}\n\nPlease try again or contact support.",
                        "task_type": task_type
                    }
            else:
                return {
                    "status": "error",
                    "response": "API integration not available"
                }
                
        except Exception as e:
            logger.error(f"API call error: {e}")
            return {
                "status": "error", 
                "response": f"❌ **System Error**: {e}\n\nPlease try again later."
            }

    def _analyze_user_intent(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Analyze what the user wants to do before asking for credentials"""
        
        try:
            prompt = f"""Analyze this user request and determine what they want to do:

User: "{user_input}"

Available collections and their typical use cases:
- user_registration: Register new users/employees
- supplier_registration: Register new suppliers/vendors  
- purchase_order: Create purchase orders
- travel_request: Submit travel requests
- expense_reimbursement: Request expense reimbursements
- employee_leave_request: Apply for employee leave
- interview_scheduling: Schedule job interviews
- training_registration: Register for training programs
- payroll_management: Process payroll and salary
- performance_review: Conduct performance reviews
- inventory_management: Manage inventory and stock
- customer_support_ticket: Create support tickets
- role_management: Create and manage user roles/permissions
- access_control: Manage user access permissions
- contract_management: Manage contracts and agreements
- invoice_management: Process invoices and billing
- attendance_tracking: Track employee attendance
- shift_scheduling: Schedule employee shifts
- meeting_scheduler: Schedule meetings
- project_assignment: Assign employees to projects
- order_placement: Place product orders
- product_catalog: Manage product catalog
- client_registration: Register new clients
- vendor_management: Manage vendor relationships
- warehouse_management: Manage warehouse operations
- And 24 other specialized business operations...

Respond with JSON:
{{
    "detected_task": "collection_name or null",
    "user_intent": "clear description of what user wants",
    "requires_authorization": true/false,
    "required_roles": ["list", "of", "roles", "who", "can", "do", "this"],
    "confidence": 0.0-1.0,
    "response": "professional response acknowledging their request"
}}"""

            response = self.model.generate_content(prompt)
            analysis = self._parse_json_response(response.text)
            
            if analysis and analysis.get("detected_task"):
                state["intent_analyzed"] = True
                state["detected_task"] = analysis["detected_task"]
                state["required_roles"] = analysis.get("required_roles", ["admin"])
                state["user_intent"] = analysis.get("user_intent")
                
                if analysis.get("requires_authorization", True):
                    # Determine who can access this
                    access_requirements = get_endpoint_access_requirements()
                    required_positions = access_requirements.get(analysis["detected_task"], ["admin"])
                    
                    authorized_users = []
                    if "admin" in required_positions:
                        authorized_users.append("**EMP001** (Admin User)")
                    if "hr_manager" in required_positions:
                        authorized_users.append("**EMP002** (HR Manager)")
                    if "procurement_manager" in required_positions:
                        authorized_users.append("**EMP003** (Procurement Manager)")
                    if "finance_manager" in required_positions:
                        authorized_users.append("**EMP004** (Finance Manager)")
                    if "director" in required_positions:
                        authorized_users.append("**EMP005** (Director)")
                    
                    if not authorized_users:
                        authorized_users = ["**EMP001** (Admin User)"]
                    
                    return {
                        "status": "authorization_required",
                        "response": f"""🔐 **Authorization Required**

I understand you want to: **{analysis.get('user_intent', 'perform this operation')}**

This operation requires appropriate authorization. Only the following personnel can access this:
• {chr(10).join(authorized_users)}

If you are one of these authorized personnel, please provide your **Employee ID** to continue.""",
                        "intent": analysis.get("user_intent"),
                        "task": analysis["detected_task"],
                        "required_roles": required_positions,
                        "session_id": session_id
                    }
                else:
                    # No authorization needed (rare case)
                    state["user_validated"] = True
                    return {
                        "status": "success",
                        "response": analysis.get("response", "I'll help you with that."),
                        "intent": analysis.get("user_intent"),
                        "task": analysis["detected_task"],
                        "session_id": session_id
                    }
            else:
                # Couldn't determine intent - ask for clarification
                return {
                    "status": "clarification_needed",
                    "response": """👋 **Welcome to the Enterprise System!**

I'm here to help you with various business operations. I can assist with:

🏢 **Business Operations:**
• User & Supplier Registration
• Purchase Orders & Procurement
• Inventory & Warehouse Management

👥 **HR & Employee Services:**
• Interview Scheduling
• Training Registration
• Performance Reviews & Payroll
• Leave Requests & Attendance

💼 **Finance & Administration:**
• Invoice Management
• Expense Reimbursement
• Contract Management

🎯 **Customer & Support:**
• Support Ticket Creation
• Customer Feedback Management
• Knowledge Base Management

Please tell me what you'd like to do, and I'll guide you through the process.""",
                    "intent": "welcome",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                "status": "error",
                "response": "I'm having trouble understanding your request. Could you please rephrase what you'd like to do?",
                "session_id": session_id
            }

    def _handle_user_validation(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Handle user position validation after intent is known"""
        
        # Check if user provided an employee ID
        user_input_upper = user_input.upper()
        employee_id = None
        
        # Extract employee ID from input
        if "EMP" in user_input_upper:
            import re
            match = re.search(r'EMP\d+', user_input_upper)
            if match:
                employee_id = match.group()
        
        if not employee_id:
            # Request employee ID based on the detected task
            task_type = state.get("detected_task")
            required_roles = state.get("required_roles", ["admin"])
            
            authorized_users = []
            if "admin" in required_roles:
                authorized_users.append("**EMP001** (Admin User)")
            if "hr_manager" in required_roles:
                authorized_users.append("**EMP002** (HR Manager)")
            if "procurement_manager" in required_roles:
                authorized_users.append("**EMP003** (Procurement Manager)")
            if "finance_manager" in required_roles:
                authorized_users.append("**EMP004** (Finance Manager)")
            if "director" in required_roles:
                authorized_users.append("**EMP005** (Director)")
            
            if not authorized_users:
                authorized_users = ["**EMP001** (Admin User)"]
            
            return {
                "status": "awaiting_employee_id",
                "response": f"""🆔 **Employee ID Required**

For **{state.get('user_intent', 'this operation')}**, please provide your Employee ID.

**Authorized Personnel:**
• {chr(10).join(authorized_users)}

Enter your Employee ID (e.g., EMP001):""",
                "intent": "request_employee_id",
                "action": "request_employee_id",
                "session_id": session_id
            }
        
        # Get required positions for detected task
        task_type = state.get("detected_task") or state.get("current_task")
        if not task_type:
            # If no detected task, validate with general permissions
            validation_result = validate_user_position(employee_id, ["admin", "manager", "director"])
        else:
            access_requirements = get_endpoint_access_requirements()
            required_positions = access_requirements.get(task_type, access_requirements.get('default', ['admin']))
            validation_result = validate_user_position(employee_id, required_positions)
        
        if validation_result['valid']:
            # User is authorized
            state["user_validated"] = True
            state["user_details"] = validation_result['user_details']
            
            if task_type:
                # Set the current task and continue processing
                state["current_task"] = task_type
                user_intent = state.get("user_intent", f"{task_type.replace('_', ' ')}")
                
                return {
                    "status": "success", 
                    "response": f"""✅ **Access Granted**

Welcome, {validation_result['user_details']['name']} ({validation_result['user_details']['position']})

You are authorized to proceed with: **{user_intent}**

Please provide the required information to continue.""",
                    "intent": "access_granted",
                    "action": "collect_data",
                    "task": task_type,
                    "session_id": session_id
                }
            else:
                return {
                    "status": "success",
                    "response": f"""✅ **Access Granted**

Welcome, {validation_result['user_details']['name']} ({validation_result['user_details']['position']})

I'm ready to assist you with enterprise operations. What would you like to do?""",
                    "intent": "user_authenticated",
                    "action": "ready_for_requests",
                    "session_id": session_id
                }
        else:
            # User is not authorized
            return {
                "status": "error",
                "response": f"""🚫 **Access Denied**

{validation_result['reason']}

**Required Positions for {task_type.replace('_', ' ').title() if task_type else 'this operation'}:**
{', '.join(get_endpoint_access_requirements().get(task_type, ['admin'])) if task_type else 'Valid employee'}

Please contact your administrator if you believe this is an error.""",
                "intent": "access_denied",
                "action": "access_denied",
                "session_id": session_id
            }

# Initialize chatbot and create dummy users for testing
chatbot = DynamicChatBot()

# Create dummy users for position-based access testing
try:
    create_dummy_users()
except Exception as e:
    logger.warning(f"⚠️ Could not create dummy users: {e}")

def process_chat(message: str, session_id: str = "default") -> Dict[str, Any]:
    """Main chat processing function"""
    return chatbot.process_message(message, session_id)

def reset_chat_session(session_id: str = "default"):
    """Reset chat session"""
    chatbot.reset_session(session_id)

if __name__ == "__main__":
    print("🤖 Dynamic ChatBot (Zero Hardcoding)")
    print("=" * 60)
    print("\nTest conversation:")
    print("-" * 60)
    
    # Test with natural conversation
    test_messages = [
        "Hi there!",
        "I want to register as a new user",
        "My name is Sarah Johnson, email sarah.j@example.com and phone is 555-123-4567",
        "My password should be SecurePass123!",
        "Yes, save it please"
    ]
    
    test_session = "test_001"
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = process_chat(msg, test_session)
        print(f"🤖 Bot: {result['response']}")
        print(f"📊 Status: {result.get('status', 'N/A')}")
        if result.get('data'):
            print(f"📦 Data: {result['data']}")