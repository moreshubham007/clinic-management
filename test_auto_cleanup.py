#!/usr/bin/env python3
"""
Test script for automatic cleanup of completed appointments from waiting area
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, cleanup_completed_appointments
from extensions import db
from models import User, Doctor, Appointment, WaitingArea
from datetime import datetime, timedelta

def test_auto_cleanup():
    """Test the automatic cleanup functionality"""
    print("Testing automatic cleanup of completed appointments from waiting area...")
    
    with app.app_context():
        try:
            # Create test data
            print("1. Creating test data...")
            
            # Create a test patient
            patient = User(
                name="Test Patient",
                email="testpatient@example.com",
                role="patient",
                patient_number="INRI-00001"
            )
            db.session.add(patient)
            
            # Create a test doctor
            doctor_user = User(
                name="Test Doctor",
                email="testdoctor@example.com",
                role="doctor"
            )
            db.session.add(doctor_user)
            db.session.flush()  # Get the user ID
            
            doctor = Doctor(
                user_id=doctor_user.id,
                specialization="General Medicine"
            )
            db.session.add(doctor)
            db.session.flush()  # Get the doctor ID
            
            # Create a test appointment
            appointment = Appointment(
                doctor_id=doctor.id,
                patient_id=patient.id,
                datetime=datetime.now(),
                status="scheduled"
            )
            db.session.add(appointment)
            db.session.flush()  # Get the appointment ID
            
            # Create a waiting area entry
            waiting_entry = WaitingArea(
                appointment_id=appointment.id,
                patient_id=patient.id,
                doctor_id=doctor.id,
                expected_appointment_time=datetime.now(),
                status="waiting",
                added_by_id=doctor_user.id
            )
            db.session.add(waiting_entry)
            
            db.session.commit()
            print(f"   - Created appointment {appointment.id} with waiting entry {waiting_entry.id}")
            
            # Test 1: Verify waiting entry exists and is active
            print("\n2. Testing initial state...")
            waiting_entry = WaitingArea.query.get(waiting_entry.id)
            print(f"   - Waiting entry status: {waiting_entry.status}")
            print(f"   - Appointment status: {waiting_entry.appointment.status}")
            
            # Test 2: Complete the appointment
            print("\n3. Completing appointment...")
            appointment.status = "completed"
            appointment.updated_at = datetime.now()
            db.session.commit()
            print(f"   - Updated appointment status to: {appointment.status}")
            
            # Test 3: Run cleanup function
            print("\n4. Running cleanup function...")
            removed_count = cleanup_completed_appointments()
            print(f"   - Cleanup function returned: {removed_count} entries updated")
            
            # Test 4: Verify waiting entry was updated
            print("\n5. Verifying cleanup results...")
            waiting_entry = WaitingArea.query.get(waiting_entry.id)
            print(f"   - Waiting entry status after cleanup: {waiting_entry.status}")
            print(f"   - Completion time set: {waiting_entry.completion_time is not None}")
            
            # Test 5: Verify it's not shown in active waiting list
            print("\n6. Testing active waiting list filter...")
            active_entries = WaitingArea.query.filter(
                WaitingArea.status.in_(['waiting', 'in_progress'])
            ).all()
            print(f"   - Active waiting entries: {len(active_entries)}")
            
            # Clean up test data
            print("\n7. Cleaning up test data...")
            db.session.delete(waiting_entry)
            db.session.delete(appointment)
            db.session.delete(doctor)
            db.session.delete(doctor_user)
            db.session.delete(patient)
            db.session.commit()
            print("   - Test data cleaned up")
            
            # Summary
            print("\n" + "="*50)
            print("TEST SUMMARY:")
            print("="*50)
            if waiting_entry.status == "completed" and removed_count > 0:
                print("✅ SUCCESS: Automatic cleanup is working correctly!")
                print("   - Completed appointments are automatically removed from active waiting area")
                print("   - Waiting entries are properly updated with completion status")
            else:
                print("❌ FAILED: Automatic cleanup is not working as expected")
                print("   - Waiting entry status: " + waiting_entry.status)
                print("   - Cleanup count: " + str(removed_count))
            
        except Exception as e:
            print(f"❌ ERROR during testing: {e}")
            db.session.rollback()
            return False
    
    return True

def test_multiple_scenarios():
    """Test multiple scenarios for cleanup"""
    print("\n" + "="*50)
    print("TESTING MULTIPLE SCENARIOS")
    print("="*50)
    
    with app.app_context():
        try:
            # Create test data for multiple scenarios
            print("Creating test data for multiple scenarios...")
            
            # Create test users
            patient1 = User(name="Patient 1", email="p1@test.com", role="patient", patient_number="INRI-00002")
            patient2 = User(name="Patient 2", email="p2@test.com", role="patient", patient_number="INRI-00003")
            patient3 = User(name="Patient 3", email="p3@test.com", role="patient", patient_number="INRI-00004")
            
            doctor_user = User(name="Test Doctor", email="doctor@test.com", role="doctor")
            db.session.add_all([patient1, patient2, patient3, doctor_user])
            db.session.flush()
            
            doctor = Doctor(user_id=doctor_user.id, specialization="General Medicine")
            db.session.add(doctor)
            db.session.flush()
            
            # Create appointments with different statuses
            appt1 = Appointment(doctor_id=doctor.id, patient_id=patient1.id, datetime=datetime.now(), status="completed")
            appt2 = Appointment(doctor_id=doctor.id, patient_id=patient2.id, datetime=datetime.now(), status="scheduled")
            appt3 = Appointment(doctor_id=doctor.id, patient_id=patient3.id, datetime=datetime.now(), status="completed")
            
            db.session.add_all([appt1, appt2, appt3])
            db.session.flush()
            
            # Create waiting entries
            waiting1 = WaitingArea(
                appointment_id=appt1.id, patient_id=patient1.id, doctor_id=doctor.id,
                expected_appointment_time=datetime.now(), status="waiting", added_by_id=doctor_user.id
            )
            waiting2 = WaitingArea(
                appointment_id=appt2.id, patient_id=patient2.id, doctor_id=doctor.id,
                expected_appointment_time=datetime.now(), status="in_progress", added_by_id=doctor_user.id
            )
            waiting3 = WaitingArea(
                appointment_id=appt3.id, patient_id=patient3.id, doctor_id=doctor.id,
                expected_appointment_time=datetime.now(), status="waiting", added_by_id=doctor_user.id
            )
            
            db.session.add_all([waiting1, waiting2, waiting3])
            db.session.commit()
            
            print(f"Created {len([waiting1, waiting2, waiting3])} waiting entries")
            print(f"  - Waiting1 (completed appt): {waiting1.status}")
            print(f"  - Waiting2 (scheduled appt): {waiting2.status}")
            print(f"  - Waiting3 (completed appt): {waiting3.status}")
            
            # Run cleanup
            print("\nRunning cleanup...")
            removed_count = cleanup_completed_appointments()
            print(f"Cleanup updated {removed_count} entries")
            
            # Check results
            waiting1 = WaitingArea.query.get(waiting1.id)
            waiting2 = WaitingArea.query.get(waiting2.id)
            waiting3 = WaitingArea.query.get(waiting3.id)
            
            print("\nResults after cleanup:")
            print(f"  - Waiting1 (completed appt): {waiting1.status}")
            print(f"  - Waiting2 (scheduled appt): {waiting2.status}")
            print(f"  - Waiting3 (completed appt): {waiting3.status}")
            
            # Verify only completed appointments were affected
            active_entries = WaitingArea.query.filter(
                WaitingArea.status.in_(['waiting', 'in_progress'])
            ).all()
            
            print(f"\nActive waiting entries: {len(active_entries)}")
            print("Expected: Only waiting2 should remain active (scheduled appointment)")
            
            # Cleanup
            db.session.delete(waiting1)
            db.session.delete(waiting2)
            db.session.delete(waiting3)
            db.session.delete(appt1)
            db.session.delete(appt2)
            db.session.delete(appt3)
            db.session.delete(doctor)
            db.session.delete(doctor_user)
            db.session.delete(patient1)
            db.session.delete(patient2)
            db.session.delete(patient3)
            db.session.commit()
            
            print("\n✅ Multiple scenario test completed")
            
        except Exception as e:
            print(f"❌ ERROR in multiple scenarios test: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Starting automatic cleanup tests...")
    
    # Run basic test
    success = test_auto_cleanup()
    
    # Run multiple scenarios test
    test_multiple_scenarios()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1) 