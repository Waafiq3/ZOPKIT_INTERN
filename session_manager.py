"""
Enhanced Session Management and Task Registration System
Tracks user login sessions, registration history, and task assignments
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import logging
logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions, login history, and task tracking"""
    
    def __init__(self):
        self.active_sessions = {}  # In-memory session storage
        try:
            from db import get_database
            self.db = get_database()
        except Exception as e:
            logger.warning(f"Database not available: {e}")
            self.db = None
        
    def create_user_session(self, employee_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user session after successful login"""
        
        session_id = f"session_{employee_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        session_data = {
            "session_id": session_id,
            "employee_id": employee_id,
            "user_data": user_data,
            "login_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversation_history": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "registration_history": [],
            "session_status": "active"
        }
        
        # Store in memory
        self.active_sessions[session_id] = session_data
        
        # Store in database
        if self.db:
            try:
                self.db.user_sessions.insert_one({
                    **session_data,
                    "created_at": datetime.now()
                })
                logger.info(f"Session created for {employee_id}: {session_id}")
            except Exception as e:
                logger.error(f"Failed to store session in DB: {e}")
        
        return session_data
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session data"""
        
        # Check in-memory first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
            return session
        
        # Check database
        if self.db:
            try:
                session = self.db.user_sessions.find_one({"session_id": session_id})
                if session:
                    # Convert ObjectId to string
                    session["_id"] = str(session["_id"])
                    # Load into memory
                    self.active_sessions[session_id] = session
                    return session
            except Exception as e:
                logger.error(f"Failed to retrieve session from DB: {e}")
        
        return None
    
    def update_session_activity(self, session_id: str, activity_data: Dict[str, Any]):
        """Update session with new activity"""
        
        session = self.get_user_session(session_id)
        if not session:
            return False
        
        # Update session data
        session["last_activity"] = datetime.now().isoformat()
        session["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_data.get("type", "unknown"),
            "data": activity_data
        })
        
        # Update in database
        if self.db:
            try:
                self.db.user_sessions.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "last_activity": session["last_activity"],
                            "conversation_history": session["conversation_history"]
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Failed to update session in DB: {e}")
        
        return True
    
    def add_registration_to_history(self, session_id: str, registration_data: Dict[str, Any]):
        """Add a registration event to user's history"""
        
        session = self.get_user_session(session_id)
        if not session:
            return False
        
        registration_entry = {
            "registration_id": f"reg_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.now().isoformat(),
            "type": registration_data.get("type", "unknown"),
            "collection": registration_data.get("collection"),
            "data": registration_data.get("data", {}),
            "status": registration_data.get("status", "completed"),
            "document_id": registration_data.get("document_id")
        }
        
        session["registration_history"].append(registration_entry)
        
        # Update in database
        if self.db:
            try:
                self.db.user_sessions.update_one(
                    {"session_id": session_id},
                    {
                        "$push": {
                            "registration_history": registration_entry
                        }
                    }
                )
                logger.info(f"Registration added to history for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to update registration history: {e}")
        
        return registration_entry
    
    def assign_task_to_user(self, employee_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task to a user based on their employee ID"""
        
        task_id = f"task_{employee_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
        
        task_entry = {
            "task_id": task_id,
            "employee_id": employee_id,
            "assigned_at": datetime.now().isoformat(),
            "task_type": task_data.get("type", "general"),
            "title": task_data.get("title", "Untitled Task"),
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", "medium"),
            "due_date": task_data.get("due_date"),
            "status": "pending",
            "assigned_by": task_data.get("assigned_by", "system"),
            "completion_data": None,
            "completion_time": None
        }
        
        # Store in database
        if self.db:
            try:
                self.db.user_tasks.insert_one({
                    **task_entry,
                    "created_at": datetime.now()
                })
                
                # Update user's current session if active
                for session_id, session in self.active_sessions.items():
                    if session.get("employee_id") == employee_id:
                        session["pending_tasks"].append(task_entry)
                        break
                
                logger.info(f"Task {task_id} assigned to {employee_id}")
                return task_entry
                
            except Exception as e:
                logger.error(f"Failed to assign task: {e}")
        
        return {}
    
    def complete_task(self, task_id: str, completion_data: Dict[str, Any]) -> bool:
        """Mark a task as completed"""
        
        if self.db:
            try:
                result = self.db.user_tasks.update_one(
                    {"task_id": task_id},
                    {
                        "$set": {
                            "status": "completed",
                            "completion_time": datetime.now().isoformat(),
                            "completion_data": completion_data
                        }
                    }
                )
                
                if result.modified_count > 0:
                    # Update active sessions
                    for session in self.active_sessions.values():
                        # Move from pending to completed
                        pending_tasks = session.get("pending_tasks", [])
                        for i, task in enumerate(pending_tasks):
                            if task.get("task_id") == task_id:
                                completed_task = pending_tasks.pop(i)
                                completed_task["status"] = "completed"
                                completed_task["completion_time"] = datetime.now().isoformat()
                                completed_task["completion_data"] = completion_data
                                session["completed_tasks"].append(completed_task)
                                break
                    
                    logger.info(f"Task {task_id} marked as completed")
                    return True
                
            except Exception as e:
                logger.error(f"Failed to complete task: {e}")
        
        return False
    
    def get_user_registration_history(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get all registration history for a user"""
        
        history = []
        
        # Check active sessions first
        for session in self.active_sessions.values():
            if session.get("employee_id") == employee_id:
                history.extend(session.get("registration_history", []))
        
        # Check database for historical sessions
        if self.db:
            try:
                sessions = self.db.user_sessions.find({"employee_id": employee_id})
                for session in sessions:
                    history.extend(session.get("registration_history", []))
            except Exception as e:
                logger.error(f"Failed to retrieve registration history: {e}")
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return history
    
    def get_user_tasks(self, employee_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get tasks for a user, optionally filtered by status"""
        
        query = {"employee_id": employee_id}
        if status:
            query["status"] = status
        
        tasks = []
        if self.db:
            try:
                db_tasks = self.db.user_tasks.find(query).sort("assigned_at", -1)
                for task in db_tasks:
                    task["_id"] = str(task["_id"])
                    tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to retrieve tasks: {e}")
        
        return tasks
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of the user session"""
        
        session = self.get_user_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        employee_id = session.get("employee_id")
        
        summary = {
            "session_info": {
                "session_id": session_id,
                "employee_id": employee_id,
                "login_time": session.get("login_time"),
                "last_activity": session.get("last_activity"),
                "session_duration": self._calculate_session_duration(session),
                "status": session.get("session_status", "active")
            },
            "user_profile": session.get("user_data", {}),
            "activity_stats": {
                "total_conversations": len(session.get("conversation_history", [])),
                "registrations_completed": len(session.get("registration_history", [])),
                "tasks_completed": len(session.get("completed_tasks", [])),
                "tasks_pending": len(session.get("pending_tasks", []))
            },
            "recent_registrations": session.get("registration_history", [])[-5:],  # Last 5
            "pending_tasks": session.get("pending_tasks", []),
            "completed_tasks": session.get("completed_tasks", [])[-3:]  # Last 3
        }
        
        return summary
    
    def _calculate_session_duration(self, session: Dict[str, Any]) -> str:
        """Calculate session duration in human-readable format"""
        
        try:
            login_time = datetime.fromisoformat(session.get("login_time", ""))
            last_activity = datetime.fromisoformat(session.get("last_activity", ""))
            duration = last_activity - login_time
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception:
            return "Unknown"

# Global session manager instance
session_manager = SessionManager()

def create_session_for_user(employee_id: str, user_data: Dict[str, Any]) -> str:
    """Helper function to create a session for a user"""
    session_data = session_manager.create_user_session(employee_id, user_data)
    return session_data["session_id"]

def track_user_registration(session_id: str, registration_type: str, collection: str, 
                          data: Dict[str, Any], document_id: str = None) -> Dict[str, Any]:
    """Helper function to track user registrations"""
    registration_data = {
        "type": registration_type,
        "collection": collection,
        "data": data,
        "status": "completed",
        "document_id": document_id
    }
    return session_manager.add_registration_to_history(session_id, registration_data)

def assign_user_task(employee_id: str, task_title: str, task_description: str, 
                    task_type: str = "general", priority: str = "medium") -> Dict[str, Any]:
    """Helper function to assign tasks to users"""
    task_data = {
        "title": task_title,
        "description": task_description,
        "type": task_type,
        "priority": priority
    }
    return session_manager.assign_task_to_user(employee_id, task_data)

def get_user_dashboard_data(employee_id: str) -> Dict[str, Any]:
    """Get comprehensive dashboard data for a user"""
    
    # Get current session if active
    current_session = None
    for session_id, session in session_manager.active_sessions.items():
        if session.get("employee_id") == employee_id:
            current_session = session_manager.get_session_summary(session_id)
            break
    
    # Get registration history
    registration_history = session_manager.get_user_registration_history(employee_id)
    
    # Get tasks
    pending_tasks = session_manager.get_user_tasks(employee_id, "pending")
    completed_tasks = session_manager.get_user_tasks(employee_id, "completed")
    
    dashboard_data = {
        "employee_id": employee_id,
        "current_session": current_session,
        "statistics": {
            "total_registrations": len(registration_history),
            "pending_tasks": len(pending_tasks),
            "completed_tasks": len(completed_tasks),
            "active_session": current_session is not None
        },
        "recent_activity": {
            "registrations": registration_history[:10],  # Last 10 registrations
            "pending_tasks": pending_tasks[:5],          # Top 5 pending tasks
            "completed_tasks": completed_tasks[:5]       # Last 5 completed tasks
        }
    }
    
    return dashboard_data

if __name__ == "__main__":
    # Test the session management system
    print("🧪 Testing Session Management System")
    
    # Create test user data
    test_user = {
        "employee_id": "EMP001",
        "name": "Admin User",
        "position": "admin",
        "department": "IT",
        "email": "admin@company.com"
    }
    
    # Create session
    session_id = create_session_for_user("EMP001", test_user)
    print(f"✅ Created session: {session_id}")
    
    # Track some registrations
    reg1 = track_user_registration(session_id, "user_registration", "user_registration", 
                                 {"name": "John Doe", "email": "john@example.com"})
    print(f"✅ Tracked registration: {reg1.get('registration_id')}")
    
    # Assign a task
    task = assign_user_task("EMP001", "Complete onboarding", "Help new employee with onboarding process")
    print(f"✅ Assigned task: {task.get('task_id')}")
    
    # Get dashboard data
    dashboard = get_user_dashboard_data("EMP001")
    print(f"✅ Dashboard data loaded for {dashboard['employee_id']}")
    print(f"   - Registrations: {dashboard['statistics']['total_registrations']}")
    print(f"   - Pending tasks: {dashboard['statistics']['pending_tasks']}")
    print(f"   - Active session: {dashboard['statistics']['active_session']}")