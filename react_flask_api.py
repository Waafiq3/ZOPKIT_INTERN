"""
ZOPKIT ReAct Flask API Server
Modern Flask server that integrates with the new ReAct chatbot system

This server provides RESTful endpoints for the ReAct chatbot,
eliminating all hardcoded patterns and providing dynamic responses
based on AI reasoning and intelligent action execution.
"""

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import logging
import uuid
import os
from typing import Dict, Any

# Import the new ReAct chatbot system
from react_chatbot import create_react_chatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Initialize ReAct chatbot
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
react_chatbot = create_react_chatbot(gemini_api_key=GEMINI_API_KEY)

logger.info("🚀 ZOPKIT ReAct Flask API Server initialized")

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('react_chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint for ReAct chatbot interaction
    
    Handles all user messages dynamically without hardcoded patterns
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get user context from request
        user_context = {
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'timestamp': data.get('timestamp'),
            'user_validated': session.get('user_validated', False),
            'employee_id': session.get('employee_id'),
            'department': session.get('department'),
            'user_profile': session.get('user_profile')
        }
        
        logger.info(f"💬 Chat request - Session: {session_id}, Message: '{user_message[:50]}...'")
        
        # Process message through ReAct system
        response = react_chatbot.process_user_message(
            user_input=user_message,
            session_id=session_id,
            user_context=user_context
        )
        
        # Update Flask session if user was authenticated
        if response.get('action_result', {}).get('action') == 'authentication_success':
            user_profile_data = response['action_result'].get('user_profile', {})
            session['user_validated'] = True
            session['employee_id'] = user_profile_data.get('employee_id')
            session['department'] = user_profile_data.get('department')
            session['user_profile'] = user_profile_data
        
        # Add session ID to response
        response['session_id'] = session_id
        
        logger.info(f"✅ Chat response sent - Action: {response.get('action_result', {}).get('action', 'unknown')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error',
            'response': 'I apologize, but I encountered an error processing your request. Please try again.'
        }), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id: str):
    """Get current session status and context"""
    try:
        status = react_chatbot.get_session_status(session_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"❌ Session status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/reset', methods=['POST'])
def reset_session(session_id: str):
    """Reset session to initial state"""
    try:
        result = react_chatbot.reset_session(session_id)
        
        # Clear Flask session as well
        session.clear()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Session reset error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections', methods=['GET'])
def get_collections():
    """Get list of all available collections"""
    try:
        collections = react_chatbot.get_available_collections()
        return jsonify({
            'collections': collections,
            'total_count': len(collections)
        })
    except Exception as e:
        logger.error(f"❌ Collections endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<collection_name>/requirements', methods=['GET'])
def get_collection_requirements(collection_name: str):
    """Get detailed requirements for a specific collection"""
    try:
        requirements = react_chatbot.field_processor.get_collection_requirements(collection_name)
        return jsonify(requirements)
    except Exception as e:
        logger.error(f"❌ Collection requirements error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user with employee ID"""
    try:
        data = request.get_json()
        
        if not data or 'employee_id' not in data:
            return jsonify({
                'error': 'Employee ID is required',
                'status': 'error'
            }), 400
        
        employee_id = data['employee_id']
        additional_context = data.get('context', {})
        
        # Authenticate through the authorization system
        user_profile = react_chatbot.auth_system.authenticate_user(employee_id, additional_context)
        
        # Store in Flask session
        session['user_validated'] = True
        session['employee_id'] = user_profile.employee_id
        session['department'] = user_profile.department
        session['user_profile'] = {
            'employee_id': user_profile.employee_id,
            'department': user_profile.department,
            'position': user_profile.position,
            'roles': user_profile.roles,
            'access_level': user_profile.access_level.value
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Authentication successful',
            'user_profile': session['user_profile']
        })
        
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        return jsonify({
            'error': 'Authentication failed',
            'status': 'error'
        }), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout current user"""
    try:
        session.clear()
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    try:
        if not session.get('user_validated'):
            return jsonify({
                'error': 'Not authenticated',
                'status': 'unauthenticated'
            }), 401
        
        user_profile = session.get('user_profile', {})
        
        # Get accessible collections for this user
        if 'employee_id' in user_profile:
            # Recreate user profile object for authorization check
            auth_user_profile = react_chatbot.auth_system.authenticate_user(
                user_profile['employee_id']
            )
            accessible_collections = react_chatbot.auth_system.get_user_accessible_collections(auth_user_profile)
            user_profile['accessible_collections'] = accessible_collections
        
        return jsonify({
            'status': 'authenticated',
            'user_profile': user_profile
        })
        
    except Exception as e:
        logger.error(f"❌ Profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status and health"""
    try:
        status = react_chatbot.get_system_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"❌ System status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            'active_sessions': len(react_chatbot.active_sessions),
            'total_collections': len(react_chatbot.collection_schemas),
            'system_uptime': 'Available on request',  # Could implement uptime tracking
            'ai_status': 'Enabled' if react_chatbot.react_engine.ai_model else 'Disabled',
            'database_status': 'Connected' if react_chatbot.db_collections else 'Disconnected'
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"❌ System stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<collection_name>/simulate', methods=['POST'])
def simulate_collection_operation(collection_name: str):
    """Simulate a collection operation for testing"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', f'I want to create a {collection_name}')
        
        # Create a temporary session for simulation
        temp_session_id = f"sim_{uuid.uuid4()}"
        
        # Process through ReAct system
        response = react_chatbot.process_user_message(
            user_input=user_input,
            session_id=temp_session_id,
            user_context={'simulation': True}
        )
        
        # Clean up temporary session
        react_chatbot.reset_session(temp_session_id)
        
        return jsonify({
            'simulation_result': response,
            'collection': collection_name,
            'input': user_input
        })
        
    except Exception as e:
        logger.error(f"❌ Simulation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'not_found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'status': 'server_error'
    }), 500

if __name__ == '__main__':
    # Get configuration from environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    logger.info(f"🌟 Starting ZOPKIT ReAct Flask Server on {host}:{port}")
    logger.info(f"🔧 Debug mode: {debug_mode}")
    logger.info(f"🤖 AI-powered: {react_chatbot.react_engine.ai_model is not None}")
    
    # Import schema to get collection count
    from schema import COLLECTION_SCHEMAS
    logger.info(f"📊 Supporting {len(COLLECTION_SCHEMAS)} collections dynamically")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )