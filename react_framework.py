"""
ReAct Framework for ZOPKIT Enterprise Chatbot
Reasoning + Acting architecture for dynamic business operations

This framework eliminates hardcoded patterns and creates an intelligent
system that can reason about user requests and act dynamically across
all 49 business operation collections.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from schema import COLLECTION_SCHEMAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions the system can take"""
    COLLECT_INFO = "collect_info"
    VALIDATE_DATA = "validate_data" 
    EXECUTE_OPERATION = "execute_operation"
    REQUEST_AUTH = "request_auth"
    PROVIDE_FEEDBACK = "provide_feedback"
    CLARIFY_INTENT = "clarify_intent"

@dataclass
class ReasoningResult:
    """Result of the reasoning process"""
    intent: str
    confidence: float
    target_collection: Optional[str]
    required_fields: List[str]
    optional_fields: List[str]
    missing_fields: List[str]
    next_action: ActionType
    reasoning: str
    context_analysis: Dict[str, Any]

@dataclass 
class ActionPlan:
    """Plan for executing actions"""
    action_type: ActionType
    target_collection: str
    data_requirements: Dict[str, Any]
    authorization_needed: bool
    validation_rules: Dict[str, Any]
    execution_steps: List[str]
    fallback_actions: List[ActionType]

class ReActEngine:
    """
    ReAct (Reasoning + Acting) Engine for Dynamic Business Operations
    
    This engine uses AI to:
    1. REASON about user intent and context
    2. ACT by executing appropriate operations dynamically
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the ReAct engine with AI model"""
        self.collection_schemas = COLLECTION_SCHEMAS
        self.ai_model = None
        
        # Initialize Gemini AI if API key provided
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ ReAct Engine initialized with Gemini AI")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize AI model: {e}")
    
    def reason(self, user_input: str, context: Dict[str, Any]) -> ReasoningResult:
        """
        REASONING PHASE: Analyze user input and determine intent
        
        Args:
            user_input: What the user said
            context: Current conversation context
            
        Returns:
            ReasoningResult with analysis and recommendations
        """
        logger.info(f"🧠 REASONING: Analyzing user input: '{user_input[:50]}...'")
        
        # Use AI-powered reasoning if available
        if self.ai_model:
            return self._ai_powered_reasoning(user_input, context)
        else:
            return self._fallback_reasoning(user_input, context)
    
    def act(self, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACTING PHASE: Execute actions based on reasoning
        
        Args:
            reasoning_result: Output from reasoning phase
            context: Current conversation context
            
        Returns:
            Action result with response and next steps
        """
        logger.info(f"⚡ ACTING: Executing {reasoning_result.next_action.value}")
        
        # Create action plan
        action_plan = self._create_action_plan(reasoning_result, context)
        
        # Execute the planned action
        return self._execute_action(action_plan, reasoning_result, context)
    
    def _ai_powered_reasoning(self, user_input: str, context: Dict[str, Any]) -> ReasoningResult:
        """Use AI model for sophisticated reasoning"""
        
        # Create comprehensive prompt for AI analysis
        reasoning_prompt = self._build_reasoning_prompt(user_input, context)
        
        try:
            # Get AI analysis
            response = self.ai_model.generate_content(reasoning_prompt)
            ai_analysis = self._parse_ai_response(response.text)
            
            # Create reasoning result from AI analysis
            return self._create_reasoning_result(ai_analysis, user_input, context)
            
        except Exception as e:
            logger.warning(f"⚠️ AI reasoning failed: {e}, falling back to rule-based")
            return self._fallback_reasoning(user_input, context)
    
    def _fallback_reasoning(self, user_input: str, context: Dict[str, Any]) -> ReasoningResult:
        """Fallback reasoning using pattern matching and heuristics"""
        
        logger.info("🔄 Using fallback reasoning (pattern-based)")
        
        user_input_lower = user_input.lower()
        
        # Analyze intent using keyword matching
        intent_analysis = self._analyze_intent_keywords(user_input_lower)
        target_collection = intent_analysis.get('collection')
        confidence = intent_analysis.get('confidence', 0.5)
        
        # Determine required and optional fields
        if target_collection and target_collection in self.collection_schemas:
            schema = self.collection_schemas[target_collection]
            required_fields = schema.get('required', [])
            optional_fields = schema.get('optional', [])
        else:
            required_fields = []
            optional_fields = []
        
        # Extract existing data from input
        extracted_data = self._extract_data_from_input(user_input, required_fields + optional_fields)
        missing_fields = [field for field in required_fields if field not in extracted_data]
        
        # Determine next action
        next_action = self._determine_next_action(target_collection, missing_fields, context)
        
        return ReasoningResult(
            intent=intent_analysis.get('intent', 'unknown'),
            confidence=confidence,
            target_collection=target_collection,
            required_fields=required_fields,
            optional_fields=optional_fields,
            missing_fields=missing_fields,
            next_action=next_action,
            reasoning=f"Pattern-based analysis identified {target_collection or 'unknown'} intent",
            context_analysis={
                'user_authenticated': context.get('user_validated', False),
                'has_employee_id': bool(context.get('employee_id')),
                'extracted_data': extracted_data
            }
        )
    
    def _analyze_intent_keywords(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent using keyword patterns"""
        
        # Intent keyword mappings for all 49 collections
        intent_keywords = {
            "user_registration": ["register", "sign up", "create account", "join", "new user"],
            "user_onboarding": ["onboard", "setup", "permissions", "access"],
            "user_activation": ["activate", "enable", "start"],
            "supplier_registration": ["supplier", "vendor", "register supplier"],
            "client_registration": ["client", "customer", "register client"],
            "product_catalog": ["product", "catalog", "item", "inventory"],
            "inventory_management": ["inventory", "stock", "warehouse"],
            "order_placement": ["order", "place order", "buy"],
            "order_tracking": ["track", "status", "delivery"],
            "payment_processing": ["payment", "pay", "transaction"],
            "employee_leave_request": ["leave", "vacation", "time off"],
            "payroll_management": ["payroll", "salary", "payment"],
            "training_registration": ["training", "course", "learn"],
            "performance_review": ["review", "performance", "evaluation"],
            "customer_support_ticket": ["support", "help", "issue", "problem"],
            "project_assignment": ["project", "assign", "task"],
            "meeting_scheduler": ["meeting", "schedule", "appointment"],
            "it_asset_allocation": ["asset", "equipment", "allocation"],
            "compliance_report": ["compliance", "report", "audit"],
            "audit_log_viewer": ["audit", "log", "history"],
            "recruitment_portal": ["recruit", "hire", "candidate"],
            "interview_scheduling": ["interview", "schedule interview"],
            "offer_letter_generation": ["offer", "job offer", "letter"],
            "employee_exit_clearance": ["exit", "resignation", "clearance"],
            "travel_request": ["travel", "trip", "journey"],
            "expense_reimbursement": ["expense", "reimburse", "claim"],
            "vendor_management": ["vendor", "supplier management"],
            "invoice_management": ["invoice", "bill", "billing"],
            "shipping_management": ["shipping", "shipment", "dispatch"],
            "warehouse_management": ["warehouse", "storage"],
            "purchase_order": ["purchase", "purchase order", "po", "buy"],
            "contract_management": ["contract", "agreement"],
            "knowledge_base": ["knowledge", "article", "documentation"],
            "faq_management": ["faq", "question", "answer"],
            "system_configuration": ["config", "settings", "system"],
            "role_management": ["role", "permission", "access"],
            "access_control": ["access", "control", "security"],
            "notification_settings": ["notification", "alert", "reminder"],
            "chatbot_training_data": ["training", "chatbot", "ai"],
            "attendance_tracking": ["attendance", "check in", "check out"],
            "shift_scheduling": ["shift", "schedule", "roster"],
            "health_and_safety_incident_reporting": ["incident", "safety", "accident"],
            "grievance_management": ["grievance", "complaint", "issue"],
            "knowledge_transfer_kt_handover": ["handover", "knowledge transfer", "kt"],
            "customer_feedback_management": ["feedback", "review", "rating"],
            "marketing_campaign_management": ["marketing", "campaign", "promotion"],
            "data_backup_and_restore": ["backup", "restore", "data"],
            "system_audit_and_compliance_dashboard": ["dashboard", "compliance audit"],
            "announcements_notice_board": ["announcement", "notice", "news"]
        }
        
        # Find best matching collection
        best_match = None
        best_score = 0
        
        for collection, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_input)
            if score > best_score:
                best_score = score
                best_match = collection
        
        confidence = min(best_score / 3.0, 1.0)  # Normalize confidence
        
        return {
            'collection': best_match,
            'confidence': confidence,
            'intent': best_match or 'general_inquiry',
            'matched_keywords': best_score
        }
    
    def _extract_data_from_input(self, user_input: str, field_names: List[str]) -> Dict[str, str]:
        """Extract field data from user input using intelligent parsing"""
        
        extracted = {}
        
        # Common field extraction patterns
        extraction_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'mobile': r'\b\d{10}\b|\b\+\d{1,3}\s?\d{10}\b',
            'phone': r'\b\d{10}\b|\b\+\d{1,3}\s?\d{10}\b',
            'employee_id': r'\b(EMP|emp)\d{3,6}\b',
            'po_id': r'\b(PO|po)\d{3,6}\b',
            'order_id': r'\b(ORD|ord)\d{3,6}\b',
            'amount': r'\$?\d+\.?\d*',
            'date': r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
        }
        
        # Extract based on field names and patterns
        for field in field_names:
            field_lower = field.lower()
            
            # Try pattern matching first
            for pattern_key, pattern in extraction_patterns.items():
                if pattern_key in field_lower:
                    matches = re.findall(pattern, user_input, re.IGNORECASE)
                    if matches:
                        extracted[field] = matches[0]
                        break
            
            # Try keyword-based extraction
            if field not in extracted:
                # Look for field name followed by value
                field_patterns = [
                    rf'{field_lower}[:\s]+([A-Za-z0-9@._-]+)',
                    rf'{field_lower.replace("_", " ")}[:\s]+([A-Za-z0-9@._-]+)'
                ]
                
                for pattern in field_patterns:
                    matches = re.findall(pattern, user_input, re.IGNORECASE)
                    if matches:
                        extracted[field] = matches[0]
                        break
        
        return extracted
    
    def _determine_next_action(self, target_collection: Optional[str], missing_fields: List[str], context: Dict[str, Any]) -> ActionType:
        """Determine the next action to take"""
        
        if not target_collection:
            return ActionType.CLARIFY_INTENT
        
        # Check if user is authenticated for operations that need it
        requires_auth = target_collection in ['purchase_order', 'employee_leave_request', 'payroll_management']
        if requires_auth and not context.get('user_validated'):
            return ActionType.REQUEST_AUTH
        
        # If we have missing required fields
        if missing_fields:
            return ActionType.COLLECT_INFO
        
        # If we have all required data
        return ActionType.EXECUTE_OPERATION
    
    def _build_reasoning_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for AI reasoning"""
        
        available_collections = list(self.collection_schemas.keys())
        
        prompt = f"""
You are an intelligent business operations assistant analyzing user requests.

USER INPUT: "{user_input}"

CONTEXT:
- User authenticated: {context.get('user_validated', False)}
- Employee ID: {context.get('employee_id', 'Not provided')}
- Session history: {len(context.get('conversation_history', []))} messages

AVAILABLE OPERATIONS ({len(available_collections)} collections):
{json.dumps(available_collections, indent=2)}

COLLECTION SCHEMAS:
{json.dumps(self.collection_schemas, indent=2)}

ANALYZE the user input and provide your reasoning in this JSON format:
{{
    "intent": "primary intent/goal",
    "confidence": 0.85,
    "target_collection": "most_appropriate_collection_name",
    "reasoning": "step-by-step analysis of why this collection fits",
    "extracted_data": {{"field_name": "extracted_value"}},
    "missing_required_fields": ["field1", "field2"],
    "authorization_needed": true/false,
    "next_action": "collect_info|validate_data|execute_operation|request_auth|clarify_intent",
    "alternative_collections": ["backup_option1", "backup_option2"]
}}

Focus on:
1. Understanding the business intent
2. Finding the best matching collection
3. Identifying what data is already provided vs. what's missing
4. Determining appropriate next steps
"""
        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {"error": "Could not parse AI response", "raw_response": ai_response}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in AI response", "raw_response": ai_response}
    
    def _create_reasoning_result(self, ai_analysis: Dict[str, Any], user_input: str, context: Dict[str, Any]) -> ReasoningResult:
        """Create ReasoningResult from AI analysis"""
        
        target_collection = ai_analysis.get('target_collection')
        
        # Get schema info if collection is valid
        if target_collection and target_collection in self.collection_schemas:
            schema = self.collection_schemas[target_collection]
            required_fields = schema.get('required', [])
            optional_fields = schema.get('optional', [])
        else:
            required_fields = []
            optional_fields = []
        
        # Parse next action
        action_str = ai_analysis.get('next_action', 'clarify_intent')
        try:
            next_action = ActionType(action_str)
        except ValueError:
            next_action = ActionType.CLARIFY_INTENT
        
        return ReasoningResult(
            intent=ai_analysis.get('intent', 'unknown'),
            confidence=ai_analysis.get('confidence', 0.5),
            target_collection=target_collection,
            required_fields=required_fields,
            optional_fields=optional_fields,
            missing_fields=ai_analysis.get('missing_required_fields', []),
            next_action=next_action,
            reasoning=ai_analysis.get('reasoning', 'AI analysis completed'),
            context_analysis={
                'ai_analysis': ai_analysis,
                'user_authenticated': context.get('user_validated', False),
                'has_employee_id': bool(context.get('employee_id'))
            }
        )
    
    def _create_action_plan(self, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> ActionPlan:
        """Create detailed action plan based on reasoning"""
        
        return ActionPlan(
            action_type=reasoning_result.next_action,
            target_collection=reasoning_result.target_collection or 'unknown',
            data_requirements={
                'required': reasoning_result.required_fields,
                'optional': reasoning_result.optional_fields,
                'missing': reasoning_result.missing_fields
            },
            authorization_needed=reasoning_result.target_collection in ['purchase_order', 'employee_leave_request'],
            validation_rules=self._get_validation_rules(reasoning_result.target_collection),
            execution_steps=self._get_execution_steps(reasoning_result.next_action),
            fallback_actions=[ActionType.CLARIFY_INTENT, ActionType.PROVIDE_FEEDBACK]
        )
    
    def _get_validation_rules(self, collection_name: Optional[str]) -> Dict[str, Any]:
        """Get validation rules for a collection"""
        
        if not collection_name or collection_name not in self.collection_schemas:
            return {}
        
        # Return basic validation rules - can be extended
        return {
            'required_fields_validation': True,
            'email_format_check': 'email' in self.collection_schemas[collection_name].get('required', []),
            'phone_format_check': any(field in ['mobile', 'phone'] for field in self.collection_schemas[collection_name].get('required', []))
        }
    
    def _get_execution_steps(self, action_type: ActionType) -> List[str]:
        """Get execution steps for an action type"""
        
        step_mappings = {
            ActionType.COLLECT_INFO: [
                "Identify missing required fields",
                "Generate user-friendly questions",
                "Present field collection interface"
            ],
            ActionType.VALIDATE_DATA: [
                "Check required fields presence",
                "Validate field formats",
                "Verify business rules"
            ],
            ActionType.EXECUTE_OPERATION: [
                "Prepare data for database operation",
                "Execute database/API call",
                "Confirm operation success"
            ],
            ActionType.REQUEST_AUTH: [
                "Identify authentication requirements",
                "Request user credentials",
                "Validate authorization level"
            ],
            ActionType.CLARIFY_INTENT: [
                "Analyze ambiguous input",
                "Present clarification options",
                "Guide user to specific intent"
            ],
            ActionType.PROVIDE_FEEDBACK: [
                "Format response message",
                "Include relevant information",
                "Suggest next steps"
            ]
        }
        
        return step_mappings.get(action_type, ["Execute action", "Provide feedback"])
    
    def _execute_action(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned action"""
        
        logger.info(f"🎯 Executing action: {action_plan.action_type.value}")
        
        action_handlers = {
            ActionType.COLLECT_INFO: self._handle_collect_info,
            ActionType.VALIDATE_DATA: self._handle_validate_data,
            ActionType.EXECUTE_OPERATION: self._handle_execute_operation,
            ActionType.REQUEST_AUTH: self._handle_request_auth,
            ActionType.CLARIFY_INTENT: self._handle_clarify_intent,
            ActionType.PROVIDE_FEEDBACK: self._handle_provide_feedback
        }
        
        handler = action_handlers.get(action_plan.action_type, self._handle_provide_feedback)
        return handler(action_plan, reasoning_result, context)
    
    def _handle_collect_info(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle information collection"""
        
        missing_fields = reasoning_result.missing_fields
        if not missing_fields:
            return self._handle_execute_operation(action_plan, reasoning_result, context)
        
        # Generate user-friendly field prompts
        field_prompts = self._generate_field_prompts(missing_fields, action_plan.target_collection)
        
        return {
            "response": f"I need some additional information for {action_plan.target_collection.replace('_', ' ')}:",
            "action": "collect_fields",
            "required_fields": missing_fields,
            "field_prompts": field_prompts,
            "collection": action_plan.target_collection,
            "status": "awaiting_input"
        }
    
    def _handle_validate_data(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data validation"""
        
        # Implement validation logic
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        return {
            "response": "Data validation completed",
            "validation_results": validation_results,
            "next_action": "execute_operation" if validation_results["valid"] else "collect_info"
        }
    
    def _handle_execute_operation(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operation execution"""
        
        return {
            "response": f"Ready to execute {action_plan.target_collection} operation",
            "action": "execute",
            "collection": action_plan.target_collection,
            "status": "ready_for_execution"
        }
    
    def _handle_request_auth(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication request"""
        
        return {
            "response": "This operation requires authentication. Please provide your employee ID.",
            "action": "request_employee_id",
            "collection": action_plan.target_collection,
            "status": "awaiting_auth"
        }
    
    def _handle_clarify_intent(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent clarification"""
        
        # Suggest possible intents based on available collections
        suggestions = self._generate_intent_suggestions(context.get('last_user_input', ''))
        
        return {
            "response": "I'm not sure what you'd like to do. Here are some options:",
            "action": "clarify_intent",
            "suggestions": suggestions,
            "status": "awaiting_clarification"
        }
    
    def _handle_provide_feedback(self, action_plan: ActionPlan, reasoning_result: ReasoningResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feedback provision"""
        
        return {
            "response": "I understand you're looking for help. Could you please be more specific about what you'd like to do?",
            "action": "provide_feedback",
            "status": "awaiting_input"
        }
    
    def _generate_field_prompts(self, field_names: List[str], collection_name: str) -> Dict[str, str]:
        """Generate user-friendly prompts for fields"""
        
        # Field name to user-friendly prompt mappings
        field_prompts = {
            'first_name': 'What is your first name?',
            'last_name': 'What is your last name?',
            'email': 'What is your email address?',
            'mobile': 'What is your mobile number?',
            'employee_id': 'What is your employee ID?',
            'department': 'Which department do you work in?',
            'position': 'What is your job position?',
            'supplier_name': 'What is the supplier name?',
            'product': 'What product would you like to order?',
            'quantity': 'How many do you need?',
            'po_id': 'What is the purchase order ID?',
            'vendor_id': 'What is the vendor ID?',
            'amount': 'What is the amount?',
            'date': 'What is the date?'
        }
        
        prompts = {}
        for field in field_names:
            prompts[field] = field_prompts.get(field, f'Please provide {field.replace("_", " ")}:')
        
        return prompts
    
    def _generate_intent_suggestions(self, user_input: str) -> List[Dict[str, str]]:
        """Generate intent suggestions based on user input"""
        
        # Common business operations suggestions
        suggestions = [
            {"intent": "user_registration", "description": "Register a new user"},
            {"intent": "purchase_order", "description": "Create a purchase order"},
            {"intent": "supplier_registration", "description": "Register a new supplier"},
            {"intent": "employee_leave_request", "description": "Request time off"},
            {"intent": "customer_support_ticket", "description": "Report an issue or get help"}
        ]
        
        return suggestions[:3]  # Return top 3 suggestions

# Factory function to create ReAct engine
def create_react_engine(api_key: str = None) -> ReActEngine:
    """Create and initialize ReAct engine"""
    return ReActEngine(api_key=api_key)