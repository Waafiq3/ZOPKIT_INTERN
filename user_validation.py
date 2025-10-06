"""
User Registration Validation System
===================================

This module provides comprehensive validation for user registration including:
- Email uniqueness validation
- Mobile number format validation (Indian numbers)
- ID uniqueness validation (except Employee ID)
- Integration with MongoDB database

Requirements:
1. Email IDs must be unique
2. Mobile numbers must be 10 digits starting with 6, 7, 8, or 9
3. All IDs except Employee ID must be unique
4. Proper error messaging
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from pymongo import MongoClient
from datetime import datetime

logger = logging.getLogger(__name__)

class UserRegistrationValidator:
    def __init__(self, db_connection_string: str = "mongodb://localhost:27017", db_name: str = "enterprise_db"):
        """Initialize validator with database connection"""
        self.client = MongoClient(db_connection_string)
        self.db = self.client[db_name]
        self.user_collection = self.db["user_registration"]
        
        # Define which fields must be unique (excluding employee_id)
        self.unique_fields = {
            'email', 'asset_id', 'user_id', 'badge_id', 'card_id', 
            'license_id', 'passport_id', 'national_id', 'tax_id'
        }
        
    def validate_email_format(self, email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email:
            return False, "Email is required"
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
            
        return True, ""
    
    def validate_email_uniqueness(self, email: str, exclude_id: str = None) -> Tuple[bool, str]:
        """Check if email already exists in database"""
        try:
            query = {"email": email.lower()}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
                
            existing_user = self.user_collection.find_one(query)
            if existing_user:
                return False, "Email ID already exists"
                
            return True, ""
        except Exception as e:
            logger.error(f"Email uniqueness check failed: {e}")
            return False, "Database error during email validation"
    
    def validate_mobile_number(self, mobile: str) -> Tuple[bool, str]:
        """
        Validate Indian mobile number format
        Rules: 
        - Must be exactly 10 digits
        - Must start with 6, 7, 8, or 9
        - No letters or special characters
        """
        if not mobile:
            return False, "Mobile number is required"
        
        # Remove any spaces or formatting
        mobile_clean = re.sub(r'[^\d]', '', mobile)
        
        # Check if contains any letters
        if re.search(r'[a-zA-Z]', mobile):
            return False, "Mobile number cannot contain letters"
        
        # Check length
        if len(mobile_clean) != 10:
            return False, "Mobile number must be exactly 10 digits"
        
        # Check if starts with valid digits (6, 7, 8, 9)
        if not mobile_clean.startswith(('6', '7', '8', '9')):
            return False, "Mobile number must start with 6, 7, 8, or 9"
        
        # Check if all characters are digits
        if not mobile_clean.isdigit():
            return False, "Mobile number must contain only digits"
            
        return True, ""
    
    def validate_mobile_uniqueness(self, mobile: str, exclude_id: str = None) -> Tuple[bool, str]:
        """Check if mobile number already exists"""
        try:
            mobile_clean = re.sub(r'[^\d]', '', mobile)
            query = {"mobile": mobile_clean}
            if exclude_id:
                query["_id"] = {"$ne": exclude_id}
                
            existing_user = self.user_collection.find_one(query)
            if existing_user:
                return False, "Mobile number already exists"
                
            return True, ""
        except Exception as e:
            logger.error(f"Mobile uniqueness check failed: {e}")
            return False, "Database error during mobile validation"
    
    def validate_id_uniqueness(self, field_name: str, field_value: str, exclude_id: str = None) -> Tuple[bool, str]:
        """
        Validate uniqueness of ID fields (except employee_id)
        """
        if field_name.lower() == 'employee_id':
            return True, ""  # Employee ID can repeat
            
        if field_name.lower() in self.unique_fields and field_value:
            try:
                query = {field_name.lower(): field_value}
                if exclude_id:
                    query["_id"] = {"$ne": exclude_id}
                    
                existing_record = self.user_collection.find_one(query)
                if existing_record:
                    return False, f"{field_name.replace('_', ' ').title()} already exists"
                    
                return True, ""
            except Exception as e:
                logger.error(f"ID uniqueness check failed for {field_name}: {e}")
                return False, f"Database error during {field_name} validation"
        
        return True, ""
    
    def validate_required_fields(self, user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate required fields are present"""
        required_fields = ['email', 'first_name', 'last_name']
        missing_fields = []
        
        for field in required_fields:
            if not user_data.get(field, '').strip():
                missing_fields.append(field.replace('_', ' ').title())
        
        if missing_fields:
            return False, missing_fields
            
        return True, []
    
    def validate_user_registration(self, user_data: Dict[str, Any], exclude_id: str = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation for user registration
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # 1. Check required fields
        valid_required, missing_fields = self.validate_required_fields(user_data)
        if not valid_required:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # 2. Validate email format
        email = user_data.get('email', '').strip()
        if email:
            valid_email_format, email_error = self.validate_email_format(email)
            if not valid_email_format:
                errors.append(email_error)
            else:
                # 3. Check email uniqueness
                valid_email_unique, email_unique_error = self.validate_email_uniqueness(email, exclude_id)
                if not valid_email_unique:
                    errors.append(email_unique_error)
        
        # 4. Validate mobile number if provided
        mobile = user_data.get('mobile', '').strip()
        if mobile:
            valid_mobile_format, mobile_error = self.validate_mobile_number(mobile)
            if not valid_mobile_format:
                errors.append(mobile_error)
            else:
                # Check mobile uniqueness
                valid_mobile_unique, mobile_unique_error = self.validate_mobile_uniqueness(mobile, exclude_id)
                if not valid_mobile_unique:
                    errors.append(mobile_unique_error)
        
        # 5. Validate ID field uniqueness
        for field_name, field_value in user_data.items():
            if field_name.lower() in self.unique_fields and field_value:
                valid_id, id_error = self.validate_id_uniqueness(field_name, str(field_value).strip(), exclude_id)
                if not valid_id:
                    errors.append(id_error)
        
        return len(errors) == 0, errors
    
    def get_validation_summary(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed validation summary for debugging"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "validations_performed": [],
            "passed": [],
            "failed": []
        }
        
        # Email validation
        email = user_data.get('email', '').strip()
        if email:
            summary["validations_performed"].append("email_format")
            summary["validations_performed"].append("email_uniqueness")
            
            valid_format, format_error = self.validate_email_format(email)
            if valid_format:
                summary["passed"].append("email_format")
                valid_unique, unique_error = self.validate_email_uniqueness(email)
                if valid_unique:
                    summary["passed"].append("email_uniqueness")
                else:
                    summary["failed"].append(f"email_uniqueness: {unique_error}")
            else:
                summary["failed"].append(f"email_format: {format_error}")
        
        # Mobile validation
        mobile = user_data.get('mobile', '').strip()
        if mobile:
            summary["validations_performed"].append("mobile_format")
            summary["validations_performed"].append("mobile_uniqueness")
            
            valid_format, format_error = self.validate_mobile_number(mobile)
            if valid_format:
                summary["passed"].append("mobile_format")
                valid_unique, unique_error = self.validate_mobile_uniqueness(mobile)
                if valid_unique:
                    summary["passed"].append("mobile_uniqueness")
                else:
                    summary["failed"].append(f"mobile_uniqueness: {unique_error}")
            else:
                summary["failed"].append(f"mobile_format: {format_error}")
        
        return summary

# Convenience functions for easy integration
def validate_user_data(user_data: Dict[str, Any], exclude_id: str = None) -> Tuple[bool, List[str]]:
    """Quick validation function"""
    validator = UserRegistrationValidator()
    return validator.validate_user_registration(user_data, exclude_id)

def validate_mobile_number_quick(mobile: str) -> Tuple[bool, str]:
    """Quick mobile number validation"""
    validator = UserRegistrationValidator()
    return validator.validate_mobile_number(mobile)

def validate_email_quick(email: str) -> Tuple[bool, str]:
    """Quick email validation"""
    validator = UserRegistrationValidator()
    valid_format, format_error = validator.validate_email_format(email)
    if not valid_format:
        return False, format_error
    
    valid_unique, unique_error = validator.validate_email_uniqueness(email)
    return valid_unique, unique_error

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "name": "Valid user",
            "data": {
                "email": "test@example.com",
                "mobile": "9876543210",
                "first_name": "John",
                "last_name": "Doe",
                "asset_id": "AS001"
            }
        },
        {
            "name": "Invalid mobile - starts with 5",
            "data": {
                "email": "test2@example.com", 
                "mobile": "5876543210",
                "first_name": "Jane",
                "last_name": "Doe"
            }
        },
        {
            "name": "Invalid mobile - contains letters",
            "data": {
                "email": "test3@example.com",
                "mobile": "987654321A",
                "first_name": "Bob",
                "last_name": "Smith"
            }
        },
        {
            "name": "Invalid email format",
            "data": {
                "email": "invalid-email",
                "mobile": "9876543210",
                "first_name": "Alice",
                "last_name": "Johnson"
            }
        }
    ]
    
    validator = UserRegistrationValidator()
    
    print("🧪 Running User Registration Validation Tests")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        is_valid, errors = validator.validate_user_registration(test_case['data'])
        
        if is_valid:
            print("✅ PASSED - User registration is valid")
        else:
            print("❌ FAILED - Validation errors:")
            for error in errors:
                print(f"   • {error}")
        
        print(f"📊 Summary: {validator.get_validation_summary(test_case['data'])}")