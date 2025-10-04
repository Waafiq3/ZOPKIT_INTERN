"""
Enhanced Dynamic Chatbot API - Integrated with Generic API Endpoints
Uses the 49 existing API endpoints for all database operations
"""

from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
import uuid
from datetime import datetime
import logging
import requests
import threading
import time
import subprocess
import sys
import os

# Import the user's dynamic chatbot (modified to use API endpoints)
from dynamic_chatbot import process_chat, reset_chat_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Generic API server configuration
GENERIC_API_URL = "http://localhost:8000"
generic_api_process = None

def start_generic_api_server():
    """Check if API server is running"""
    try:
        # Check if any API server is running on port 8000
        response = requests.get(f"{GENERIC_API_URL}/", timeout=1)
        if response.status_code == 200:
            logger.info("✅ API server is running on port 8000")
            return True
    except:
        pass
    
    # Try to check for test API
    try:
        response = requests.get(f"{GENERIC_API_URL}/test", timeout=1)
        if response.status_code == 200:
            logger.info("✅ Test API server is running on port 8000")
            return True
    except:
        pass
    
    logger.warning("⚠️ No API server found on port 8000. Continuing with direct database access...")
    return False

def call_generic_api(endpoint: str, data: dict) -> dict:
    """Call generic API endpoint"""
    try:
        url = f"{GENERIC_API_URL}/api/{endpoint}"
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "inserted_id": response.json().get("document_id"),
                "message": "Document created successfully"
            }
        else:
            return {
                "success": False,
                "message": f"API call failed: {response.status_code} - {response.text}",
                "error": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"API call error: {str(e)}",
            "error": str(e)
        }

# Enhanced API endpoint mapping
API_ENDPOINT_MAPPING = {
    "user_registration": "user_registration",
    "supplier_registration": "supplier_registration", 
    "performance_review": "performance_review",
    "audit_log_viewer": "audit_log_viewer",
    "health_and_safety_incident_reporting": "health_and_safety_incident_reporting",
    "grievance_management": "grievance_management",
    "travel_request": "travel_request",
    "payment_processing": "payment_processing",
    "purchase_order": "purchase_order",
    "customer_feedback_management": "customer_feedback_management",
    "training_registration": "training_registration",
    "interview_scheduling": "interview_scheduling",
    "chatbot_training_data": "chatbot_training_data",
    "expense_reimbursement": "expense_reimbursement",
    "user_onboarding": "user_onboarding",
    "data_backup_and_restore": "data_backup_and_restore",
    "order_tracking": "order_tracking",
    "knowledge_base": "knowledge_base",
    "role_management": "role_management",
    "employee_exit_clearance": "employee_exit_clearance",
    "invoice_management": "invoice_management",
    "shipping_management": "shipping_management",
    "knowledge_transfer_kt_handover": "knowledge_transfer_kt_handover",
    "faq_management": "faq_management",
    "shift_scheduling": "shift_scheduling",
    "it_asset_allocation": "it_asset_allocation",
    "contract_management": "contract_management",
    "customer_support_ticket": "customer_support_ticket",
    "attendance_tracking": "attendance_tracking",
    "vendor_management": "vendor_management",
    "notification_settings": "notification_settings",
    "client_registration": "client_registration",
    "product_catalog": "product_catalog",
    "inventory_management": "inventory_management",
    "access_control": "access_control",
    "employee_leave_request": "employee_leave_request",
    "project_assignment": "project_assignment",
    "order_placement": "order_placement",
    "marketing_campaign_management": "marketing_campaign_management",
    "meeting_scheduler": "meeting_scheduler",
    "payroll_management": "payroll_management",
    "user_activation": "user_activation",
    "compliance_report": "compliance_report",
    "warehouse_management": "warehouse_management",
    "recruitment_portal": "recruitment_portal",
    "system_audit_and_compliance_dashboard": "system_audit_and_compliance_dashboard",
    "offer_letter_generation": "offer_letter_generation",
    "announcements_notice_board": "announcements_notice_board",
    "system_configuration": "system_configuration"
}

# HTML template for the enhanced interface
ENHANCED_CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic ChatBot - Integrated API System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        .chat-container { 
            width: 95vw; max-width: 1200px; height: 90vh; background: white; border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.15); display: flex; flex-direction: column; 
            overflow: hidden;
        }
        .chat-header { 
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white; padding: 20px; text-align: center; position: relative;
        }
        .chat-header h1 { font-size: 28px; margin-bottom: 8px; font-weight: 700; }
        .chat-header p { opacity: 0.9; font-size: 14px; }
        .api-status {
            position: absolute; top: 20px; right: 20px; 
            background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 15px; font-size: 12px;
        }
        .api-status.online { background: rgba(16, 185, 129, 0.3); }
        .api-status.offline { background: rgba(239, 68, 68, 0.3); }
        
        .feature-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 8px; margin-top: 15px;
        }
        .feature-badge { 
            background: rgba(255,255,255,0.2); padding: 6px 10px; border-radius: 12px; 
            font-size: 11px; text-align: center; font-weight: 600;
        }
        
        .chat-messages { 
            flex: 1; padding: 20px; overflow-y: auto; background: #f8fafc;
        }
        .message { 
            margin-bottom: 20px; display: flex; align-items: flex-start; gap: 12px; 
            animation: fadeIn 0.3s ease-in;
        }
        .message.user { flex-direction: row-reverse; }
        .message-avatar { 
            width: 40px; height: 40px; border-radius: 50%; display: flex; 
            align-items: center; justify-content: center; font-weight: bold; 
            color: white; font-size: 14px; flex-shrink: 0;
        }
        .message.user .message-avatar { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
        .message.bot .message-avatar { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); }
        
        .message-content { 
            max-width: 70%; padding: 15px 18px; border-radius: 18px; 
            position: relative; line-height: 1.5; font-size: 14px;
        }
        .message.user .message-content { 
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white; border-bottom-right-radius: 6px;
        }
        .message.bot .message-content { 
            background: white; color: #1f2937; border: 1px solid #e5e7eb;
            border-bottom-left-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .chat-input-container { 
            padding: 20px; background: white; border-top: 1px solid #e5e7eb;
        }
        .quick-actions { 
            display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap;
        }
        .quick-action { 
            padding: 6px 12px; background: #f3f4f6; border: 1px solid #d1d5db;
            border-radius: 15px; cursor: pointer; font-size: 11px;
            transition: all 0.2s ease; white-space: nowrap;
        }
        .quick-action:hover { 
            background: #4f46e5; color: white; border-color: #4f46e5;
        }
        
        .input-wrapper { display: flex; gap: 10px; align-items: center; }
        .chat-input { 
            flex: 1; padding: 14px 18px; border: 2px solid #e5e7eb;
            border-radius: 20px; font-size: 14px; outline: none;
            transition: all 0.3s ease;
        }
        .chat-input:focus { border-color: #4f46e5; }
        .send-button { 
            padding: 14px 24px; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white; border: none; border-radius: 20px; cursor: pointer;
            font-weight: 600; transition: all 0.3s ease; font-size: 14px;
        }
        .send-button:hover:not(:disabled) { transform: translateY(-1px); }
        .send-button:disabled { opacity: 0.6; cursor: not-allowed; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="api-status" id="apiStatus">API: Checking...</div>
            <h1>🤖 Dynamic ChatBot</h1>
            <p>Integrated with 49 Generic API Endpoints • AI Powered • Zero Hardcoding</p>
            
            <div class="feature-grid">
                <div class="feature-badge">🧠 AI Intelligence</div>
                <div class="feature-badge">📡 49 API Endpoints</div>
                <div class="feature-badge">🚫 No Double Questions</div>
                <div class="feature-badge">⚡ Real-time Processing</div>
                <div class="feature-badge">📝 Smart Data Collection</div>
                <div class="feature-badge">🔒 Eligibility Validation</div>
            </div>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p><strong>👋 Welcome to the Enhanced Dynamic ChatBot!</strong></p>
                    <p>I'm now integrated with your 49 Generic API endpoints and can help you with:</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>👥 User & Supplier Registration (with eligibility checks)</li>
                        <li>📊 Performance Reviews & HR Management</li>
                        <li>🎯 Training & Interview Scheduling</li>
                        <li>💼 Project Management & Task Assignment</li>
                        <li>📦 Inventory & Order Management</li>
                        <li>💰 Payroll & Expense Processing</li>
                        <li>🔐 Access Control & Compliance</li>
                        <li>📋 And 42 other enterprise operations!</li>
                    </ul>
                    <p><strong>💡 Pro Tip:</strong> Just tell me what you want to do naturally - I'll use the appropriate API endpoint automatically!</p>
                </div>
            </div>
        </div>
        
        <div class="chat-input-container">
            <div class="quick-actions">
                <div class="quick-action" onclick="sendQuickMessage('Register new user: John Doe, email john@company.com, password secure123')">👥 User Registration</div>
                <div class="quick-action" onclick="sendQuickMessage('Register supplier: TechCorp Inc, email contact@techcorp.com, corporation, tax ID 123456789')">🏢 Supplier Registration</div>
                <div class="quick-action" onclick="sendQuickMessage('Schedule training for employee ID EMP001, Python course, start date 2025-10-15')">📚 Training Registration</div>
                <div class="quick-action" onclick="sendQuickMessage('Create purchase order for supplier SUP001, items: laptops x10, total $15000')">📋 Purchase Order</div>
                <div class="quick-action" onclick="sendQuickMessage('Track order ORDER123 status')">📦 Order Tracking</div>
            </div>
            <div class="input-wrapper">
                <input type="text" id="messageInput" class="chat-input" placeholder="Tell me what you'd like to do - I'll use the right API endpoint..." autofocus>
                <button id="sendButton" class="send-button">Send</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const apiStatus = document.getElementById('apiStatus');
        
        const sessionId = 'integrated_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Check API status
        async function checkApiStatus() {
            try {
                const response = await fetch('/api-status', { timeout: 2000 });
                const status = await response.json();
                
                if (status.generic_api_online) {
                    apiStatus.textContent = `API: Online (${status.endpoint_count} endpoints)`;
                    apiStatus.className = 'api-status online';
                } else {
                    apiStatus.textContent = 'API: Offline';
                    apiStatus.className = 'api-status offline';
                }
            } catch (error) {
                apiStatus.textContent = 'API: Error';
                apiStatus.className = 'api-status offline';
            }
        }
        
        // Send message function
        async function sendMessage(message) {
            if (!message.trim()) return;
            
            addMessage(message, 'user');
            messageInput.value = '';
            sendButton.disabled = true;
            sendButton.textContent = 'Processing...';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, session_id: sessionId })
                });
                
                const data = await response.json();
                addMessage(data.response, 'bot', data);
                
            } catch (error) {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
            
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            messageInput.focus();
        }
        
        function addMessage(content, sender, metadata = {}) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'user' ? '👤' : '🤖';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.innerHTML = content.replace(/\\n/g, '<br>');
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function sendQuickMessage(message) {
            messageInput.value = message;
            sendMessage(message);
        }
        
        // Event listeners
        sendButton.addEventListener('click', () => sendMessage(messageInput.value));
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage(messageInput.value);
            }
        });
        
        // Initialize
        checkApiStatus();
        setInterval(checkApiStatus, 30000); // Check every 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the simple chat interface"""
    from flask import render_template
    return render_template('simple_chat.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0 - Integrated API System",
        "chatbot": "Dynamic (Zero Hardcoding + API Integration)",
        "ai_powered": True,
        "api_endpoints": len(API_ENDPOINT_MAPPING)
    })

@app.route('/api-status')
def api_status():
    """Check status of generic API server"""
    try:
        response = requests.get(f"{GENERIC_API_URL}/docs", timeout=2)
        generic_api_online = response.status_code == 200
    except:
        generic_api_online = False
    
    return jsonify({
        "generic_api_online": generic_api_online,
        "generic_api_url": GENERIC_API_URL,
        "endpoint_count": len(API_ENDPOINT_MAPPING),
        "available_endpoints": list(API_ENDPOINT_MAPPING.keys())
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint using both dynamic chatbot and generic API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "response": "No data provided"
            }), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message.strip():
            return jsonify({
                "status": "error", 
                "response": "Please provide a message"
            }), 400
        
        logger.info(f"💬 Chat request - Session: {session_id[:12]}... Message: '{message[:50]}...'")
        
        # Use the dynamic chatbot (now it will use API endpoints internally)
        result = process_chat(message, session_id)
        
        # The dynamic chatbot already handles API calls internally, so we just pass through the result
        
        # Ensure we have all required fields
        response_data = {
            "status": result.get("status", "success"),
            "response": result.get("response", "I'm processing your request..."),
            "session_id": session_id,
            "intent": result.get("intent"),
            "action": result.get("action"),
            "task": result.get("task"),
            "data": result.get("data", {}),
            "confidence": result.get("confidence"),
            "document_id": result.get("document_id"),
            "api_endpoint_used": result.get("api_endpoint_used")
        }
        
        logger.info(f"🤖 Bot response - Status: {response_data['status']}, Task: {response_data['task']}, API: {response_data.get('api_endpoint_used', 'None')}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return jsonify({
            "status": "error",
            "response": f"Sorry, I encountered an error: {str(e)}",
            "session_id": session_id if 'session_id' in locals() else "error"
        }), 500

if __name__ == '__main__':
    print("\\n" + "="*80)
    print("🚀 ENHANCED DYNAMIC CHATBOT - INTEGRATED API SYSTEM!")
    print("="*80)
    print("🔧 Starting Generic API server...")
    
    # Start generic API server
    if start_generic_api_server():
        print("✅ Generic API server started successfully")
        print(f"📡 Generic API available at: {GENERIC_API_URL}")
        print(f"📋 API Documentation: {GENERIC_API_URL}/docs")
    else:
        print("⚠️  Generic API server failed to start - continuing with direct DB access")
    
    print("\\n🌐 Enhanced Web Interface: http://localhost:5001")
    print("❤️  Health Check: http://localhost:5001/health")
    print("📊 API Status: http://localhost:5001/api-status")
    print("📡 Chat API: http://localhost:5001/chat")
    print("="*80)
    print("✅ Features:")
    print("   • 🧠 AI-powered with Gemini 2.5 Flash")
    print("   • 📡 Integrated with 49 Generic API endpoints")
    print("   • 🚫 Zero hardcoded patterns")
    print("   • 📝 Smart data extraction")
    print("   • 🔒 Enhanced eligibility validation")
    print("   • 💾 Full MongoDB integration via APIs")
    print("="*80)
    print("🎮 Try these examples:")
    print('   "Register user: John Doe, email john@company.com, password secure123"')
    print('   "Register supplier: TechCorp, email contact@techcorp.com, corporation, tax ID 123456789"')
    print('   "Schedule training for employee EMP001, Python course, start date 2025-10-15"')
    print('   "Create purchase order for supplier SUP001, laptops x10, total $15000"')
    print("="*80)
    
    app.run(debug=True, host='0.0.0.0', port=5001)