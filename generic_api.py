"""
Generic FastAPI MongoDB API
Works with existing enterprise_db collections and their schema validations
"""

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, WriteError
from bson import ObjectId
from datetime import datetime
import json
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "enterprise_db"

class MongoManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URL)
            self.db = self.client[DATABASE_NAME]
            # Test connection
            self.client.server_info()
            logger.info(f"✅ Connected to MongoDB: {MONGODB_URL}")
            logger.info(f"✅ Using database: {DATABASE_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection_names(self) -> List[str]:
        """Get all collection names from the database"""
        return self.db.list_collection_names()
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        return collection_name in self.get_collection_names()
    
    def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get collection schema validation rules"""
        try:
            collection_info = self.db.get_collection(collection_name).options()
            if 'validator' in collection_info:
                return collection_info['validator']
            else:
                # If no validator, return empty schema
                return {}
        except Exception as e:
            logger.error(f"Error getting schema for {collection_name}: {e}")
            return {}
    
    def get_required_fields(self, collection_name: str) -> List[str]:
        """Extract required fields from collection schema"""
        try:
            schema = self.get_collection_schema(collection_name)
            
            # Navigate through the schema structure to find required fields
            if '$jsonSchema' in schema:
                json_schema = schema['$jsonSchema']
                if 'required' in json_schema:
                    # Filter out _id from required fields as it's auto-generated
                    required_fields = [field for field in json_schema['required'] if field != '_id']
                    return required_fields
            
            # If no schema validation found, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error extracting required fields for {collection_name}: {e}")
            return []
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert document into collection"""
        try:
            collection = self.db[collection_name]
            
            # Add timestamps
            document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            
            # Insert document
            result = collection.insert_one(document)
            
            # Return the inserted document with ID
            document['_id'] = str(result.inserted_id)
            
            logger.info(f"✅ Document inserted in {collection_name}: {result.inserted_id}")
            return document
            
        except WriteError as e:
            logger.error(f"❌ Validation error in {collection_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Document validation failed: {e}")
        except DuplicateKeyError as e:
            logger.error(f"❌ Duplicate key error in {collection_name}: {e}")
            raise HTTPException(status_code=409, detail="Document with this data already exists")
        except Exception as e:
            logger.error(f"❌ Error inserting document in {collection_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    def get_all_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get all documents from collection"""
        try:
            collection = self.db[collection_name]
            documents = list(collection.find())
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                # Convert datetime objects to ISO format
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
            
            logger.info(f"✅ Retrieved {len(documents)} documents from {collection_name}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error retrieving documents from {collection_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Initialize MongoDB manager
mongo_manager = MongoManager()

# FastAPI app
app = FastAPI(
    title="Enterprise MongoDB API",
    description="Generic API for enterprise collections with automatic schema validation",
    version="1.0.0"
)

def validate_required_fields(document: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Check which required fields are missing from the document"""
    missing_fields = []
    
    for field in required_fields:
        if field not in document or document[field] is None or document[field] == "":
            missing_fields.append(field)
    
    return missing_fields

@app.get("/")
async def root():
    """Root endpoint with API information"""
    collections = mongo_manager.get_collection_names()
    return {
        "status": "success",
        "message": "Enterprise MongoDB API is running",
        "data": {
            "database": DATABASE_NAME,
            "total_collections": len(collections),
            "collections": collections[:10],  # Show first 10
            "endpoints": {
                "POST": "/api/{collection_name} - Insert document",
                "GET": "/api/{collection_name} - Get all documents",
                "GET": "/collections - List all collections"
            }
        }
    }

@app.get("/collections")
async def list_collections():
    """List all available collections"""
    try:
        collections = mongo_manager.get_collection_names()
        return {
            "status": "success",
            "message": f"Found {len(collections)} collections",
            "data": {
                "collections": collections,
                "total": len(collections)
            }
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error listing collections: {str(e)}"
        }, status_code=500)

@app.post("/api/{collection_name}")
async def create_document(
    collection_name: str = Path(..., description="Name of the collection"),
    document: Dict[str, Any] = None
):
    """Generic POST endpoint for any collection"""
    
    # Validate collection exists
    if not mongo_manager.collection_exists(collection_name):
        return JSONResponse({
            "status": "error",
            "message": f"Collection '{collection_name}' does not exist",
            "available_collections": mongo_manager.get_collection_names()
        }, status_code=404)
    
    # Validate request body
    if not document:
        return JSONResponse({
            "status": "error",
            "message": "Request body is required"
        }, status_code=400)
    
    try:
        # Get required fields for this collection
        required_fields = mongo_manager.get_required_fields(collection_name)
        
        # Check for missing required fields
        missing_fields = validate_required_fields(document, required_fields)
        
        if missing_fields:
            return JSONResponse({
                "status": "error",
                "message": "Missing required fields",
                "missing_fields": missing_fields,
                "required_fields": required_fields
            }, status_code=400)
        
        # Insert document
        inserted_doc = mongo_manager.insert_document(collection_name, document)
        
        return {
            "status": "success",
            "message": f"Document created successfully in {collection_name}",
            "data": inserted_doc
        }
        
    except HTTPException as e:
        return JSONResponse({
            "status": "error",
            "message": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in create_document: {e}")
        return JSONResponse({
            "status": "error",
            "message": "Internal server error"
        }, status_code=500)

@app.get("/api/{collection_name}")
async def get_documents(
    collection_name: str = Path(..., description="Name of the collection")
):
    """Generic GET endpoint for any collection"""
    
    # Validate collection exists
    if not mongo_manager.collection_exists(collection_name):
        return JSONResponse({
            "status": "error",
            "message": f"Collection '{collection_name}' does not exist",
            "available_collections": mongo_manager.get_collection_names()
        }, status_code=404)
    
    try:
        # Get all documents from collection
        documents = mongo_manager.get_all_documents(collection_name)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(documents)} documents from {collection_name}",
            "data": {
                "collection": collection_name,
                "count": len(documents),
                "documents": documents
            }
        }
        
    except HTTPException as e:
        return JSONResponse({
            "status": "error",
            "message": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in get_documents: {e}")
        return JSONResponse({
            "status": "error",
            "message": "Internal server error"
        }, status_code=500)

@app.get("/api/{collection_name}/schema")
async def get_collection_schema(
    collection_name: str = Path(..., description="Name of the collection")
):
    """Get schema information for a collection"""
    
    # Validate collection exists
    if not mongo_manager.collection_exists(collection_name):
        return JSONResponse({
            "status": "error",
            "message": f"Collection '{collection_name}' does not exist"
        }, status_code=404)
    
    try:
        schema = mongo_manager.get_collection_schema(collection_name)
        required_fields = mongo_manager.get_required_fields(collection_name)
        
        return {
            "status": "success",
            "message": f"Schema information for {collection_name}",
            "data": {
                "collection": collection_name,
                "required_fields": required_fields,
                "schema": schema
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting schema for {collection_name}: {e}")
        return JSONResponse({
            "status": "error",
            "message": "Error retrieving schema information"
        }, status_code=500)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo_manager.client.server_info()
        return {
            "status": "success",
            "message": "API is healthy",
            "data": {
                "mongodb": "connected",
                "database": DATABASE_NAME
            }
        }
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("🚀 ENTERPRISE MONGODB API")
    print("="*80)
    print(f"🗄️  Database: {DATABASE_NAME}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"📋 Collections: http://localhost:8000/collections")
    print("="*80)
    print("📝 Example Usage:")
    print("  POST /api/user_registration")
    print("  GET  /api/user_registration")
    print("  POST /api/supplier_registration")
    print("  GET  /api/supplier_registration")
    print("="*80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)