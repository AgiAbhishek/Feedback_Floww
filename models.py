import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DATABASE_PATH = 'feedback.db'

def init_database():
    """Initialize SQLite database with tables and sample data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute('DROP TABLE IF EXISTS feedback')
    cursor.execute('DROP TABLE IF EXISTS manager_employee')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create manager_employee relationships table
    cursor.execute('''
        CREATE TABLE manager_employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users (id),
            FOREIGN KEY (employee_id) REFERENCES users (id),
            UNIQUE(manager_id, employee_id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            strengths TEXT NOT NULL,
            areas_to_improve TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            acknowledged BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manager_id) REFERENCES users (id),
            FOREIGN KEY (employee_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample users
    users = [
        ('manager1', generate_password_hash('password123'), 'Kunal', 'manager'),
        ('employee1', generate_password_hash('password123'), 'Ankit', 'employee'),
        ('employee2', generate_password_hash('password123'), 'Abhishek', 'employee')
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)',
        users
    )
    
    # Insert manager-employee relationships
    relationships = [
        (1, 2),  # manager1 manages employee1
        (1, 3)   # manager1 manages employee2
    ]
    
    cursor.executemany(
        'INSERT INTO manager_employee (manager_id, employee_id) VALUES (?, ?)',
        relationships
    )
    
    conn.commit()
    conn.close()
    print("SQLite database initialized successfully")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_employees_for_manager(manager_id):
    """Get list of employees for a specific manager"""
    conn = get_db_connection()
    employees = conn.execute('''
        SELECT u.* FROM users u
        JOIN manager_employee me ON u.id = me.employee_id
        WHERE me.manager_id = ?
    ''', (manager_id,)).fetchall()
    conn.close()
    return [dict(emp) for emp in employees]

def is_manager_of_employee(manager_id, employee_id):
    """Check if manager is responsible for employee"""
    conn = get_db_connection()
    relationship = conn.execute(
        'SELECT 1 FROM manager_employee WHERE manager_id = ? AND employee_id = ?',
        (manager_id, employee_id)
    ).fetchone()
    conn.close()
    return relationship is not None

def add_feedback(manager_id, employee_id, strengths, areas_to_improve, sentiment):
    """Add feedback entry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (manager_id, employee_id, strengths, areas_to_improve, sentiment)
        VALUES (?, ?, ?, ?, ?)
    ''', (manager_id, employee_id, strengths, areas_to_improve, sentiment))
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id

def update_feedback(feedback_id, strengths, areas_to_improve, sentiment):
    """Update existing feedback entry"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE feedback 
        SET strengths = ?, areas_to_improve = ?, sentiment = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (strengths, areas_to_improve, sentiment, feedback_id))
    conn.commit()
    conn.close()

def get_feedback(feedback_id):
    """Get feedback by ID"""
    conn = get_db_connection()
    feedback = conn.execute(
        'SELECT * FROM feedback WHERE id = ?', (feedback_id,)
    ).fetchone()
    conn.close()
    return dict(feedback) if feedback else None

def get_feedback_for_employee(employee_id):
    """Get all feedback for an employee"""
    conn = get_db_connection()
    feedback_list = conn.execute(
        'SELECT * FROM feedback WHERE employee_id = ? ORDER BY created_at DESC',
        (employee_id,)
    ).fetchall()
    conn.close()
    return [dict(fb) for fb in feedback_list]

def get_feedback_by_manager(manager_id):
    """Get all feedback submitted by a manager"""
    conn = get_db_connection()
    feedback_list = conn.execute(
        'SELECT * FROM feedback WHERE manager_id = ? ORDER BY created_at DESC',
        (manager_id,)
    ).fetchall()
    conn.close()
    return [dict(fb) for fb in feedback_list]

def acknowledge_feedback(feedback_id):
    """Mark feedback as acknowledged by employee"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE feedback SET acknowledged = 1 WHERE id = ?', (feedback_id,)
    )
    conn.commit()
    conn.close()

def get_sentiment_stats_for_manager(manager_id):
    """Get sentiment statistics for a manager's team"""
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT 
            COUNT(CASE WHEN sentiment = 'positive' THEN 1 END) as positive,
            COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral,
            COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative
        FROM feedback WHERE manager_id = ?
    ''', (manager_id,)).fetchone()
    conn.close()
    return dict(stats) if stats else {'positive': 0, 'neutral': 0, 'negative': 0}

def get_employee_feedback_summary(employee_ids):
    """Get feedback summary for a list of employees"""
    conn = get_db_connection()
    placeholders = ','.join('?' * len(employee_ids))
    summary = conn.execute(f'''
        SELECT employee_id, COUNT(*) as total_feedback,
               COUNT(CASE WHEN acknowledged = 1 THEN 1 END) as acknowledged_count
        FROM feedback 
        WHERE employee_id IN ({placeholders})
        GROUP BY employee_id
    ''', employee_ids).fetchall()
    conn.close()
    return {row['employee_id']: dict(row) for row in summary}