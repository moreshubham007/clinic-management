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
| GET | `/appointments` | ✅ | Get patient appointments |
| GET | `/appointments?status=scheduled` | ✅ | Get appointments by status |
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

### 2. Use Token
```bash
curl -X GET http://127.0.0.1:5000/api/patient/profile \
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
| 500 | Server Error |

## Test Files
- `test_api.py` - Python test script
- `test_api.html` - Browser test page
- `Patient_API_Postman_Collection.json` - Postman collection 