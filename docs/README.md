# Documentation Index

Welcome to the Clinic Management System documentation. This directory contains comprehensive documentation for all aspects of the system.

## 📚 Documentation Files

### API Documentation
- **[Patient API Documentation](Patient_API_Documentation.md)** - Complete API reference with examples, error codes, and troubleshooting
- **[API Quick Reference](API_Quick_Reference.md)** - Concise endpoint summary and quick start guide

### Testing Tools
- **[test_api.py](../test_api.py)** - Python script for testing the Patient API
- **[test_api.html](../test_api.html)** - Interactive HTML page for API testing
- **[Patient_API_Postman_Collection.json](../Patient_API_Postman_Collection.json)** - Postman collection for API testing

## 🚀 Quick Start

### For Developers
1. Read the [API Quick Reference](API_Quick_Reference.md) for a quick overview
2. Use the [test_api.py](../test_api.py) script to test the API
3. Import the Postman collection for comprehensive testing

### For API Users
1. Start with the [Patient API Documentation](Patient_API_Documentation.md)
2. Use the provided testing tools to verify your implementation
3. Check the troubleshooting section for common issues

## 📖 Documentation Structure

```
docs/
├── README.md                           # This file - documentation index
├── Patient_API_Documentation.md        # Complete API documentation
└── API_Quick_Reference.md              # Quick reference guide
```

## 🔧 Testing Tools Overview

### Python Test Script (`test_api.py`)
- Complete API workflow demonstration
- Error handling examples
- Token management
- Response parsing

### HTML Test Page (`test_api.html`)
- Interactive browser-based testing
- User-friendly interface
- Real-time response display
- No installation required

### Postman Collection (`Patient_API_Postman_Collection.json`)
- Pre-configured requests
- Automatic token management
- Environment variables
- Complete endpoint coverage

## 📋 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/patient/login` | Patient authentication |
| GET | `/api/patient/profile` | Get patient profile |
| GET | `/api/patient/appointments` | Get appointments |
| GET | `/api/patient/cases` | Get medical cases |
| GET | `/api/patient/questions` | Get questions |
| POST | `/api/patient/questions` | Ask new question |
| POST | `/api/patient/feedback` | Submit feedback |

## 🛠️ Common Tasks

### Setting up API Testing
1. **Using Python:**
   ```bash
   python test_api.py
   ```

2. **Using HTML:**
   - Open `test_api.html` in your browser
   - Enter patient credentials
   - Test endpoints interactively

3. **Using Postman:**
   - Import `Patient_API_Postman_Collection.json`
   - Set environment variables
   - Run login request first

### Authentication Flow
1. Login with patient credentials
2. Extract JWT token from response
3. Include token in Authorization header
4. Access protected endpoints

### Error Handling
- Check HTTP status codes
- Review error message in response body
- Verify authentication token
- Ensure correct endpoint URLs

## 🔍 Troubleshooting

### Common Issues
1. **401 Unauthorized** - Check token validity and format
2. **404 Not Found** - Verify endpoint URL and server status
3. **400 Bad Request** - Check request body format and required fields

### Debug Steps
1. Test server connectivity
2. Verify login credentials
3. Check token expiration
4. Review request headers and body

## 📞 Support

For additional support:
1. Check the main [README.md](../README.md) file
2. Review the troubleshooting sections in the documentation
3. Use the provided testing tools to isolate issues
4. Check server logs for detailed error information

## 📝 Contributing to Documentation

To improve the documentation:
1. Update the relevant markdown files
2. Test all examples and code snippets
3. Ensure consistency across all documents
4. Update this index file if adding new documentation

---

**Last Updated:** January 2025  
**Version:** 1.0.0 