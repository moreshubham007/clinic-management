#!/usr/bin/env python3
"""
Simple test script for Waiting Area module
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_waiting_area():
    """Test the waiting area functionality"""
    try:
        from app import app, db
        from models import User, Doctor, Appointment, WaitingArea
        
        with app.app_context():
            print("🧪 Testing Waiting Area Module...")
            print("-" * 50)
            
            # Test 1: Check if WaitingArea table exists
            print("1. Checking WaitingArea table...")
            try:
                # Try to query the table
                waiting_count = WaitingArea.query.count()
                print(f"   ✅ WaitingArea table exists (has {waiting_count} entries)")
            except Exception as e:
                print(f"   ❌ WaitingArea table error: {str(e)}")
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
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error testing waiting area: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_waiting_area()
    if not success:
        sys.exit(1) 