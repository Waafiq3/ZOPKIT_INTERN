# ZOPKIT ReAct Enterprise Chatbot 🚀

> Revolutionary AI-powered business operations assistant that eliminates hardcoded patterns using ReAct (Reasoning + Acting) methodology

## 🌟 What Makes This Special

This is not just another chatbot - it's a **revolutionary AI system** that completely eliminates hardcoded patterns and adapts dynamically to any business operation. Using cutting-edge **ReAct (Reasoning + Acting)** methodology, it can understand, reason about, and execute operations across **49 different business collections** without any hardcoded logic.

### 🧠 ReAct Methodology
- **REASONING**: AI analyzes user intent and context using advanced language models
- **ACTING**: System executes appropriate actions dynamically based on reasoning results
- **ADAPTING**: Learns and adapts to new patterns without code changes

## ✨ Key Features

### 🎯 Zero Hardcoding Architecture
- **Dynamic Collection Routing**: Intelligent mapping to 49+ business operations
- **Universal Field Processing**: Generic field handling for any data structure  
- **Smart Authorization**: Role-based access control without hardcoded rules
- **AI-Powered Intent Recognition**: Context-aware understanding of user requests

### 🔧 Advanced Components
- **ReAct Engine**: Core reasoning and acting framework
- **Dynamic Router**: Intelligent collection selection system
- **Universal Field Processor**: Generic field validation and processing
- **Authorization System**: Dynamic role-based access control
- **Modern UI**: Responsive chat interface with real-time feedback

### 📊 Supported Operations (49 Collections)

#### 👥 User Management
- User Registration & Onboarding
- User Activation & Role Management
- Access Control & Permissions

#### 🏭 Supplier & Vendor Management  
- Supplier Registration
- Vendor Management
- Contract Management
- Purchase Orders

#### 👤 Customer & Client Operations
- Client Registration
- Customer Support Tickets
- Order Placement & Tracking
- Customer Feedback Management

#### 💼 HR & Employee Operations
- Employee Leave Requests
- Payroll Management
- Training Registration
- Performance Reviews
- Recruitment & Interviews
- Attendance Tracking
- Shift Scheduling

#### 📦 Inventory & Operations
- Product Catalog Management
- Inventory Management
- Warehouse Management  
- Shipping Management

#### 💰 Financial Operations
- Payment Processing
- Expense Reimbursement
- Invoice Management

#### 🔧 IT & System Operations
- IT Asset Allocation
- System Configuration
- Data Backup & Restore
- Audit Logging

#### 📚 Knowledge & Support
- Knowledge Base Management
- FAQ Management
- Chatbot Training Data
- Knowledge Transfer

#### 🏢 Business Operations
- Project Assignment
- Meeting Scheduling
- Travel Requests
- Compliance Reporting
- Marketing Campaigns
- Announcements

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Gemini API key (optional, for enhanced AI features)

### Installation

1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd zopkit
pip install -r react_requirements.txt
```

2. **Environment Configuration**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
echo "MONGODB_URI=mongodb://localhost:27017/zopkit" >> .env
echo "SECRET_KEY=your_secret_key_here" >> .env
```

3. **Run the System**
```bash
python react_flask_api.py
```

4. **Access the Interface**
Open http://localhost:5000 in your browser

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ZOPKIT ReAct System                      │
├─────────────────────────────────────────────────────────────┤
│  🎯 React Chat Interface (HTML/CSS/JS)                     │
├─────────────────────────────────────────────────────────────┤
│  🌐 Flask API Server (react_flask_api.py)                  │
├─────────────────────────────────────────────────────────────┤
│  🤖 ReAct Chatbot Engine (react_chatbot.py)                │
│    │                                                       │
│    ├── 🧠 ReAct Framework (react_framework.py)             │
│    │    ├── Reasoning Engine                               │
│    │    └── Acting Engine                                  │
│    │                                                       │
│    ├── 🎯 Dynamic Router (dynamic_router.py)               │
│    │    ├── Intent Analysis                                │
│    │    ├── Collection Mapping                             │
│    │    └── Confidence Scoring                             │
│    │                                                       │
│    ├── ⚙️ Field Processor (universal_field_processor.py)   │
│    │    ├── Dynamic Field Detection                        │
│    │    ├── Validation Engine                              │
│    │    └── Data Extraction                                │
│    │                                                       │
│    └── 🔐 Authorization (dynamic_authorization.py)         │
│         ├── Role-Based Access Control                      │
│         ├── Department Permissions                         │
│         └── Collection Access Rules                        │
├─────────────────────────────────────────────────────────────┤
│  📊 Schema System (schema.py)                              │
│    └── 49 Business Collection Definitions                  │
├─────────────────────────────────────────────────────────────┤
│  🗄️ Database Layer (db.py)                                 │
│    └── MongoDB Integration                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 How It Works

### 1. **User Input Processing**
```python
# User says: "I want to create a purchase order for laptops"
user_input = "I want to create a purchase order for laptops"
```

### 2. **ReAct Reasoning Phase**
```python
# AI analyzes intent and context
reasoning_result = react_engine.reason(user_input, context)
# Result: intent="purchase_order", confidence=0.95, target_collection="purchase_order"
```

### 3. **Dynamic Routing**
```python
# Router maps to appropriate collection
routing_result = collection_router.route_request(user_input)
# Result: target_collection="purchase_order", confidence="high"
```

### 4. **Field Processing**
```python
# Universal processor extracts and validates fields
processing_result = field_processor.process_collection_data(
    "purchase_order", user_input, existing_data
)
# Result: extracted fields, validation status, missing requirements
```

### 5. **Authorization Check**
```python
# Dynamic authorization verification
auth_result = auth_system.authorize_collection_access(
    user_profile, "purchase_order", "write"
)
# Result: authorized=True, permissions granted
```

### 6. **Acting Phase**
```python
# Execute appropriate action based on reasoning
action_result = react_engine.act(reasoning_result, context)
# Result: data collection, validation, or operation execution
```

## 🛠️ Usage Examples

### Basic User Registration
```
User: "I want to register a new employee"
ReAct: "I'll help you register a new employee. Please provide their first name:"
User: "John"
ReAct: "Great! Now, what's their last name?"
User: "Smith"
ReAct: [Continues dynamically collecting required fields]
```

### Purchase Order Creation
```
User: "Create PO for 50 laptops from supplier SUP001"
ReAct: [Analyzes intent, extracts: product="laptops", quantity=50, supplier_id="SUP001"]
ReAct: "I've extracted some information. What's the expected delivery date?"
User: "2024-01-15"
ReAct: [Validates all fields and creates purchase order]
```

### Authentication Flow
```
User: "I need access to HR functions"
ReAct: "This requires authentication. Please provide your Employee ID:"
User: "EMP003"
ReAct: [Authenticates, determines HR manager role, grants appropriate access]
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key        # Optional: Enhanced AI features
OPENAI_API_KEY=your_openai_key            # Alternative AI provider

# Database Configuration  
MONGODB_URI=mongodb://localhost:27017/zopkit
DATABASE_NAME=zopkit

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
SECRET_KEY=your_secret_key_here

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret
SESSION_TIMEOUT=3600
```

### Customization Options

#### Adding New Collections
1. Update `schema.py` with new collection definition
2. System automatically adapts - no code changes needed!

```python
# In schema.py
COLLECTION_SCHEMAS = {
    "your_new_collection": {
        "required": ["field1", "field2"],
        "optional": ["field3", "field4"]
    }
}
```

#### Custom Authorization Rules
```python
# The system automatically creates access rules based on:
# - Collection sensitivity
# - Department requirements  
# - Role hierarchies
# - Business logic patterns
```

## 📡 API Endpoints

### Chat Operations
- `POST /api/chat` - Process user message through ReAct system
- `GET /api/session/{session_id}/status` - Get session status
- `POST /api/session/{session_id}/reset` - Reset session

### System Information
- `GET /api/collections` - List all available collections
- `GET /api/collections/{name}/requirements` - Get collection requirements
- `GET /api/system/status` - System health and status
- `GET /api/system/stats` - Usage statistics

### Authentication
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile

### Testing
- `POST /api/collections/{name}/simulate` - Simulate collection operation

## 🧪 Testing the System

### Quick Test Commands

1. **User Registration Test**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to register a new user", "session_id": "test123"}'
```

2. **Purchase Order Test**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create purchase order for 10 laptops", "session_id": "test123"}'
```

3. **Authentication Test**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "EMP001"}'
```

### Test Scenarios

1. **Multi-step Data Collection**
   - Start with partial information
   - System guides through required fields
   - Validates data at each step

2. **Authorization Scenarios**
   - Test different employee IDs (EMP001-EMP005)
   - Verify role-based access control
   - Check department restrictions

3. **Error Handling**
   - Invalid data formats
   - Missing required fields
   - Unauthorized access attempts

## 🎯 Advanced Features

### AI-Powered Reasoning
- **Context Awareness**: Understands conversation history and user intent
- **Multi-turn Conversations**: Maintains context across message exchanges
- **Intelligent Fallbacks**: Graceful handling when AI is unavailable

### Dynamic Validation
- **Field Type Detection**: Automatically infers data types from field names
- **Pattern Recognition**: Smart extraction using regex patterns
- **Contextual Validation**: Validates based on business rules

### Smart Authorization
- **Role Hierarchy**: Inherits permissions from role relationships
- **Department Boundaries**: Enforces department-specific access
- **Collection Security**: Different security levels per collection

## 🚀 Deployment

### Development
```bash
python react_flask_api.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 react_flask_api:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY react_requirements.txt .
RUN pip install -r react_requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "react_flask_api:app"]
```

## 📊 Monitoring and Analytics

### System Metrics
- Active sessions count
- Collection usage statistics  
- Authentication success rates
- Response time analytics
- Error rate monitoring

### User Analytics
- Most used collections
- Common user journeys
- Field completion rates
- Authorization patterns

## 🛡️ Security Features

### Authentication & Authorization
- Employee ID-based authentication
- Role-based access control (RBAC)
- Department-level permissions
- Session management with timeouts

### Data Protection
- Input validation and sanitization
- XSS protection in web interface
- CORS configuration for API security
- Secure session handling

### Audit Trail
- Complete conversation logging
- User action tracking
- System access monitoring
- Error and security event logging

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests
5. Submit pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add comprehensive docstrings
- Include unit tests for new features

## 📈 Roadmap

### Version 2.1 (Next Release)
- [ ] Enhanced AI reasoning with GPT-4 integration
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Workflow automation

### Version 2.2 (Future)
- [ ] Voice interaction support
- [ ] Mobile app integration
- [ ] Real-time collaboration features
- [ ] Advanced reporting system

## 🐛 Troubleshooting

### Common Issues

1. **AI Not Working**
   - Check GEMINI_API_KEY environment variable
   - System falls back to pattern matching automatically

2. **Database Connection Issues**
   - Verify MongoDB is running
   - Check MONGODB_URI in environment

3. **Authorization Problems**
   - Verify employee ID format (EMP001-EMP005 for testing)
   - Check user profile creation in logs

4. **Field Processing Issues**
   - Check field names in schema.py
   - Verify data format requirements

### Debug Mode
```bash
export FLASK_DEBUG=true
python react_flask_api.py
```

### Logging
All components use structured logging. Check console output for detailed information about:
- ReAct reasoning processes
- Collection routing decisions
- Field processing results
- Authorization checks

## 📞 Support

For questions, issues, or contributions:

- **Documentation**: This README and inline code comments
- **Issues**: GitHub issues for bugs and feature requests
- **Discussions**: GitHub discussions for questions and ideas

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**ZOPKIT ReAct Enterprise Chatbot** - Revolutionizing business operations with AI-powered, zero-hardcoding architecture! 🚀

> Built with ❤️ using ReAct methodology, modern Python, and advanced AI technologies.