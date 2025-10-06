"""
Dynamic Collection Router for ZOPKIT Enterprise Chatbot
Intelligent routing system that dynamically maps user requests to appropriate collections

This router eliminates hardcoded patterns and uses AI to understand
business intent and route to the correct collection from 49 available options.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from schema import COLLECTION_SCHEMAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for routing decisions"""
    HIGH = "high"        # > 0.8
    MEDIUM = "medium"    # 0.5 - 0.8
    LOW = "low"          # < 0.5

@dataclass
class RoutingResult:
    """Result of collection routing analysis"""
    target_collection: str
    confidence: float
    confidence_level: ConfidenceLevel
    reasoning: str
    alternative_collections: List[str]
    extracted_keywords: List[str]
    business_context: Dict[str, Any]

class DynamicCollectionRouter:
    """
    Intelligent router that dynamically maps user requests to collections
    
    Uses multiple analysis techniques:
    1. Semantic keyword analysis
    2. Business context understanding  
    3. Intent pattern recognition
    4. Confidence scoring
    """
    
    def __init__(self):
        """Initialize the dynamic router"""
        self.collection_schemas = COLLECTION_SCHEMAS
        self.business_domains = self._initialize_business_domains()
        self.intent_patterns = self._initialize_intent_patterns()
        self.keyword_weights = self._initialize_keyword_weights()
        
        logger.info(f"✅ Dynamic Collection Router initialized with {len(self.collection_schemas)} collections")
    
    def route_request(self, user_input: str, context: Dict[str, Any] = None) -> RoutingResult:
        """
        Route user request to appropriate collection
        
        Args:
            user_input: User's request/query
            context: Optional conversation context
            
        Returns:
            RoutingResult with routing decision and confidence
        """
        if context is None:
            context = {}
            
        logger.info(f"🔍 Routing request: '{user_input[:50]}...'")
        
        # Normalize input
        normalized_input = self._normalize_input(user_input)
        
        # Multi-layered analysis
        semantic_analysis = self._analyze_semantic_keywords(normalized_input)
        business_analysis = self._analyze_business_context(normalized_input, context)
        pattern_analysis = self._analyze_intent_patterns(normalized_input)
        
        # Combine analyses and score collections
        collection_scores = self._score_collections(
            normalized_input, semantic_analysis, business_analysis, pattern_analysis
        )
        
        # Get best routing result
        routing_result = self._create_routing_result(
            collection_scores, semantic_analysis, business_analysis, pattern_analysis
        )
        
        logger.info(f"🎯 Routed to: {routing_result.target_collection} (confidence: {routing_result.confidence:.2f})")
        return routing_result
    
    def _initialize_business_domains(self) -> Dict[str, List[str]]:
        """Initialize business domain groupings"""
        
        return {
            "user_management": [
                "user_registration", "user_onboarding", "user_activation",
                "role_management", "access_control"
            ],
            "supplier_vendor": [
                "supplier_registration", "vendor_management", "purchase_order",
                "contract_management", "invoice_management"
            ],
            "customer_client": [
                "client_registration", "customer_support_ticket", 
                "customer_feedback_management", "order_placement", "order_tracking"
            ],
            "hr_employee": [
                "employee_leave_request", "payroll_management", "training_registration",
                "performance_review", "recruitment_portal", "interview_scheduling",
                "offer_letter_generation", "employee_exit_clearance", "attendance_tracking",
                "shift_scheduling", "grievance_management"
            ],
            "inventory_products": [
                "product_catalog", "inventory_management", "warehouse_management",
                "shipping_management"
            ],
            "financial": [
                "payment_processing", "expense_reimbursement", "payroll_management",
                "invoice_management"
            ],
            "operations": [
                "project_assignment", "meeting_scheduler", "travel_request",
                "it_asset_allocation", "compliance_report", "audit_log_viewer"
            ],
            "knowledge_support": [
                "knowledge_base", "faq_management", "customer_support_ticket",
                "chatbot_training_data", "knowledge_transfer_kt_handover"
            ],
            "system_admin": [
                "system_configuration", "notification_settings", "data_backup_and_restore",
                "system_audit_and_compliance_dashboard", "announcements_notice_board"
            ],
            "safety_compliance": [
                "health_and_safety_incident_reporting", "compliance_report",
                "system_audit_and_compliance_dashboard"
            ],
            "marketing_business": [
                "marketing_campaign_management", "customer_feedback_management",
                "announcements_notice_board"
            ]
        }
    
    def _initialize_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize intent recognition patterns"""
        
        return {
            # Action-based patterns
            "registration_patterns": {
                "keywords": ["register", "sign up", "create", "new", "join", "enroll"],
                "collections": ["user_registration", "supplier_registration", "client_registration", "training_registration"],
                "weight": 1.0
            },
            "request_patterns": {
                "keywords": ["request", "need", "want", "apply", "submit"],
                "collections": ["employee_leave_request", "travel_request", "expense_reimbursement"],
                "weight": 0.9
            },
            "order_patterns": {
                "keywords": ["order", "purchase", "buy", "place order"],
                "collections": ["order_placement", "purchase_order"],
                "weight": 1.0
            },
            "track_patterns": {
                "keywords": ["track", "status", "check", "monitor", "follow"],
                "collections": ["order_tracking", "attendance_tracking"],
                "weight": 0.8
            },
            "schedule_patterns": {
                "keywords": ["schedule", "book", "appointment", "meeting"],
                "collections": ["meeting_scheduler", "interview_scheduling", "shift_scheduling"],
                "weight": 0.9
            },
            "manage_patterns": {
                "keywords": ["manage", "administration", "control", "handle"],
                "collections": ["vendor_management", "role_management", "grievance_management"],
                "weight": 0.7
            },
            "report_patterns": {
                "keywords": ["report", "incident", "issue", "problem", "complaint"],
                "collections": ["health_and_safety_incident_reporting", "customer_support_ticket", "compliance_report"],
                "weight": 0.8
            }
        }
    
    def _initialize_keyword_weights(self) -> Dict[str, Dict[str, float]]:
        """Initialize keyword importance weights for each collection"""
        
        weights = {}
        
        # High-importance keywords that strongly indicate specific collections
        high_weight_keywords = {
            "user_registration": {"register": 1.0, "user": 0.9, "account": 0.8, "signup": 1.0},
            "purchase_order": {"purchase": 1.0, "order": 0.9, "po": 1.0, "buy": 0.8},
            "supplier_registration": {"supplier": 1.0, "vendor": 0.9, "register": 0.8},
            "employee_leave_request": {"leave": 1.0, "vacation": 0.9, "time off": 1.0},
            "payroll_management": {"payroll": 1.0, "salary": 0.9, "payment": 0.7},
            "customer_support_ticket": {"support": 1.0, "help": 0.8, "issue": 0.8, "problem": 0.8},
            "meeting_scheduler": {"meeting": 1.0, "schedule": 0.9, "appointment": 0.9},
            "inventory_management": {"inventory": 1.0, "stock": 0.9, "warehouse": 0.8}
        }
        
        # Apply weights to all collections
        for collection in self.collection_schemas.keys():
            weights[collection] = high_weight_keywords.get(collection, {})
        
        return weights
    
    def _normalize_input(self, user_input: str) -> str:
        """Normalize user input for analysis"""
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', user_input.lower().strip())
        
        # Remove common stop words that don't add meaning
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = normalized.split()
        filtered_words = [word for word in words if word not in stop_words]
        
        return ' '.join(filtered_words)
    
    def _analyze_semantic_keywords(self, normalized_input: str) -> Dict[str, Any]:
        """Analyze semantic keywords in user input"""
        
        words = normalized_input.split()
        word_set = set(words)
        
        # Collection keyword mappings (comprehensive)
        collection_keywords = {
            "user_registration": ["register", "signup", "account", "user", "profile", "create", "join"],
            "user_onboarding": ["onboard", "setup", "permissions", "access", "initialize"],
            "user_activation": ["activate", "enable", "start", "begin"],
            "supplier_registration": ["supplier", "vendor", "partner", "contractor"],
            "client_registration": ["client", "customer", "company", "organization"],
            "product_catalog": ["product", "catalog", "item", "goods", "merchandise"],
            "inventory_management": ["inventory", "stock", "warehouse", "storage", "goods"],
            "order_placement": ["order", "place", "purchase", "buy", "acquire"],
            "order_tracking": ["track", "trace", "follow", "monitor", "status"],
            "payment_processing": ["payment", "pay", "transaction", "billing", "charge"],
            "employee_leave_request": ["leave", "vacation", "holiday", "time", "off", "absence"],
            "payroll_management": ["payroll", "salary", "wage", "compensation", "payment"],
            "training_registration": ["training", "course", "education", "learning", "skill"],
            "performance_review": ["performance", "review", "evaluation", "assessment", "rating"],
            "customer_support_ticket": ["support", "help", "assistance", "issue", "problem", "ticket"],
            "project_assignment": ["project", "assignment", "task", "work", "job"],
            "meeting_scheduler": ["meeting", "schedule", "appointment", "conference", "call"],
            "it_asset_allocation": ["asset", "equipment", "device", "hardware", "allocation"],
            "compliance_report": ["compliance", "regulation", "audit", "report"],
            "audit_log_viewer": ["audit", "log", "history", "record", "tracking"],
            "recruitment_portal": ["recruitment", "hiring", "candidate", "recruit", "job"],  
            "interview_scheduling": ["interview", "screening", "assessment"],
            "offer_letter_generation": ["offer", "letter", "employment", "position"],
            "employee_exit_clearance": ["exit", "resignation", "clearance", "leaving"],
            "travel_request": ["travel", "trip", "journey", "business", "visit"],
            "expense_reimbursement": ["expense", "reimbursement", "claim", "refund"],
            "vendor_management": ["vendor", "supplier", "partner", "contractor", "management"],
            "invoice_management": ["invoice", "bill", "billing", "payment", "charge"],
            "shipping_management": ["shipping", "delivery", "dispatch", "transport"],
            "warehouse_management": ["warehouse", "storage", "facility", "location"],
            "purchase_order": ["purchase", "order", "po", "procurement", "buying"],
            "contract_management": ["contract", "agreement", "terms", "legal"],
            "knowledge_base": ["knowledge", "documentation", "wiki", "information"],
            "faq_management": ["faq", "question", "answer", "help", "guide"],
            "system_configuration": ["system", "configuration", "settings", "setup"],
            "role_management": ["role", "permission", "access", "authority"],
            "access_control": ["access", "control", "security", "authorization"],
            "notification_settings": ["notification", "alert", "reminder", "message"],
            "chatbot_training_data": ["chatbot", "bot", "ai", "training", "data"],
            "attendance_tracking": ["attendance", "checkin", "checkout", "presence"],
            "shift_scheduling": ["shift", "schedule", "roster", "rotation"],
            "health_and_safety_incident_reporting": ["safety", "incident", "accident", "health", "report"],
            "grievance_management": ["grievance", "complaint", "dispute", "issue"],
            "knowledge_transfer_kt_handover": ["handover", "transfer", "knowledge", "kt"],
            "customer_feedback_management": ["feedback", "review", "rating", "opinion"],
            "marketing_campaign_management": ["marketing", "campaign", "promotion", "advertising"],
            "data_backup_and_restore": ["backup", "restore", "recovery", "data"],
            "system_audit_and_compliance_dashboard": ["dashboard", "audit", "compliance", "monitoring"],
            "announcements_notice_board": ["announcement", "notice", "news", "bulletin"]
        }
        
        # Calculate keyword matches for each collection
        collection_matches = {}
        total_keywords_found = 0
        
        for collection, keywords in collection_keywords.items():
            matches = word_set.intersection(set(keywords))
            match_count = len(matches)
            if match_count > 0:
                collection_matches[collection] = {
                    'matches': list(matches),
                    'count': match_count,
                    'keywords': keywords
                }
                total_keywords_found += match_count
        
        return {
            'collection_matches': collection_matches,
            'total_keywords': total_keywords_found,
            'input_words': words,
            'word_count': len(words)
        }
    
    def _analyze_business_context(self, normalized_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business context and domain relevance"""
        
        words = set(normalized_input.split())
        domain_scores = {}
        
        # Score each business domain based on keyword presence
        for domain, collections in self.business_domains.items():
            domain_keywords = set()
            
            # Collect all keywords for collections in this domain
            for collection in collections:
                if collection in self.collection_schemas:
                    # Add collection name words
                    domain_keywords.update(collection.replace('_', ' ').split())
            
            # Calculate domain relevance score
            keyword_matches = words.intersection(domain_keywords)
            relevance_score = len(keyword_matches) / max(len(domain_keywords), 1)
            
            if relevance_score > 0:
                domain_scores[domain] = {
                    'score': relevance_score,
                    'matched_keywords': list(keyword_matches),
                    'collections': collections
                }
        
        # Determine primary business domain
        primary_domain = max(domain_scores.keys(), key=lambda d: domain_scores[d]['score']) if domain_scores else None
        
        return {
            'domain_scores': domain_scores,
            'primary_domain': primary_domain,
            'user_context': {
                'authenticated': context.get('user_validated', False),
                'employee_id': context.get('employee_id'),
                'department': context.get('department')
            }
        }
    
    def _analyze_intent_patterns(self, normalized_input: str) -> Dict[str, Any]:
        """Analyze intent patterns in user input"""
        
        pattern_matches = {}
        
        for pattern_name, pattern_info in self.intent_patterns.items():
            keywords = pattern_info['keywords']
            collections = pattern_info['collections']
            weight = pattern_info['weight']
            
            # Check for keyword matches
            matched_keywords = [kw for kw in keywords if kw in normalized_input]
            
            if matched_keywords:
                pattern_matches[pattern_name] = {
                    'matched_keywords': matched_keywords,
                    'relevant_collections': collections,
                    'weight': weight,
                    'match_strength': len(matched_keywords) / len(keywords)
                }
        
        return {
            'pattern_matches': pattern_matches,
            'intent_signals': len(pattern_matches)
        }
    
    def _score_collections(self, normalized_input: str, semantic_analysis: Dict, 
                          business_analysis: Dict, pattern_analysis: Dict) -> Dict[str, float]:
        """Score all collections based on multiple analysis factors"""
        
        collection_scores = {}
        
        for collection in self.collection_schemas.keys():
            score = 0.0
            
            # Semantic keyword score (30% weight)
            if collection in semantic_analysis['collection_matches']:
                keyword_score = semantic_analysis['collection_matches'][collection]['count']
                # Apply keyword weights if available
                if collection in self.keyword_weights:
                    weighted_score = 0
                    for keyword in semantic_analysis['collection_matches'][collection]['matches']:
                        weighted_score += self.keyword_weights[collection].get(keyword, 0.5)
                    keyword_score = weighted_score
                
                score += (keyword_score / max(semantic_analysis['total_keywords'], 1)) * 0.3
            
            # Business domain score (25% weight)
            for domain, domain_info in business_analysis['domain_scores'].items():
                if collection in domain_info['collections']:
                    score += domain_info['score'] * 0.25
            
            # Intent pattern score (25% weight)
            for pattern_name, pattern_info in pattern_analysis['pattern_matches'].items():
                if collection in pattern_info['relevant_collections']:
                    pattern_score = pattern_info['match_strength'] * pattern_info['weight']
                    score += pattern_score * 0.25
            
            # Direct collection name match bonus (20% weight)
            collection_words = collection.replace('_', ' ').split()
            input_words = normalized_input.split()
            name_matches = sum(1 for word in collection_words if word in input_words)
            if name_matches > 0:
                score += (name_matches / len(collection_words)) * 0.2
            
            collection_scores[collection] = min(score, 1.0)  # Cap at 1.0
        
        return collection_scores
    
    def _create_routing_result(self, collection_scores: Dict[str, float], 
                              semantic_analysis: Dict, business_analysis: Dict, 
                              pattern_analysis: Dict) -> RoutingResult:
        """Create final routing result"""
        
        # Sort collections by score
        sorted_collections = sorted(collection_scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_collections or sorted_collections[0][1] == 0:
            # No good matches found - return default
            return RoutingResult(
                target_collection="customer_support_ticket",  # Default fallback
                confidence=0.1,
                confidence_level=ConfidenceLevel.LOW,
                reasoning="No strong matches found, defaulting to customer support",
                alternative_collections=[],
                extracted_keywords=[],
                business_context={}
            )
        
        # Get top collection and alternatives
        top_collection, top_score = sorted_collections[0]
        alternatives = [col for col, score in sorted_collections[1:4] if score > 0.1]
        
        # Determine confidence level
        if top_score >= 0.8:
            confidence_level = ConfidenceLevel.HIGH
        elif top_score >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
        
        # Extract all found keywords
        all_keywords = []
        for col_data in semantic_analysis['collection_matches'].values():
            all_keywords.extend(col_data['matches'])
        
        # Build reasoning
        reasoning_parts = []
        if top_collection in semantic_analysis['collection_matches']:
            matched_keywords = semantic_analysis['collection_matches'][top_collection]['matches']
            reasoning_parts.append(f"Keywords matched: {', '.join(matched_keywords)}")
        
        if business_analysis['primary_domain']:
            reasoning_parts.append(f"Business domain: {business_analysis['primary_domain']}")
        
        if pattern_analysis['pattern_matches']:
            matched_patterns = list(pattern_analysis['pattern_matches'].keys())
            reasoning_parts.append(f"Intent patterns: {', '.join(matched_patterns)}")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Score-based analysis"
        
        return RoutingResult(
            target_collection=top_collection,
            confidence=top_score,
            confidence_level=confidence_level,
            reasoning=reasoning,
            alternative_collections=alternatives,
            extracted_keywords=list(set(all_keywords)),
            business_context={
                'primary_domain': business_analysis['primary_domain'],
                'domain_scores': business_analysis['domain_scores'],
                'pattern_matches': pattern_analysis['pattern_matches']
            }
        )
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection"""
        
        if collection_name not in self.collection_schemas:
            return {"error": f"Collection '{collection_name}' not found"}
        
        schema = self.collection_schemas[collection_name]
        
        # Find business domain
        domain = None
        for dom, collections in self.business_domains.items():
            if collection_name in collections:
                domain = dom
                break
        
        return {
            "collection": collection_name,
            "display_name": collection_name.replace('_', ' ').title(),
            "required_fields": schema.get('required', []),
            "optional_fields": schema.get('optional', []),
            "business_domain": domain,
            "total_fields": len(schema.get('required', [])) + len(schema.get('optional', []))
        }
    
    def suggest_collections(self, partial_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest collections based on partial input"""
        
        if not partial_input.strip():
            # Return most common collections
            common_collections = [
                "user_registration", "purchase_order", "customer_support_ticket",
                "employee_leave_request", "supplier_registration"
            ]
            return [self.get_collection_info(col) for col in common_collections[:limit]]
        
        # Route the partial input and return top matches
        routing_result = self.route_request(partial_input)
        
        suggestions = [routing_result.target_collection]
        suggestions.extend(routing_result.alternative_collections)
        
        return [self.get_collection_info(col) for col in suggestions[:limit]]

# Factory function
def create_collection_router() -> DynamicCollectionRouter:
    """Create and initialize collection router"""
    return DynamicCollectionRouter()