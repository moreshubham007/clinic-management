# Patient API Quick Reference

## Base URL
```
http://127.0.0.1:5000/api/patient
```

## Authentication
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/login` | ❌ | Patient login |
| GET | `/profile` | ✅ | Get patient profile |
| GET | `/appointments` | ✅ | Get all appointments |
| POST | `/appointments` | ✅ | Create new appointment |
| GET | `/appointments/{id}` | ✅ | Get appointment details |
| PUT | `/appointments/{id}` | ✅ | Update appointment |
| DELETE | `/appointments/{id}` | ✅ | Cancel appointment |
| GET | `/appointments/upcoming` | ✅ | Get upcoming appointments |
| GET | `/appointments/history` | ✅ | Get appointment history |
| GET | `/doctors` | ✅ | Get available doctors |
| GET | `/cases` | ✅ | Get patient medical cases |
| GET | `/questions` | ✅ | Get patient questions |
| POST | `/questions` | ✅ | Ask new question |
| POST | `/feedback` | ✅ | Submit doctor feedback |

## Quick Start

### 1. Login
```bash
curl -X POST http://127.0.0.1:5000/api/patient/login \
  -H "Content-Type: application/json" \
  -d '{"email": "patient@example.com", "password": "password123"}'
```

### 2. Create Appointment
```bash
curl -X POST http://127.0.0.1:5000/api/patient/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "datetime": "2025-01-20 14:00",
    "notes": "Follow-up consultation"
  }'
```

### 3. Get Upcoming Appointments
```bash
curl -X GET http://127.0.0.1:5000/api/patient/appointments/upcoming \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict (Time slot booked) |
| 500 | Server Error |

## Test Files
- `test_api.py` - Python test script
- `test_api.html` - Browser test page
- `Patient_API_Postman_Collection.json` - Postman collection 