# FeedbackHub - Enterprise Performance Management Platform

A professional feedback management system designed for corporate environments, enabling structured performance reviews and team communication between managers and employees.

## Features

- **Corporate Login Interface**: Professional dual-portal authentication (Manager/Employee)
- **Manager Dashboard**: Team overview, performance analytics, and feedback management
- **Employee Dashboard**: Personal feedback timeline and acknowledgment system
- **Role-Based Access Control**: Secure authentication with proper authorization
- **SQLite Database**: Persistent data storage with proper relationships
- **Professional UI**: Bootstrap-based responsive design with corporate styling

## Tech Stack

### Backend
- **Flask 3.0.0**: Lightweight Python web framework
- **SQLite**: File-based database for development and small deployments
- **Werkzeug**: WSGI utilities and security features
- **python-dotenv**: Environment variable management

### Frontend
- **Bootstrap 5**: Professional CSS framework with dark theme
- **Font Awesome 6**: Icon library for UI elements
- **Vanilla JavaScript**: Client-side interactivity

### Security
- **Werkzeug Security**: Password hashing and verification
- **Session Management**: Flask session handling with secure cookies
- **Role-Based Authorization**: Manager/Employee access control

## Design Decisions

### Architecture
- **MVC Pattern**: Clean separation of concerns
- **SQLite Choice**: Simple file-based database perfect for development and small teams
- **Raw SQL**: Direct database queries for better performance and control
- **Session-Based Auth**: Traditional web authentication suitable for corporate environments

### Database Schema
- **Users Table**: Stores manager and employee accounts
- **Manager-Employee Relationships**: Many-to-many relationship for team management
- **Feedback Table**: Structured performance reviews with sentiment tracking

### UI/UX Design
- **Corporate Aesthetic**: Professional styling suitable for business environments
- **Responsive Design**: Works on desktop and mobile devices
- **Accessibility**: Proper contrast ratios and semantic HTML

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd feedback-hub
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   touch .env
   
   # Generate secret key
   python3 -c "import secrets; print(f'SESSION_SECRET={secrets.token_hex(32)}')" >> .env
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open browser to `http://localhost:5000`
   - Use demo credentials below

### Demo Credentials

**Manager Account:**
- Username: `manager1`
- Password: `password123`
- Name: Kunal

**Employee Accounts:**
- Username: `employee1` / Password: `password123` (Ankit)
- Username: `employee2` / Password: `password123` (Abhishek)

## Docker Setup

### Build and Run with Docker

1. **Build the Docker image**
   ```bash
   docker build -t feedback-hub .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 \
     -e SESSION_SECRET="your-secret-key-here" \
     -v $(pwd)/feedback.db:/app/feedback.db \
     feedback-hub
   ```

3. **Access the application**
   - Open browser to `http://localhost:5000`

### Docker Compose (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  feedback-hub:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SESSION_SECRET=your-secret-key-here
    volumes:
      - ./feedback.db:/app/feedback.db
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Project Structure

```
feedback-hub/
├── app.py                 # Flask application and configuration
├── models.py              # SQLite database functions
├── auth.py                # Authentication and authorization
├── routes.py              # Web routes and controllers
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker build configuration
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore patterns
├── feedback.db          # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── custom.css   # Custom styling
│   └── js/
│       └── main.js      # JavaScript functionality
└── templates/
    ├── base.html        # Base template
    ├── login.html       # Login interface
    ├── manager_dashboard.html
    ├── employee_dashboard.html
    ├── submit_feedback.html
    ├── edit_feedback.html
    └── feedback_history.html
```

## Development

### Adding New Features

1. **Database Changes**: Modify `models.py` for new tables or functions
2. **Routes**: Add new endpoints in `routes.py`
3. **Templates**: Create HTML templates in `templates/`
4. **Styling**: Update `static/css/custom.css` for UI changes

### Database Management

The SQLite database is automatically initialized with sample data on first run. To reset:

```bash
rm feedback.db
python app.py  # Will recreate with fresh sample data
```

### Environment Configuration

Required environment variables:
- `SESSION_SECRET`: Secure random key for session encryption

Optional environment variables:
- `FLASK_ENV`: Set to `development` for debug mode
- `DATABASE_PATH`: Custom path for SQLite database file

## Production Deployment

### Security Considerations

1. **Change Default Credentials**: Update sample user passwords
2. **Environment Variables**: Use secure secret management
3. **HTTPS**: Enable SSL/TLS in production
4. **Database**: Consider PostgreSQL for larger deployments
5. **Session Security**: Configure secure session settings

### Scaling Options

- **Database**: Migrate to PostgreSQL or MySQL for larger teams
- **Caching**: Add Redis for session storage and caching
- **Load Balancing**: Use nginx or similar for multiple instances
- **Monitoring**: Add logging and monitoring solutions

## API Endpoints

### Authentication
- `GET /` - Home page (redirects based on login status)
- `GET/POST /login` - Login interface
- `GET /logout` - Logout and clear session

### Manager Routes
- `GET /manager/dashboard` - Manager overview and team analytics
- `GET/POST /feedback/submit/<employee_id>` - Submit new feedback
- `GET/POST /feedback/edit/<feedback_id>` - Edit existing feedback

### Employee Routes  
- `GET /employee/dashboard` - Employee feedback timeline
- `GET /feedback/acknowledge/<feedback_id>` - Acknowledge feedback
- `GET /feedback/history/<employee_id>` - View feedback history

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the documentation above
2. Review the demo credentials and setup steps
3. Ensure all dependencies are properly installed
4. Verify environment variables are set correctly

## Changelog

- **v1.0.0** (June 2025): Initial release with core feedback management features
- SQLite database implementation
- Corporate login interface
- Manager and employee dashboards
- Role-based access control
- Professional UI design
