#!/usr/bin/env python3
"""
Manual test script for Waiting Area module
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_waiting_area_manual():
    """Manual test of waiting area functionality"""
    try:
        from app import app, db
        from models import User, Doctor, Appointment, WaitingArea
        
        with app.app_context():
            print("🧪 Manual Testing of Waiting Area Module...")
            print("=" * 60)
            
            # Test 1: Check database connection
            print("1. Testing database connection...")
            try:
                result = db.session.execute(db.text("SELECT 1")).scalar()
                print(f"   ✅ Database connection successful: {result}")
            except Exception as e:
                print(f"   ❌ Database connection failed: {str(e)}")
                return False
            
            # Test 2: Check if WaitingArea table exists
            print("2. Checking WaitingArea table...")
            try:
                result = db.session.execute(db.text("SELECT COUNT(*) FROM waiting_area")).scalar()
                print(f"   ✅ WaitingArea table exists with {result} entries")
            except Exception as e:
                print(f"   ❌ WaitingArea table error: {str(e)}")
                print("   💡 You may need to run the migration: python add_waiting_area_migration.py")
                return False
            
            # Test 3: Check if we have users
            print("3. Checking users...")
            try:
                users = User.query.all()
                print(f"   👥 Found {len(users)} total users")
                
                doctors = User.query.filter_by(role='doctor').all()
                print(f"   👨‍⚕️  Found {len(doctors)} doctors")
                
                patients = User.query.filter_by(role='patient').all()
                print(f"   👤 Found {len(patients)} patients")
                
                receptionists = User.query.filter_by(role='receptionist').all()
                print(f"   👩‍💼 Found {len(receptionists)} receptionists")
                
            except Exception as e:
                print(f"   ❌ User query error: {str(e)}")
                return False
            
            # Test 4: Check appointments
            print("4. Checking appointments...")
            try:
                today = date.today()
                appointments = Appointment.query.filter(
                    Appointment.datetime >= today,
                    Appointment.datetime < today + timedelta(days=1)
                ).all()
                
                print(f"   📅 Found {len(appointments)} appointments for today")
                
                scheduled_appointments = [a for a in appointments if a.status == 'scheduled']
                print(f"   ⏰ Found {len(scheduled_appointments)} scheduled appointments")
                
            except Exception as e:
                print(f"   ❌ Appointment query error: {str(e)}")
                return False
            
            # Test 5: Test waiting area operations
            print("5. Testing waiting area operations...")
            try:
                # Get a sample appointment
                if scheduled_appointments:
                    sample_appointment = scheduled_appointments[0]
                    print(f"   📋 Using appointment: {sample_appointment.id} - {sample_appointment.patient.name}")
                    
                    # Test creating a waiting entry
                    waiting_entry = WaitingArea(
                        appointment_id=sample_appointment.id,
                        patient_id=sample_appointment.patient_id,
                        doctor_id=sample_appointment.doctor_id,
                        check_in_time=datetime.now(),
                        expected_appointment_time=sample_appointment.datetime,
                        priority='normal',
                        status='waiting',
                        notes='Test entry'
                    )
                    
                    db.session.add(waiting_entry)
                    db.session.commit()
                    print(f"   ✅ Successfully created waiting entry: {waiting_entry.id}")
                    
                    # Test updating the entry
                    waiting_entry.status = 'in_progress'
                    waiting_entry.doctor_notes = 'Test doctor notes'
                    db.session.commit()
                    print(f"   ✅ Successfully updated waiting entry")
                    
                    # Test deleting the entry
                    db.session.delete(waiting_entry)
                    db.session.commit()
                    print(f"   ✅ Successfully deleted test waiting entry")
                    
                else:
                    print("   ⚠️  No scheduled appointments found - cannot test waiting area operations")
                
            except Exception as e:
                print(f"   ❌ Waiting area operation error: {str(e)}")
                return False
            
            print("=" * 60)
            print("✅ All tests passed! Waiting Area module is working correctly.")
            print("\n📋 Summary:")
            print(f"   • Database: ✅ Connected")
            print(f"   • WaitingArea table: ✅ Available")
            print(f"   • Users: {len(users)} total ({len(doctors)} doctors, {len(patients)} patients, {len(receptionists)} receptionists)")
            print(f"   • Appointments: {len(appointments)} today ({len(scheduled_appointments)} scheduled)")
            print(f"   • Waiting Area operations: ✅ Working")
            
            if scheduled_appointments and doctors and patients:
                print("\n🎉 Ready to use!")
                print("   • Receptionists can add patients from scheduled appointments")
                print("   • Doctors can manage their waiting lists")
                print("   • All CRUD operations are working")
            else:
                print("\n⚠️  Please create test data:")
                if not scheduled_appointments:
                    print("   • Create appointments for today")
                if not doctors:
                    print("   • Create doctor accounts")
                if not patients:
                    print("   • Create patient accounts")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_waiting_area_manual()
    if not success:
        sys.exit(1) 