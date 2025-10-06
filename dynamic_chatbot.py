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
    USE_API_INTEGRATION = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ API Integration layer not available - will use direct database")
    from db import insert_document, check_supplier_eligibility

# Import validation system
try:
    from user_validation import validate_user_data
    VALIDATION_AVAILABLE = True
    logger.info("✅ User validation system loaded - will validate user registrations")
except ImportError:
    VALIDATION_AVAILABLE = False
    logger.warning("⚠️ User validation system not available - will skip validation")
    validate_user_data = None

# Import session management
try:
    from session_manager import SessionManager
    session_manager = SessionManager()
    logger.info("✅ Session Manager loaded")
except ImportError:
    session_manager = None
    logger.warning("⚠️ Session Manager not available")
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
        """Process any user message dynamically with session tracking"""
        logger.info(f"💬 [{session_id}] User: {user_input}")
        
        # Initialize conversation state
        if session_id not in self.conversation_state:
            self.conversation_state[session_id] = {
                "history": [],
                "current_task": None,
                "collected_data": {},
                "context": {},
                "session_initialized": False
            }
        
        state = self.conversation_state[session_id]
        
        # Track user activity in session management system
        from session_manager import session_manager
        if state.get("user_validated") and state.get("employee_id"):
            session_manager.update_session_activity(session_id, {
                "type": "user_message",
                "message": user_input,
                "employee_id": state.get("employee_id")
            })
        
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
        
        # Check if authenticated user is starting a new task (supplier product check patterns)
        if state.get("user_validated", False):
            # Check for supplier product check patterns
            import re
            user_input_upper = user_input.upper()
            supplier_patterns = [
                r'\bCHECK\s+SUP\d+\s+PRODUCTS?\b',
                r'\bSUP\d+\s+PRODUCTS?\b',
                r'\bSHOW\s+.*SUP\d+.*PRODUCTS?\b',
                r'\bLIST\s+.*SUP\d+.*ITEMS?\b',
                r'\bWHAT\s+.*SUP\d+.*HAVE\b',
                r'\bAVAILABLE\s+.*SUP\d+\b',
                r'\bSUP\d+\s+INVENTORY\b'
            ]
            
            # Check for purchase order patterns
            purchase_order_patterns = [
                r'\bCREATE\s+.*PURCHASE\s+ORDER\b',
                r'\bPURCHASE\s+ORDER\b',
                r'\bNEW\s+.*PURCHASE\s+ORDER\b',
                r'\bWANT\s+TO\s+CREATE\s+.*PURCHASE\s+ORDER\b',
                r'\bI\s+WANT\s+TO\s+CREATE\s+A\s+PURCHASE\s+ORDER\b',
                r'\bMAKE\s+.*PURCHASE\s+ORDER\b',
                r'\bSUBMIT\s+.*PURCHASE\s+ORDER\b',
                r'\bPLACE\s+.*PURCHASE\s+ORDER\b'
            ]
            
            # Check for other new task patterns
            other_task_patterns = [
                r'\bCREATE\s+.*USER\b',
                r'\bREGISTER\s+.*USER\b',
                r'\bNEW\s+.*USER\b',
                r'\bREGISTER\s+.*SUPPLIER\b',
                r'\bTRAVEL\s+REQUEST\b',
                r'\bEXPENSE\s+REIMBURSEMENT\b',
                r'\bLEAVE\s+REQUEST\b',
                r'\bSCHEDULE\s+.*INTERVIEW\b',
                r'\bTRAINING\s+REGISTRATION\b'
            ]
            
            is_supplier_check = any(re.search(pattern, user_input_upper) for pattern in supplier_patterns)
            is_purchase_order = any(re.search(pattern, user_input_upper) for pattern in purchase_order_patterns)
            is_other_task = any(re.search(pattern, user_input_upper) for pattern in other_task_patterns)
            
            if is_supplier_check:
                logger.info(f"🔄 Detected new supplier product check request from authenticated user")
                # Reset session for new task but keep authentication
                state["intent_analyzed"] = False
                state["current_task"] = None
                state["collected_data"] = {}
                state["operation_type"] = None
                # Re-analyze intent for the new task
                return self._analyze_user_intent(user_input, state, session_id)
            elif is_purchase_order:
                logger.info(f"🔄 Detected new purchase order request from authenticated user")
                # Reset session for new task but keep authentication
                state["intent_analyzed"] = False
                state["current_task"] = None
                state["collected_data"] = {}
                state["operation_type"] = None
                # Re-analyze intent for the new task
                return self._analyze_user_intent(user_input, state, session_id)
            elif is_other_task:
                logger.info(f"🔄 Detected new task request from authenticated user")
                # Reset session for new task but keep authentication
                state["intent_analyzed"] = False
                state["current_task"] = None
                state["collected_data"] = {}
                state["operation_type"] = None
                # Re-analyze intent for the new task
                return self._analyze_user_intent(user_input, state, session_id)
        
        # Route to Query Node if this is a query operation
        if state.get("operation_type") == "query" and state.get("user_validated", False):
            return self._process_query_node(user_input, state, session_id)
        
        # Build dynamic context for data operations
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
        
        # Handle special task: supplier_product_check
        if task_type == "supplier_product_check":
            return self._handle_supplier_product_check(user_input, state, session_id)
        
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
            
            # Validate user registration data
            if state["current_task"] == "user_registration" and VALIDATION_AVAILABLE:
                validation_result = validate_user_data(state["collected_data"])
                is_valid = validation_result.get("valid", False)
                validation_errors = validation_result.get("errors", [])
                
                if not is_valid:
                    error_message = f"""❌ **User Registration Validation Failed**

**Please fix the following issues:**
{chr(10).join(f'• {error}' for error in validation_errors)}

Please provide the correct information and try again."""
                    
                    return {
                        "status": "error",
                        "response": error_message,
                        "intent": "user_registration_validation_failed",
                        "action": "validation_failed",
                        "validation_errors": validation_errors
                    }
            
            # Use API integration or direct database
            if USE_API_INTEGRATION:
                result = api_insert_document(state["current_task"], state["collected_data"])
            else:
                result = insert_document(state["current_task"], state["collected_data"])
            
            if result["success"]:
                task_name = state["current_task"].replace("_", " ").title()
                
                # Track successful registration in user session
                if session_manager and "session_id" in state and state["session_id"]:
                    try:
                        session_manager.track_user_registration(
                            state["session_id"],
                            state["current_task"],
                            state["current_task"],
                            state["collected_data"],
                            result.get('inserted_id')
                        )
                        logger.info(f"Tracked registration {state['current_task']} for session {state['session_id']}")
                    except Exception as e:
                        logger.warning(f"Failed to track registration: {e}")
                
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
            
            # Validate user registration data immediately when updated
            if task_type == "user_registration" and VALIDATION_AVAILABLE:
                validation_result = validate_user_data(state["collected_data"])
                is_valid = validation_result.get("valid", False)
                validation_errors = validation_result.get("errors", [])
                
                if not is_valid:
                    error_message = f"""❌ **Data Validation Error**

**Please fix the following issues:**
{chr(10).join(f'• {error}' for error in validation_errors)}

Please provide the correct information."""
                    
                    return {
                        "status": "error",
                        "response": error_message,
                        "intent": "user_registration_validation_failed",
                        "action": "validation_failed",
                        "validation_errors": validation_errors
                    }
            
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

    def _handle_supplier_product_check(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Handle supplier product availability check"""
        try:
            import re
            import requests
            
            # Extract supplier ID from user input
            supplier_match = re.search(r'\bSUP\d+\b', user_input.upper())
            
            if not supplier_match:
                return {
                    "status": "field_collection",
                    "response": """🔍 **Product Availability Check**

Please provide the **Supplier ID** you want to check.

**Example**: SUP001, SUP002, or SUP003

**Format**: SUPxxx (where xxx is numbers)

Which supplier would you like to check?""",
                    "task": "supplier_product_check",
                    "session_id": session_id
                }
            
            supplier_id = supplier_match.group(0)
            
            # Call the supplier products API
            try:
                api_response = requests.post(
                    'http://localhost:5001/api/check-supplier-products',
                    json={"supplier_id": supplier_id},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if api_response.status_code == 200:
                    result = api_response.json()
                    
                    if result.get("success"):
                        # Clear the task since we're done
                        state["current_task"] = None
                        state["collected_data"] = {}
                        
                        return {
                            "status": "success",
                            "response": result["message"],
                            "task": "purchase_order" if result.get("show_purchase_button") else None,
                            "action": "product_check_complete",
                            "data": {
                                "supplier_id": supplier_id,
                                "products_available": result.get("products_count", 0)
                            },
                            "session_id": session_id,
                            "show_purchase_button": result.get("show_purchase_button", False)
                        }
                    else:
                        return {
                            "status": "error",
                            "response": result.get("message", f"❌ Error checking products for {supplier_id}"),
                            "task": "supplier_product_check",
                            "session_id": session_id
                        }
                else:
                    return {
                        "status": "error",
                        "response": f"❌ **Server Error**\n\nUnable to check products for {supplier_id}. Please try again later.",
                        "task": "supplier_product_check",
                        "session_id": session_id
                    }
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API call failed for supplier product check: {e}")
                return {
                    "status": "error",
                    "response": f"❌ **Connection Error**\n\nUnable to connect to product service. Please try again later.",
                    "task": "supplier_product_check",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Supplier product check error: {e}")
            return {
                "status": "error",
                "response": f"❌ **System Error**\n\nError processing your request: {str(e)}",
                "task": "supplier_product_check",
                "session_id": session_id
            }

    def _analyze_user_intent(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Analyze what the user wants to do before asking for credentials"""
        
        try:
            # Check if user provided Employee ID in their initial request
            user_input_upper = user_input.upper()
            embedded_employee_id = None
            if "EMP" in user_input_upper:
                import re
                match = re.search(r'EMP\d+', user_input_upper)
                if match:
                    embedded_employee_id = match.group()
            
            prompt = f"""Analyze this user request and determine what they want to do:

User: "{user_input}"

IMPORTANT: Check if the user has provided an Employee ID (like EMP001, EMP002, etc.) in their message.
If they have, they should be immediately authenticated if they are authorized for the requested operation.

**CRITICAL DOCUMENT ID RECOGNITION**:
If the user says something like:
- "I ALREADY REGISTER AS USER 68de2e97dce38701b5c19a8f" 
- "This is my document ID 68de2e97dce38701b5c19a8f"
- "My user ID is 68de2e97dce38701b5c19a8f"
- Any 24-character hexadecimal string following words like "register", "user", "document id", "my id"

This should be detected as:
- detected_task: "user_registration"
- operation_type: "query" 
- user_intent: "retrieve existing user registration details using document ID"
- natural_query: "find user with document ID 68de2e97dce38701b5c19a8f"

Available collections and their typical use cases:
- user_registration: Register new users/employees
- supplier_registration: Register new suppliers/vendors  
- supplier_product_check: Check what products are available from a specific supplier
  EXACT PATTERNS TO DETECT:
  * "Check SUP001 products" -> supplier_product_check
  * "Check SUP002 products" -> supplier_product_check
  * "Check SUP003 products" -> supplier_product_check
  * "What products does SUP001 have" -> supplier_product_check
  * "Show me SUP002 inventory" -> supplier_product_check
  * "List SUP003 items" -> supplier_product_check
  * "Available products from SUP001" -> supplier_product_check
  * "SUP001 product catalog" -> supplier_product_check
  * "See what SUP002 offers" -> supplier_product_check
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

Determine if this is:
1. DATA CREATION/UPDATE: User wants to register, create, submit, schedule, or modify something
2. DATA QUERY: User is asking questions, requesting information, wanting to search or view data

Query examples:
- "How many orders in June 2025?" -> purchase_order query
- "When did employee 37644 check in?" -> attendance_tracking query
- "Show all leave requests for HR department" -> employee_leave_request query
- "List suppliers in California" -> supplier_registration query
- "What is the status of purchase order 12345?" -> purchase_order query
- "I already registered as supplier, this is my id 68de3..., I want my details" -> supplier_registration query
- "Get my supplier information using ID 68de3..." -> supplier_registration query
- "Show my user registration details" -> user_registration query
- "I already register as role management, this is my id 68df..., I want my details" -> role_management query
- "Get my role management information" -> role_management query
- "I registered for training, show my details" -> training_registration query
- "My contract management ID is xyz, get my details" -> contract_management query
- "show me which details i given in structured way" -> customer_support_ticket query (user wants to see their recent ticket)
- "show me my details" -> Last created collection query (find user's most recent record)
- "what did I provide" -> Last created collection query (retrieve user's recent submission)
- "display my information" -> Last created collection query (show user's data)

**Critical Collection Detection Rules**:
1. **SUPPLIER PRODUCT CHECK PATTERNS** (highest priority):
   - "Check SUP001 products" -> supplier_product_check
   - "Check SUP002 products" -> supplier_product_check  
   - "Check SUP003 products" -> supplier_product_check
   - "What products does SUP001 have" -> supplier_product_check
   - "Show me SUP002 inventory" -> supplier_product_check
   - "List SUP003 items" -> supplier_product_check
   - "Available products from SUP001" -> supplier_product_check
   - Any mention of "SUP" + numbers + ("products"|"items"|"inventory"|"available"|"check"|"show"|"list") -> supplier_product_check
2. If user mentions "supplier" for registration -> supplier_registration
3. If user mentions "role management" -> role_management  
4. If user mentions "training" -> training_registration
5. If user mentions "contract" -> contract_management
6. If user mentions "purchase order" -> purchase_order
7. If user mentions "user registration" or just "user" -> user_registration
8. If user mentions "support ticket" or "ticket" -> customer_support_ticket
9. Always match the EXACT collection name the user mentions in their request

**Context-Aware Query Detection**:
- If user asks "show me my details" or "what did I provide" or "display my information" WITHOUT specifying collection:
  -> This is a contextual query to retrieve their most recent submission
  -> Look at session context to determine which collection they last interacted with
  -> Default to customer_support_ticket if no context available

Respond with JSON:
{{
    "detected_task": "collection_name or null",
    "user_intent": "clear description of what user wants",
    "operation_type": "create|query|update|general",
    "query_type": "count|list|find|search|aggregate|null",
    "natural_query": "extracted query intent for natural language processing",
    "requires_authorization": true/false,
    "required_roles": ["list", "of", "roles", "who", "can", "do", "this"],
    "confidence": 0.0-1.0,
    "response": "professional response acknowledging their request"
}}"""

            response = self.model.generate_content(prompt)
            analysis = self._parse_json_response(response.text)
            
            # Debug logging for intent detection
            logger.info(f"🔍 Intent Analysis Debug for input: '{user_input}'")
            logger.info(f"🤖 AI Raw Response: {response.text}")
            logger.info(f"📋 Parsed Analysis: {analysis}")
            
            if analysis and analysis.get("detected_task"):
                logger.info(f"✅ Task detected: {analysis.get('detected_task')}")
                logger.info(f"🎯 Operation type: {analysis.get('operation_type')}")
                logger.info(f"💡 User intent: {analysis.get('user_intent')}")
                state["intent_analyzed"] = True
                state["detected_task"] = analysis["detected_task"]
                state["required_roles"] = analysis.get("required_roles", ["admin"])
                state["user_intent"] = analysis.get("user_intent")
                state["operation_type"] = analysis.get("operation_type", "create")
                state["query_type"] = analysis.get("query_type")
                state["natural_query"] = analysis.get("natural_query")
                
                if analysis.get("requires_authorization", True):
                    # Determine who can access this
                    access_requirements = get_endpoint_access_requirements()
                    required_positions = access_requirements.get(analysis["detected_task"], ["admin"])
                    
                    # Check if user is already authenticated and authorized
                    if state.get("user_validated", False):
                        user_position = state.get("user_position", "admin")
                        if user_position in required_positions or "admin" in user_position:
                            logger.info(f"✅ User already authenticated with sufficient privileges for {analysis['detected_task']}")
                            # User is already validated and has access, proceed directly
                            if analysis.get("operation_type") == "query":
                                return self._process_query_node(user_input, state, session_id)
                            else:
                                # Check if this is a purchase order creation request
                                if analysis.get("detected_task") == "purchase_order":
                                    return {
                                        "status": "authenticated_proceed",
                                        "response": f"""🔄 **Purchase Order Creation Started**

You are authorized to proceed with: **{analysis.get('user_intent', 'create a new purchase order')}**

🛒 **Ready to create a new purchase order**

Please provide the following required information:
• **Purchase Order ID**: Unique identifier for this purchase order
• **Vendor ID**: Supplier/vendor identifier (e.g., SUP001)
• **Product Name**: Item or service to be purchased
• **Quantity**: Number of units needed

You can provide all details at once or one by one.""",
                                        "intent": analysis.get("user_intent"),
                                        "task": analysis["detected_task"],
                                        "operation_type": analysis.get("operation_type", "create"),
                                        "show_purchase_button": True,
                                        "session_id": session_id
                                    }
                                else:
                                    # Continue with normal data operation flow
                                    return {
                                        "status": "authenticated_proceed",
                                        "response": f"""🔄 **New Task Started**

You are authorized to proceed with: **{analysis.get('user_intent', 'this operation')}**

Please provide the required information to continue.""",
                                        "intent": analysis.get("user_intent"),
                                        "task": analysis["detected_task"],
                                        "operation_type": analysis.get("operation_type", "create"),
                                        "session_id": session_id
                                    }
                        else:
                            return {
                                "status": "access_denied",
                                "response": f"""❌ **Access Denied**

Your position ({user_position}) is not authorized for **{analysis['detected_task'].replace('_', ' ').title()}**.

**Required Positions:** {', '.join(required_positions)}

Please contact your administrator if you believe this is an error.""",
                                "session_id": session_id
                            }
                    
                    # Check if user provided Employee ID in their request
                    elif embedded_employee_id:
                        # Validate the embedded Employee ID immediately
                        task_type = analysis["detected_task"]
                        validation_result = validate_user_position(embedded_employee_id, required_positions)
                        
                        if validation_result["valid"]:
                            # Create user session immediately
                            if session_manager:
                                try:
                                    user_session_data = session_manager.create_user_session(
                                        embedded_employee_id, 
                                        validation_result["user_details"]
                                    )
                                    state["session_id"] = user_session_data.get("session_id")
                                    logger.info(f"Created user session {state['session_id']} for {embedded_employee_id}")
                                except Exception as e:
                                    logger.warning(f"Failed to create session: {e}")
                            
                            # Set user as validated and proceed
                            state["user_validated"] = True
                            state["employee_id"] = embedded_employee_id
                            state["user_position"] = validation_result["user_details"].get("position", "admin")
                            
                            # Route to appropriate processor based on operation type
                            if analysis.get("operation_type") == "query":
                                return self._process_query_node(user_input, state, session_id)
                            else:
                                # Check if this is a purchase order creation request
                                if analysis.get("detected_task") == "purchase_order":
                                    return {
                                        "status": "authenticated_proceed",
                                        "response": f"""✅ **Purchase Order Creation - Access Granted**

Welcome, {validation_result["user_details"].get("name", "User")} ({validation_result["user_details"].get("position", "admin")})
🆔 Employee ID: {embedded_employee_id}
📅 Login: {datetime.now().strftime("%Y-%m-%d %H:%M")}

🛒 **Ready to create a new purchase order**

Please provide the following required information:
• **Purchase Order ID**: Unique identifier for this purchase order
• **Vendor ID**: Supplier/vendor identifier (e.g., SUP001)
• **Product Name**: Item or service to be purchased
• **Quantity**: Number of units needed

You can provide all details at once or one by one.""",
                                        "intent": analysis.get("user_intent"),
                                        "task": analysis["detected_task"],
                                        "operation_type": analysis.get("operation_type", "create"),
                                        "show_purchase_button": True,
                                        "session_id": session_id
                                    }
                                else:
                                    # Continue with normal data operation flow
                                    return {
                                        "status": "authenticated_proceed",
                                        "response": f"""✅ **Access Granted - Session Active**

Welcome, {validation_result["user_details"].get("name", "User")} ({validation_result["user_details"].get("position", "admin")})
🆔 Employee ID: {embedded_employee_id}
📅 Login: {datetime.now().strftime("%Y-%m-%d %H:%M")}

You are authorized to proceed with: **{analysis.get('user_intent', 'this operation')}**

Please provide the required information to continue.""",
                                        "intent": analysis.get("user_intent"),
                                    "task": analysis["detected_task"],
                                    "operation_type": analysis.get("operation_type", "create"),
                                    "session_id": session_id
                                }
                        else:
                            # Invalid Employee ID
                            return {
                                "status": "access_denied",
                                "response": f"""❌ **Access Denied**

Employee ID {embedded_employee_id} is not authorized for this operation.

{validation_result['reason']}

**Required Positions for {analysis['detected_task'].replace('_', ' ').title()}:**
{', '.join(required_positions)}

Please contact your administrator if you believe this is an error.""",
                                "session_id": session_id
                            }
                    
                    # No embedded Employee ID - request it
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
                        "operation_type": analysis.get("operation_type", "create"),
                        "query_type": analysis.get("query_type"),
                        "natural_query": analysis.get("natural_query"),
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

    def _format_query_results(self, collection_name: str, results: list, count: int) -> str:
        """Format query results in a user-friendly way based on collection type"""
        
        if collection_name == "supplier_products":
            return self._format_supplier_products(results, count)
        elif collection_name == "user_registration":
            return self._format_user_registration(results, count)
        elif collection_name == "supplier_registration":
            return self._format_supplier_registration(results, count)
        elif collection_name == "purchase_order":
            return self._format_purchase_order(results, count)
        else:
            # Default formatting for other collections
            return self._format_default_results(results, count)
    
    def _format_supplier_products(self, results: list, count: int) -> str:
        """Format supplier products in a catalog-style display"""
        response_text = f"🛒 **Product Catalog** ({count} products available)\n\n"
        
        for i, product in enumerate(results[:10], 1):
            name = product.get('name', 'N/A')
            price = product.get('price', 0)
            stock = product.get('stock_quantity', 0)
            category = product.get('category', 'N/A')
            brand = product.get('brand', 'N/A')
            description = product.get('description', 'No description available')
            warranty = product.get('warranty_months', 0)
            
            # Stock status
            min_stock = product.get('min_stock_level', 0)
            if stock > min_stock * 2:
                stock_status = "✅ In Stock"
            elif stock > min_stock:
                stock_status = "⚠️ Low Stock"
            else:
                stock_status = "❌ Out of Stock"
            
            response_text += f"**{i}. {name}**\n"
            response_text += f"   💰 **Price:** ${price:.2f}\n"
            response_text += f"   📦 **Stock:** {stock} units ({stock_status})\n"
            response_text += f"   🏷️ **Category:** {category}\n"
            response_text += f"   🏢 **Brand:** {brand}\n"
            if warranty > 0:
                response_text += f"   🛡️ **Warranty:** {warranty} months\n"
            response_text += f"   📝 **Description:** {description}\n\n"
        
        return response_text
    
    def _format_user_registration(self, results: list, count: int) -> str:
        """Format user registration results"""
        response_text = f"👤 **User Profile** ({count} record found)\n\n"
        
        for i, user in enumerate(results[:5], 1):
            first_name = user.get('first_name', 'N/A')
            last_name = user.get('last_name', 'N/A')
            email = user.get('email', 'N/A')
            created_at = user.get('created_at', 'N/A')
            position = user.get('position', 'Not specified')
            
            response_text += f"**{i}. {first_name} {last_name}**\n"
            response_text += f"   📧 **Email:** {email}\n"
            response_text += f"   💼 **Position:** {position}\n"
            response_text += f"   📅 **Registered:** {created_at}\n\n"
        
        return response_text
    
    def _format_default_results(self, results: list, count: int) -> str:
        """Default formatting for other collections"""
        response_text = f"📊 **Query Results** ({count} records)\n\n"
        
        for i, doc in enumerate(results[:10], 1):
            response_text += f"**{i}.** "
            # Format document fields nicely, excluding technical fields
            exclude_fields = ['_id', 'created_at', 'updated_at', '__v']
            for key, value in doc.items():
                if key not in exclude_fields:
                    response_text += f"{key.replace('_', ' ').title()}: {value}, "
            response_text = response_text.rstrip(", ") + "\n"
        
        return response_text

    def _query_via_api(self, collection_name: str, mongodb_query: Dict, query_config: Dict) -> Dict[str, Any]:
        """Query data using API endpoints instead of direct database access"""
        try:
            import requests
            
            # Map collection names to API endpoints
            # The API integration has endpoints for all 49 collections
            api_url = f"http://localhost:5000/api/{collection_name}"
            
            logger.info(f"🔗 Calling API endpoint: {api_url}")
            logger.info(f"📄 Query parameters: {mongodb_query}")
            
            # Convert MongoDB query to API parameters
            params = {}
            
            # Handle ObjectId queries - convert to string for API
            if "_id" in mongodb_query:
                id_value = mongodb_query["_id"]
                # Handle different ObjectId formats
                if isinstance(id_value, dict) and "$oid" in id_value:
                    params["_id"] = id_value["$oid"]
                elif hasattr(id_value, '__str__'):
                    params["_id"] = str(id_value)
                else:
                    params["_id"] = id_value
            
            # Add other query parameters
            for key, value in mongodb_query.items():
                if key != "_id":
                    if isinstance(value, dict):
                        # Handle complex query operators by converting to string
                        params[key] = str(value)
                    else:
                        params[key] = str(value) if value is not None else ""
            
            logger.info(f"🎯 Final API parameters: {params}")
            
            # Make API request
            response = requests.get(api_url, params=params, timeout=10)
            
            logger.info(f"📡 API Response Status: {response.status_code}")
            logger.info(f"📋 API Response Preview: {response.text[:200]}...")
            
            if response.status_code == 200:
                api_data = response.json()
                if api_data.get("status") == "success":
                    data = api_data.get("data", [])
                    count = api_data.get("count", len(data))
                    logger.info(f"✅ API Success: Found {count} records")
                    return {
                        "success": True,
                        "data": data,
                        "count": count
                    }
                else:
                    logger.warning(f"❌ API Error: {api_data.get('message', 'Unknown error')}")
                    return {
                        "success": False,
                        "error": api_data.get("message", "API query failed")
                    }
            else:
                logger.error(f"❌ API Request Failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.ConnectionError:
            # Fallback to direct database access if API is not available
            logger.warning("API server not available, falling back to database")
            return self._query_via_database(collection_name, mongodb_query, query_config)
        except Exception as e:
            logger.error(f"API query error: {e}")
            return {
                "success": False,
                "error": f"API query failed: {str(e)}"
            }

    def _query_via_database(self, collection_name: str, mongodb_query: Dict, query_config: Dict) -> Dict[str, Any]:
        """Fallback method for direct database queries"""
        try:
            from db import get_database
            from bson import ObjectId
            
            logger.info(f"🗄️ Database Fallback Query - Collection: {collection_name}")
            logger.info(f"📋 Original MongoDB Query: {mongodb_query}")
            
            db = get_database()
            collection = db[collection_name]
            operation = query_config.get("mongodb_operation", "find")
            
            # Handle ObjectId conversion if needed
            if "_id" in mongodb_query:
                id_value = mongodb_query["_id"]
                logger.info(f"🔑 Processing _id field: {id_value} (type: {type(id_value)})")
                if isinstance(id_value, str) and len(id_value) == 24:
                    try:
                        original_id = id_value
                        mongodb_query["_id"] = ObjectId(id_value)
                        logger.info(f"✅ ObjectId conversion successful: {original_id} -> {mongodb_query['_id']}")
                    except Exception as e:
                        logger.error(f"❌ ObjectId conversion failed: {e}")
                        pass
            
            logger.info(f"🎯 Final MongoDB Query: {mongodb_query}")
            logger.info(f"⚙️ Operation: {operation}")
            
            if operation == "count_documents":
                result = collection.count_documents(mongodb_query)
                logger.info(f"📊 Count Query Result: {result} documents found")
                return {"success": True, "count": result, "data": []}
            elif operation == "find":
                try:
                    limit = int(query_config.get("limit", 50))
                except (ValueError, TypeError):
                    limit = 50
                
                logger.info(f"🔍 Executing find query with limit {limit}")
                cursor = collection.find(mongodb_query).limit(limit)
                results = list(cursor)
                logger.info(f"📋 Find Query Result: {len(results)} documents found")
                
                if results:
                    logger.info(f"📄 Sample result: {results[0]}")
                
                return {"success": True, "data": results, "count": len(results)}
            else:
                return {"success": False, "error": "Unsupported operation"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _process_query_node(self, user_input: str, state: Dict, session_id: str) -> Dict[str, Any]:
        """Query Node: Process natural language queries and convert to MongoDB operations"""
        
        try:
            # Extract query parameters from state
            detected_task = state.get("detected_task")
            
            # Map task names to actual collection names
            task_to_collection_mapping = {
                "supplier_product_check": "supplier_products",
                "user_registration": "user_registration",
                "supplier_registration": "supplier_registration",
                "purchase_order": "purchase_order",
                "travel_request": "travel_request",
                "expense_reimbursement": "expense_reimbursement",
                "employee_leave_request": "employee_leave_request",
                "interview_scheduling": "interview_scheduling",
                "training_registration": "training_registration",
                "payroll_management": "payroll_management",
                "performance_review": "performance_review",
                "inventory_management": "inventory_management",
                "customer_support_ticket": "customer_support_ticket",
                "role_management": "role_management",
                "access_control": "access_control",
                "contract_management": "contract_management",
                "invoice_management": "invoice_management",
                "attendance_tracking": "attendance_tracking",
                "shift_scheduling": "shift_scheduling",
                "meeting_scheduler": "meeting_scheduler",
                "project_assignment": "project_assignment"
            }
            
            collection_name = task_to_collection_mapping.get(detected_task, detected_task)
            natural_query = state.get("natural_query", user_input)
            query_type = state.get("query_type", "find")
            
            # Generate MongoDB query from natural language
            query_prompt = f"""Convert this natural language query to MongoDB query for collection '{collection_name}':

Natural Query: "{natural_query}"
Query Type: {query_type}
Collection: {collection_name}

Available fields for {collection_name}: {list(COLLECTION_SCHEMAS.get(collection_name, {}).keys())}

**CRITICAL INSTRUCTION**: 
The user is authenticated as an employee, but this does NOT mean you should add employee_id to the query.
ONLY query by the fields that the user explicitly mentions in their natural query.
DO NOT automatically add employee_id, user_id, or any authentication fields unless the user specifically asks for them.

**CRITICAL DOCUMENT ID DETECTION**:
Look for these patterns in the natural query:
- "document id 68e116d1b88401b56ae6c4ca" -> Extract: 68e116d1b88401b56ae6c4ca
- "my document id is 68e116d1b88401b56ae6c4ca" -> Extract: 68e116d1b88401b56ae6c4ca  
- "id 68e116d1b88401b56ae6c4ca" -> Extract: 68e116d1b88401b56ae6c4ca
- Any 24-character hexadecimal string -> Use as _id

If you find a 24-character hex string (like 68e116d1b88401b56ae6c4ca), create query: {{"_id": "68e116d1b88401b56ae6c4ca"}}

IMPORTANT: If the query contains a MongoDB ObjectId (like _id 68de3a043af7466cd71bfff9), use it to find the specific document.

Convert to MongoDB operations and provide results formatting:

Respond with JSON:
{{
    "mongodb_query": {{"field": "value"}},
    "mongodb_operation": "find|count_documents|aggregate",
    "sort_criteria": {{"field": 1}},
    "limit": 10,
    "projection": {{}},
    "aggregation_pipeline": [],
    "result_format": "list|count|summary",
    "response_template": "How to format the results for user"
}}

Examples:
- "How many orders in June 2025?" -> {{"mongodb_query": {{"created_at": {{"$gte": "2025-06-01", "$lt": "2025-07-01"}}}}, "mongodb_operation": "count_documents", "limit": 10}}
- "Show employee 37644 attendance" -> {{"mongodb_query": {{"employee_id": "37644"}}, "mongodb_operation": "find", "limit": 10}}
- "List all pending leave requests" -> {{"mongodb_query": {{"status": "pending"}}, "mongodb_operation": "find", "limit": 10}}
- "_id 68de3a043af7466cd71bfff9 my details" -> {{"mongodb_query": {{"_id": "68de3a043af7466cd71bfff9"}}, "mongodb_operation": "find", "limit": 1}}
- "this is my document id 68e116d1b88401b56ae6c4ca.i want my details" -> {{"mongodb_query": {{"_id": "68e116d1b88401b56ae6c4ca"}}, "mongodb_operation": "find", "limit": 1}}
- "document ID 68e116d1b88401b56ae6c4ca details" -> {{"mongodb_query": {{"_id": "68e116d1b88401b56ae6c4ca"}}, "mongodb_operation": "find", "limit": 1}}
- "68de2e97dce38701b5c19a8f this is my document id" -> {{"mongodb_query": {{"_id": "68de2e97dce38701b5c19a8f"}}, "mongodb_operation": "find", "limit": 1}}

**WRONG EXAMPLES** (DO NOT DO THIS):
- "68de2e97dce38701b5c19a8f this is my document id" -> {{"mongodb_query": {{"_id": "68de2e97dce38701b5c19a8f", "employee_id": "EMP001"}}, "mongodb_operation": "find", "limit": 1}} ❌ WRONG!
- Document ID query should NEVER include employee_id or any other field ❌

**CRITICAL RULES**:
1. For ObjectId queries (_id field), use simple string format like "_id": "68de3a043af7466cd71bfff9", NOT $oid format
2. When user provides a 24-character hex string (document ID), ALWAYS query by _id field ONLY
3. Set limit to 1 for document ID queries to ensure single result
4. Look for patterns: "document id", "doc id", "id", followed by 24-character hex string
5. **NEVER combine _id with other fields** - if user provides document ID, query should be: {{"_id": "document_id"}} and NOTHING ELSE
6. **DO NOT add employee_id, user_id, or any other fields** when querying by document _id

Return ONLY valid JSON."""

            response = self.model.generate_content(query_prompt)
            query_config = self._parse_json_response(response.text)
            
            if not query_config:
                return {
                    "status": "error",
                    "response": "I couldn't understand your query. Could you please rephrase it?",
                    "session_id": session_id
                }
            
            # Execute the query using API endpoints
            from bson import ObjectId
            import requests
            
            try:
                # Use API integration instead of direct database access
                mongodb_query = query_config.get("mongodb_query", {})
                operation = query_config.get("mongodb_operation", "find")
                
                # Call the appropriate API endpoint
                api_result = self._query_via_api(collection_name, mongodb_query, query_config)
                
                # Process the API result
                if api_result.get("success"):
                    results = api_result.get("data", [])
                    count = api_result.get("count", 0)
                    
                    if operation == "count_documents" or count == 0:
                        if count > 0:
                            response_text = f"🔢 **Query Results**\n\nFound **{count}** records matching your criteria."
                        else:
                            response_text = "📭 **No Results Found**\n\nNo records match your query criteria."
                    else:
                        response_text = self._format_query_results(collection_name, results, count)
                        
                        if len(results) > 10:
                            response_text += f"\n*... and {len(results) - 10} more records*"
                else:
                    # API query failed
                    error_msg = api_result.get("error", "Unknown API error")
                    response_text = f"❌ **API Query Error**\n\n{error_msg}"
                
                return {
                    "status": "query_completed",
                    "response": response_text,
                    "query_results": api_result.get("data", []) if api_result.get("success") else [],
                    "session_id": session_id
                }
                
            except Exception as db_error:
                logger.error(f"Database query error: {db_error}")
                return {
                    "status": "error",
                    "response": f"❌ **Database Error**\n\nThere was an issue executing your query: {str(db_error)}",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "status": "error",
                "response": "❌ **Query Processing Error**\n\nI encountered an issue processing your query. Please try again.",
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
            # User is authorized - create/update session
            state["user_validated"] = True
            state["user_details"] = validation_result['user_details']
            state["employee_id"] = employee_id
            
            # Initialize session management for this user
            from session_manager import session_manager, create_session_for_user
            
            if not state.get("session_initialized"):
                # Create a proper user session with full details
                user_session_id = create_session_for_user(employee_id, validation_result['user_details'])
                state["user_session_id"] = user_session_id
                state["login_time"] = datetime.now().isoformat()
                state["session_initialized"] = True
                
                logger.info(f"Created user session {user_session_id} for {employee_id}")
            
            if task_type:
                # Set the current task and continue processing
                state["current_task"] = task_type
                user_intent = state.get("user_intent", f"{task_type.replace('_', ' ')}")
                
                return {
                    "status": "success", 
                    "response": f"""✅ **Access Granted - Session Active**

Welcome, {validation_result['user_details']['name']} ({validation_result['user_details']['position']})
🆔 Employee ID: {employee_id}
📅 Login: {datetime.now().strftime('%Y-%m-%d %H:%M')}

You are authorized to proceed with: **{user_intent}**

Please provide the required information to continue.""",
                    "intent": "access_granted",
                    "action": "collect_data",
                    "task": task_type,
                    "session_id": session_id,
                    "user_session_id": state.get("user_session_id"),
                    "employee_id": employee_id
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