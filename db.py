"""
MongoDB Connection Module for ReAct Chatbot
Handles database connection and document operations
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import Dict, Any, Optional, List
import logging
from bson import ObjectId
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "enterprise_db"

# Global MongoDB client and database objects
client: Optional[MongoClient] = None
db = None

def init_db() -> bool:
    """
    Initialize MongoDB connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    global client, db
    
    try:
        # Create MongoDB client
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        # Get database
        db = client[DATABASE_NAME]
        
        logger.info(f"✅ Connected to MongoDB at {MONGODB_URL}")
        logger.info(f"✅ Using database: {DATABASE_NAME}")
        
        return True
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
        return False

def get_database():
    """
    Get the database object
    
    Returns:
        Database object or None if not connected
    """
    return db

def get_collection(collection_name: str):
    """
    Get a specific collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection object or None if database not connected
    """
    if db is None:
        logger.error("Database not initialized. Call init_db() first.")
        return None
    
    return db[collection_name]

def insert_document(collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a document into the specified collection
    
    Args:
        collection_name: Name of the collection
        document: Document to insert
        
    Returns:
        Dictionary with success status and result
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        
        # Add timestamp
        document['created_at'] = datetime.now()
        document['updated_at'] = datetime.now()
        
        # Insert document
        result = collection.insert_one(document)
        
        logger.info(f"✅ Document inserted in {collection_name}: {result.inserted_id}")
        
        return {
            'success': True,
            'inserted_id': str(result.inserted_id),
            'message': f'Document successfully inserted into {collection_name}'
        }
        
    except DuplicateKeyError as e:
        logger.error(f"❌ Duplicate key error in {collection_name}: {e}")
        return {
            'success': False,
            'error': 'duplicate_key',
            'message': 'Document with this key already exists'
        }
        
    except Exception as e:
        logger.error(f"❌ Error inserting document in {collection_name}: {e}")
        return {
            'success': False,
            'error': 'insert_failed',
            'message': f'Failed to insert document: {str(e)}'
        }

def find_documents(collection_name: str, query: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find documents in a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query filter
        limit: Maximum number of documents to return
        
    Returns:
        List of documents
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        query = query or {}
        
        # Find documents
        cursor = collection.find(query).limit(limit)
        documents = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        logger.info(f"✅ Found {len(documents)} documents in {collection_name}")
        return documents
        
    except Exception as e:
        logger.error(f"❌ Error finding documents in {collection_name}: {e}")
        return []

def count_documents(collection_name: str, query: Dict[str, Any] = None) -> int:
    """
    Count documents in a collection
    
    Args:
        collection_name: Name of the collection
        query: MongoDB query filter (optional)
        
    Returns:
        Number of documents matching the query
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        
        if query is None:
            query = {}
            
        count = collection.count_documents(query)
        logger.info(f"✅ Found {count} documents in {collection_name}")
        return count
        
    except Exception as e:
        logger.error(f"❌ Error counting documents in {collection_name}: {e}")
        return 0

def update_document(collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a document in the collection
    
    Args:
        collection_name: Name of the collection
        query: Query to find the document
        update: Update operations
        
    Returns:
        Dictionary with success status and result
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        
        # Add updated timestamp
        update.setdefault('$set', {})['updated_at'] = datetime.now()
        
        # Update document
        result = collection.update_one(query, update)
        
        logger.info(f"✅ Updated {result.modified_count} document(s) in {collection_name}")
        
        return {
            'success': True,
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
            'message': f'Document updated in {collection_name}'
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating document in {collection_name}: {e}")
        return {
            'success': False,
            'error': 'update_failed',
            'message': f'Failed to update document: {str(e)}'
        }

def delete_document(collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a document from the collection
    
    Args:
        collection_name: Name of the collection
        query: Query to find the document to delete
        
    Returns:
        Dictionary with success status and result
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        
        # Delete document
        result = collection.delete_one(query)
        
        logger.info(f"✅ Deleted {result.deleted_count} document(s) from {collection_name}")
        
        return {
            'success': True,
            'deleted_count': result.deleted_count,
            'message': f'Document deleted from {collection_name}'
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting document from {collection_name}: {e}")
        return {
            'success': False,
            'error': 'delete_failed',
            'message': f'Failed to delete document: {str(e)}'
        }

def get_collection_stats(collection_name: str) -> Dict[str, Any]:
    """
    Get statistics for a collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dictionary with collection statistics
    """
    try:
        if db is None:
            raise Exception("Database not initialized")
        
        collection = db[collection_name]
        
        # Get collection stats
        stats = {
            'collection_name': collection_name,
            'document_count': collection.count_documents({}),
            'indexes': list(collection.list_indexes())
        }
        
        logger.info(f"✅ Retrieved stats for {collection_name}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting stats for {collection_name}: {e}")
        return {'error': str(e)}

def check_supplier_eligibility(supplier_data: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check if supplier is eligible for registration with enhanced access control checks
    
    Args:
        supplier_data: Supplier registration data
        
    Returns:
        Dictionary with eligibility status and reason
    """
    try:
        # Basic eligibility criteria
        eligibility_checks = {
            'has_company_name': bool(supplier_data.get('company_name', '').strip()),
            'has_valid_business_type': supplier_data.get('business_type', '') in [
                'corporation', 'llc', 'partnership', 'sole_proprietorship', 'non_profit'
            ],
            'has_contact_email': '@' in str(supplier_data.get('contact_email', '')),
            'has_tax_id': bool(supplier_data.get('tax_id', '').strip()),
        }
        
        # Enhanced validation checks
        company_name = supplier_data.get('company_name', '').strip()
        contact_email = supplier_data.get('contact_email', '').strip()
        tax_id = supplier_data.get('tax_id', '').strip()
        
        # Additional business rule checks
        eligibility_checks['valid_company_name_length'] = len(company_name) >= 2
        eligibility_checks['valid_tax_id_format'] = len(tax_id) >= 9  # Minimum tax ID length
        eligibility_checks['valid_email_domain'] = not any(
            domain in contact_email.lower() 
            for domain in ['example.com', 'test.com', 'fake.com', 'invalid.com']
        )
        
        if db is not None:
            # Check if company already exists
            existing_supplier = db.supplier_registration.find_one({
                'company_name': {'$regex': f'^{company_name}$', '$options': 'i'}  # Case insensitive
            })
            eligibility_checks['not_duplicate_company'] = existing_supplier is None
            
            # Check if email already exists
            existing_email = db.supplier_registration.find_one({
                'contact_email': {'$regex': f'^{contact_email}$', '$options': 'i'}
            })
            eligibility_checks['not_duplicate_email'] = existing_email is None
            
            # Check if tax ID already exists
            existing_tax_id = db.supplier_registration.find_one({
                'tax_id': tax_id
            })
            eligibility_checks['not_duplicate_tax_id'] = existing_tax_id is None
            
            # Check for business access control (if access_control collection exists)
            try:
                access_control = db.access_control.find_one({
                    'entity_type': 'supplier',
                    'entity_identifier': contact_email
                })
                
                if access_control:
                    eligibility_checks['has_access_permission'] = access_control.get('allowed', True)
                    eligibility_checks['access_level_sufficient'] = access_control.get('access_level', 'basic') in ['basic', 'standard', 'premium']
                else:
                    # If no specific access control, default to allowed
                    eligibility_checks['has_access_permission'] = True
                    eligibility_checks['access_level_sufficient'] = True
                    
            except Exception:
                # If access_control collection doesn't exist, default to allowed
                eligibility_checks['has_access_permission'] = True
                eligibility_checks['access_level_sufficient'] = True
            
            # Check for business restrictions (if restrictions collection exists)
            try:
                restriction = db.business_restrictions.find_one({
                    '$or': [
                        {'company_name': {'$regex': f'^{company_name}$', '$options': 'i'}},
                        {'email_domain': contact_email.split('@')[-1] if '@' in contact_email else ''},
                        {'tax_id': tax_id}
                    ]
                })
                eligibility_checks['not_restricted'] = restriction is None
                
            except Exception:
                # If restrictions collection doesn't exist, default to not restricted
                eligibility_checks['not_restricted'] = True
                
        else:
            # If no database connection, skip database-dependent checks
            eligibility_checks['not_duplicate_company'] = True
            eligibility_checks['not_duplicate_email'] = True
            eligibility_checks['not_duplicate_tax_id'] = True
            eligibility_checks['has_access_permission'] = True
            eligibility_checks['access_level_sufficient'] = True
            eligibility_checks['not_restricted'] = True
        
        # Overall eligibility
        is_eligible = all(eligibility_checks.values())
        
        # Generate detailed reason
        if is_eligible:
            reason = "✅ All eligibility criteria met - supplier approved for registration"
        else:
            failed_checks = [check for check, passed in eligibility_checks.items() if not passed]
            reason = f"❌ Failed eligibility requirements: {', '.join(failed_checks)}"
        
        result = {
            'eligible': is_eligible,
            'checks': eligibility_checks,
            'reason': reason,
            'company_name': company_name,
            'contact_email': contact_email
        }
        
        logger.info(f"✅ Enhanced supplier eligibility check: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error checking supplier eligibility: {e}")
        return {
            'eligible': False,
            'checks': {},
            'reason': f'❌ Error during eligibility check: {str(e)}'
        }

def get_collections_info() -> Dict[str, Any]:
    """
    Get information about all collections in the database
    
    Returns:
        dict: Information about collections and their schemas
    """
    try:
        if not db:
            init_db()
        
        collections_info = {}
        collection_names = db.list_collection_names()
        
        for collection_name in collection_names:
            try:
                collection = db[collection_name]
                
                # Get sample document to infer schema
                sample_doc = collection.find_one()
                schema_fields = []
                
                if sample_doc:
                    for field, value in sample_doc.items():
                        if field != '_id':  # Skip ObjectId field
                            field_type = type(value).__name__
                            schema_fields.append({
                                'name': field,
                                'type': field_type,
                                'required': True  # Default assumption
                            })
                
                collections_info[collection_name] = {
                    'name': collection_name,
                    'document_count': collection.count_documents({}),
                    'schema_fields': schema_fields,
                    'sample_document': sample_doc
                }
                
            except Exception as e:
                logger.warning(f"Could not get info for collection {collection_name}: {e}")
                collections_info[collection_name] = {
                    'name': collection_name,
                    'error': str(e)
                }
        
        return collections_info
        
    except Exception as e:
        logger.error(f"❌ Error getting collections info: {e}")
        return {}

# Test connection function
def test_connection():
    """Test MongoDB connection"""
# Position-based access control functions
def validate_user_position(user_id: str, required_positions: List[str]) -> Dict[str, Any]:
    """
    Validate if user has required position/role for accessing specific endpoints
    
    Args:
        user_id: User ID to validate
        required_positions: List of positions allowed for this operation
        
    Returns:
        Dictionary with validation status and user details
    """
    try:
        if db is None:
            init_db()
            
        # Check if user exists in user_registration
        user = db.user_registration.find_one({'employee_id': user_id})
        
        if not user:
            return {
                'valid': False,
                'reason': f'User ID {user_id} not found in system',
                'user_details': None
            }
        
        user_position = user.get('position', '').lower()
        
        # Check if user's position is in required positions
        allowed_positions = [pos.lower() for pos in required_positions]
        
        if user_position in allowed_positions:
            return {
                'valid': True,
                'reason': f'User {user_id} has valid position: {user_position}',
                'user_details': {
                    'employee_id': user.get('employee_id'),
                    'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    'email': user.get('email'),
                    'position': user.get('position')
                }
            }
        else:
            return {
                'valid': False,
                'reason': f'User {user_id} position "{user_position}" not authorized. Required: {", ".join(required_positions)}',
                'user_details': {
                    'employee_id': user.get('employee_id'),
                    'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    'position': user.get('position')
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error validating user position: {e}")
        return {
            'valid': False,
            'reason': f'System error during validation: {str(e)}',
            'user_details': None
        }

def get_endpoint_access_requirements() -> Dict[str, List[str]]:
    """
    Define which positions can access which endpoints
    
    Returns:
        Dictionary mapping endpoint names to required positions
    """
    return {
        'supplier_registration': ['procurement_manager', 'admin', 'director', 'ceo'],
        'purchase_order': ['procurement_manager', 'admin', 'director', 'finance_manager'],
        'payroll_management': ['hr_manager', 'admin', 'director', 'ceo'],
        'employee_exit_clearance': ['hr_manager', 'admin', 'director'],
        'performance_review': ['hr_manager', 'manager', 'director', 'admin'],
        'user_registration': ['hr_manager', 'admin', 'director'],
        'compliance_report': ['compliance_officer', 'admin', 'director', 'ceo'],
        'audit_log_viewer': ['admin', 'security_officer', 'director'],
        'system_configuration': ['admin', 'it_manager'],
        'role_management': ['admin', 'hr_manager', 'director'],
        'contract_management': ['legal_manager', 'admin', 'director', 'ceo'],
        'invoice_management': ['finance_manager', 'accounting_manager', 'admin'],
        'warehouse_management': ['warehouse_manager', 'operations_manager', 'admin'],
        # Add more as needed - default to manager level for others
        'default': ['manager', 'admin', 'director', 'ceo']
    }

def create_dummy_users():
    """
    Create dummy users with different positions for testing
    """
    dummy_users = [
        {
            'employee_id': 'EMP001',
            'email': 'admin@company.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'position': 'admin',
            'phone': '+1-555-0001'
        },
        {
            'employee_id': 'EMP002', 
            'email': 'hr.manager@company.com',
            'first_name': 'HR',
            'last_name': 'Manager', 
            'position': 'hr_manager',
            'phone': '+1-555-0002'
        },
        {
            'employee_id': 'EMP003',
            'email': 'procurement@company.com', 
            'first_name': 'Procurement',
            'last_name': 'Manager',
            'position': 'procurement_manager',
            'phone': '+1-555-0003'
        },
        {
            'employee_id': 'EMP004',
            'email': 'finance@company.com',
            'first_name': 'Finance', 
            'last_name': 'Manager',
            'position': 'finance_manager',
            'phone': '+1-555-0004'
        },
        {
            'employee_id': 'EMP005',
            'email': 'director@company.com',
            'first_name': 'Company',
            'last_name': 'Director',
            'position': 'director', 
            'phone': '+1-555-0005'
        }
    ]
    
    try:
        if db is None:
            init_db()
            
        for user in dummy_users:
            # Check if user already exists
            existing = db.user_registration.find_one({'employee_id': user['employee_id']})
            if not existing:
                result = db.user_registration.insert_one(user)
                logger.info(f"✅ Created dummy user: {user['employee_id']} - {user['position']}")
            else:
                logger.info(f"ℹ️ User {user['employee_id']} already exists")
                
    except Exception as e:
        logger.error(f"❌ Error creating dummy users: {e}")

    if init_db():
        print("✅ MongoDB connection test successful!")
        return True
    else:
        print("❌ MongoDB connection test failed!")
        return False

if __name__ == "__main__":
    test_connection()