# Clinic Management System

A comprehensive Flask application for managing clinic appointments, patient cases, and user interactions.

## Features

- Multi-user system with four roles:
  - Admin: Manage users and system settings
  - Doctor: Manage appointments, cases, and patient interactions
  - Receptionist: Manage appointments for all doctors
  - Patient: Book and manage appointments, view cases, and interact with doctors

- Appointment Management:
  - Create, update, and cancel appointments
  - View appointment schedules
  - Automatic email notifications

- Case Management:
  - Create and manage patient cases
  - Track case history
  - Transfer cases between doctors
  - Control patient access to case information

- Patient Features:
  - Google account login integration
  - Ask questions to doctors
  - View approved case histories
  - Provide feedback for doctors

- Doctor Features:
  - Manage appointments
  - Create and update cases
  - Answer patient questions
  - Transfer cases to other doctors

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/moreshubham007/clinic-management.git
cd clinic-management
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the MariaDB database:
```sql
CREATE DATABASE clinic_db;
```

5. Create a `.env` file with the following configuration:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
DATABASE_URL=mysql://username:password@localhost/clinic_db

# Google OAuth settings
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

6. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

7. Create an admin user:
```bash
flask create-admin
flask create-admin EMAIL NAME
flask create-admin admin@example.com "Admin User"
```

8. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## User Types and Permissions

### Admin
- Create and manage all user types
- View system statistics
- Manage system settings

### Doctor
- View and manage their appointments
- Create and manage patient cases
- Answer patient questions
- Transfer cases to other doctors
- View case histories

### Receptionist
- Manage appointments for all doctors
- View doctor schedules
- Handle patient check-ins

### Patient
- Book and manage appointments
- View their case history (if enabled by doctor)
- Ask questions to their doctors
- Provide feedback
- Login with Google account

## API Documentation

The application provides a RESTful API for integration with other systems. API documentation is available at `/api/docs` when running in development mode.

## Security Features

- Password hashing using bcrypt
- CSRF protection
- Secure session handling
- Role-based access control
- Google OAuth2 integration
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
