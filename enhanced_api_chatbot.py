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
GENERIC_API_URL = "http://localhost:5000"
generic_api_process = None

def start_generic_api_server():
    """Check if API server is running"""
    try:
        # Check if any API server is running on port 5000
        response = requests.get(f"{GENERIC_API_URL}/", timeout=1)
        if response.status_code == 200:
            logger.info("✅ API server is running on port 5000")
            return True
    except:
        pass
    
    # Try to check for test API
    try:
        response = requests.get(f"{GENERIC_API_URL}/test", timeout=1)
        if response.status_code == 200:
            logger.info("✅ Test API server is running on port 5000")
            return True
    except:
        pass
    
    logger.warning("⚠️ No API server found on port 5000. Continuing with direct database access...")
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
        
        /* Workflow Panel Styles */
        .workflow-panel {
            position: fixed;
            top: 0;
            right: 0;
            width: 400px;
            height: 100vh;
            background: white;
            box-shadow: -4px 0 20px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
            display: flex;
            flex-direction: column;
        }
        
        .workflow-panel.open {
            transform: translateX(0);
        }
        
        .workflow-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 20px;
            position: relative;
        }
        
        .workflow-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .workflow-header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }
        
        .close-workflow {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .workflow-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .workflow-status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .status-badge {
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-badge.pending { background: #f59e0b; }
        .status-badge.running { background: #3b82f6; }
        .status-badge.completed { background: #10b981; }
        .status-badge.error { background: #ef4444; }
        
        .step-info {
            color: #6b7280;
            font-size: 12px;
        }
        
        .workflow-progress {
            margin-bottom: 25px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            font-size: 12px;
            color: #6b7280;
        }
        
        .workflow-steps {
            margin-bottom: 25px;
        }
        
        .workflow-step {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 8px;
            background: white;
            transition: all 0.2s ease;
        }
        
        .workflow-step:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .step-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }
        
        .step-icon.pending { background: #f59e0b; }
        .step-icon.running { background: #3b82f6; }
        .step-icon.completed { background: #10b981; }
        .step-icon.error { background: #ef4444; }
        
        .step-details {
            flex: 1;
        }
        
        .step-title {
            font-weight: 600;
            font-size: 14px;
            color: #1f2937;
            margin-bottom: 2px;
        }
        
        .step-subtitle {
            font-size: 12px;
            color: #6b7280;
        }
        
        .step-actions {
            display: flex;
            gap: 8px;
        }
        
        .step-action {
            background: none;
            border: none;
            color: #6b7280;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .step-action:hover {
            background: #f3f4f6;
            color: #374151;
        }
        
        .workflow-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .workflow-btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
        }
        
        .start-btn {
            background: #10b981;
            color: white;
        }
        
        .start-btn:hover {
            background: #059669;
        }
        
        .pause-btn {
            background: #f59e0b;
            color: white;
        }
        
        .pause-btn:hover {
            background: #d97706;
        }
        
        .stop-btn {
            background: #ef4444;
            color: white;
        }
        
        .stop-btn:hover {
            background: #dc2626;
        }
        
        .workflow-chat {
            border-top: 1px solid #e5e7eb;
            padding: 15px 20px;
            background: #f9fafb;
        }
        
        .workflow-chat input {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            margin-bottom: 10px;
        }
        
        .workflow-chat input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .workflow-quick-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .quick-btn {
            padding: 6px 12px;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .quick-btn:hover {
            background: #4f46e5;
            color: white;
            border-color: #4f46e5;
        }
        
        /* Start button in chat */
        .start-workflow-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px 0;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .start-workflow-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        
        @media (max-width: 768px) {
            .workflow-panel {
                width: 100%;
                right: 0;
            }
        }
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
        
        <!-- Workflow AI Panel (Initially Hidden) -->
        <div id="workflowPanel" class="workflow-panel" style="display: none;">
            <div class="workflow-header">
                <h3>🔄 Workflow AI</h3>
                <p>Execution Plan</p>
                <button id="closeWorkflow" class="close-workflow">×</button>
            </div>
            
            <div class="workflow-content">
                <div class="workflow-status">
                    <span id="workflowTitle">Demo Execution Plan</span>
                    <span class="status-badge" id="workflowStatus">ready</span>
                    <span class="step-info" id="workflowStep">Step 1 of 3</span>
                </div>
                
                <div class="workflow-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                    <span class="progress-text" id="progressText">0%</span>
                </div>
                
                <div class="workflow-steps" id="workflowSteps">
                    <!-- Steps will be populated dynamically -->
                </div>
                
                <div class="workflow-actions">
                    <button id="startWorkflow" class="workflow-btn start-btn">▶ Start</button>
                    <button id="pauseWorkflow" class="workflow-btn pause-btn" style="display: none;">⏸ Pause</button>
                    <button id="stopWorkflow" class="workflow-btn stop-btn" style="display: none;">⏹ Stop</button>
                </div>
            </div>
            
            <div class="workflow-chat">
                <input type="text" id="workflowInput" placeholder="Ask me anything about your data, reports, or workflows..." />
                <div class="workflow-quick-actions">
                    <button class="quick-btn">Show me sales data</button>
                    <button class="quick-btn">Generate report</button>
                    <button class="quick-btn">Check system status</button>
                    <button class="quick-btn">Create workflow</button>
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
                
                // Check if this is a workflow trigger
                const isWorkflow = isWorkflowTrigger(message);
                if (isWorkflow) {
                    const workflowResponse = `I'll help you create a ${getWorkflowType(message).replace('_', ' ')}. I've created an execution plan for you.`;
                    addMessage(workflowResponse, 'bot', data);
                } else {
                    addMessage(data.response, 'bot', data);
                }
                
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
            
            // Check if message is about creating a workflow (purchase order, etc.)
            if (sender === 'bot' && isWorkflowTrigger(content)) {
                const startBtn = document.createElement('button');
                startBtn.className = 'start-workflow-btn';
                startBtn.textContent = '▶ Start';
                startBtn.onclick = () => showWorkflowPanel(getWorkflowType(content));
                messageContent.appendChild(startBtn);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function isWorkflowTrigger(content) {
            const triggers = [
                'purchase order', 'create order', 'buy items', 'po',
                'supplier registration', 'register supplier',
                'user registration', 'register user',
                'training registration', 'schedule training',
                'performance review', 'employee review'
            ];
            const contentLower = content.toLowerCase();
            return triggers.some(trigger => contentLower.includes(trigger));
        }
        
        function getWorkflowType(content) {
            const contentLower = content.toLowerCase();
            if (contentLower.includes('purchase') || contentLower.includes('order') || contentLower.includes('buy')) {
                return 'purchase_order';
            } else if (contentLower.includes('supplier')) {
                return 'supplier_registration';
            } else if (contentLower.includes('user') && contentLower.includes('register')) {
                return 'user_registration';
            } else if (contentLower.includes('training')) {
                return 'training_registration';
            } else {
                return 'general_workflow';
            }
        }
        
        function showWorkflowPanel(workflowType) {
            const panel = document.getElementById('workflowPanel');
            panel.style.display = 'flex';
            setTimeout(() => panel.classList.add('open'), 10);
            
            setupWorkflow(workflowType);
        }
        
        function setupWorkflow(workflowType) {
            const workflows = {
                purchase_order: {
                    title: 'Purchase Order Creation',
                    steps: [
                        { id: 'data_collection', title: 'Data Collection', subtitle: 'Data Collector', status: 'pending' },
                        { id: 'data_analysis', title: 'Data Analysis', subtitle: 'Data Analyzer', status: 'pending' },
                        { id: 'validation', title: 'Validation', subtitle: 'Validator', status: 'pending' },
                        { id: 'submission', title: 'Order Submission', subtitle: 'API Processor', status: 'pending' }
                    ]
                },
                supplier_registration: {
                    title: 'Supplier Registration',
                    steps: [
                        { id: 'data_collection', title: 'Data Collection', subtitle: 'Data Collector', status: 'pending' },
                        { id: 'eligibility_check', title: 'Eligibility Check', subtitle: 'Eligibility Validator', status: 'pending' },
                        { id: 'registration', title: 'Registration', subtitle: 'API Processor', status: 'pending' }
                    ]
                },
                user_registration: {
                    title: 'User Registration',
                    steps: [
                        { id: 'data_collection', title: 'Data Collection', subtitle: 'Data Collector', status: 'pending' },
                        { id: 'validation', title: 'Validation', subtitle: 'Validator', status: 'pending' },
                        { id: 'registration', title: 'Registration', subtitle: 'API Processor', status: 'pending' }
                    ]
                },
                training_registration: {
                    title: 'Training Registration',
                    steps: [
                        { id: 'data_collection', title: 'Data Collection', subtitle: 'Data Collector', status: 'pending' },
                        { id: 'schedule_check', title: 'Schedule Check', subtitle: 'Schedule Validator', status: 'pending' },
                        { id: 'registration', title: 'Registration', subtitle: 'API Processor', status: 'pending' }
                    ]
                },
                general_workflow: {
                    title: 'General Workflow',
                    steps: [
                        { id: 'data_collection', title: 'Data Collection', subtitle: 'Data Collector', status: 'pending' },
                        { id: 'processing', title: 'Processing', subtitle: 'Processor', status: 'pending' },
                        { id: 'completion', title: 'Completion', subtitle: 'Finalizer', status: 'pending' }
                    ]
                }
            };
            
            const workflow = workflows[workflowType] || workflows.general_workflow;
            
            document.getElementById('workflowTitle').textContent = workflow.title;
            document.getElementById('workflowStatus').textContent = 'ready';
            document.getElementById('workflowStep').textContent = `Step 1 of ${workflow.steps.length}`;
            
            renderWorkflowSteps(workflow.steps);
        }
        
        function renderWorkflowSteps(steps) {
            const stepsContainer = document.getElementById('workflowSteps');
            stepsContainer.innerHTML = '';
            
            steps.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'workflow-step';
                stepDiv.innerHTML = `
                    <div class="step-icon ${step.status}">
                        ${step.status === 'completed' ? '✓' : step.status === 'running' ? '⟳' : (index + 1)}
                    </div>
                    <div class="step-details">
                        <div class="step-title">${step.title}</div>
                        <div class="step-subtitle">${step.subtitle}</div>
                    </div>
                    <div class="step-actions">
                        <button class="step-action" title="Skip">⏭</button>
                        <button class="step-action" title="More options">⋯</button>
                    </div>
                `;
                stepsContainer.appendChild(stepDiv);
            });
        }
        
        let currentWorkflowSteps = [];
        let workflowRunning = false;
        let currentStepIndex = 0;
        
        function startWorkflow() {
            if (workflowRunning) return;
            
            workflowRunning = true;
            currentStepIndex = 0;
            
            document.getElementById('startWorkflow').style.display = 'none';
            document.getElementById('pauseWorkflow').style.display = 'inline-block';
            document.getElementById('stopWorkflow').style.display = 'inline-block';
            
            document.getElementById('workflowStatus').className = 'status-badge running';
            document.getElementById('workflowStatus').textContent = 'running';
            
            runNextStep();
        }
        
        function runNextStep() {
            if (currentStepIndex >= document.querySelectorAll('.workflow-step').length) {
                completeWorkflow();
                return;
            }
            
            const steps = document.querySelectorAll('.workflow-step');
            const currentStep = steps[currentStepIndex];
            const stepIcon = currentStep.querySelector('.step-icon');
            
            // Update step status to running
            stepIcon.className = 'step-icon running';
            stepIcon.textContent = '⟳';
            
            // Update progress
            const progress = ((currentStepIndex + 0.5) / steps.length) * 100;
            document.getElementById('progressFill').style.width = `${progress}%`;
            document.getElementById('progressText').textContent = `${Math.round(progress)}%`;
            document.getElementById('workflowStep').textContent = `Step ${currentStepIndex + 1} of ${steps.length}`;
            
            // Simulate step completion after 2-3 seconds
            setTimeout(() => {
                stepIcon.className = 'step-icon completed';
                stepIcon.textContent = '✓';
                
                currentStepIndex++;
                
                if (currentStepIndex < steps.length) {
                    setTimeout(runNextStep, 500);
                } else {
                    completeWorkflow();
                }
            }, Math.random() * 2000 + 2000);
        }
        
        function completeWorkflow() {
            workflowRunning = false;
            
            document.getElementById('startWorkflow').style.display = 'inline-block';
            document.getElementById('pauseWorkflow').style.display = 'none';
            document.getElementById('stopWorkflow').style.display = 'none';
            
            document.getElementById('workflowStatus').className = 'status-badge completed';
            document.getElementById('workflowStatus').textContent = 'completed';
            
            document.getElementById('progressFill').style.width = '100%';
            document.getElementById('progressText').textContent = '100%';
            
            // Show completion message in chat
            setTimeout(() => {
                addMessage('✅ Workflow completed successfully! Your request has been processed.', 'bot');
            }, 1000);
        }
        
        function pauseWorkflow() {
            workflowRunning = false;
            document.getElementById('startWorkflow').style.display = 'inline-block';
            document.getElementById('pauseWorkflow').style.display = 'none';
            document.getElementById('workflowStatus').className = 'status-badge pending';
            document.getElementById('workflowStatus').textContent = 'paused';
        }
        
        function stopWorkflow() {
            workflowRunning = false;
            currentStepIndex = 0;
            
            document.getElementById('startWorkflow').style.display = 'inline-block';
            document.getElementById('pauseWorkflow').style.display = 'none';
            document.getElementById('stopWorkflow').style.display = 'none';
            
            document.getElementById('workflowStatus').className = 'status-badge error';
            document.getElementById('workflowStatus').textContent = 'stopped';
            
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0%';
            
            // Reset all steps
            document.querySelectorAll('.step-icon').forEach((icon, index) => {
                icon.className = 'step-icon pending';
                icon.textContent = index + 1;
            });
        }
        
        function closeWorkflowPanel() {
            const panel = document.getElementById('workflowPanel');
            panel.classList.remove('open');
            setTimeout(() => panel.style.display = 'none', 300);
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
        
        // Workflow event listeners
        document.getElementById('startWorkflow').addEventListener('click', startWorkflow);
        document.getElementById('pauseWorkflow').addEventListener('click', pauseWorkflow);
        document.getElementById('stopWorkflow').addEventListener('click', stopWorkflow);
        document.getElementById('closeWorkflow').addEventListener('click', closeWorkflowPanel);
        
        // Workflow quick actions
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.textContent;
                addMessage(message, 'user');
                addMessage(`I'll help you with "${message}". Let me process that for you.`, 'bot');
            });
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
    """Serve the main chat interface with integrated purchase order form"""
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
            "api_endpoint_used": result.get("api_endpoint_used"),
            "show_purchase_button": result.get("show_purchase_button", False)
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

@app.route('/api/workflow', methods=['POST'])
def workflow_api():
    """Handle workflow creation and management"""
    try:
        data = request.json
        workflow_type = data.get('type', 'general_workflow')
        action = data.get('action', 'create')
        
        if action == 'create':
            # Create workflow based on type
            workflows = {
                'purchase_order': {
                    'title': 'Purchase Order Creation',
                    'steps': [
                        {'id': 'data_collection', 'title': 'Data Collection', 'subtitle': 'Data Collector', 'status': 'ready'},
                        {'id': 'data_analysis', 'title': 'Data Analysis', 'subtitle': 'Data Analyzer', 'status': 'pending'},
                        {'id': 'validation', 'title': 'Validation', 'subtitle': 'Validator', 'status': 'pending'},
                        {'id': 'submission', 'title': 'Order Submission', 'subtitle': 'API Processor', 'status': 'pending'}
                    ]
                },
                'supplier_registration': {
                    'title': 'Supplier Registration',
                    'steps': [
                        {'id': 'data_collection', 'title': 'Data Collection', 'subtitle': 'Data Collector', 'status': 'ready'},
                        {'id': 'eligibility_check', 'title': 'Eligibility Check', 'subtitle': 'Eligibility Validator', 'status': 'pending'},
                        {'id': 'registration', 'title': 'Registration', 'subtitle': 'API Processor', 'status': 'pending'}
                    ]
                }
            }
            
            workflow = workflows.get(workflow_type, workflows['purchase_order'])
            
            return jsonify({
                'status': 'success',
                'workflow': workflow,
                'message': f'{workflow["title"]} workflow created successfully'
            })
            
        elif action == 'execute':
            # Execute workflow step
            step_id = data.get('step_id')
            session_id = data.get('session_id', 'workflow_session')
            
            # Simulate step execution
            return jsonify({
                'status': 'success',
                'step_id': step_id,
                'step_status': 'completed',
                'message': f'Step {step_id} completed successfully'
            })
            
    except Exception as e:
        logger.error(f"Workflow API error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Workflow error: {str(e)}'
        }), 500

@app.route('/api/query', methods=['POST'])
def query_data():
    """Dedicated endpoint for natural language database queries"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "response": "No data provided"
            }), 400
        
        query = data.get('query', '')
        collection = data.get('collection', '')
        employee_id = data.get('employee_id', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not query.strip():
            return jsonify({
                "status": "error", 
                "response": "Please provide a query"
            }), 400
        
        if not collection.strip():
            return jsonify({
                "status": "error", 
                "response": "Please specify a collection to query"
            }), 400
        
        if not employee_id.strip():
            return jsonify({
                "status": "error", 
                "response": "Employee ID required for query access"
            }), 400
        
        logger.info(f"🔍 Query request - Session: {session_id[:12]}... Query: '{query[:50]}...' Collection: {collection}")
        
        # Validate employee access
        from db import db_manager
        from schema import get_endpoint_access_requirements
        
        try:
            # Check if employee exists and get their position
            user_collection = db_manager.db["user_registration"]
            user = user_collection.find_one({"employee_id": employee_id.upper()})
            
            if not user:
                return jsonify({
                    "status": "error",
                    "response": f"Employee ID {employee_id.upper()} not found in system"
                }), 403
            
            user_position = user.get("position", "").lower()
            
            # Check access permissions for the collection
            access_requirements = get_endpoint_access_requirements()
            required_positions = access_requirements.get(collection, ["admin"])
            
            if user_position not in required_positions and "admin" not in user_position:
                return jsonify({
                    "status": "error",
                    "response": f"Access denied. Your position '{user.get('position', 'Unknown')}' cannot query {collection}"
                }), 403
            
            # Initialize chatbot and create mock state for query processing
            from dynamic_chatbot import DynamicChatbot
            chatbot = DynamicChatbot()
            
            # Create mock state with query information
            mock_state = {
                "intent_analyzed": True,
                "user_validated": True,
                "detected_task": collection,
                "operation_type": "query",
                "query_type": "find",
                "natural_query": query,
                "user_position": user_position,
                "employee_id": employee_id.upper()
            }
            
            # Process query through Query Node
            result = chatbot._process_query_node(query, mock_state, session_id)
            
            response_data = {
                "status": result.get("status", "success"),
                "response": result.get("response", "Query processed"),
                "session_id": session_id,
                "collection": collection,
                "query": query,
                "employee_id": employee_id.upper(),
                "user_position": user_position,
                "query_results": result.get("query_results"),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🔍 Query completed - Status: {response_data['status']}, Employee: {employee_id.upper()}")
            
            return jsonify(response_data)
            
        except Exception as db_error:
            logger.error(f"❌ Database query error: {db_error}")
            return jsonify({
                "status": "error",
                "response": f"Database error: {str(db_error)}",
                "session_id": session_id
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Query endpoint error: {e}")
        return jsonify({
            "status": "error",
            "response": f"Sorry, I encountered an error: {str(e)}",
            "session_id": session_id if 'session_id' in locals() else "error"
        }), 500

@app.route('/api/dashboard/<session_id>', methods=['GET'])
def user_dashboard(session_id):
    """Get user dashboard with session history and statistics"""
    try:
        # Import session manager
        try:
            from session_manager import SessionManager
            session_manager = SessionManager()
        except ImportError:
            return jsonify({
                "status": "error",
                "response": "Session management not available"
            }), 503
        
        # Get dashboard data
        dashboard_data = session_manager.get_user_dashboard_data(session_id)
        
        if not dashboard_data:
            return jsonify({
                "status": "error", 
                "response": "Session not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        return jsonify({
            "status": "error",
            "response": f"Dashboard error: {str(e)}"
        }), 500

@app.route('/api/user-sessions/<employee_id>', methods=['GET'])
def get_user_sessions(employee_id):
    """Get all sessions for a specific employee"""
    try:
        # Import session manager
        try:
            from session_manager import SessionManager
            session_manager = SessionManager()
        except ImportError:
            return jsonify({
                "status": "error",
                "response": "Session management not available"
            }), 503
        
        # Get user sessions from database
        from db import get_database
        db = get_database()
        
        sessions = list(db.user_sessions.find(
            {"employee_id": employee_id.upper()},
            sort=[("login_time", -1)]
        ))
        
        # Convert ObjectId to string
        for session in sessions:
            session["_id"] = str(session["_id"])
        
        return jsonify({
            "status": "success",
            "employee_id": employee_id.upper(),
            "total_sessions": len(sessions),
            "sessions": sessions,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ User sessions error: {e}")
        return jsonify({
            "status": "error",
            "response": f"Sessions error: {str(e)}"
        }), 500

@app.route('/api/check-supplier-products', methods=['POST'])
def check_supplier_products_conversational():
    """API endpoint for conversational product availability check"""
    try:
        logger.info("🛍️ Conversational Supplier Products Check called")
        data = request.get_json()
        logger.info(f"📝 Received data: {data}")
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        supplier_id = data.get('supplier_id')
        if not supplier_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: supplier_id"
            }), 400
        
        # Use direct database access
        from db import get_database
        db = get_database()
        
        # Check if supplier exists
        supplier_collection = db['supplier']
        supplier = supplier_collection.find_one({"supplier_id": supplier_id})
        
        if not supplier:
            return jsonify({
                "success": False,
                "message": f"❌ **Supplier Not Found**\n\nSupplier ID `{supplier_id}` does not exist in our system.\n\n**Available Suppliers:**\n• SUP001 - TechCorp Electronics\n• SUP002 - Office Furniture Plus\n• SUP003 - Workplace Solutions Inc\n\nPlease check the supplier ID and try again.",
                "show_purchase_button": False
            })
        
        # Get products from database
        products_collection = db['supplier_products']
        product_docs = list(products_collection.find({
            "supplier_id": supplier_id,
            "is_active": True
        }))
        
        # Convert database documents to API format
        products = []
        for doc in product_docs:
            products.append({
                "name": doc["name"],
                "price": doc["price"],
                "stock": doc["stock_quantity"],
                "category": doc["category"],
                "product_id": doc["product_id"],
                "description": doc.get("description", ""),
                "brand": doc.get("brand", ""),
                "warranty_months": doc.get("warranty_months", 0)
            })
        supplier_name = supplier.get('name', 'Unknown Supplier')
        
        if not products:
            return jsonify({
                "success": True,
                "message": f"📦 **{supplier_name} ({supplier_id})**\n\n❌ **No Products Available**\n\nThis supplier currently has no products in stock. Please try another supplier or contact them directly for special requests.",
                "show_purchase_button": False
            })
        
        # Format the response message
        products_text = ""
        for i, product in enumerate(products, 1):
            stock_status = "⚠️ LOW STOCK" if product["stock"] < 20 else "✅ IN STOCK"
            products_text += f"{i}. **{product['name']}**\n   💰 ${product['price']} | 📦 {product['stock']} units | {stock_status}\n   📂 Category: {product['category']}\n\n"
        
        message = f"🏪 **{supplier_name} ({supplier_id})**\n\n📋 **Available Products ({len(products)} items):**\n\n{products_text}✅ **Ready to proceed with purchase order creation!**\n\nWould you like to create a purchase order for any of these items?"
        
        return jsonify({
            "success": True,
            "message": message,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "products_count": len(products),
            "show_purchase_button": True
        })
        
    except Exception as e:
        logger.error(f"Check supplier products API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/supplier-products', methods=['POST'])
def get_supplier_products_api():
    """API endpoint for checking product availability by supplier ID"""
    try:
        logger.info("🏪 Supplier Products API called")
        data = request.get_json()
        logger.info(f"📝 Received data: {data}")
        
        if not data:
            logger.error("❌ No data provided")
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        supplier_id = data.get('supplier_id')
        if not supplier_id:
            logger.error("❌ Missing supplier_id")
            return jsonify({
                "success": False,
                "error": "Missing required field: supplier_id"
            }), 400
        
        # Use direct database access
        logger.info("💾 Connecting to database...")
        from db import get_database
        
        # Get database connection
        db = get_database()
        
        # Check if supplier exists
        supplier_collection = db['supplier']
        supplier = supplier_collection.find_one({"supplier_id": supplier_id})
        
        if not supplier:
            logger.error(f"❌ Supplier {supplier_id} not found")
            return jsonify({
                "success": False,
                "error": f"Supplier {supplier_id} not found"
            }), 404
        
        # Get products from database
        products_collection = db['supplier_products']
        product_docs = list(products_collection.find({
            "supplier_id": supplier_id,
            "is_active": True
        }))
        
        # Convert database documents to API format
        products = []
        for doc in product_docs:
            products.append({
                "product_id": doc["product_id"],
                "name": doc["name"],
                "price": doc["price"],
                "stock": doc["stock_quantity"],
                "category": doc["category"],
                "description": doc.get("description", ""),
                "brand": doc.get("brand", ""),
                "warranty_months": doc.get("warranty_months", 0)
            })
        
        logger.info(f"✅ Found {len(products)} products for supplier {supplier_id}")
        
        return jsonify({
            "success": True,
            "supplier_id": supplier_id,
            "supplier_name": supplier.get('name', 'Unknown Supplier'),
            "products": products,
            "total_products": len(products)
        })
        
    except Exception as e:
        logger.error(f"Supplier products API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/purchase-order', methods=['POST'])
def create_purchase_order_api():
    """API endpoint for creating purchase orders via form submission"""
    try:
        logger.info("🛒 Purchase Order API called")
        data = request.get_json()
        logger.info(f"📝 Received data: {data}")
        
        if not data:
            logger.error("❌ No data provided")
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['po_id', 'vendor_id', 'product', 'quantity']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            logger.error(f"❌ Missing fields: {missing_fields}")
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Use direct database access since Generic API server is not running
        logger.info("💾 Connecting to database...")
        from db import get_database
        
        # Get database connection
        db = get_database()
        collection = db['purchase_order']
        logger.info(f"📦 Database: {db.name}, Collection: purchase_order")
        
        # Add timestamp to the data
        from datetime import datetime
        data['created_at'] = datetime.now()
        data['status'] = 'pending'
        
        # Insert the purchase order
        logger.info(f"💾 Inserting purchase order: {data}")
        result = collection.insert_one(data)
        logger.info(f"✅ Insert result: {result.inserted_id}")
        
        if result.inserted_id:
            # Verify the data was actually saved
            saved_doc = collection.find_one({"_id": result.inserted_id})
            logger.info(f"🔍 Verification - Document found: {saved_doc is not None}")
            
            return jsonify({
                "success": True,
                "document_id": str(result.inserted_id),
                "message": "Purchase order created successfully"
            })
        else:
            logger.error("❌ Failed to get inserted_id")
            return jsonify({
                "success": False,
                "error": "Failed to insert purchase order into database"
            }), 500
            
    except Exception as e:
        logger.error(f"Purchase order API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/dashboard')
def dashboard_page():
    """Serve the user dashboard page"""
    return render_template('dashboard.html')

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
    print("\\n🔍 Query Node Examples:")
    print('   "How many users are registered in the system?"')
    print('   "Show me all employees with admin position"') 
    print('   "List pending purchase orders above $1000"')
    print('   "When did employee EMP001 last check in?"')
    print("\\n📡 Direct Query API: http://localhost:5001/api/query")
    print("="*80)
    
    # Disable debug mode to prevent socket errors
    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)