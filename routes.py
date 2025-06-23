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
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
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
    employee_ids = [emp['id'] for emp in employees]
    
    # Get feedback summary for all employees
    feedback_summary = get_employee_feedback_summary(employee_ids)
    
    # Get sentiment statistics
    sentiment_stats = get_sentiment_stats_for_manager(user['id'])
    
    # Get recent feedback
    recent_feedback = get_feedback_by_manager(user['id'])
    recent_feedback.sort(key=lambda x: x['created_at'], reverse=True)
    recent_feedback = recent_feedback[:5]  # Last 5 feedback entries
    
    return render_template('manager_dashboard.html', 
                         user=user, 
                         employees=employees,
                         feedback_summary=feedback_summary,
                         sentiment_stats=sentiment_stats,
                         recent_feedback=recent_feedback)

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    """Employee dashboard with personal feedback timeline"""
    user = get_current_user()
    
    if user['role'] != 'employee':
        flash('Employee access only.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all feedback for this employee
    feedback_list = get_feedback_for_employee(user['id'])
    feedback_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Get statistics
    total_feedback = len(feedback_list)
    unacknowledged = len([f for f in feedback_list if not f['acknowledged']])
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for feedback in feedback_list:
        sentiment = feedback['sentiment'].lower()
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
    
    return render_template('employee_dashboard.html',
                         user=user,
                         feedback_list=feedback_list,
                         total_feedback=total_feedback,
                         unacknowledged=unacknowledged,
                         sentiment_counts=sentiment_counts)

@app.route('/feedback/submit/<employee_id>', methods=['GET', 'POST'])
@manager_required
def submit_feedback(employee_id):
    """Submit feedback for an employee"""
    user = get_current_user()
    
    # Check if manager is responsible for this employee
    if not is_manager_of_employee(user['id'], employee_id):
        flash('You can only submit feedback for your team members.', 'error')
        return redirect(url_for('manager_dashboard'))
    
    employee = get_user(employee_id)
    if not employee:
        flash('Employee not found.', 'error')
        return redirect(url_for('manager_dashboard'))
    
    if request.method == 'POST':
        strengths = request.form.get('strengths', '').strip()
        areas_to_improve = request.form.get('areas_to_improve', '').strip()
        sentiment = request.form.get('sentiment', '').strip()
        
        # Validate form data
        if not strengths or not areas_to_improve or not sentiment:
            flash('Please fill in all fields.', 'error')
            return render_template('submit_feedback.html', user=user, employee=employee)
        
        if sentiment not in ['positive', 'neutral', 'negative']:
            flash('Please select a valid sentiment.', 'error')
            return render_template('submit_feedback.html', user=user, employee=employee)
        
        # Add feedback
        feedback_id = add_feedback(user['id'], employee_id, strengths, areas_to_improve, sentiment)
        flash(f'Feedback submitted successfully for {employee["name"]}.', 'success')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('submit_feedback.html', user=user, employee=employee)

@app.route('/feedback/edit/<feedback_id>', methods=['GET', 'POST'])
@manager_required
def edit_feedback(feedback_id):
    """Edit existing feedback"""
    user = get_current_user()
    feedback = get_feedback(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'error')
        return redirect(url_for('manager_dashboard'))
    
    # Check if this manager submitted the feedback
    if feedback['manager_id'] != user['id']:
        flash('You can only edit your own feedback.', 'error')
        return redirect(url_for('manager_dashboard'))
    
    employee = get_user(feedback['employee_id'])
    
    if request.method == 'POST':
        strengths = request.form.get('strengths', '').strip()
        areas_to_improve = request.form.get('areas_to_improve', '').strip()
        sentiment = request.form.get('sentiment', '').strip()
        
        # Validate form data
        if not strengths or not areas_to_improve or not sentiment:
            flash('Please fill in all fields.', 'error')
            return render_template('edit_feedback.html', user=user, feedback=feedback, employee=employee)
        
        if sentiment not in ['positive', 'neutral', 'negative']:
            flash('Please select a valid sentiment.', 'error')
            return render_template('edit_feedback.html', user=user, feedback=feedback, employee=employee)
        
        # Update feedback
        if update_feedback(feedback_id, strengths, areas_to_improve, sentiment):
            flash('Feedback updated successfully.', 'success')
        else:
            flash('Failed to update feedback.', 'error')
        
        return redirect(url_for('manager_dashboard'))
    
    return render_template('edit_feedback.html', user=user, feedback=feedback, employee=employee)

@app.route('/feedback/acknowledge/<feedback_id>')
@login_required
def acknowledge_feedback_route(feedback_id):
    """Acknowledge feedback (employee only)"""
    user = get_current_user()
    feedback = get_feedback(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if this is the employee's feedback
    if feedback['employee_id'] != user['id']:
        flash('You can only acknowledge your own feedback.', 'error')
        return redirect(url_for('dashboard'))
    
    if acknowledge_feedback(feedback_id):
        flash('Feedback acknowledged.', 'success')
    else:
        flash('Failed to acknowledge feedback.', 'error')
    
    return redirect(url_for('employee_dashboard'))

@app.route('/feedback/history/<employee_id>')
@employee_access_required
def feedback_history(employee_id):
    """View feedback history for an employee"""
    user = get_current_user()
    employee = get_user(employee_id)
    
    if not employee:
        flash('Employee not found.', 'error')
        return redirect(url_for('dashboard'))
    
    feedback_list = get_feedback_for_employee(employee_id)
    feedback_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('feedback_history.html', 
                         user=user, 
                         employee=employee, 
                         feedback_list=feedback_list)

@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def internal_error(error):
    logging.error(f'Internal error: {error}')
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('dashboard'))
