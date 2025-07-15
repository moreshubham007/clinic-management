#!/usr/bin/env python3
"""
Patient API Test Script

This script demonstrates how to use the Patient API endpoints.
It includes examples for authentication, profile management, and appointment operations.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api/patient"

# Test credentials (update these with actual patient credentials)
TEST_EMAIL = "shubham@vellichormedia.com"
TEST_PASSWORD = "shubham@vellichormedia.com"

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*50}")

def test_login():
    """Test patient login"""
    print("\n🔐 Testing Patient Login...")
    
    url = f"{API_BASE}/login"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print_response(response, "LOGIN RESPONSE")
    
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print("❌ Login failed. Please check credentials.")
        return None

def test_profile(token):
    """Test getting patient profile"""
    print("\n👤 Testing Get Profile...")
    
    url = f"{API_BASE}/profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "PROFILE RESPONSE")

def test_get_doctors(token):
    """Test getting available doctors"""
    print("\n👨‍⚕️ Testing Get Doctors...")
    
    url = f"{API_BASE}/doctors"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "DOCTORS RESPONSE")
    
    if response.status_code == 200:
        doctors = response.json()
        if doctors:
            return doctors[0]["id"]  # Return first doctor's ID for testing
    return None

def test_create_appointment(token, doctor_id):
    """Test creating a new appointment"""
    print("\n📅 Testing Create Appointment...")
    
    url = f"{API_BASE}/appointments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create appointment for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    data = {
        "doctor": {
            "id": doctor_id
        },
        "datetime": appointment_time.strftime("%Y-%m-%d %H:%M"),
        "notes": "Test appointment created via API",
        "patient_type": "existing",
        "priority": "medium"
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "CREATE APPOINTMENT RESPONSE")
    
    if response.status_code == 201:
        return response.json().get("appointment", {}).get("id")
    return None

def test_get_appointments(token):
    """Test getting all appointments"""
    print("\n📋 Testing Get All Appointments...")
    
    url = f"{API_BASE}/appointments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "ALL APPOINTMENTS RESPONSE")

def test_get_appointment_details(token, appointment_id):
    """Test getting appointment details"""
    print(f"\n📄 Testing Get Appointment Details (ID: {appointment_id})...")
    
    url = f"{API_BASE}/appointments/{appointment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "APPOINTMENT DETAILS RESPONSE")

def test_update_appointment(token, appointment_id):
    """Test updating an appointment"""
    print(f"\n✏️ Testing Update Appointment (ID: {appointment_id})...")
    
    url = f"{API_BASE}/appointments/{appointment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Update appointment for day after tomorrow
    day_after_tomorrow = datetime.now() + timedelta(days=2)
    new_time = day_after_tomorrow.replace(hour=15, minute=30, second=0, microsecond=0)
    
    data = {
        "datetime": new_time.strftime("%Y-%m-%d %H:%M"),
        "notes": "Updated appointment notes via API",
        "priority": "high"
    }
    
    response = requests.put(url, json=data, headers=headers)
    print_response(response, "UPDATE APPOINTMENT RESPONSE")

def test_get_upcoming_appointments(token):
    """Test getting upcoming appointments"""
    print("\n🔮 Testing Get Upcoming Appointments...")
    
    url = f"{API_BASE}/appointments/upcoming?days=7"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "UPCOMING APPOINTMENTS RESPONSE")

def test_get_appointment_history(token):
    """Test getting appointment history"""
    print("\n📚 Testing Get Appointment History...")
    
    url = f"{API_BASE}/appointments/history?limit=5"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "APPOINTMENT HISTORY RESPONSE")

def test_cancel_appointment(token, appointment_id):
    """Test cancelling an appointment"""
    print(f"\n❌ Testing Cancel Appointment (ID: {appointment_id})...")
    
    url = f"{API_BASE}/appointments/{appointment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(url, headers=headers)
    print_response(response, "CANCEL APPOINTMENT RESPONSE")

def test_get_cases(token):
    """Test getting patient cases"""
    print("\n🏥 Testing Get Cases...")
    
    url = f"{API_BASE}/cases"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "CASES RESPONSE")

def test_get_questions(token):
    """Test getting patient questions"""
    print("\n❓ Testing Get Questions...")
    
    url = f"{API_BASE}/questions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response, "QUESTIONS RESPONSE")

def test_ask_question(token, doctor_id):
    """Test asking a new question"""
    print("\n💬 Testing Ask Question...")
    
    url = f"{API_BASE}/questions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "doctor": {
            "id": doctor_id
        },
        "question": "What are the side effects of the prescribed medication?",
        "is_private": False
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "ASK QUESTION RESPONSE")

def test_submit_feedback(token, doctor_id):
    """Test submitting feedback"""
    print("\n⭐ Testing Submit Feedback...")
    
    url = f"{API_BASE}/feedback"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "doctor": {
            "id": doctor_id
        },
        "rating": 5,
        "comment": "Excellent service and very professional doctor.",
        "is_anonymous": False
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "SUBMIT FEEDBACK RESPONSE")

def main():
    """Main test function"""
    print("🚀 Patient API Test Script")
    print("This script will test all Patient API endpoints")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # Test profile
    test_profile(token)
    
    # Test getting doctors
    doctor_id = test_get_doctors(token)
    if not doctor_id:
        print("❌ No doctors available for testing")
        return
    
    # Test appointment operations
    test_create_appointment(token, doctor_id)
    test_get_appointments(token)
    
    # Get the created appointment ID for further testing
    appointments_response = requests.get(
        f"{API_BASE}/appointments",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    
    if appointments_response.status_code == 200:
        appointments = appointments_response.json()
        if appointments:
            appointment_id = appointments[0]["id"]
            
            # Test appointment details and updates
            test_get_appointment_details(token, appointment_id)
            test_update_appointment(token, appointment_id)
            
            # Test upcoming and history
            test_get_upcoming_appointments(token)
            test_get_appointment_history(token)
            
            # Test cancellation
            test_cancel_appointment(token, appointment_id)
    
    # Test other endpoints
    test_get_cases(token)
    test_get_questions(token)
    test_ask_question(token, doctor_id)
    test_submit_feedback(token, doctor_id)
    
    print("\n🎉 All tests completed!")
    print("\n📝 Notes:")
    print("- Some endpoints may return empty results if no data exists")
    print("- Check the response status codes and messages for details")
    print("- Use the HTML test page (test_api.html) for interactive testing")

if __name__ == "__main__":
    main() 