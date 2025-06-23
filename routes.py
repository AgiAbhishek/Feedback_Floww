from flask import render_template, request, redirect, url_for, flash, session
from app import app
from auth import login_required, manager_required, employee_access_required, get_current_user
from models import (
    authenticate_user, get_user, get_employees_for_manager, is_manager_of_employee,
    add_feedback, update_feedback, get_feedback, get_feedback_for_employee,
    get_feedback_by_manager, acknowledge_feedback, get_sentiment_stats_for_manager,
    get_employee_feedback_summary
)
import logging

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - redirects to role-specific dashboard"""
    user = get_current_user()
    if user['role'] == 'manager':
        return redirect(url_for('manager_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

@app.route('/manager/dashboard')
@manager_required
def manager_dashboard():
    """Manager dashboard with team overview"""
    user = get_current_user()
    employees = get_employees_for_manager(user['id'])
    sentiment_stats = get_sentiment_stats_for_manager(user['id'])
    
    # Get employee IDs for feedback summary
    employee_ids = [emp['id'] for emp in employees]
    feedback_summary = get_employee_feedback_summary(employee_ids)
    
    return render_template('manager_dashboard.html',
                         user=user,
                         employees=employees,
                         sentiment_stats=sentiment_stats,
                         feedback_summary=feedback_summary)

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    """Employee dashboard with personal feedback timeline"""
    user = get_current_user()
    if user['role'] != 'employee':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    feedback_list = get_feedback_for_employee(user['id'])
    return render_template('employee_dashboard.html',
                         user=user,
                         feedback_list=feedback_list)

@app.route('/feedback/submit/<int:employee_id>', methods=['GET', 'POST'])
@manager_required
def submit_feedback(employee_id):
    """Submit feedback for an employee"""
    user = get_current_user()
    
    # Check if manager can submit feedback for this employee
    if not is_manager_of_employee(user['id'], employee_id):
        flash('You can only submit feedback for your team members.', 'danger')
        return redirect(url_for('manager_dashboard'))
    
    employee = get_user(employee_id)
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('manager_dashboard'))
    
    if request.method == 'POST':
        strengths = request.form['strengths']
        areas_to_improve = request.form['areas_to_improve']
        sentiment = request.form['sentiment']
        
        if strengths and areas_to_improve and sentiment:
            feedback_id = add_feedback(user['id'], employee_id, strengths, areas_to_improve, sentiment)
            flash(f'Feedback submitted successfully for {employee["name"]}.', 'success')
            logging.info(f"Feedback added: feedback_{feedback_id}")
            return redirect(url_for('manager_dashboard'))
        else:
            flash('All fields are required.', 'danger')
    
    return render_template('submit_feedback.html', employee=employee)

@app.route('/feedback/edit/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def edit_feedback(feedback_id):
    """Edit existing feedback"""
    user = get_current_user()
    feedback = get_feedback(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Only the manager who created the feedback can edit it
    if user['role'] != 'manager' or feedback['manager_id'] != user['id']:
        flash('You can only edit feedback that you created.', 'danger')
        return redirect(url_for('dashboard'))
    
    employee = get_user(feedback['employee_id'])
    
    if request.method == 'POST':
        strengths = request.form['strengths']
        areas_to_improve = request.form['areas_to_improve']
        sentiment = request.form['sentiment']
        
        if strengths and areas_to_improve and sentiment:
            update_feedback(feedback_id, strengths, areas_to_improve, sentiment)
            flash('Feedback updated successfully.', 'success')
            return redirect(url_for('manager_dashboard'))
        else:
            flash('All fields are required.', 'danger')
    
    return render_template('edit_feedback.html', feedback=feedback, employee=employee)

@app.route('/feedback/acknowledge/<int:feedback_id>')
@login_required
def acknowledge_feedback_route(feedback_id):
    """Acknowledge feedback (employee only)"""
    user = get_current_user()
    feedback = get_feedback(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Only the employee who received the feedback can acknowledge it
    if user['role'] != 'employee' or feedback['employee_id'] != user['id']:
        flash('You can only acknowledge feedback directed to you.', 'danger')
        return redirect(url_for('dashboard'))
    
    acknowledge_feedback(feedback_id)
    flash('Feedback acknowledged.', 'success')
    logging.info(f"Feedback acknowledged: feedback_{feedback_id}")
    return redirect(url_for('employee_dashboard'))

@app.route('/feedback/history/<int:employee_id>')
@employee_access_required
def feedback_history(employee_id):
    """View feedback history for an employee"""
    employee = get_user(employee_id)
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    feedback_list = get_feedback_for_employee(employee_id)
    return render_template('feedback_history.html',
                         employee=employee,
                         feedback_list=feedback_list)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500