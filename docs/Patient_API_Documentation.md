# Patient API Documentation

## Overview

The Patient API provides secure access to patient-related functionality including profile management, appointments, medical cases, questions, and feedback. All endpoints (except login) require JWT authentication.

## Base URL

```
http://127.0.0.1:5000/api/patient
```

## Authentication

The API uses JWT (JSON Web Token) authentication. You must first login to obtain a token, then include it in the Authorization header for all subsequent requests.

### Getting a Token

**Endpoint:** `POST /api/patient/login`

**Request Body:**
```json
{
  "email": "patient@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "patient@example.com",
    "patient_number": "INRI-12345"
  }
}
```

### Using the Token

Include the token in the Authorization header for all protected endpoints:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## API Endpoints

### 1. Authentication

#### Patient Login
- **URL:** `POST /api/patient/login`
- **Description:** Authenticate a patient and receive a JWT token
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "patient@example.com",
    "password": "password123"
  }
  ```
- **Response (200):**
  ```json
  {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "patient@example.com",
      "patient_number": "INRI-12345"
    }
  }
  ```
- **Response (401):**
  ```json
  {
    "message": "Invalid credentials"
  }
  ```

### 2. Profile Management

#### Get Patient Profile
- **URL:** `GET /api/patient/profile`
- **Description:** Retrieve the authenticated patient's profile information
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  {
    "id": 1,
    "name": "John Doe",
    "email": "patient@example.com",
    "patient_number": "INRI-12345",
    "mobile_number": "+91-9876543210",
    "gender": "male",
    "date_of_birth": "1990-01-01",
    "address": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pin_code": "400001"
  }
  ```

### 3. Appointment Management

#### Get All Appointments
- **URL:** `GET /api/patient/appointments`
- **Description:** Retrieve all appointments for the authenticated patient
- **Authentication:** Required (Bearer token)
- **Query Parameters:**
  - `status` (optional): Filter by appointment status (`scheduled`, `completed`, `cancelled`)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "datetime": "2025-01-15 10:00",
      "status": "scheduled",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      },
      "notes": "Regular checkup",
      "patient_type": "existing",
      "priority": "medium",
      "created_at": "2025-01-10 14:30"
    }
  ]
  ```

#### Create New Appointment
- **URL:** `POST /api/patient/appointments`
- **Description:** Create a new appointment with a doctor
- **Authentication:** Required (Bearer token)
- **Request Body:**
  ```json
  {
    "doctor_id": 1,
    "datetime": "2025-01-20 14:00",
    "notes": "Follow-up consultation",
    "patient_type": "existing",
    "priority": "medium"
  }
  ```
- **Response (201):**
  ```json
  {
    "message": "Appointment created successfully",
    "appointment": {
      "id": 2,
      "datetime": "2025-01-20 14:00",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      },
      "status": "scheduled"
    }
  }
  ```
- **Response (409):**
  ```json
  {
    "message": "This time slot is already booked"
  }
  ```

#### Get Appointment Details
- **URL:** `GET /api/patient/appointments/{appointment_id}`
- **Description:** Get detailed information about a specific appointment
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  {
    "id": 1,
    "datetime": "2025-01-15 10:00",
    "status": "scheduled",
    "doctor": {
      "id": 1,
      "name": "Dr. Smith",
      "specialization": "Cardiology"
    },
    "notes": "Regular checkup",
    "patient_type": "existing",
    "priority": "medium",
    "created_at": "2025-01-10 14:30",
    "updated_at": "2025-01-12 09:15"
  }
  ```

#### Update Appointment
- **URL:** `PUT /api/patient/appointments/{appointment_id}`
- **Description:** Update an existing appointment (only scheduled appointments)
- **Authentication:** Required (Bearer token)
- **Request Body:**
  ```json
  {
    "datetime": "2025-01-20 15:00",
    "notes": "Updated consultation notes",
    "priority": "high"
  }
  ```
- **Response (200):**
  ```json
  {
    "message": "Appointment updated successfully",
    "appointment": {
      "id": 1,
      "datetime": "2025-01-20 15:00",
      "status": "scheduled"
    }
  }
  ```

#### Cancel Appointment
- **URL:** `DELETE /api/patient/appointments/{appointment_id}`
- **Description:** Cancel a scheduled appointment
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  {
    "message": "Appointment cancelled successfully"
  }
  ```

#### Get Upcoming Appointments
- **URL:** `GET /api/patient/appointments/upcoming`
- **Description:** Get upcoming scheduled appointments
- **Authentication:** Required (Bearer token)
- **Query Parameters:**
  - `days` (optional): Number of days to look ahead (default: 7)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "datetime": "2025-01-15 10:00",
      "status": "scheduled",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      },
      "notes": "Regular checkup",
      "days_until": 3
    }
  ]
  ```

#### Get Appointment History
- **URL:** `GET /api/patient/appointments/history`
- **Description:** Get past appointments
- **Authentication:** Required (Bearer token)
- **Query Parameters:**
  - `limit` (optional): Number of appointments to return (default: 10)
  - `status` (optional): Filter by status (`completed`, `cancelled`)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "datetime": "2025-01-10 10:00",
      "status": "completed",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      },
      "notes": "Regular checkup",
      "days_ago": 5
    }
  ]
  ```

### 4. Doctor Management

#### Get Available Doctors
- **URL:** `GET /api/patient/doctors`
- **Description:** Get list of all available doctors
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "name": "Dr. Smith",
      "specialization": "Cardiology",
      "email": "dr.smith@hospital.com"
    }
  ]
  ```

### 5. Medical Cases

#### Get Patient Cases
- **URL:** `GET /api/patient/cases`
- **Description:** Retrieve medical cases for the authenticated patient
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "diagnosis": "Hypertension",
      "treatment": "Prescribed medication and lifestyle changes",
      "status": "active",
      "created_at": "2025-01-10T09:00:00",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      }
    }
  ]
  ```

### 6. Questions & Answers

#### Get Patient Questions
- **URL:** `GET /api/patient/questions`
- **Description:** Retrieve all questions asked by the authenticated patient
- **Authentication:** Required (Bearer token)
- **Response (200):**
  ```json
  [
    {
      "id": 1,
      "question": "What are the side effects of the medication?",
      "answer": "Common side effects include dizziness and nausea...",
      "created_at": "2025-01-12T14:30:00",
      "answered_at": "2025-01-12T15:00:00",
      "doctor": {
        "id": 1,
        "name": "Dr. Smith"
      }
    }
  ]
  ```

#### Ask New Question
- **URL:** `POST /api/patient/questions`
- **Description:** Submit a new question to a doctor
- **Authentication:** Required (Bearer token)
- **Request Body:**
  ```json
  {
    "doctor_id": 1,
    "question": "What are the side effects of the medication?",
    "is_private": false
  }
  ```
- **Response (201):**
  ```json
  {
    "message": "Question submitted successfully",
    "id": 1
  }
  ```

### 7. Feedback

#### Submit Feedback
- **URL:** `POST /api/patient/feedback`
- **Description:** Submit feedback for a doctor
- **Authentication:** Required (Bearer token)
- **Request Body:**
  ```json
  {
    "doctor_id": 1,
    "rating": 5,
    "comment": "Excellent service and very professional doctor.",
    "is_anonymous": false
  }
  ```
- **Response (201):**
  ```json
  {
    "message": "Feedback submitted successfully"
  }
  ```

## Error Responses

### Common Error Codes

#### 400 Bad Request
```json
{
  "message": "Missing email or password"
}
```

#### 401 Unauthorized
```json
{
  "message": "Invalid credentials"
}
```

#### 403 Forbidden
```json
{
  "message": "Not a patient account"
}
```

#### 404 Not Found
```json
{
  "message": "Resource not found"
}
```

#### 409 Conflict
```json
{
  "message": "This time slot is already booked"
}
```

#### 500 Internal Server Error
```json
{
  "message": "Internal server error"
}
```

## Usage Examples

### cURL Examples

#### 1. Login
```bash
curl -X POST http://127.0.0.1:5000/api/patient/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'
```

#### 2. Get Profile (with token)
```bash
curl -X GET http://127.0.0.1:5000/api/patient/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 3. Create Appointment
```bash
curl -X POST http://127.0.0.1:5000/api/patient/appointments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "datetime": "2025-01-20 14:00",
    "notes": "Follow-up consultation",
    "patient_type": "existing",
    "priority": "medium"
  }'
```

#### 4. Get Upcoming Appointments
```bash
curl -X GET http://127.0.0.1:5000/api/patient/appointments/upcoming?days=7 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

#### 5. Update Appointment
```bash
curl -X PUT http://127.0.0.1:5000/api/patient/appointments/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "2025-01-20 15:00",
    "notes": "Updated consultation notes"
  }'
```

#### 6. Cancel Appointment
```bash
curl -X DELETE http://127.0.0.1:5000/api/patient/appointments/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### Python Examples

```python
import requests

# Base URL
BASE_URL = "http://127.0.0.1:5000"

# 1. Login
def login(email, password):
    response = requests.post(
        f"{BASE_URL}/api/patient/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# 2. Create appointment
def create_appointment(token, doctor_id, datetime_str, notes=None):
    response = requests.post(
        f"{BASE_URL}/api/patient/appointments",
        json={
            "doctor_id": doctor_id,
            "datetime": datetime_str,
            "notes": notes,
            "patient_type": "existing",
            "priority": "medium"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    return response.json()

# 3. Get upcoming appointments
def get_upcoming_appointments(token, days=7):
    response = requests.get(
        f"{BASE_URL}/api/patient/appointments/upcoming?days={days}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    return response.json()

# Usage
login_data = login("patient@example.com", "password123")
token = login_data["token"]

# Create appointment
appointment = create_appointment(token, 1, "2025-01-20 14:00", "Follow-up consultation")
print(f"Appointment created: {appointment}")

# Get upcoming appointments
upcoming = get_upcoming_appointments(token)
print(f"Upcoming appointments: {upcoming}")
```

### JavaScript Examples

```javascript
const BASE_URL = 'http://127.0.0.1:5000';

// 1. Login
async function login(email, password) {
    const response = await fetch(`${BASE_URL}/api/patient/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });
    return response.json();
}

// 2. Create appointment
async function createAppointment(token, doctorId, datetime, notes) {
    const response = await fetch(`${BASE_URL}/api/patient/appointments`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            doctor_id: doctorId,
            datetime: datetime,
            notes: notes,
            patient_type: 'existing',
            priority: 'medium'
        })
    });
    return response.json();
}

// 3. Get upcoming appointments
async function getUpcomingAppointments(token, days = 7) {
    const response = await fetch(`${BASE_URL}/api/patient/appointments/upcoming?days=${days}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    return response.json();
}

// Usage
login('patient@example.com', 'password123')
    .then(data => {
        const token = data.token;
        return createAppointment(token, 1, '2025-01-20 14:00', 'Follow-up consultation');
    })
    .then(appointment => {
        console.log('Appointment created:', appointment);
        return getUpcomingAppointments(token);
    })
    .then(upcoming => console.log('Upcoming appointments:', upcoming));
```

## Postman Collection

A complete Postman collection is available at `Patient_API_Postman_Collection.json` that includes:

- All API endpoints
- Pre-configured authentication
- Automatic token management
- Example request bodies
- Environment variables

### Import Instructions:

1. Open Postman
2. Click "Import"
3. Select `Patient_API_Postman_Collection.json`
4. Set up environment variables:
   - `base_url`: `http://127.0.0.1:5000`
   - `token`: (will be auto-filled after login)

## Testing Tools

### HTML Test Page

An interactive test page is available at `test_api.html` that allows you to:

- Login with patient credentials
- Test all API endpoints
- View responses in a user-friendly format
- Debug authentication issues

### Python Test Script

A Python test script is available at `test_api.py` that demonstrates:

- Complete API workflow
- Error handling
- Response parsing
- Token management

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized Error
**Problem:** Getting 401 errors on protected endpoints
**Solution:** 
- Make sure you've logged in first
- Check that the token is valid and not expired
- Ensure the Authorization header format is correct: `Bearer TOKEN`

#### 2. 404 Not Found Error
**Problem:** Endpoint not found
**Solution:**
- Verify the URL is correct (should start with `/api/patient/`)
- Check that the Flask server is running
- Ensure the endpoint exists in the API

#### 3. 400 Bad Request Error
**Problem:** Invalid request data
**Solution:**
- Check that all required fields are provided
- Verify JSON format is correct
- Ensure Content-Type header is set to `application/json`

#### 4. 409 Conflict Error
**Problem:** Time slot already booked
**Solution:**
- Choose a different time slot
- Check doctor availability
- Use the doctors endpoint to get available doctors

#### 5. Token Expired
**Problem:** Getting 401 errors after successful login
**Solution:**
- Tokens expire after 7 days
- Re-login to get a new token
- Store tokens securely and refresh when needed

### Debug Steps

1. **Check Server Status:**
   ```bash
   curl http://127.0.0.1:5000/test-db
   ```

2. **Verify Login:**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/patient/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   ```

3. **Test Token:**
   ```bash
   curl -X GET http://127.0.0.1:5000/api/patient/profile \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Security Considerations

1. **Token Security:**
   - Store tokens securely
   - Don't expose tokens in client-side code
   - Use HTTPS in production

2. **Password Security:**
   - Use strong passwords
   - Never send passwords in plain text over HTTP
   - Implement password reset functionality

3. **Rate Limiting:**
   - Implement rate limiting for login attempts
   - Monitor for suspicious activity

4. **Data Privacy:**
   - Only return necessary patient data
   - Implement proper access controls
   - Log access for audit purposes

## Rate Limits

Currently, there are no rate limits implemented. Consider implementing rate limiting for production use:

- Login attempts: 5 per minute per IP
- API calls: 100 per minute per user
- File uploads: 10 per hour per user

## Versioning

Current API version: v1

Future versions will be available at:
- v2: `/api/v2/patient/`
- v3: `/api/v3/patient/`

## Support

For API support and questions:

1. Check this documentation first
2. Review the test examples
3. Use the provided test tools
4. Check server logs for detailed error messages

## Changelog

### v1.0.0 (Current)
- Initial API release
- JWT authentication
- Patient profile management
- Complete appointment management (CRUD operations)
- Doctor availability
- Medical cases
- Questions and answers
- Feedback system 