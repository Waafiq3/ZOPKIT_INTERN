"""
Dynamic Authorization System for ZOPKIT Enterprise Chatbot
Role-based authorization that works dynamically with any collection

This system eliminates hardcoded employee IDs and positions,
creating a flexible authorization framework based on roles, 
departments, and collection-specific access rules.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from schema import COLLECTION_SCHEMAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Access levels for operations"""
    PUBLIC = "public"          # No authentication required
    AUTHENTICATED = "authenticated"  # Basic authentication required
    ROLE_BASED = "role_based"  # Specific role required
    DEPARTMENT = "department"  # Department-based access
    ADMIN_ONLY = "admin_only"  # Administrator access only

class Permission(Enum):
    """Types of permissions"""
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    ADMIN = "admin"

@dataclass
class UserProfile:
    """User profile with roles and permissions"""
    employee_id: str
    department: str
    position: str
    roles: List[str]
    permissions: Set[Permission]
    access_level: AccessLevel
    is_active: bool = True

@dataclass
class CollectionAccessRule:
    """Access rule for a specific collection"""
    collection_name: str
    required_access_level: AccessLevel
    allowed_roles: List[str]
    allowed_departments: List[str]
    required_permissions: List[Permission]
    restrictions: Dict[str, Any]

@dataclass
class AuthorizationResult:
    """Result of authorization check"""
    is_authorized: bool
    user_profile: Optional[UserProfile]
    access_level: AccessLevel
    granted_permissions: Set[Permission]
    restrictions: Dict[str, Any]
    denial_reason: Optional[str]
    required_action: Optional[str]

class DynamicAuthorizationSystem:
    """
    Dynamic authorization system that adapts to any collection
    
    Features:
    - Role-based access control (RBAC)
    - Department-based permissions
    - Collection-specific access rules
    - Dynamic permission evaluation
    - User profile management
    """
    
    def __init__(self):
        """Initialize the authorization system"""
        self.collection_schemas = COLLECTION_SCHEMAS
        self.access_rules = self._initialize_access_rules()
        self.role_hierarchy = self._initialize_role_hierarchy()
        self.department_permissions = self._initialize_department_permissions()
        self.user_profiles = {}  # Cache for user profiles
        
        logger.info("✅ Dynamic Authorization System initialized")
    
    def authenticate_user(self, employee_id: str, additional_context: Dict[str, Any] = None) -> UserProfile:
        """
        Authenticate user and create/retrieve user profile
        
        Args:
            employee_id: User's employee ID
            additional_context: Additional user context (department, position, etc.)
            
        Returns:
            UserProfile with roles and permissions
        """
        if additional_context is None:
            additional_context = {}
            
        logger.info(f"🔐 Authenticating user: {employee_id}")
        
        # Check cache first
        if employee_id in self.user_profiles:
            return self.user_profiles[employee_id]
        
        # Create user profile (in real system, this would query database)
        user_profile = self._create_user_profile(employee_id, additional_context)
        
        # Cache the profile
        self.user_profiles[employee_id] = user_profile
        
        logger.info(f"✅ User authenticated: {employee_id} with roles: {user_profile.roles}")
        return user_profile
    
    def authorize_collection_access(self, user_profile: UserProfile, collection_name: str, 
                                  operation: str = "write") -> AuthorizationResult:
        """
        Check if user is authorized to access a collection
        
        Args:
            user_profile: Authenticated user profile
            collection_name: Target collection name
            operation: Operation type (read, write, update, delete)
            
        Returns:
            AuthorizationResult with authorization decision
        """
        logger.info(f"🛡️ Checking authorization: {user_profile.employee_id} -> {collection_name} ({operation})")
        
        if collection_name not in self.collection_schemas:
            return AuthorizationResult(
                is_authorized=False,
                user_profile=user_profile,
                access_level=AccessLevel.PUBLIC,
                granted_permissions=set(),
                restrictions={},
                denial_reason=f"Collection '{collection_name}' not found",
                required_action="contact_admin"
            )
        
        # Get access rules for collection
        access_rule = self.access_rules.get(collection_name)
        if not access_rule:
            # Default to authenticated access if no specific rule
            access_rule = self._get_default_access_rule(collection_name)
        
        # Check access level requirements
        if not self._check_access_level(user_profile, access_rule.required_access_level):
            return AuthorizationResult(
                is_authorized=False,
                user_profile=user_profile,
                access_level=user_profile.access_level,
                granted_permissions=set(),
                restrictions={},
                denial_reason=f"Insufficient access level for {collection_name}",
                required_action="upgrade_access"
            )
        
        # Check role requirements
        if access_rule.allowed_roles and not self._check_role_access(user_profile, access_rule.allowed_roles):
            return AuthorizationResult(
                is_authorized=False,
                user_profile=user_profile,
                access_level=user_profile.access_level,
                granted_permissions=set(),
                restrictions={},
                denial_reason=f"Role not authorized for {collection_name}",
                required_action="contact_admin"
            )
        
        # Check department requirements
        if access_rule.allowed_departments and user_profile.department not in access_rule.allowed_departments:
            return AuthorizationResult(
                is_authorized=False,
                user_profile=user_profile,
                access_level=user_profile.access_level,
                granted_permissions=set(),
                restrictions={},
                denial_reason=f"Department '{user_profile.department}' not authorized for {collection_name}",
                required_action="contact_admin"
            )
        
        # Check specific permissions
        required_permission = self._operation_to_permission(operation)
        if required_permission not in user_profile.permissions:
            return AuthorizationResult(
                is_authorized=False,
                user_profile=user_profile,
                access_level=user_profile.access_level,
                granted_permissions=user_profile.permissions,
                restrictions={},
                denial_reason=f"Missing '{required_permission.value}' permission for {collection_name}",
                required_action="request_permission"
            )
        
        # User is authorized
        granted_permissions = self._get_granted_permissions(user_profile, access_rule)
        restrictions = self._get_user_restrictions(user_profile, access_rule)
        
        return AuthorizationResult(
            is_authorized=True,
            user_profile=user_profile,
            access_level=user_profile.access_level,
            granted_permissions=granted_permissions,
            restrictions=restrictions,
            denial_reason=None,
            required_action=None
        )
    
    def check_field_access(self, user_profile: UserProfile, collection_name: str, 
                          field_name: str, operation: str = "write") -> bool:
        """
        Check if user can access a specific field in a collection
        
        Args:
            user_profile: Authenticated user profile
            collection_name: Target collection name
            field_name: Field name to check
            operation: Operation type
            
        Returns:
            bool indicating if access is allowed
        """
        # First check collection access
        collection_auth = self.authorize_collection_access(user_profile, collection_name, operation)
        if not collection_auth.is_authorized:
            return False
        
        # Check field-specific restrictions
        field_restrictions = collection_auth.restrictions.get('field_restrictions', {})
        if field_name in field_restrictions:
            field_rule = field_restrictions[field_name]
            
            # Check if user's role can access this field
            if 'allowed_roles' in field_rule:
                return any(role in user_profile.roles for role in field_rule['allowed_roles'])
            
            # Check if user's department can access this field
            if 'allowed_departments' in field_rule:
                return user_profile.department in field_rule['allowed_departments']
        
        return True  # Default to allow if no specific restrictions
    
    def _initialize_access_rules(self) -> Dict[str, CollectionAccessRule]:
        """Initialize access rules for collections"""
        
        rules = {}
        
        # High-security collections (Admin/HR only)
        admin_collections = [
            "payroll_management", "performance_review", "employee_exit_clearance",
            "system_configuration", "role_management", "access_control",
            "system_audit_and_compliance_dashboard", "data_backup_and_restore"
        ]
        
        for collection in admin_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.ADMIN_ONLY,
                allowed_roles=["admin", "hr_manager", "system_admin"],
                allowed_departments=["HR", "IT", "Administration"],
                required_permissions=[Permission.ADMIN],
                restrictions={"approval_required": True}
            )
        
        # HR-specific collections
        hr_collections = [
            "user_registration", "user_onboarding", "user_activation",
            "employee_leave_request", "training_registration", "recruitment_portal",
            "interview_scheduling", "offer_letter_generation", "attendance_tracking",
            "shift_scheduling", "grievance_management"
        ]
        
        for collection in hr_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.ROLE_BASED,
                allowed_roles=["hr_staff", "hr_manager", "admin", "manager"],
                allowed_departments=["HR", "Administration"],
                required_permissions=[Permission.WRITE],
                restrictions={}
            )
        
        # Finance-specific collections
        finance_collections = [
            "payment_processing", "expense_reimbursement", "invoice_management",
            "vendor_management", "contract_management"
        ]
        
        for collection in finance_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.ROLE_BASED,
                allowed_roles=["finance_staff", "finance_manager", "admin", "accountant"],
                allowed_departments=["Finance", "Accounting", "Administration"],
                required_permissions=[Permission.WRITE],
                restrictions={"approval_required_above": 10000}
            )
        
        # Procurement collections
        procurement_collections = [
            "purchase_order", "supplier_registration", "inventory_management",
            "warehouse_management", "shipping_management"
        ]
        
        for collection in procurement_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.ROLE_BASED,
                allowed_roles=["procurement_staff", "warehouse_manager", "admin", "manager"],
                allowed_departments=["Procurement", "Warehouse", "Operations", "Administration"],
                required_permissions=[Permission.WRITE],
                restrictions={"approval_required_above": 5000}
            )
        
        # Customer-facing collections
        customer_collections = [
            "customer_support_ticket", "client_registration", "order_placement",
            "order_tracking", "customer_feedback_management"
        ]
        
        for collection in customer_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.AUTHENTICATED,
                allowed_roles=["customer_service", "sales", "manager", "admin"],
                allowed_departments=["Customer Service", "Sales", "Administration"],
                required_permissions=[Permission.WRITE],
                restrictions={}
            )
        
        # General access collections
        general_collections = [
            "project_assignment", "meeting_scheduler", "travel_request",
            "it_asset_allocation", "knowledge_base", "faq_management",
            "announcements_notice_board", "knowledge_transfer_kt_handover"
        ]
        
        for collection in general_collections:
            rules[collection] = CollectionAccessRule(
                collection_name=collection,
                required_access_level=AccessLevel.AUTHENTICATED,
                allowed_roles=["employee", "manager", "admin"],
                allowed_departments=[],  # All departments
                required_permissions=[Permission.WRITE],
                restrictions={}
            )
        
        return rules
    
    def _initialize_role_hierarchy(self) -> Dict[str, Dict[str, Any]]:
        """Initialize role hierarchy and permissions"""
        
        return {
            "admin": {
                "level": 10,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE, 
                              Permission.DELETE, Permission.APPROVE, Permission.ADMIN],
                "inherits_from": [],
                "description": "System administrator with full access"
            },
            "hr_manager": {
                "level": 8,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE, 
                              Permission.DELETE, Permission.APPROVE],
                "inherits_from": ["hr_staff"],
                "description": "HR manager with approval authority"
            },
            "finance_manager": {
                "level": 8,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE, 
                              Permission.DELETE, Permission.APPROVE],
                "inherits_from": ["finance_staff"],
                "description": "Finance manager with approval authority"
            },
            "manager": {
                "level": 7,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE, Permission.APPROVE],
                "inherits_from": ["employee"],
                "description": "General manager role"
            },
            "hr_staff": {
                "level": 6,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE],
                "inherits_from": ["employee"],
                "description": "HR staff member"
            },
            "finance_staff": {
                "level": 6,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE],
                "inherits_from": ["employee"],
                "description": "Finance staff member"
            },
            "procurement_staff": {
                "level": 6,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE],
                "inherits_from": ["employee"],
                "description": "Procurement staff member"
            },
            "customer_service": {
                "level": 5,
                "permissions": [Permission.READ, Permission.WRITE, Permission.UPDATE],
                "inherits_from": ["employee"],
                "description": "Customer service representative"
            },
            "employee": {
                "level": 3,
                "permissions": [Permission.READ, Permission.WRITE],
                "inherits_from": [],
                "description": "Regular employee"
            },
            "contractor": {
                "level": 2,
                "permissions": [Permission.READ],
                "inherits_from": [],
                "description": "External contractor"
            },
            "guest": {
                "level": 1,
                "permissions": [Permission.READ],
                "inherits_from": [],
                "description": "Guest user with read-only access"
            }
        }
    
    def _initialize_department_permissions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize department-specific permissions"""
        
        return {
            "Administration": {
                "default_roles": ["admin", "manager"],
                "collections": ["all"],
                "restrictions": {}
            },
            "HR": {
                "default_roles": ["hr_staff", "hr_manager"],
                "collections": [
                    "user_registration", "user_onboarding", "employee_leave_request",
                    "payroll_management", "training_registration", "performance_review",
                    "recruitment_portal", "attendance_tracking"
                ],
                "restrictions": {"sensitive_data_access": True}
            },
            "Finance": {
                "default_roles": ["finance_staff", "finance_manager"],
                "collections": [
                    "payment_processing", "expense_reimbursement", "invoice_management",
                    "vendor_management", "contract_management", "payroll_management"
                ],
                "restrictions": {"financial_approval_limit": 50000}
            },
            "IT": {
                "default_roles": ["system_admin", "employee"],
                "collections": [
                    "system_configuration", "it_asset_allocation", "chatbot_training_data",
                    "data_backup_and_restore", "audit_log_viewer"
                ],
                "restrictions": {"system_access": True}
            },
            "Procurement": {
                "default_roles": ["procurement_staff", "employee"],
                "collections": [
                    "purchase_order", "supplier_registration", "inventory_management",
                    "warehouse_management", "vendor_management"
                ],
                "restrictions": {"procurement_limit": 25000}
            },
            "Sales": {
                "default_roles": ["employee", "manager"],
                "collections": [
                    "client_registration", "order_placement", "order_tracking",
                    "customer_feedback_management", "marketing_campaign_management"
                ],
                "restrictions": {}
            },
            "Customer Service": {
                "default_roles": ["customer_service", "employee"],
                "collections": [
                    "customer_support_ticket", "client_registration", "order_tracking",
                    "customer_feedback_management", "faq_management"
                ],
                "restrictions": {}
            }
        }
    
    def _create_user_profile(self, employee_id: str, context: Dict[str, Any]) -> UserProfile:
        """Create user profile based on employee ID and context"""
        
        # In a real system, this would query a database
        # For now, we'll use intelligent defaults based on employee ID and context
        
        department = context.get('department', self._infer_department(employee_id))
        position = context.get('position', self._infer_position(employee_id, department))
        
        # Determine roles based on department and position
        roles = self._assign_roles(department, position, employee_id)
        
        # Get permissions for assigned roles
        permissions = self._get_role_permissions(roles)
        
        # Determine access level
        access_level = self._determine_access_level(roles, department)
        
        return UserProfile(
            employee_id=employee_id,
            department=department,
            position=position,
            roles=roles,
            permissions=permissions,
            access_level=access_level,
            is_active=True
        )
    
    def _infer_department(self, employee_id: str) -> str:
        """Infer department from employee ID pattern"""
        
        # Simple pattern-based inference (can be enhanced)
        emp_id_upper = employee_id.upper()
        
        if emp_id_upper.startswith('EMP001') or emp_id_upper.startswith('EMP002'):
            return "Administration"
        elif emp_id_upper.startswith('EMP003'):
            return "HR"
        elif emp_id_upper.startswith('EMP004'):
            return "Finance"
        elif emp_id_upper.startswith('EMP005'):
            return "Procurement"
        else:
            return "General"  # Default department
    
    def _infer_position(self, employee_id: str, department: str) -> str:
        """Infer position based on employee ID and department"""
        
        # Simple inference logic
        emp_id_upper = employee_id.upper()
        
        if emp_id_upper in ['EMP001', 'EMP002']:
            return "Administrator"
        elif emp_id_upper == 'EMP003':
            return "HR Manager"
        elif emp_id_upper == 'EMP004':
            return "Finance Manager"
        elif emp_id_upper == 'EMP005':
            return "Procurement Manager"
        else:
            return "Employee"  # Default position
    
    def _assign_roles(self, department: str, position: str, employee_id: str) -> List[str]:
        """Assign roles based on department, position, and employee ID"""
        
        roles = ["employee"]  # Base role for everyone
        
        # Admin roles
        if employee_id.upper() in ['EMP001', 'EMP002'] or position.lower().startswith('admin'):
            roles.append("admin")
        
        # Department-specific roles
        dept_roles = {
            "Administration": ["admin", "manager"],
            "HR": ["hr_staff", "hr_manager"] if "manager" in position.lower() else ["hr_staff"],
            "Finance": ["finance_staff", "finance_manager"] if "manager" in position.lower() else ["finance_staff"],
            "Procurement": ["procurement_staff", "warehouse_manager"] if "manager" in position.lower() else ["procurement_staff"],
            "Customer Service": ["customer_service"],
            "IT": ["system_admin"] if "admin" in position.lower() else ["employee"]
        }
        
        if department in dept_roles:
            roles.extend(dept_roles[department])
        
        # Position-based roles
        if "manager" in position.lower() and "manager" not in roles:
            roles.append("manager")
        
        return list(set(roles))  # Remove duplicates
    
    def _get_role_permissions(self, roles: List[str]) -> Set[Permission]:
        """Get combined permissions for all user roles"""
        
        all_permissions = set()
        
        for role in roles:
            if role in self.role_hierarchy:
                role_permissions = self.role_hierarchy[role]["permissions"]
                all_permissions.update(role_permissions)
                
                # Add inherited permissions
                inherits_from = self.role_hierarchy[role].get("inherits_from", [])
                for inherited_role in inherits_from:
                    inherited_permissions = self._get_role_permissions([inherited_role])
                    all_permissions.update(inherited_permissions)
        
        return all_permissions
    
    def _determine_access_level(self, roles: List[str], department: str) -> AccessLevel:
        """Determine user's access level"""
        
        if "admin" in roles:
            return AccessLevel.ADMIN_ONLY
        elif any(role.endswith("_manager") for role in roles):
            return AccessLevel.ROLE_BASED
        elif department in ["HR", "Finance", "Procurement"]:
            return AccessLevel.ROLE_BASED
        else:
            return AccessLevel.AUTHENTICATED
    
    def _get_default_access_rule(self, collection_name: str) -> CollectionAccessRule:
        """Get default access rule for collections without specific rules"""
        
        return CollectionAccessRule(
            collection_name=collection_name,
            required_access_level=AccessLevel.AUTHENTICATED,
            allowed_roles=["employee", "manager", "admin"],
            allowed_departments=[],  # All departments
            required_permissions=[Permission.WRITE],
            restrictions={}
        )
    
    def _check_access_level(self, user_profile: UserProfile, required_level: AccessLevel) -> bool:
        """Check if user meets required access level"""
        
        level_hierarchy = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.AUTHENTICATED: 1,
            AccessLevel.ROLE_BASED: 2,
            AccessLevel.DEPARTMENT: 3,
            AccessLevel.ADMIN_ONLY: 4
        }
        
        user_level = level_hierarchy.get(user_profile.access_level, 0)
        required_level_num = level_hierarchy.get(required_level, 0)
        
        return user_level >= required_level_num
    
    def _check_role_access(self, user_profile: UserProfile, allowed_roles: List[str]) -> bool:
        """Check if user has any of the allowed roles"""
        
        return any(role in user_profile.roles for role in allowed_roles)
    
    def _operation_to_permission(self, operation: str) -> Permission:
        """Convert operation string to Permission enum"""
        
        operation_map = {
            "read": Permission.READ,
            "write": Permission.WRITE,
            "create": Permission.WRITE,
            "update": Permission.UPDATE,
            "delete": Permission.DELETE,
            "approve": Permission.APPROVE,
            "admin": Permission.ADMIN
        }
        
        return operation_map.get(operation.lower(), Permission.WRITE)
    
    def _get_granted_permissions(self, user_profile: UserProfile, access_rule: CollectionAccessRule) -> Set[Permission]:
        """Get permissions granted to user for this collection"""
        
        # Start with user's permissions
        granted = user_profile.permissions.copy()
        
        # Apply collection-specific restrictions
        if access_rule.required_permissions:
            # Only grant permissions that are both in user's permissions and required by collection
            granted = granted.intersection(set(access_rule.required_permissions))
        
        return granted
    
    def _get_user_restrictions(self, user_profile: UserProfile, access_rule: CollectionAccessRule) -> Dict[str, Any]:
        """Get restrictions applied to user for this collection"""
        
        restrictions = access_rule.restrictions.copy()
        
        # Add department-specific restrictions
        if user_profile.department in self.department_permissions:
            dept_restrictions = self.department_permissions[user_profile.department].get("restrictions", {})
            restrictions.update(dept_restrictions)
        
        # Add role-based restrictions
        for role in user_profile.roles:
            if role in self.role_hierarchy:
                role_info = self.role_hierarchy[role]
                # Add any role-specific restrictions here if needed
        
        return restrictions
    
    def get_user_accessible_collections(self, user_profile: UserProfile) -> List[str]:
        """Get list of collections user can access"""
        
        accessible = []
        
        for collection_name in self.collection_schemas.keys():
            auth_result = self.authorize_collection_access(user_profile, collection_name)
            if auth_result.is_authorized:
                accessible.append(collection_name)
        
        return accessible
    
    def get_authorization_summary(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Get comprehensive authorization summary for user"""
        
        accessible_collections = self.get_user_accessible_collections(user_profile)
        
        return {
            "user_id": user_profile.employee_id,
            "department": user_profile.department,
            "position": user_profile.position,
            "roles": user_profile.roles,
            "access_level": user_profile.access_level.value,
            "permissions": [p.value for p in user_profile.permissions],
            "accessible_collections": accessible_collections,
            "total_collections": len(self.collection_schemas),
            "access_percentage": len(accessible_collections) / len(self.collection_schemas) * 100
        }

# Factory function
def create_authorization_system() -> DynamicAuthorizationSystem:
    """Create and initialize authorization system"""
    return DynamicAuthorizationSystem()