# Clinic Management System

A comprehensive hospital management system with role-based access for administrators, doctors, receptionists, and patients.

## Features

### 🏥 Multi-Role System
- **Admin**: System management, user management, analytics
- **Doctor**: Patient management, appointments, medical cases
- **Receptionist**: Appointment scheduling, patient registration
- **Patient**: View appointments, medical history, ask questions

### 📱 Patient API
- RESTful API for patient mobile applications
- JWT authentication
- Profile management
- Appointment tracking
- Medical case history
- Q&A system
- Feedback submission

### 🎨 Modern UI
- Responsive Bootstrap design
- Clean and intuitive interface
- Role-based navigation
- Real-time notifications

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL/PostgreSQL (or SQLite for development)
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clinic-management
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   flask db upgrade
   ```

5. **Create admin user**
   ```bash
   flask create-admin admin@example.com "Admin Name"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://127.0.0.1:5000`

## Patient API Documentation

### Overview
The Patient API provides secure access to patient functionality through RESTful endpoints with JWT authentication.

### Quick Start

1. **Login to get a token:**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/patient/login \
     -H "Content-Type: application/json" \
     -d '{"email": "patient@example.com", "password": "password123"}'
   ```

2. **Use the token for protected endpoints:**
   ```bash
   curl -X GET http://127.0.0.1:5000/api/patient/profile \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/patient/login` | Patient authentication |
| GET | `/api/patient/profile` | Get patient profile |
| GET | `/api/patient/appointments` | Get appointments |
| GET | `/api/patient/cases` | Get medical cases |
| GET | `/api/patient/questions` | Get questions |
| POST | `/api/patient/questions` | Ask new question |
| POST | `/api/patient/feedback` | Submit feedback |

### Testing Tools

- **📄 Complete Documentation**: `docs/Patient_API_Documentation.md`
- **⚡ Quick Reference**: `docs/API_Quick_Reference.md`
- **🐍 Python Test Script**: `test_api.py`
- **🌐 HTML Test Page**: `test_api.html`
- **📮 Postman Collection**: `Patient_API_Postman_Collection.json`

## API Testing

### Using Python Script
```bash
python test_api.py
```

### Using HTML Test Page
1. Open `test_api.html` in your browser
2. Enter patient credentials
3. Test all endpoints interactively

### Using Postman
1. Import `Patient_API_Postman_Collection.json`
2. Set up environment variables
3. Run the login request first
4. Test other endpoints

## Project Structure

```
clinic-management/
├── app.py                          # Main application file
├── models.py                       # Database models
├── requirements.txt                # Python dependencies
├── routes/                         # Route handlers
│   ├── auth.py                    # Authentication routes
│   ├── admin.py                   # Admin routes
│   ├── dashboard.py               # Dashboard routes
│   ├── patient.py                 # Patient web routes
│   ├── doctor.py                  # Doctor routes
│   ├── appointments.py            # Appointment routes
│   ├── cases.py                   # Medical case routes
│   └── api/                       # API routes
│       └── patient.py             # Patient API
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── auth/                      # Authentication templates
│   ├── dashboard/                 # Dashboard templates
│   └── ...
├── static/                        # Static files (CSS, JS, images)
├── docs/                          # Documentation
│   ├── Patient_API_Documentation.md
│   └── API_Quick_Reference.md
├── test_api.py                    # Python API test script
├── test_api.html                  # HTML API test page
└── Patient_API_Postman_Collection.json
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///clinic.db

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Database Models

### Core Entities
- **User**: Base user model with role-based access
- **Doctor**: Doctor-specific information and relationships
- **Appointment**: Patient-doctor appointments
- **Case**: Medical cases and treatment history
- **Question**: Patient-doctor Q&A system
- **Feedback**: Patient feedback for doctors

## Security Features

- JWT-based authentication for API
- Role-based access control
- Password hashing with bcrypt
- CSRF protection for web forms
- Session management
- Input validation and sanitization

## Development

### Running in Development Mode
```bash
python app.py
```

### Database Migrations
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Creating Test Data
```bash
# Create admin user
flask create-admin admin@example.com "Admin Name"

# Create test patients (via web interface or database)
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Ensure you're using the correct API endpoint (`/api/patient/login`)
   - Check that the token is valid and not expired
   - Verify the Authorization header format: `Bearer TOKEN`

2. **Database Connection Issues**
   - Check your DATABASE_URL in .env
   - Ensure the database server is running
   - Run `flask db upgrade` to create tables

3. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

### Debug Steps

1. **Check server status:**
   ```bash
   curl http://127.0.0.1:5000/test-db
   ```

2. **Test API login:**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/patient/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   ```

3. **Check logs:**
   - Application logs are in `logs/app.log`
   - Database queries are logged to console in debug mode

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the documentation in the `docs/` folder
2. Review the troubleshooting section
3. Check the test examples
4. Open an issue on GitHub

## Changelog

### v1.0.0
- Initial release
- Multi-role system
- Patient API with JWT authentication
- Modern responsive UI
- Complete documentation and testing tools 