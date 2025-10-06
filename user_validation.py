"""
User Validation System for ZOPKIT Enterprise Chatbot
Provides validation functions for user data and registrations
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "cleaned_data": user_data.copy()
    }
    
    try:
        # Email validation
        if "email" in user_data:
            email = user_data["email"]
            if not email or not isinstance(email, str):
                validation_result["errors"].append("Email is required and must be a string")
                validation_result["valid"] = False
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                validation_result["errors"].append("Invalid email format")
                validation_result["valid"] = False
            else:
                # Clean and normalize email
                validation_result["cleaned_data"]["email"] = email.lower().strip()
        else:
            validation_result["errors"].append("Email is required")
            validation_result["valid"] = False
        
        # Name validation
        for field in ["first_name", "last_name"]:
            if field in user_data:
                name = user_data[field]
                if not name or not isinstance(name, str):
                    validation_result["errors"].append(f"{field.replace('_', ' ').title()} is required and must be a string")
                    validation_result["valid"] = False
                elif len(name.strip()) < 2:
                    validation_result["errors"].append(f"{field.replace('_', ' ').title()} must be at least 2 characters long")
                    validation_result["valid"] = False
                else:
                    # Clean and normalize name
                    validation_result["cleaned_data"][field] = name.strip().title()
            else:
                validation_result["errors"].append(f"{field.replace('_', ' ').title()} is required")
                validation_result["valid"] = False
        
        # Password validation (if provided)
        if "password" in user_data:
            password = user_data["password"]
            if not password or not isinstance(password, str):
                validation_result["errors"].append("Password is required and must be a string")
                validation_result["valid"] = False
            elif len(password) < 6:
                validation_result["errors"].append("Password must be at least 6 characters long")
                validation_result["valid"] = False
            elif not re.search(r'[a-zA-Z]', password):
                validation_result["warnings"].append("Password should contain at least one letter")
            elif not re.search(r'[0-9]', password):
                validation_result["warnings"].append("Password should contain at least one number")
        
        # Phone validation (if provided)
        if "phone" in user_data and user_data["phone"]:
            phone = str(user_data["phone"]).strip()
            # Remove common separators
            phone_clean = re.sub(r'[^\d+]', '', phone)
            if len(phone_clean) < 10:
                validation_result["warnings"].append("Phone number may be too short")
            else:
                validation_result["cleaned_data"]["phone"] = phone_clean
        
        # Employee ID validation (if provided)
        if "employee_id" in user_data and user_data["employee_id"]:
            emp_id = str(user_data["employee_id"]).strip()
            if not re.match(r'^[A-Z]{3}\d{3}$', emp_id):
                validation_result["warnings"].append("Employee ID should follow format: ABC123 (3 letters + 3 numbers)")
            else:
                validation_result["cleaned_data"]["employee_id"] = emp_id.upper()
        
        # Position validation (if provided)
        if "position" in user_data and user_data["position"]:
            position = user_data["position"].strip()
            validation_result["cleaned_data"]["position"] = position.title()
        
        logger.info(f"✅ User validation completed - Valid: {validation_result['valid']}")
        if validation_result["errors"]:
            logger.warning(f"⚠️ Validation errors: {validation_result['errors']}")
        if validation_result["warnings"]:
            logger.info(f"💡 Validation warnings: {validation_result['warnings']}")
            
    except Exception as e:
        logger.error(f"❌ Error during user validation: {e}")
        validation_result["valid"] = False
        validation_result["errors"].append(f"Validation error: {str(e)}")
    
    return validation_result

def validate_supplier_data(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate supplier registration data
    
    Args:
        supplier_data: Dictionary containing supplier information
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "cleaned_data": supplier_data.copy()
    }
    
    try:
        # Company name validation
        if "company_name" in supplier_data:
            company_name = supplier_data["company_name"]
            if not company_name or not isinstance(company_name, str):
                validation_result["errors"].append("Company name is required and must be a string")
                validation_result["valid"] = False
            elif len(company_name.strip()) < 2:
                validation_result["errors"].append("Company name must be at least 2 characters long")
                validation_result["valid"] = False
            else:
                validation_result["cleaned_data"]["company_name"] = company_name.strip()
        else:
            validation_result["errors"].append("Company name is required")
            validation_result["valid"] = False
        
        # Contact email validation
        if "contact_email" in supplier_data:
            email = supplier_data["contact_email"]
            if not email or not isinstance(email, str):
                validation_result["errors"].append("Contact email is required and must be a string")
                validation_result["valid"] = False
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                validation_result["errors"].append("Invalid contact email format")
                validation_result["valid"] = False
            else:
                validation_result["cleaned_data"]["contact_email"] = email.lower().strip()
        else:
            validation_result["errors"].append("Contact email is required")
            validation_result["valid"] = False
        
        # Business type validation
        if "business_type" in supplier_data and supplier_data["business_type"]:
            business_type = supplier_data["business_type"].strip().lower()
            valid_types = ["corporation", "llc", "partnership", "sole_proprietorship", "other"]
            if business_type not in valid_types:
                validation_result["warnings"].append(f"Business type should be one of: {', '.join(valid_types)}")
            validation_result["cleaned_data"]["business_type"] = business_type
        
        # Tax ID validation (if provided)
        if "tax_id" in supplier_data and supplier_data["tax_id"]:
            tax_id = str(supplier_data["tax_id"]).strip()
            # Basic tax ID format validation (US EIN format: XX-XXXXXXX)
            if not re.match(r'^\d{2}-?\d{7}$', tax_id):
                validation_result["warnings"].append("Tax ID should follow format: XX-XXXXXXX")
            else:
                # Normalize format
                tax_id_clean = re.sub(r'[^0-9]', '', tax_id)
                validation_result["cleaned_data"]["tax_id"] = f"{tax_id_clean[:2]}-{tax_id_clean[2:]}"
        
        logger.info(f"✅ Supplier validation completed - Valid: {validation_result['valid']}")
        if validation_result["errors"]:
            logger.warning(f"⚠️ Validation errors: {validation_result['errors']}")
        if validation_result["warnings"]:
            logger.info(f"💡 Validation warnings: {validation_result['warnings']}")
            
    except Exception as e:
        logger.error(f"❌ Error during supplier validation: {e}")
        validation_result["valid"] = False
        validation_result["errors"].append(f"Validation error: {str(e)}")
    
    return validation_result

# For backward compatibility - main function used by dynamic_chatbot
def validate_user_data_main(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main validation function for backward compatibility"""
    return validate_user_data(user_data)