"""
ZOPKIT ReAct System - Quick Start Script
Handles startup and common issues automatically
"""

import sys
import time
import subprocess
import requests
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required modules are available"""
    required_modules = [
        'flask', 'flask_cors', 'pymongo', 'google.generativeai'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module.replace('.', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"❌ Missing dependencies: {missing}")
        logger.info("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies available")
    return True

def start_server():
    """Start the ReAct Flask server"""
    try:
        logger.info("🚀 Starting ZOPKIT ReAct Server...")
        
        # Import and start the Flask app
        from react_flask_api import app
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False  # Prevent double startup
        )
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        return False

def wait_for_server(timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=2)
            if response.status_code == 200:
                logger.info("✅ Server is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
    
    logger.warning("⚠️ Server not responding within timeout")
    return False

def test_system():
    """Test basic system functionality"""
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            logger.info("✅ Health check passed")
        
        # Test system status
        response = requests.get('http://localhost:5000/api/system/status', timeout=10)
        if response.status_code == 200:
            logger.info("✅ System status check passed")
        
        # Test simple chat
        response = requests.post('http://localhost:5000/api/chat', 
                               json={'message': 'Hello', 'session_id': 'test'}, 
                               timeout=15)
        if response.status_code == 200:
            logger.info("✅ Chat endpoint working")
            return True
        
    except Exception as e:
        logger.error(f"❌ System test failed: {e}")
    
    return False

def main():
    """Main startup routine"""
    logger.info("🎯 ZOPKIT ReAct System Startup")
    logger.info("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready
    if wait_for_server():
        # Test the system
        if test_system():
            logger.info("🎉 ZOPKIT ReAct System is fully operational!")
            logger.info("🌐 Access at: http://localhost:5000")
            logger.info("📚 API Documentation: http://localhost:5000/api")
            logger.info("")
            logger.info("Try these test messages:")
            logger.info("- 'I want to register a user'")
            logger.info("- 'Create a purchase order'")
            logger.info("- 'My employee ID is EMP001'")
            logger.info("")
            logger.info("Press Ctrl+C to stop the server")
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("👋 Shutting down ZOPKIT system...")
        else:
            logger.error("❌ System tests failed")
            sys.exit(1)
    else:
        logger.error("❌ Server failed to start properly")
        sys.exit(1)

if __name__ == "__main__":
    main()