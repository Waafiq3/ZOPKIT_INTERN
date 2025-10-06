# ZOPKIT ReAct System Deployment Guide

## 🚀 Complete Production Deployment Instructions

### Prerequisites

1. **Python Environment**
   ```powershell
   # Ensure Python 3.8+ is installed
   python --version
   
   # Create virtual environment
   python -m venv react_env
   
   # Activate virtual environment
   react_env\Scripts\activate  # Windows
   # source react_env/bin/activate  # Linux/Mac
   ```

2. **Database Setup**
   ```powershell
   # Install MongoDB (Windows)
   # Download from https://www.mongodb.com/try/download/community
   
   # Start MongoDB service
   net start MongoDB
   
   # Or use MongoDB Atlas (cloud) - update connection string in db.py
   ```

3. **Gemini AI API (Optional but Recommended)**
   ```powershell
   # Get API key from https://makersuite.google.com/app/apikey
   # Set environment variable
   $env:GEMINI_API_KEY = "your_api_key_here"
   ```

### Installation Steps

1. **Clone and Setup Project**
   ```powershell
   # Navigate to project directory
   cd "c:\Users\Likith\OneDrive\Desktop\zopkit"
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Verify installation
   python test_react_system.py
   ```

2. **Configuration**
   ```powershell
   # Update database configuration in db.py if needed
   # Default: mongodb://localhost:27017
   
   # Configure email settings in universal_field_processor.py
   # Update business domains in dynamic_router.py if needed
   ```

### Running the System

1. **Start the Flask API Server**
   ```powershell
   # Method 1: Direct execution
   python react_flask_api.py
   
   # Method 2: Using Flask command
   $env:FLASK_APP = "react_flask_api.py"
   flask run --host=0.0.0.0 --port=5000
   ```

2. **Access the Application**
   - Open browser: `http://localhost:5000`
   - API endpoints: `http://localhost:5000/api/`
   - System status: `http://localhost:5000/api/system/status`

### Production Deployment Options

#### Option 1: Windows Server with IIS

1. **Install IIS and Python**
   ```powershell
   # Enable IIS features
   Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
   Enable-WindowsOptionalFeature -Online -FeatureName IIS-CGI
   
   # Install wfastcgi
   pip install wfastcgi
   wfastcgi-enable
   ```

2. **Configure IIS**
   - Create new site in IIS Manager
   - Point to project directory
   - Configure Python handler for *.py files
   - Set up web.config with FastCGI settings

#### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install -r requirements.txt
   
   EXPOSE 5000
   CMD ["python", "react_flask_api.py"]
   ```

2. **Build and Run Container**
   ```powershell
   # Build image
   docker build -t zopkit-react .
   
   # Run container
   docker run -p 5000:5000 -e GEMINI_API_KEY=your_key zopkit-react
   ```

#### Option 3: Cloud Deployment (Azure/AWS)

1. **Azure App Service**
   ```powershell
   # Install Azure CLI
   # Create app service
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name zopkit-react --runtime "PYTHON|3.9"
   
   # Deploy code
   az webapp deployment source config-zip --resource-group myResourceGroup --name zopkit-react --src zopkit.zip
   ```

2. **AWS Elastic Beanstalk**
   ```powershell
   # Install EB CLI
   # Initialize and deploy
   eb init
   eb create production
   eb deploy
   ```

### Environment Variables

Set these environment variables for production:

```powershell
# Required
$env:FLASK_ENV = "production"
$env:FLASK_SECRET_KEY = "your-secret-key-here"

# Optional but recommended
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:MONGODB_URI = "mongodb://your-db-connection-string"

# Email configuration (if using email notifications)
$env:SMTP_SERVER = "your-smtp-server"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "your-email@company.com"
$env:SMTP_PASSWORD = "your-email-password"
```

### Security Configuration

1. **Update Flask Security Settings**
   ```python
   # In react_flask_api.py
   app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'change-in-production')
   app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
   ```

2. **Enable HTTPS**
   ```powershell
   # For production, always use HTTPS
   # Configure SSL certificate in your web server
   # Update CORS settings in react_flask_api.py for your domain
   ```

3. **Database Security**
   ```python
   # Use authentication for MongoDB
   # Update connection string with credentials
   MONGODB_URI = "mongodb://username:password@localhost:27017/enterprise_db"
   ```

### Performance Optimization

1. **Caching**
   ```python
   # Add Redis for session storage and caching
   pip install redis flask-session
   
   # Configure in react_flask_api.py
   import redis
   from flask_session import Session
   
   app.config['SESSION_TYPE'] = 'redis'
   app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
   ```

2. **Database Optimization**
   ```python
   # Add indexes to MongoDB collections
   # Configure connection pooling in db.py
   ```

3. **Load Balancing**
   ```powershell
   # Use multiple Flask instances with nginx/HAProxy
   # Configure session sharing with Redis
   ```

### Monitoring and Logging

1. **Application Logging**
   ```python
   # Configure production logging in each module
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('zopkit_react.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Health Checks**
   ```python
   # Use /api/system/status endpoint for monitoring
   # Set up alerts for system failures
   ```

3. **Performance Monitoring**
   ```python
   # Add APM tools like New Relic or DataDog
   # Monitor response times and error rates
   ```

### Backup and Recovery

1. **Database Backup**
   ```powershell
   # MongoDB backup
   mongodump --host localhost:27017 --db enterprise_db --out backup/
   
   # Restore
   mongorestore --host localhost:27017 --db enterprise_db backup/enterprise_db/
   ```

2. **Application Backup**
   ```powershell
   # Backup entire application directory
   # Include configuration files and logs
   # Store in version control and secure storage
   ```

### Testing in Production

1. **Smoke Tests**
   ```powershell
   # Test basic functionality
   curl http://your-domain/api/system/status
   
   # Test authentication
   curl -X POST http://your-domain/api/auth/login -d '{"employee_id":"EMP001"}'
   ```

2. **Load Testing**
   ```powershell
   # Use tools like Apache Bench or LoadRunner
   ab -n 1000 -c 10 http://your-domain/api/system/status
   ```

### Troubleshooting

1. **Common Issues**
   ```powershell
   # Database connection issues
   # Check MongoDB service status
   net start MongoDB
   
   # Python import errors
   # Verify virtual environment and dependencies
   pip list
   
   # Port conflicts
   # Check what's running on port 5000
   netstat -an | findstr :5000
   ```

2. **Log Analysis**
   ```powershell
   # Check application logs
   Get-Content zopkit_react.log -Tail 50
   
   # Check system logs
   Get-EventLog -LogName Application -Newest 10
   ```

### Maintenance

1. **Regular Updates**
   ```powershell
   # Update Python packages
   pip list --outdated
   pip install --upgrade package_name
   
   # Update system dependencies
   # Test in staging environment first
   ```

2. **Database Maintenance**
   ```powershell
   # MongoDB maintenance
   # Optimize indexes
   # Clean up old session data
   ```

### Support and Contact

- **Documentation**: See REACT_README.md for detailed system documentation
- **API Reference**: Access `/api/docs` endpoint for interactive API documentation
- **Test Suite**: Run `python test_react_system.py` for system validation
- **Issues**: Check logs and system status for troubleshooting

---

## 🎉 Deployment Complete!

Your ZOPKIT ReAct system is now ready for production use with:
- ✅ Dynamic collection routing (49 business operations)
- ✅ Universal field processing
- ✅ Role-based authorization
- ✅ AI-powered reasoning and acting
- ✅ Modern REST API
- ✅ Responsive web interface
- ✅ Comprehensive testing
- ✅ Production deployment guide

The system eliminates all hardcoded elements and provides intelligent, dynamic business operation handling!