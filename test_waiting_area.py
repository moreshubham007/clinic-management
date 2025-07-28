#!/usr/bin/env python3
"""
Test script for Waiting Area module
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Doctor, Appointment, WaitingArea

def test_waiting_area():
    """Test the waiting area functionality"""
    with app.app_context():
        try:
            print("🧪 Testing Waiting Area Module...")
            print("-" * 50)
            
            # Test 1: Check if WaitingArea table exists
            print("1. Checking WaitingArea table...")
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SHOW TABLES LIKE 'waiting_area'"))
                    if result.fetchone():
                        print("   ✅ WaitingArea table exists")
                    else:
                        print("   ❌ WaitingArea table not found")
                        return False
            except Exception as e:
                print(f"   ❌ Error checking table: {str(e)}")
                return False
            
            # Test 2: Check if we have any appointments for today
            print("2. Checking today's appointments...")
            today = date.today()
            appointments = Appointment.query.filter(
                Appointment.datetime >= today,
                Appointment.datetime < today + timedelta(days=1),
                Appointment.status == 'scheduled'
            ).all()
            
            print(f"   📅 Found {len(appointments)} scheduled appointments for today")
            
            if appointments:
                print("   ✅ Appointments found - receptionist can add patients to waiting area")
            else:
                print("   ⚠️  No appointments found - create some appointments first")
            
            # Test 3: Check if we have any doctors
            print("3. Checking doctors...")
            doctors = Doctor.query.all()
            print(f"   👨‍⚕️  Found {len(doctors)} doctors")
            
            if doctors:
                print("   ✅ Doctors found - doctor waiting area will work")
            else:
                print("   ⚠️  No doctors found - create doctor profiles first")
            
            # Test 4: Check if we have any patients
            print("4. Checking patients...")
            patients = User.query.filter_by(role='patient').all()
            print(f"   👥 Found {len(patients)} patients")
            
            if patients:
                print("   ✅ Patients found")
            else:
                print("   ⚠️  No patients found - create patient accounts first")
            
            # Test 5: Check current waiting area entries
            print("5. Checking current waiting area...")
            waiting_entries = WaitingArea.query.filter(
                WaitingArea.check_in_time >= today
            ).all()
            
            print(f"   ⏰ Found {len(waiting_entries)} patients in waiting area")
            
            # Test 6: Test URL routes
            print("6. Testing URL routes...")
            routes_to_test = [
                '/waiting-area/receptionist/waiting-area',
                '/waiting-area/doctor/waiting-area',
                '/waiting-area/api/waiting-stats',
                '/waiting-area/api/doctor-waiting-list'
            ]
            
            with app.test_client() as client:
                for route in routes_to_test:
                    response = client.get(route)
                    if response.status_code in [200, 302, 401]:  # 401 is expected for unauthenticated
                        print(f"   ✅ {route} - Status: {response.status_code}")
                    else:
                        print(f"   ❌ {route} - Status: {response.status_code}")
            
            print("-" * 50)
            print("✅ Waiting Area module test completed!")
            print("\n📋 Summary:")
            print(f"   • Appointments for today: {len(appointments)}")
            print(f"   • Doctors available: {len(doctors)}")
            print(f"   • Patients available: {len(patients)}")
            print(f"   • Current waiting entries: {len(waiting_entries)}")
            
            if appointments and doctors and patients:
                print("\n🎉 Waiting Area module is ready to use!")
                print("   Receptionists can add patients from today's appointments")
                print("   Doctors can view and manage their waiting lists")
            else:
                print("\n⚠️  Please create some test data first:")
                if not appointments:
                    print("   • Create appointments for today")
                if not doctors:
                    print("   • Create doctor profiles")
                if not patients:
                    print("   • Create patient accounts")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing waiting area: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_waiting_area()
    if not success:
        sys.exit(1) 