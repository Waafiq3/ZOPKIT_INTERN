"""
Enhanced Purchase Order API Integration
Extends the existing API with purchase order specific functionality
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Import existing API integration
from api_integration import app as api_app
from dynamic_chatbot import DynamicChatBot

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize chatbot for communication mode
chatbot = DynamicChatBot()

@app.route('/')
def index():
    """Serve the purchase order interface"""
    return send_from_directory('.', 'purchase_order_interface.html')

@app.route('/api/purchase_order/chat', methods=['POST'])
def purchase_order_chat():
    """Handle chat-based purchase order creation"""
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', 'purchase_order_session')
        
        if not message:
            return jsonify({
                "status": "error",
                "message": "Please provide a message"
            }), 400
        
        # Process message through chatbot
        result = chatbot.process_message(message, session_id)
        
        return jsonify({
            "status": "success",
            "response": result.get("response", ""),
            "data": result.get("data", {}),
            "task": result.get("task"),
            "intent": result.get("intent"),
            "action": result.get("action", ""),
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Chat processing failed: {str(e)}"
        }), 500

@app.route('/api/purchase_order/validate', methods=['POST'])
def validate_purchase_order():
    """Validate purchase order data"""
    try:
        data = request.json
        
        required_fields = ['supplier_id', 'order_date', 'total_amount', 'items']
        errors = {}
        
        # Check required fields
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required"
        
        # Specific validations
        if data.get('supplier_id') and not data['supplier_id'].upper().startswith('SUP'):
            errors['supplier_id'] = 'Supplier ID must start with SUP (e.g., SUP001)'
        
        if data.get('total_amount'):
            try:
                amount = float(data['total_amount'])
                if amount <= 0:
                    errors['total_amount'] = 'Total amount must be greater than 0'
            except ValueError:
                errors['total_amount'] = 'Total amount must be a valid number'
        
        if data.get('order_date'):
            try:
                datetime.strptime(data['order_date'], '%Y-%m-%d')
            except ValueError:
                errors['order_date'] = 'Order date must be in YYYY-MM-DD format'
        
        return jsonify({
            "status": "success" if not errors else "error",
            "errors": errors,
            "valid": len(errors) == 0
        })
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Validation failed: {str(e)}"
        }), 500

@app.route('/api/purchase_order/submit', methods=['POST'])
def submit_purchase_order():
    """Submit purchase order (enhanced version of existing API)"""
    try:
        data = request.json
        
        # Auto-generate fields
        if not data.get('po_id'):
            data['po_id'] = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract quantity from items if present
        if 'items' in data and 'quantity' not in data:
            import re
            items_text = str(data.get('items', ''))
            qty_match = re.search(r'x(\\d+)', items_text, re.IGNORECASE)
            if qty_match:
                data['quantity'] = int(qty_match.group(1))
                # Clean items text
                data['items'] = re.sub(r'\\s*x\\d+', '', items_text).strip()
            else:
                data['quantity'] = 1
        
        # Add timestamps
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Call the existing API endpoint
        import requests
        response = requests.post('http://localhost:5000/api/purchase_order', 
                               json=data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            return jsonify({
                "status": "success",
                "message": "Purchase order created successfully",
                "po_id": data['po_id'],
                "id": result.get('id'),
                "data": data
            })
        else:
            # Fallback to direct database if API fails
            from api_integration import api_insert_document
            db_result = api_insert_document('purchase_order', data)
            
            if db_result.get('success'):
                return jsonify({
                    "status": "success",
                    "message": "Purchase order created successfully (via database)",
                    "po_id": data['po_id'],
                    "id": db_result.get('inserted_id'),
                    "data": data
                })
            else:
                raise Exception(db_result.get('error', 'Database insertion failed'))
        
    except Exception as e:
        logger.error(f"Submission error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create purchase order: {str(e)}"
        }), 500

@app.route('/api/purchase_order/templates', methods=['GET'])
def get_purchase_order_templates():
    """Get purchase order templates and examples"""
    templates = {
        "office_supplies": {
            "name": "Office Supplies Order",
            "supplier_id": "SUP001",
            "items": "Laptops x10, Wireless Mice x20, USB Cables x50",
            "total_amount": 15000.00,
            "description": "Monthly office equipment order"
        },
        "furniture": {
            "name": "Office Furniture Order", 
            "supplier_id": "SUP002",
            "items": "Desk Chairs x25, Standing Desks x10, Filing Cabinets x5",
            "total_amount": 25000.00,
            "description": "New office setup furniture"
        },
        "software_licenses": {
            "name": "Software Licenses",
            "supplier_id": "SUP003", 
            "items": "Microsoft Office 365 x100, Adobe Creative Suite x20",
            "total_amount": 8000.00,
            "description": "Annual software license renewal"
        }
    }
    
    return jsonify({
        "status": "success",
        "templates": templates
    })

@app.route('/api/purchase_order/suppliers', methods=['GET'])
def get_suppliers():
    """Get available suppliers"""
    suppliers = [
        {"id": "SUP001", "name": "TechCorp Solutions", "category": "Electronics"},
        {"id": "SUP002", "name": "Office Furniture Ltd", "category": "Furniture"},
        {"id": "SUP003", "name": "Software Solutions Inc", "category": "Software"},
        {"id": "SUP004", "name": "Stationery World", "category": "Office Supplies"},
        {"id": "SUP005", "name": "Industrial Equipment Co", "category": "Equipment"}
    ]
    
    return jsonify({
        "status": "success",
        "suppliers": suppliers
    })

@app.route('/api/purchase_order/history', methods=['GET'])
def get_purchase_order_history():
    """Get purchase order history"""
    try:
        # Try to fetch from API first
        import requests
        response = requests.get('http://localhost:5000/api/purchase_order', timeout=10)
        
        if response.status_code == 200:
            api_data = response.json()
            return jsonify({
                "status": "success",
                "orders": api_data.get('data', []),
                "count": api_data.get('count', 0)
            })
        else:
            # Fallback to direct database query
            from db import get_database
            db = get_database()
            collection = db['purchase_order']
            
            orders = list(collection.find().sort('created_at', -1).limit(50))
            
            # Convert ObjectId to string
            for order in orders:
                order['_id'] = str(order['_id'])
            
            return jsonify({
                "status": "success", 
                "orders": orders,
                "count": len(orders)
            })
            
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch purchase order history: {str(e)}"
        }), 500

@app.route('/api/purchase_order/stats', methods=['GET'])
def get_purchase_order_stats():
    """Get purchase order statistics"""
    try:
        from db import get_database
        db = get_database()
        collection = db['purchase_order']
        
        # Get basic stats
        total_orders = collection.count_documents({})
        pending_orders = collection.count_documents({"status": "pending"})
        approved_orders = collection.count_documents({"status": "approved"})
        
        # Get total amount (aggregate)
        pipeline = [
            {"$group": {
                "_id": None,
                "total_amount": {"$sum": {"$toDouble": "$total_amount"}}
            }}
        ]
        
        amount_result = list(collection.aggregate(pipeline))
        total_amount = amount_result[0]['total_amount'] if amount_result else 0
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "approved_orders": approved_orders,
                "total_amount": total_amount,
                "completion_rate": round((approved_orders / total_orders * 100) if total_orders > 0 else 0, 2)
            }
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch statistics: {str(e)}"
        }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check for purchase order API"""
    return jsonify({
        "status": "healthy",
        "service": "Purchase Order API",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Chat Mode",
            "Form Mode", 
            "Validation",
            "Templates",
            "History",
            "Statistics"
        ]
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🛒 PURCHASE ORDER INTERFACE SERVER")
    print("=" * 80)
    print("🌐 Main Interface: http://localhost:8080/")
    print("💬 Chat API: POST /api/purchase_order/chat")
    print("✅ Validation API: POST /api/purchase_order/validate") 
    print("📋 Submit API: POST /api/purchase_order/submit")
    print("📊 Templates API: GET /api/purchase_order/templates")
    print("🏢 Suppliers API: GET /api/purchase_order/suppliers")
    print("📈 History API: GET /api/purchase_order/history")
    print("📊 Stats API: GET /api/purchase_order/stats")
    print("🔧 Health Check: GET /health")
    print("=" * 80)
    print("🎯 Features:")
    print("  • Dual Mode Interface (Chat + Form)")
    print("  • Real-time Validation")
    print("  • Auto-generation of PO IDs")
    print("  • Integration with Existing API")
    print("  • Fallback to Direct Database")
    print("  • Purchase Order Templates")
    print("  • Supplier Management")
    print("  • Order History & Statistics")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=8080)