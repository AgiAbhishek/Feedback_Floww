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
            flash('Access denied. Manager role required.', 'danger')
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
            flash('User not found.', 'danger')
            return redirect(url_for('login'))
        
        # Extract employee_id from route parameters
        employee_id = kwargs.get('employee_id') or kwargs.get('user_id')
        
        if user['role'] == 'manager':
            # Managers can access their employees' data
            if employee_id and not is_manager_of_employee(user['id'], employee_id):
                flash('Access denied. You can only view data for your team members.', 'danger')
                return redirect(url_for('dashboard'))
        elif user['role'] == 'employee':
            # Employees can only access their own data
            if employee_id and int(employee_id) != user['id']:
                flash('Access denied. You can only view your own data.', 'danger')
                return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return get_user(session['user_id'])
    return None