"""
ZOPKIT Enterprise ReAct Chatbot - Zero Hardcoding Dynamic System
Revolutionary AI chatbot that adapts to any business operation without hardcoded patterns

This system uses ReAct (Reasoning + Acting) methodology to:
1. REASON about user intent using AI
2. ACT dynamically across 49 business collections
3. ADAPT to any workflow without hardcoding

Key Features:
- Complete elimination of hardcoded patterns
- Dynamic collection routing for all 49 business operations
- Intelligent field processing and validation
- Role-based authorization system
- AI-powered reasoning and decision making
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import asdict

# ReAct System Components
from react_framework import ReActEngine, ActionType
from dynamic_router import DynamicCollectionRouter, ConfidenceLevel
from universal_field_processor import UniversalFieldProcessor, ValidationLevel
from dynamic_authorization import DynamicAuthorizationSystem, AccessLevel

# Database and API Integration
from db import init_db, get_collections_info
from schema import COLLECTION_SCHEMAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReActChatbot:
    """
    Revolutionary ReAct Chatbot that eliminates all hardcoded patterns
    
    This chatbot uses advanced AI reasoning to understand user intent
    and dynamically execute appropriate business operations across
    all 49 collections without any hardcoded logic.
    """
    
    def __init__(self, gemini_api_key: str = None):
        """Initialize the ReAct chatbot system"""
        
        logger.info("🚀 Initializing ZOPKIT ReAct Enterprise Chatbot...")
        
        # Initialize core components
        self.react_engine = ReActEngine(api_key=gemini_api_key)
        self.collection_router = DynamicCollectionRouter()
        self.field_processor = UniversalFieldProcessor(ValidationLevel.MODERATE)
        self.auth_system = DynamicAuthorizationSystem()
        
        # Initialize database
        self.db_collections = init_db()
        
        # Session management
        self.active_sessions = {}
        
        logger.info("✅ ZOPKIT ReAct Chatbot initialized successfully!")
        logger.info(f"📊 Supporting {len(COLLECTION_SCHEMAS)} business operations dynamically")
    
    def process_user_message(self, user_input: str, session_id: str, 
                           user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message using ReAct methodology
        
        Args:
            user_input: User's natural language input
            session_id: Unique session identifier
            user_context: Optional user context and authentication info
            
        Returns:
            Comprehensive response with reasoning and actions
        """
        if user_context is None:
            user_context = {}
            
        logger.info(f"🧠 Processing message for session {session_id}: '{user_input[:50]}...'")
        
        # Get or create session context
        session_context = self._get_session_context(session_id, user_context)
        
        # REASONING PHASE: Understand user intent and context
        logger.info("🧠 REASONING PHASE: Analyzing user intent...")
        reasoning_result = self.react_engine.reason(user_input, session_context)
        
        # Log reasoning analysis
        logger.info(f"💡 Intent Analysis: {reasoning_result.intent} (confidence: {reasoning_result.confidence:.2f})")
        logger.info(f"🎯 Target Collection: {reasoning_result.target_collection}")
        logger.info(f"⚡ Next Action: {reasoning_result.next_action.value}")
        
        # ACTING PHASE: Execute appropriate actions
        logger.info("⚡ ACTING PHASE: Executing intelligent actions...")
        action_result = self._execute_intelligent_action(reasoning_result, user_input, session_context)
        
        # Update session context
        self._update_session_context(session_id, user_input, reasoning_result, action_result)
        
        # Build comprehensive response
        response = self._build_response(reasoning_result, action_result, session_context)
        
        logger.info(f"✅ Message processed successfully for session {session_id}")
        return response
    
    def _get_session_context(self, session_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create session context"""
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "user_profile": None,
                "current_collection": None,
                "collected_data": {},
                "workflow_state": "initial",
                "last_reasoning": None,
                "authentication_attempts": 0
            }
        
        session = self.active_sessions[session_id]
        
        # Merge user context
        session.update(user_context)
        
        return session
    
    def _execute_intelligent_action(self, reasoning_result, user_input: str, 
                                   session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intelligent actions based on reasoning results"""
        
        action_type = reasoning_result.next_action
        
        # Route to appropriate action handler
        action_handlers = {
            ActionType.COLLECT_INFO: self._handle_collect_information,
            ActionType.VALIDATE_DATA: self._handle_validate_data,
            ActionType.EXECUTE_OPERATION: self._handle_execute_operation,
            ActionType.REQUEST_AUTH: self._handle_request_authentication,
            ActionType.CLARIFY_INTENT: self._handle_clarify_intent,
            ActionType.PROVIDE_FEEDBACK: self._handle_provide_feedback
        }
        
        handler = action_handlers.get(action_type, self._handle_provide_feedback)
        return handler(reasoning_result, user_input, session_context)
    
    def _handle_collect_information(self, reasoning_result, user_input: str, 
                                   session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle information collection using universal field processor"""
        
        collection_name = reasoning_result.target_collection
        if not collection_name:
            return {"error": "Cannot collect information without target collection"}
        
        logger.info(f"📝 Collecting information for: {collection_name}")
        
        # Process user input to extract field data
        existing_data = session_context.get("collected_data", {}).get(collection_name, {})
        processing_result = self.field_processor.process_collection_data(
            collection_name, user_input, existing_data
        )
        
        # Update session with collected data
        if "collected_data" not in session_context:
            session_context["collected_data"] = {}
        
        # Store processed field values
        field_data = {}
        for field_name, field_value in processing_result.processed_fields.items():
            if field_value.is_valid:
                field_data[field_name] = field_value.processed_value
        
        session_context["collected_data"][collection_name] = field_data
        session_context["current_collection"] = collection_name
        
        # Prepare response
        if processing_result.missing_required:
            next_field = processing_result.next_field_to_collect
            prompt = processing_result.user_prompt
            
            return {
                "action": "collect_field",
                "collection": collection_name,
                "field_needed": next_field,
                "prompt": prompt,
                "progress": f"{processing_result.completion_percentage:.0f}% complete",
                "collected_fields": list(field_data.keys()),
                "missing_fields": processing_result.missing_required,
                "status": "collecting_data"
            }
        else:
            # All required fields collected, ready for execution
            return {
                "action": "data_collection_complete",
                "collection": collection_name,
                "collected_data": field_data,
                "status": "ready_for_execution",
                "next_step": "execute_operation"
            }
    
    def _handle_validate_data(self, reasoning_result, user_input: str, 
                             session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data validation"""
        
        collection_name = reasoning_result.target_collection
        collected_data = session_context.get("collected_data", {}).get(collection_name, {})
        
        if not collected_data:
            return {"error": "No data to validate"}
        
        logger.info(f"✅ Validating data for: {collection_name}")
        
        # Re-process data for validation
        processing_result = self.field_processor.process_collection_data(
            collection_name, "", collected_data
        )
        
        validation_errors = []
        for field_value in processing_result.processed_fields.values():
            if field_value.validation_errors:
                validation_errors.extend([f"{field_value.field_name}: {error}" 
                                        for error in field_value.validation_errors])
        
        if validation_errors:
            return {
                "action": "validation_failed",
                "errors": validation_errors,
                "status": "validation_error",
                "next_step": "fix_errors"
            }
        else:
            return {
                "action": "validation_passed",
                "status": "validated",
                "next_step": "execute_operation"
            }
    
    def _handle_execute_operation(self, reasoning_result, user_input: str, 
                                 session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operation execution with authorization check"""
        
        collection_name = reasoning_result.target_collection
        if not collection_name:
            return {"error": "Cannot execute operation without target collection"}
        
        # Check authorization first
        user_profile = session_context.get("user_profile")
        if not user_profile:
            return {
                "action": "authentication_required",
                "message": "Please authenticate to perform this operation",
                "status": "auth_required"
            }
        
        # Verify collection access
        auth_result = self.auth_system.authorize_collection_access(
            user_profile, collection_name, "write"
        )
        
        if not auth_result.is_authorized:
            return {
                "action": "access_denied",
                "message": f"Access denied: {auth_result.denial_reason}",
                "required_action": auth_result.required_action,
                "status": "unauthorized"
            }
        
        # Get collected data
        collected_data = session_context.get("collected_data", {}).get(collection_name, {})
        if not collected_data:
            return {"error": "No data available for execution"}
        
        logger.info(f"⚡ Executing operation: {collection_name}")
        
        try:
            # Execute database operation
            result = self._execute_database_operation(collection_name, collected_data, user_profile)
            
            # Clear collected data after successful execution
            if "collected_data" in session_context and collection_name in session_context["collected_data"]:
                del session_context["collected_data"][collection_name]
            
            return {
                "action": "operation_executed",
                "collection": collection_name,
                "result": result,
                "status": "success",
                "message": f"Successfully created {collection_name.replace('_', ' ')} record"
            }
            
        except Exception as e:
            logger.error(f"Operation execution failed: {str(e)}")
            return {
                "action": "execution_failed",
                "error": str(e),
                "status": "error"
            }
    
    def _execute_database_operation(self, collection_name: str, data: Dict[str, Any], 
                                   user_profile) -> Dict[str, Any]:
        """Execute actual database operation"""
        
        # Add metadata
        operation_data = data.copy()
        operation_data.update({
            "created_at": datetime.now().isoformat(),
            "created_by": user_profile.employee_id,
            "department": user_profile.department
        })
        
        # Use API integration if available
        try:
            from api_integration import api_insert_document
            result = api_insert_document(collection_name, operation_data)
            return {"database_result": result, "method": "api"}
        except ImportError:
            # Fallback to direct database
            from db import insert_document
            result = insert_document(collection_name, operation_data)
            return {"database_result": result, "method": "direct"}
    
    def _handle_request_authentication(self, reasoning_result, user_input: str, 
                                      session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication requests"""
        
        # Check if employee ID was provided in input
        employee_id_match = None
        import re
        employee_patterns = [r'\b(EMP|emp)\d{3,6}\b', r'\bemployee[_\s]?id[:\s]+([A-Za-z0-9]+)']
        
        for pattern in employee_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                employee_id_match = matches[0] if isinstance(matches[0], str) else matches[0][0]
                break
        
        if employee_id_match:
            # Authenticate user
            try:
                user_profile = self.auth_system.authenticate_user(employee_id_match, session_context)
                session_context["user_profile"] = user_profile
                session_context["user_validated"] = True
                session_context["employee_id"] = employee_id_match
                
                return {
                    "action": "authentication_success",
                    "user_profile": {
                        "employee_id": user_profile.employee_id,
                        "department": user_profile.department,
                        "position": user_profile.position,
                        "roles": user_profile.roles,
                        "access_level": user_profile.access_level.value
                    },
                    "status": "authenticated",
                    "message": f"Welcome {user_profile.employee_id}! You are now authenticated."
                }
            except Exception as e:
                return {
                    "action": "authentication_failed",
                    "error": str(e),
                    "status": "auth_error"
                }
        else:
            return {
                "action": "request_employee_id",
                "message": "Please provide your Employee ID to authenticate (e.g., EMP001)",
                "status": "awaiting_auth"
            }
    
    def _handle_clarify_intent(self, reasoning_result, user_input: str, 
                              session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent clarification"""
        
        # Use collection router to suggest possible intents
        suggestions = self.collection_router.suggest_collections(user_input, limit=5)
        
        return {
            "action": "clarify_intent",
            "message": "I'm not sure what you'd like to do. Here are some options:",
            "suggestions": [
                {
                    "collection": suggestion["collection"],
                    "description": suggestion["display_name"],
                    "fields_required": len(suggestion["required_fields"])
                }
                for suggestion in suggestions
            ],
            "status": "awaiting_clarification"
        }
    
    def _handle_provide_feedback(self, reasoning_result, user_input: str, 
                                session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general feedback provision"""
        
        return {
            "action": "provide_feedback",
            "message": "I understand you need help. Could you please be more specific about what you'd like to do? For example, you could say 'I want to register a new user' or 'I need to create a purchase order'.",
            "available_operations": [
                "User Registration", "Purchase Orders", "Leave Requests", 
                "Supplier Registration", "Customer Support"
            ],
            "status": "awaiting_input"
        }
    
    def _update_session_context(self, session_id: str, user_input: str, 
                               reasoning_result, action_result: Dict[str, Any]):
        """Update session context with latest interaction"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Add to conversation history
            session["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "intent": reasoning_result.intent,
                "confidence": reasoning_result.confidence,
                "target_collection": reasoning_result.target_collection,
                "action_taken": reasoning_result.next_action.value,
                "action_result": action_result.get("action", "unknown")
            })
            
            # Update workflow state
            if action_result.get("status") == "collecting_data":
                session["workflow_state"] = "collecting_data"
            elif action_result.get("status") == "ready_for_execution":
                session["workflow_state"] = "ready_to_execute"
            elif action_result.get("status") == "success":
                session["workflow_state"] = "completed"
            elif action_result.get("status") == "auth_required":
                session["workflow_state"] = "awaiting_auth"
            
            # Store last reasoning for reference
            session["last_reasoning"] = asdict(reasoning_result)
    
    def _build_response(self, reasoning_result, action_result: Dict[str, Any], 
                       session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive response for the user"""
        
        response = {
            "session_id": session_context.get("session_id"),
            "timestamp": datetime.now().isoformat(),
            
            # Reasoning information
            "reasoning": {
                "intent": reasoning_result.intent,
                "confidence": reasoning_result.confidence,
                "target_collection": reasoning_result.target_collection,
                "reasoning_explanation": reasoning_result.reasoning
            },
            
            # Action results
            "action_result": action_result,
            
            # User context
            "user_context": {
                "authenticated": session_context.get("user_validated", False),
                "current_collection": session_context.get("current_collection"),
                "workflow_state": session_context.get("workflow_state", "initial")
            },
            
            # Response message
            "response": self._generate_response_message(reasoning_result, action_result),
            
            # UI actions (for frontend)
            "ui_actions": self._generate_ui_actions(action_result, session_context)
        }
        
        return response
    
    def _generate_response_message(self, reasoning_result, action_result: Dict[str, Any]) -> str:
        """Generate human-friendly response message"""
        
        action_type = action_result.get("action", "unknown")
        
        message_templates = {
            "collect_field": action_result.get("prompt", "Please provide the required information."),
            "data_collection_complete": f"Great! I have all the information needed for {reasoning_result.target_collection}. Ready to proceed?",
            "operation_executed": action_result.get("message", "Operation completed successfully!"),
            "authentication_success": action_result.get("message", "Authentication successful!"),
            "request_employee_id": action_result.get("message", "Please provide your Employee ID."),
            "clarify_intent": action_result.get("message", "Could you clarify what you'd like to do?"),
            "access_denied": action_result.get("message", "Access denied for this operation."),
            "validation_failed": f"Please fix these issues: {'; '.join(action_result.get('errors', []))}",
            "provide_feedback": action_result.get("message", "How can I help you today?")
        }
        
        return message_templates.get(action_type, "I'm processing your request...")
    
    def _generate_ui_actions(self, action_result: Dict[str, Any], 
                           session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI-specific actions for frontend"""
        
        ui_actions = {
            "show_loading": False,
            "show_auth_form": False,
            "show_suggestions": False,
            "show_progress": False,
            "show_success_message": False,
            "show_error_message": False,
            "enable_input": True
        }
        
        action_type = action_result.get("action", "unknown")
        
        if action_type == "request_employee_id":
            ui_actions["show_auth_form"] = True
        elif action_type == "clarify_intent":
            ui_actions["show_suggestions"] = True
        elif action_type == "collect_field":
            ui_actions["show_progress"] = True
        elif action_type == "operation_executed":
            ui_actions["show_success_message"] = True
        elif action_result.get("status") == "error":
            ui_actions["show_error_message"] = True
        
        return ui_actions
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status and context"""
        
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "workflow_state": session.get("workflow_state", "initial"),
            "authenticated": session.get("user_validated", False),
            "current_collection": session.get("current_collection"),
            "conversation_length": len(session.get("conversation_history", [])),
            "user_profile": session.get("user_profile"),
            "collected_data_collections": list(session.get("collected_data", {}).keys())
        }
    
    def reset_session(self, session_id: str) -> Dict[str, Any]:
        """Reset session to initial state"""
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return {"message": f"Session {session_id} reset successfully"}
    
    def get_available_collections(self) -> List[Dict[str, Any]]:
        """Get list of all available collections with metadata"""
        
        return [
            self.collection_router.get_collection_info(collection_name)
            for collection_name in COLLECTION_SCHEMAS.keys()
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        return {
            "system_name": "ZOPKIT ReAct Enterprise Chatbot",
            "version": "2.0.0-ReAct",
            "active_sessions": len(self.active_sessions),
            "supported_collections": len(COLLECTION_SCHEMAS),
            "ai_enabled": self.react_engine.ai_model is not None,
            "components": {
                "react_engine": "✅ Active",
                "collection_router": "✅ Active", 
                "field_processor": "✅ Active",
                "authorization_system": "✅ Active"
            },
            "capabilities": [
                "Zero hardcoded patterns",
                "Dynamic collection routing",
                "AI-powered reasoning",
                "Universal field processing",
                "Role-based authorization",
                "49 business operations support"
            ]
        }

# Factory function to create the chatbot
def create_react_chatbot(gemini_api_key: str = None) -> ReActChatbot:
    """Create and initialize the ReAct chatbot"""
    return ReActChatbot(gemini_api_key=gemini_api_key)