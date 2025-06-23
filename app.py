import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SQLite database
from models import init_database
init_database()

# Make functions available to templates
from auth import get_current_user
from models import get_user, get_employees_for_manager
from datetime import datetime

@app.context_processor
def inject_template_functions():
    def format_date(date_str):
        if not date_str:
            return 'N/A'
        try:
            if isinstance(date_str, str):
                # SQLite returns timestamps as strings
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%b %d, %Y at %I:%M %p')
            else:
                return date_str.strftime('%b %d, %Y at %I:%M %p')
        except:
            return str(date_str)
    
    return {
        'get_current_user': get_current_user,
        'get_user': get_user,
        'get_employees_for_manager': get_employees_for_manager,
        'format_date': format_date
    }

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)