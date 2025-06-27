import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_patient_api():
    """Test the patient API endpoints"""
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "email": "patient@example.com",  # Replace with actual patient email
        "password": "password123"        # Replace with actual password
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/patient/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('token')
        print(f"✅ Login successful! Token: {token[:50]}...")
        
        # Step 2: Use token to get profile
        print("\n2. Getting patient profile...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        profile_response = requests.get(
            f"{BASE_URL}/api/patient/profile",
            headers=headers
        )
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print("✅ Profile retrieved successfully!")
            print(f"   Name: {profile.get('name')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   Patient Number: {profile.get('patient_number')}")
        else:
            print(f"❌ Profile request failed: {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
        
        # Step 3: Get appointments
        print("\n3. Getting patient appointments...")
        appointments_response = requests.get(
            f"{BASE_URL}/api/patient/appointments",
            headers=headers
        )
        
        if appointments_response.status_code == 200:
            appointments = appointments_response.json()
            print(f"✅ Retrieved {len(appointments)} appointments!")
            for apt in appointments:
                print(f"   - {apt.get('datetime')} with Dr. {apt.get('doctor', {}).get('name')}")
        else:
            print(f"❌ Appointments request failed: {appointments_response.status_code}")
            print(f"   Response: {appointments_response.text}")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        print("\n💡 Make sure you have a patient account with the correct email and password!")

if __name__ == "__main__":
    test_patient_api() 