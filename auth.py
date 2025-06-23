from functools import wraps
from flask import session, redirect, url_for, flash
from models import get_user, is_manager_of_employee

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator to require manager role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = get_user(session['user_id'])
        if not user or user['role'] != 'manager':
            flash('Manager access required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def employee_access_required(f):
    """Decorator to ensure user can only access their own data or their manager's data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = get_user(session['user_id'])
        if not user:
            flash('Invalid user session.', 'error')
            return redirect(url_for('login'))
        
        # Extract employee_id from kwargs if present
        employee_id = kwargs.get('employee_id')
        if employee_id:
            # Manager can access their employees' data
            if user['role'] == 'manager' and is_manager_of_employee(user['id'], employee_id):
                return f(*args, **kwargs)
            # Employee can only access their own data
            elif user['role'] == 'employee' and user['id'] == employee_id:
                return f(*args, **kwargs)
            else:
                flash('Access denied.', 'error')
                return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return get_user(session['user_id'])
    return None
