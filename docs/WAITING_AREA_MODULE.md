# Waiting Area Module

## Overview

The Waiting Area module is a comprehensive solution for managing patient wait times and appointment flow in the clinic. It provides real-time tracking of patient wait times, priority management, and alerts for long waits.

## Features

### For Receptionists
- **Add patients to waiting area**: Select from today's scheduled appointments
- **Real-time wait time tracking**: Automatic calculation of wait times
- **Priority management**: Set urgent, high, normal, or low priority
- **Notes and comments**: Add receptionist notes for each patient
- **Statistics dashboard**: View waiting area statistics
- **Long wait alerts**: Automatic alerts for patients waiting >1 hour

### For Doctors
- **Patient waiting list**: View all patients waiting for their appointments
- **Start appointments**: Move patients from waiting to in-progress
- **Complete appointments**: Mark appointments as completed with notes
- **Long wait notifications**: Visual alerts for patients waiting >1-2 hours
- **Real-time updates**: Auto-refresh every 30 seconds
- **Statistics view**: Track performance metrics

## Database Schema

### WaitingArea Model
```python
class WaitingArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    
    # Time tracking
    check_in_time = db.Column(db.DateTime, default=datetime.now)
    expected_appointment_time = db.Column(db.DateTime, nullable=False)
    actual_start_time = db.Column(db.DateTime)
    completion_time = db.Column(db.DateTime)
    
    # Status tracking
    status = db.Column(db.String(20), default='waiting')  # waiting, in_progress, completed, cancelled
    priority = db.Column(db.String(10), default='normal')  # urgent, high, normal, low
    
    # Additional details
    notes = db.Column(db.Text)  # Receptionist notes
    doctor_notes = db.Column(db.Text)  # Doctor's notes
    wait_time_minutes = db.Column(db.Integer)
    
    # Created by
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

## Installation & Setup

### 1. Run the Migration
```bash
python run_waiting_area_migration.py
```

### 2. Restart the Flask Application
```bash
python app.py
```

### 3. Access the Module
- **Receptionist View**: `/waiting-area/receptionist/waiting-area`
- **Doctor View**: `/waiting-area/doctor/waiting-area`

## Usage Guide

### Receptionist Workflow

1. **Access Waiting Area**
   - Navigate to "Waiting Area" in the sidebar menu
   - View today's scheduled appointments and current waiting list

2. **Add Patient to Waiting Area**
   - Select a patient from "Today's Scheduled Appointments"
   - Click "Add to Waiting" button
   - Set priority level (urgent, high, normal, low)
   - Add any notes or special instructions
   - Confirm to add patient to waiting area

3. **Manage Waiting List**
   - View all patients currently in waiting area
   - Edit patient details (priority, notes)
   - Remove patients from waiting area if needed
   - Monitor wait times and long wait alerts

4. **Monitor Statistics**
   - View real-time statistics
   - Track total waiting, in-progress, and completed patients
   - Monitor long wait alerts (>1 hour)

### Doctor Workflow

1. **View Waiting List**
   - Access "Waiting Area" from sidebar menu
   - View all patients waiting for appointments
   - See wait times, priorities, and patient details

2. **Start Appointment**
   - Click "Start" button next to a waiting patient
   - Patient status changes from "waiting" to "in-progress"
   - Check-in time is recorded

3. **Complete Appointment**
   - Click "Complete" button for in-progress patients
   - Add doctor notes about the appointment
   - Patient status changes to "completed"
   - Completion time is recorded

4. **Monitor Long Waits**
   - Visual alerts for patients waiting >1 hour
   - Red highlighting for patients waiting >2 hours
   - Statistics dashboard for performance tracking

## API Endpoints

### Waiting Statistics
```
GET /waiting-area/api/waiting-stats
```
Returns:
- Total waiting patients
- Total in-progress patients
- Total completed patients
- Long wait alerts
- Average wait time
- List of patients waiting >1 hour

### Doctor Waiting List
```
GET /waiting-area/api/doctor-waiting-list
```
Returns:
- List of patients waiting for the doctor
- Wait times, priorities, and status
- Patient details and notes

## Wait Time Calculations

### Automatic Calculations
- **Current Wait Time**: Time since check-in for waiting patients
- **Completed Wait Time**: Time from check-in to actual start for completed appointments
- **Long Wait Alert**: Triggered when wait time > 60 minutes
- **Very Long Wait Alert**: Triggered when wait time > 120 minutes

### Wait Status Categories
- **Normal**: < 30 minutes
- **Moderate**: 30-60 minutes
- **Long**: 60-120 minutes
- **Very Long**: > 120 minutes

## Security & Permissions

### Role-Based Access
- **Receptionists**: Can add, edit, and remove patients from waiting area
- **Doctors**: Can view their waiting list and manage appointments
- **Admins**: Full access to all waiting areas and statistics

### Data Validation
- Only today's appointments can be added to waiting area
- Patients can only be in waiting area once per appointment
- Doctors can only manage their own appointments
- All actions are logged with user information

## Real-Time Features

### Auto-Refresh
- Waiting lists refresh every 30 seconds
- Statistics update automatically
- Long wait alerts appear in real-time

### Visual Indicators
- **Green**: Normal wait times
- **Yellow**: Moderate wait times (30-60 min)
- **Orange**: Long wait times (60-120 min)
- **Red**: Very long wait times (>120 min)

## Troubleshooting

### Common Issues

1. **Patient not appearing in waiting area**
   - Check if appointment is scheduled for today
   - Verify appointment status is "scheduled"
   - Ensure patient isn't already in waiting area

2. **Wait times not updating**
   - Refresh the page
   - Check if auto-refresh is enabled
   - Verify server is running

3. **Permission errors**
   - Ensure user has correct role (receptionist/doctor)
   - Check if user is logged in
   - Verify appointment ownership (for doctors)

### Performance Tips
- Database indexes are created for optimal performance
- Auto-refresh interval can be adjusted if needed
- Large waiting lists are paginated for better performance

## Future Enhancements

### Planned Features
- **SMS notifications** for long waits
- **Integration with digital displays** in waiting rooms
- **Advanced analytics** and reporting
- **Mobile app support**
- **Integration with appointment scheduling**

### Customization Options
- Configurable wait time thresholds
- Custom priority levels
- Flexible notification settings
- Branding and theming options

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository. 