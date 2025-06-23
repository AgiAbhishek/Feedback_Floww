from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# In-memory data storage
users = {}
feedback_entries = {}
manager_employee_relationships = {}
feedback_counter = 0

def init_data_store():
    """Initialize the data store with sample users and relationships"""
    global users, manager_employee_relationships
    
    # Create sample users
    users['manager1'] = {
        'id': 'manager1',
        'username': 'manager1',
        'password_hash': generate_password_hash('password123'),
        'role': 'manager',
        'name': 'Kunal'
    }
    
    users['employee1'] = {
        'id': 'employee1',
        'username': 'employee1',
        'password_hash': generate_password_hash('password123'),
        'role': 'employee',
        'name': 'Ankit'
    }
    
    users['employee2'] = {
        'id': 'employee2',
        'username': 'employee2',
        'password_hash': generate_password_hash('password123'),
        'role': 'employee',
        'name': 'Abhishek'
    }
    
    # Set up manager-employee relationships
    manager_employee_relationships['manager1'] = ['employee1', 'employee2']
    
    logging.info("Data store initialized with sample users")

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = users.get(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user(user_id):
    """Get user by ID"""
    return users.get(user_id)

def get_employees_for_manager(manager_id):
    """Get list of employees for a specific manager"""
    employee_ids = manager_employee_relationships.get(manager_id, [])
    return [users[emp_id] for emp_id in employee_ids if emp_id in users]

def is_manager_of_employee(manager_id, employee_id):
    """Check if manager is responsible for employee"""
    return employee_id in manager_employee_relationships.get(manager_id, [])

def add_feedback(manager_id, employee_id, strengths, areas_to_improve, sentiment):
    """Add feedback entry"""
    global feedback_counter
    feedback_counter += 1
    
    feedback_id = f"feedback_{feedback_counter}"
    feedback_entries[feedback_id] = {
        'id': feedback_id,
        'manager_id': manager_id,
        'employee_id': employee_id,
        'strengths': strengths,
        'areas_to_improve': areas_to_improve,
        'sentiment': sentiment,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'acknowledged': False
    }
    
    logging.info(f"Feedback added: {feedback_id}")
    return feedback_id

def update_feedback(feedback_id, strengths, areas_to_improve, sentiment):
    """Update existing feedback entry"""
    if feedback_id in feedback_entries:
        feedback_entries[feedback_id].update({
            'strengths': strengths,
            'areas_to_improve': areas_to_improve,
            'sentiment': sentiment,
            'updated_at': datetime.now()
        })
        logging.info(f"Feedback updated: {feedback_id}")
        return True
    return False

def get_feedback(feedback_id):
    """Get feedback by ID"""
    return feedback_entries.get(feedback_id)

def get_feedback_for_employee(employee_id):
    """Get all feedback for an employee"""
    return [feedback for feedback in feedback_entries.values() 
            if feedback['employee_id'] == employee_id]

def get_feedback_by_manager(manager_id):
    """Get all feedback submitted by a manager"""
    return [feedback for feedback in feedback_entries.values() 
            if feedback['manager_id'] == manager_id]

def acknowledge_feedback(feedback_id):
    """Mark feedback as acknowledged by employee"""
    if feedback_id in feedback_entries:
        feedback_entries[feedback_id]['acknowledged'] = True
        logging.info(f"Feedback acknowledged: {feedback_id}")
        return True
    return False

def get_sentiment_stats_for_manager(manager_id):
    """Get sentiment statistics for a manager's team"""
    manager_feedback = get_feedback_by_manager(manager_id)
    
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    for feedback in manager_feedback:
        sentiment = feedback['sentiment'].lower()
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
    
    return sentiment_counts

def get_employee_feedback_summary(employee_ids):
    """Get feedback summary for a list of employees"""
    summary = {}
    for emp_id in employee_ids:
        employee_feedback = get_feedback_for_employee(emp_id)
        summary[emp_id] = {
            'total_feedback': len(employee_feedback),
            'unacknowledged': len([f for f in employee_feedback if not f['acknowledged']]),
            'latest_feedback': max(employee_feedback, key=lambda x: x['created_at']) if employee_feedback else None
        }
    return summary
