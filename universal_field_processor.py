"""
Universal Field Processing System for ZOPKIT Enterprise Chatbot
Generic field handling that works with any collection schema without hardcoding

This system dynamically processes fields for all 49 collections based on 
their schemas, handling validation, extraction, and user interaction uniformly.
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date
import email_validator
from schema import COLLECTION_SCHEMAS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FieldType(Enum):
    """Field data types with validation rules"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    ID = "id"
    CURRENCY = "currency"
    URL = "url"
    JSON = "json"

class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"      # Fail on any validation error
    MODERATE = "moderate"  # Warn on minor issues, fail on major
    LENIENT = "lenient"    # Only fail on critical errors

@dataclass
class FieldDefinition:
    """Definition of a field with its properties"""
    name: str
    field_type: FieldType
    required: bool
    display_name: str
    description: str
    validation_rules: Dict[str, Any]
    default_value: Optional[Any] = None
    examples: List[str] = None

@dataclass
class FieldValue:
    """Processed field value with validation status"""
    field_name: str
    raw_value: str
    processed_value: Any
    is_valid: bool
    validation_errors: List[str]
    confidence: float
    source: str  # How the value was extracted

@dataclass
class FieldProcessingResult:
    """Result of field processing operation"""
    collection_name: str
    processed_fields: Dict[str, FieldValue]
    missing_required: List[str]
    validation_summary: Dict[str, Any]
    completion_percentage: float
    next_field_to_collect: Optional[str]
    user_prompt: Optional[str]

class UniversalFieldProcessor:
    """
    Universal field processing system that works with any collection
    
    Features:
    - Dynamic field type detection
    - Smart value extraction from natural language
    - Flexible validation with multiple levels
    - User-friendly prompts generation
    - Progress tracking
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        """Initialize the field processor"""
        self.collection_schemas = COLLECTION_SCHEMAS
        self.validation_level = validation_level
        self.field_definitions = self._initialize_field_definitions()
        self.extraction_patterns = self._initialize_extraction_patterns()
        self.validation_rules = self._initialize_validation_rules()
        
        logger.info(f"✅ Universal Field Processor initialized with {validation_level.value} validation")
    
    def process_collection_data(self, collection_name: str, user_input: str, 
                               existing_data: Dict[str, Any] = None) -> FieldProcessingResult:
        """
        Process user input to extract and validate fields for a collection
        
        Args:
            collection_name: Target collection name
            user_input: User's natural language input
            existing_data: Previously collected data
            
        Returns:
            FieldProcessingResult with processing status and next steps
        """
        if existing_data is None:
            existing_data = {}
            
        logger.info(f"🔧 Processing fields for collection: {collection_name}")
        
        if collection_name not in self.collection_schemas:
            raise ValueError(f"Unknown collection: {collection_name}")
        
        schema = self.collection_schemas[collection_name]
        required_fields = schema.get('required', [])
        optional_fields = schema.get('optional', [])
        all_fields = required_fields + optional_fields
        
        # Extract new field values from user input
        extracted_values = self._extract_field_values(user_input, all_fields, collection_name)
        
        # Merge with existing data
        combined_data = {**existing_data, **extracted_values}
        
        # Process each field
        processed_fields = {}
        for field_name in all_fields:
            field_def = self._get_field_definition(field_name, collection_name)
            raw_value = combined_data.get(field_name)
            
            if raw_value is not None:
                processed_fields[field_name] = self._process_single_field(
                    field_def, raw_value, user_input
                )
        
        # Identify missing required fields
        missing_required = [
            field for field in required_fields 
            if field not in processed_fields or not processed_fields[field].is_valid
        ]
        
        # Calculate completion percentage
        total_required = len(required_fields)
        completed_required = len([f for f in required_fields if f in processed_fields and processed_fields[f].is_valid])
        completion_percentage = (completed_required / total_required * 100) if total_required > 0 else 100
        
        # Determine next field to collect
        next_field = missing_required[0] if missing_required else None
        user_prompt = self._generate_field_prompt(next_field, collection_name) if next_field else None
        
        # Generate validation summary
        validation_summary = self._generate_validation_summary(processed_fields, missing_required)
        
        return FieldProcessingResult(
            collection_name=collection_name,
            processed_fields=processed_fields,
            missing_required=missing_required,
            validation_summary=validation_summary,
            completion_percentage=completion_percentage,
            next_field_to_collect=next_field,
            user_prompt=user_prompt
        )
    
    def _initialize_field_definitions(self) -> Dict[str, FieldDefinition]:
        """Initialize field definitions with types and validation rules"""
        
        # Common field definitions that apply across collections
        common_fields = {
            # Identity fields
            "employee_id": FieldDefinition(
                name="employee_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Employee ID",
                description="Unique employee identifier (e.g., EMP001)",
                validation_rules={"pattern": r"^(EMP|emp)\d{3,6}$", "min_length": 6, "max_length": 9}
            ),
            
            # Personal information
            "first_name": FieldDefinition(
                name="first_name",
                field_type=FieldType.TEXT,
                required=True,
                display_name="First Name",
                description="Your first name",
                validation_rules={"min_length": 1, "max_length": 50, "pattern": r"^[A-Za-z\s'-]+$"}
            ),
            "last_name": FieldDefinition(
                name="last_name", 
                field_type=FieldType.TEXT,
                required=True,
                display_name="Last Name",
                description="Your last name",
                validation_rules={"min_length": 1, "max_length": 50, "pattern": r"^[A-Za-z\s'-]+$"}
            ),
            "email": FieldDefinition(
                name="email",
                field_type=FieldType.EMAIL,
                required=True,
                display_name="Email Address",
                description="Your email address (e.g., john.doe@company.com)",
                validation_rules={"format": "email"}
            ),
            "mobile": FieldDefinition(
                name="mobile",
                field_type=FieldType.PHONE,
                required=True,
                display_name="Mobile Number",
                description="Your mobile phone number (10 digits)",
                validation_rules={"pattern": r"^\d{10}$", "length": 10}
            ),
            "phone": FieldDefinition(
                name="phone",
                field_type=FieldType.PHONE,
                required=False,
                display_name="Phone Number",
                description="Phone number",
                validation_rules={"pattern": r"^\d{10}$|^\+\d{1,3}\s?\d{10}$"}
            ),
            
            # Business fields
            "department": FieldDefinition(
                name="department",
                field_type=FieldType.TEXT,
                required=True,
                display_name="Department",
                description="Your department (e.g., IT, HR, Finance)",
                validation_rules={"min_length": 2, "max_length": 100}
            ),
            "position": FieldDefinition(
                name="position",
                field_type=FieldType.TEXT,
                required=True,
                display_name="Position",
                description="Your job position/title",
                validation_rules={"min_length": 2, "max_length": 100}
            ),
            
            # IDs and References
            "po_id": FieldDefinition(
                name="po_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Purchase Order ID",
                description="Purchase order identifier (e.g., PO001)",
                validation_rules={"pattern": r"^(PO|po)\d{3,6}$"}
            ),
            "vendor_id": FieldDefinition(
                name="vendor_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Vendor ID",
                description="Vendor identifier",
                validation_rules={"pattern": r"^(VEN|ven)\d{3,6}$"}
            ),
            "supplier_id": FieldDefinition(
                name="supplier_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Supplier ID",
                description="Supplier identifier",
                validation_rules={"pattern": r"^(SUP|sup)\d{3,6}$"}
            ),
            "customer_id": FieldDefinition(
                name="customer_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Customer ID",
                description="Customer identifier",
                validation_rules={"pattern": r"^(CUS|cus)\d{3,6}$"}
            ),
            "order_id": FieldDefinition(
                name="order_id",
                field_type=FieldType.ID,
                required=True,
                display_name="Order ID",
                description="Order identifier",
                validation_rules={"pattern": r"^(ORD|ord)\d{3,6}$"}
            ),
            
            # Financial fields
            "amount": FieldDefinition(
                name="amount",
                field_type=FieldType.CURRENCY,
                required=True,
                display_name="Amount",
                description="Monetary amount (e.g., 1000.00)",
                validation_rules={"min_value": 0, "max_value": 1000000, "decimal_places": 2}
            ),
            "salary": FieldDefinition(
                name="salary",
                field_type=FieldType.CURRENCY,
                required=True,
                display_name="Salary",
                description="Annual salary amount",
                validation_rules={"min_value": 0, "max_value": 10000000}
            ),
            
            # Dates
            "date": FieldDefinition(
                name="date",
                field_type=FieldType.DATE,
                required=True,
                display_name="Date",
                description="Date (YYYY-MM-DD format)",
                validation_rules={"format": "YYYY-MM-DD"}
            ),
            "start_date": FieldDefinition(
                name="start_date",
                field_type=FieldType.DATE,
                required=True,
                display_name="Start Date",
                description="Start date (YYYY-MM-DD)",
                validation_rules={"format": "YYYY-MM-DD"}
            ),
            "end_date": FieldDefinition(
                name="end_date",
                field_type=FieldType.DATE,
                required=True,
                display_name="End Date",
                description="End date (YYYY-MM-DD)",
                validation_rules={"format": "YYYY-MM-DD"}
            ),
            
            # Quantities and Numbers
            "quantity": FieldDefinition(
                name="quantity",
                field_type=FieldType.NUMBER,
                required=True,
                display_name="Quantity",
                description="Number of items",
                validation_rules={"min_value": 1, "max_value": 10000, "integer": True}
            ),
            
            # Text fields
            "product": FieldDefinition(
                name="product",
                field_type=FieldType.TEXT,
                required=True,
                display_name="Product",
                description="Product name or description",
                validation_rules={"min_length": 2, "max_length": 200}
            ),
            "description": FieldDefinition(
                name="description",
                field_type=FieldType.TEXT,
                required=False,
                display_name="Description",
                description="Additional details or description",
                validation_rules={"max_length": 1000}
            ),
            "notes": FieldDefinition(
                name="notes",
                field_type=FieldType.TEXT,
                required=False,
                display_name="Notes",
                description="Additional notes or comments",
                validation_rules={"max_length": 500}
            ),
            "reason": FieldDefinition(
                name="reason",
                field_type=FieldType.TEXT,
                required=False,
                display_name="Reason",
                description="Reason or justification",
                validation_rules={"max_length": 500}
            )
        }
        
        return common_fields
    
    def _initialize_extraction_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for extracting field values"""
        
        return {
            FieldType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            FieldType.PHONE: [
                r'\b\d{10}\b',  # 10 digit phone
                r'\b\+\d{1,3}\s?\d{10}\b',  # International format
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # US format with separators
            ],
            FieldType.ID: [
                r'\b(EMP|emp)\d{3,6}\b',  # Employee ID
                r'\b(PO|po)\d{3,6}\b',   # Purchase Order ID
                r'\b(VEN|ven)\d{3,6}\b', # Vendor ID
                r'\b(SUP|sup)\d{3,6}\b', # Supplier ID
                r'\b(CUS|cus)\d{3,6}\b', # Customer ID
                r'\b(ORD|ord)\d{3,6}\b'  # Order ID
            ],
            FieldType.DATE: [
                r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                r'\b\d{2}/\d{2}/\d{4}\b',  # MM/DD/YYYY
                r'\b\d{2}-\d{2}-\d{4}\b'   # MM-DD-YYYY
            ],
            FieldType.CURRENCY: [
                r'\$?\d+\.?\d*',  # Currency with optional $ and decimals
                r'\b\d+\s?(dollars?|USD|rupees?|INR)\b'  # Currency with words
            ],
            FieldType.NUMBER: [
                r'\b\d+\b',  # Simple integers
                r'\b\d+\.\d+\b'  # Decimals
            ]
        }
    
    def _initialize_validation_rules(self) -> Dict[FieldType, Dict[str, Any]]:
        """Initialize validation rules for each field type"""
        
        return {
            FieldType.EMAIL: {
                "validators": ["email_format"],
                "error_messages": {
                    "email_format": "Please provide a valid email address"
                }
            },
            FieldType.PHONE: {
                "validators": ["phone_format", "length"],
                "error_messages": {
                    "phone_format": "Please provide a valid phone number (10 digits)",
                    "length": "Phone number must be 10 digits"
                }
            },
            FieldType.ID: {
                "validators": ["pattern", "length"],
                "error_messages": {
                    "pattern": "ID format is invalid",
                    "length": "ID length is incorrect"
                }
            },
            FieldType.DATE: {
                "validators": ["date_format", "date_range"],
                "error_messages": {
                    "date_format": "Please provide date in YYYY-MM-DD format",
                    "date_range": "Date is outside valid range"
                }
            },
            FieldType.CURRENCY: {
                "validators": ["numeric", "range"],
                "error_messages": {
                    "numeric": "Amount must be a valid number",
                    "range": "Amount is outside valid range"
                }
            },
            FieldType.NUMBER: {
                "validators": ["numeric", "range"],
                "error_messages": {
                    "numeric": "Must be a valid number",
                    "range": "Number is outside valid range"
                }
            },
            FieldType.TEXT: {
                "validators": ["length", "pattern"],
                "error_messages": {
                    "length": "Text length is invalid",
                    "pattern": "Text contains invalid characters"
                }
            }
        }
    
    def _get_field_definition(self, field_name: str, collection_name: str) -> FieldDefinition:
        """Get field definition for a specific field"""
        
        # Return predefined definition if available
        if field_name in self.field_definitions:
            return self.field_definitions[field_name]
        
        # Create dynamic definition based on field name and collection context
        field_type = self._infer_field_type(field_name)
        is_required = False
        if collection_name and collection_name in self.collection_schemas:
            is_required = field_name in self.collection_schemas[collection_name].get('required', [])
        
        return FieldDefinition(
            name=field_name,
            field_type=field_type,
            required=is_required,
            display_name=field_name.replace('_', ' ').title(),
            description=f"Please provide {field_name.replace('_', ' ')}",
            validation_rules=self._get_default_validation_rules(field_type)
        )
    
    def _infer_field_type(self, field_name: str) -> FieldType:
        """Infer field type from field name"""
        
        field_lower = field_name.lower()
        
        # Pattern-based type inference
        if 'email' in field_lower:
            return FieldType.EMAIL
        elif any(x in field_lower for x in ['phone', 'mobile', 'contact']):
            return FieldType.PHONE
        elif any(x in field_lower for x in ['_id', 'id_']):
            return FieldType.ID
        elif any(x in field_lower for x in ['date', 'time']):
            return FieldType.DATE
        elif any(x in field_lower for x in ['amount', 'price', 'cost', 'salary', 'fee']):
            return FieldType.CURRENCY
        elif any(x in field_lower for x in ['quantity', 'count', 'number', 'age']):
            return FieldType.NUMBER
        elif 'url' in field_lower or 'website' in field_lower:
            return FieldType.URL
        else:
            return FieldType.TEXT
    
    def _get_default_validation_rules(self, field_type: FieldType) -> Dict[str, Any]:
        """Get default validation rules for a field type"""
        
        defaults = {
            FieldType.TEXT: {"min_length": 1, "max_length": 255},
            FieldType.EMAIL: {"format": "email"},
            FieldType.PHONE: {"pattern": r"^\d{10}$"},
            FieldType.ID: {"min_length": 3, "max_length": 20},
            FieldType.DATE: {"format": "YYYY-MM-DD"},
            FieldType.CURRENCY: {"min_value": 0, "max_value": 1000000},
            FieldType.NUMBER: {"min_value": 0, "max_value": 999999}
        }
        
        return defaults.get(field_type, {})
    
    def _extract_field_values(self, user_input: str, field_names: List[str], collection_name: str = None) -> Dict[str, str]:
        """Extract field values from user input using intelligent parsing"""
        
        extracted = {}
        
        # Try pattern-based extraction first
        for field_name in field_names:
            field_def = self._get_field_definition(field_name, collection_name or "")
            patterns = self.extraction_patterns.get(field_def.field_type, [])
            
            for pattern in patterns:
                matches = re.findall(pattern, user_input, re.IGNORECASE)
                if matches:
                    # For ID fields, check if the pattern matches the field type
                    if field_def.field_type == FieldType.ID:
                        for match in matches:
                            if self._id_matches_field(match, field_name):
                                extracted[field_name] = match
                                break
                    else:
                        extracted[field_name] = matches[0]
                    break
        
        # Try keyword-context extraction
        for field_name in field_names:
            if field_name not in extracted:
                context_value = self._extract_by_context(user_input, field_name)
                if context_value:
                    extracted[field_name] = context_value
        
        return extracted
    
    def _id_matches_field(self, id_value: str, field_name: str) -> bool:
        """Check if an ID value matches the expected field type"""
        
        id_prefixes = {
            'employee_id': ['EMP', 'emp'],
            'po_id': ['PO', 'po'],
            'vendor_id': ['VEN', 'ven'],
            'supplier_id': ['SUP', 'sup'],
            'customer_id': ['CUS', 'cus'],
            'order_id': ['ORD', 'ord']
        }
        
        if field_name in id_prefixes:
            return any(id_value.startswith(prefix) for prefix in id_prefixes[field_name])
        
        return True  # Default to accept if no specific rule
    
    def _extract_by_context(self, user_input: str, field_name: str) -> Optional[str]:
        """Extract field value using contextual clues"""
        
        # Create patterns for contextual extraction
        field_variations = [
            field_name,
            field_name.replace('_', ' '),
            field_name.replace('_', '-')
        ]
        
        for variation in field_variations:
            # Pattern: "field_name: value" or "field_name is value"
            patterns = [
                rf'{re.escape(variation)}\s*[:=]\s*([^\s,;]+)',
                rf'{re.escape(variation)}\s+is\s+([^\s,;]+)',
                rf'my\s+{re.escape(variation)}\s+is\s+([^\s,;]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, user_input, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
        
        return None
    
    def _process_single_field(self, field_def: FieldDefinition, raw_value: str, 
                             full_input: str) -> FieldValue:
        """Process and validate a single field value"""
        
        # Clean the raw value
        cleaned_value = raw_value.strip()
        
        # Convert to appropriate type
        processed_value, conversion_errors = self._convert_field_value(cleaned_value, field_def)
        
        # Validate the processed value
        validation_errors = []
        if conversion_errors:
            validation_errors.extend(conversion_errors)
        else:
            validation_errors = self._validate_field_value(processed_value, field_def)
        
        # Calculate confidence based on extraction method and validation
        confidence = self._calculate_field_confidence(raw_value, field_def, validation_errors, full_input)
        
        return FieldValue(
            field_name=field_def.name,
            raw_value=raw_value,
            processed_value=processed_value,
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            confidence=confidence,
            source="natural_language_extraction"
        )
    
    def _convert_field_value(self, value: str, field_def: FieldDefinition) -> Tuple[Any, List[str]]:
        """Convert string value to appropriate type"""
        
        errors = []
        
        try:
            if field_def.field_type == FieldType.NUMBER:
                if '.' in value:
                    return float(value), []
                else:
                    return int(value), []
            elif field_def.field_type == FieldType.CURRENCY:
                # Remove currency symbols and convert
                cleaned = re.sub(r'[$,\s]', '', value)
                return float(cleaned), []
            elif field_def.field_type == FieldType.DATE:
                # Try to parse different date formats
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']
                for fmt in date_formats:
                    try:
                        return datetime.strptime(value, fmt).date(), []
                    except ValueError:
                        continue
                errors.append(f"Could not parse date: {value}")
                return value, errors
            elif field_def.field_type == FieldType.BOOLEAN:
                if value.lower() in ['true', 'yes', '1', 'on', 'enable']:
                    return True, []
                elif value.lower() in ['false', 'no', '0', 'off', 'disable']:
                    return False, []
                else:
                    errors.append(f"Could not parse boolean: {value}")
                    return value, errors
            else:
                # Keep as string for text, email, phone, ID, URL
                return value, []
                
        except (ValueError, TypeError) as e:
            errors.append(f"Type conversion error: {str(e)}")
            return value, errors
    
    def _validate_field_value(self, value: Any, field_def: FieldDefinition) -> List[str]:
        """Validate a field value against its definition"""
        
        errors = []
        rules = field_def.validation_rules
        
        # Check if value is provided for required fields
        if field_def.required and (value is None or str(value).strip() == ''):
            errors.append(f"{field_def.display_name} is required")
            return errors
        
        # Skip validation if value is empty for optional fields
        if not field_def.required and (value is None or str(value).strip() == ''):
            return errors
        
        # Type-specific validation
        if field_def.field_type == FieldType.EMAIL:
            try:
                email_validator.validate_email(str(value))
            except:
                errors.append("Invalid email format")
        
        elif field_def.field_type == FieldType.PHONE:
            phone_str = str(value)
            if 'pattern' in rules:
                if not re.match(rules['pattern'], phone_str):
                    errors.append("Invalid phone number format")
        
        elif field_def.field_type == FieldType.ID:
            id_str = str(value)
            if 'pattern' in rules:
                if not re.match(rules['pattern'], id_str):
                    errors.append("Invalid ID format")
        
        # Length validation
        if 'min_length' in rules:
            if len(str(value)) < rules['min_length']:
                errors.append(f"Minimum length is {rules['min_length']} characters")
        
        if 'max_length' in rules:
            if len(str(value)) > rules['max_length']:
                errors.append(f"Maximum length is {rules['max_length']} characters")
        
        # Numeric range validation
        if 'min_value' in rules and isinstance(value, (int, float)):
            if value < rules['min_value']:
                errors.append(f"Minimum value is {rules['min_value']}")
        
        if 'max_value' in rules and isinstance(value, (int, float)):
            if value > rules['max_value']:
                errors.append(f"Maximum value is {rules['max_value']}")
        
        # Pattern validation
        if 'pattern' in rules and field_def.field_type == FieldType.TEXT:
            if not re.match(rules['pattern'], str(value)):
                errors.append("Value contains invalid characters")
        
        return errors
    
    def _calculate_field_confidence(self, raw_value: str, field_def: FieldDefinition, 
                                   validation_errors: List[str], full_input: str) -> float:
        """Calculate confidence score for field extraction"""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence if validation passes
        if not validation_errors:
            confidence += 0.3
        
        # Boost confidence for exact pattern matches
        if field_def.field_type in self.extraction_patterns:
            for pattern in self.extraction_patterns[field_def.field_type]:
                if re.search(pattern, raw_value, re.IGNORECASE):
                    confidence += 0.2
                    break
        
        # Boost confidence if field name appears near the value in input
        field_variations = [field_def.name, field_def.display_name.lower()]
        for variation in field_variations:
            if variation in full_input.lower():
                distance = abs(full_input.lower().find(variation) - full_input.lower().find(raw_value.lower()))
                if distance < 50:  # Within 50 characters
                    confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_field_prompt(self, field_name: str, collection_name: str) -> str:
        """Generate user-friendly prompt for collecting a field"""
        
        field_def = self._get_field_definition(field_name, collection_name)
        
        prompt = f"Please provide your {field_def.display_name}"
        
        if field_def.description:
            prompt += f" ({field_def.description})"
        
        # Add examples if available
        if hasattr(field_def, 'examples') and field_def.examples:
            examples = ', '.join(field_def.examples[:2])  # Show max 2 examples
            prompt += f". For example: {examples}"
        
        # Add format hints for specific field types
        format_hints = {
            FieldType.EMAIL: "email format (e.g., john@company.com)",
            FieldType.PHONE: "10-digit mobile number",
            FieldType.DATE: "YYYY-MM-DD format",
            FieldType.ID: "proper ID format"
        }
        
        if field_def.field_type in format_hints:
            prompt += f" - {format_hints[field_def.field_type]}"
        
        return prompt + ":"
    
    def _generate_validation_summary(self, processed_fields: Dict[str, FieldValue], 
                                   missing_required: List[str]) -> Dict[str, Any]:
        """Generate summary of validation results"""
        
        total_fields = len(processed_fields)
        valid_fields = sum(1 for field in processed_fields.values() if field.is_valid)
        invalid_fields = total_fields - valid_fields
        
        # Collect all validation errors
        all_errors = []
        for field in processed_fields.values():
            if field.validation_errors:
                all_errors.extend([f"{field.field_name}: {error}" for error in field.validation_errors])
        
        return {
            "total_fields_processed": total_fields,
            "valid_fields": valid_fields,
            "invalid_fields": invalid_fields,
            "missing_required_fields": len(missing_required),
            "validation_errors": all_errors,
            "overall_status": "valid" if not missing_required and not all_errors else "incomplete"
        }
    
    def get_collection_requirements(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed requirements for a collection"""
        
        if collection_name not in self.collection_schemas:
            return {"error": f"Collection '{collection_name}' not found"}
        
        schema = self.collection_schemas[collection_name]
        required_fields = schema.get('required', [])
        optional_fields = schema.get('optional', [])
        
        field_info = {}
        for field_name in required_fields + optional_fields:
            field_def = self._get_field_definition(field_name, collection_name)
            field_info[field_name] = {
                "display_name": field_def.display_name,
                "type": field_def.field_type.value,
                "required": field_def.required,
                "description": field_def.description,
                "validation_rules": field_def.validation_rules
            }
        
        return {
            "collection": collection_name,
            "required_fields": required_fields,
            "optional_fields": optional_fields,
            "field_definitions": field_info,
            "total_fields": len(required_fields) + len(optional_fields)
        }

# Factory function
def create_field_processor(validation_level: ValidationLevel = ValidationLevel.MODERATE) -> UniversalFieldProcessor:
    """Create and initialize field processor"""
    return UniversalFieldProcessor(validation_level=validation_level)