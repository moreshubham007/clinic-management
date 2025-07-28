#!/usr/bin/env python3
"""
Simple verification script for Waiting Area functionality
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_waiting_area():
    """Verify waiting area functionality"""
    try:
        print("🔍 Verifying Waiting Area functionality...")
        print("=" * 60)
        
        # Test 1: Check if we can import the app
        print("1. Testing imports...")
        try:
            from app import app
            from models import User, Doctor, Appointment, WaitingArea
            from extensions import db
            print("   ✅ All imports successful")
        except Exception as e:
            print(f"   ❌ Import error: {str(e)}")
            return False
        
        # Test 2: Check database connection
        print("2. Testing database connection...")
        try:
            with app.app_context():
                result = db.session.execute(db.text("SELECT 1")).scalar()
                print(f"   ✅ Database connection: {result}")
        except Exception as e:
            print(f"   ❌ Database error: {str(e)}")
            return False
        
        # Test 3: Check WaitingArea table
        print("3. Checking WaitingArea table...")
        try:
            with app.app_context():
                count = db.session.execute(db.text("SELECT COUNT(*) FROM waiting_area")).scalar()
                print(f"   ✅ WaitingArea table exists with {count} entries")
        except Exception as e:
            print(f"   ❌ WaitingArea table error: {str(e)}")
            return False
        
        # Test 4: Check if we have test data
        print("4. Checking test data...")
        try:
            with app.app_context():
                users = User.query.count()
                doctors = User.query.filter_by(role='doctor').count()
                patients = User.query.filter_by(role='patient').count()
                receptionists = User.query.filter_by(role='receptionist').count()
                
                print(f"   👥 Users: {users} total")
                print(f"   👨‍⚕️  Doctors: {doctors}")
                print(f"   👤 Patients: {patients}")
                print(f"   👩‍💼 Receptionists: {receptionists}")
                
                # Check appointments
                today = date.today()
                appointments = Appointment.query.filter(
                    Appointment.datetime >= today,
                    Appointment.datetime < today + timedelta(days=1)
                ).count()
                
                scheduled_appointments = Appointment.query.filter(
                    Appointment.datetime >= today,
                    Appointment.datetime < today + timedelta(days=1),
                    Appointment.status == 'scheduled'
                ).count()
                
                print(f"   📅 Appointments today: {appointments}")
                print(f"   ⏰ Scheduled appointments: {scheduled_appointments}")
                
        except Exception as e:
            print(f"   ❌ Data check error: {str(e)}")
            return False
        
        print("=" * 60)
        print("✅ Verification completed successfully!")
        print("\n📋 Summary:")
        print(f"   • Database: ✅ Connected")
        print(f"   • WaitingArea table: ✅ Available")
        print(f"   • Users: {users} total ({doctors} doctors, {patients} patients, {receptionists} receptionists)")
        print(f"   • Appointments: {appointments} today ({scheduled_appointments} scheduled)")
        
        if scheduled_appointments > 0 and doctors > 0 and patients > 0:
            print("\n🎉 Waiting Area is ready to use!")
            print("   • Receptionists can add patients from scheduled appointments")
            print("   • Doctors can manage their waiting lists")
            print("   • All database operations should work correctly")
        else:
            print("\n⚠️  Please create test data:")
            if scheduled_appointments == 0:
                print("   • Create appointments for today")
            if doctors == 0:
                print("   • Create doctor accounts")
            if patients == 0:
                print("   • Create patient accounts")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_waiting_area()
    if not success:
        sys.exit(1) 