# Clinic Management System - User Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Patient Management](#patient-management)
3. [Appointment Management](#appointment-management)
4. [Priority System](#priority-system)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### System Requirements
- Web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Valid user account with appropriate role

### Login Process
1. Navigate to the login page
2. Enter your email and password
3. Click "Login" to access the system
4. You'll be redirected to your role-specific dashboard

---

## 👥 Patient Management

### Viewing Patient Lists

#### For Receptionist Users:
The Patient List page displays all registered patients with advanced pagination for optimal performance.

#### Page Features:
- **Pagination Controls**: 
  - Maximum 100 patients displayed per page
  - Always-visible navigation (Previous/Next buttons)
  - Page information showing current position (e.g., "Page 2 of 5")
  - Smart page range with ellipsis for large datasets

- **Header Information**:
  - Total patient count
  - Current page indicator
  - Number of total pages
  - Search result count (when filtering)

#### Navigation Options:

**Basic Navigation:**
- **Previous Button**: Go to previous page (disabled on first page)
- **Next Button**: Go to next page (disabled on last page)
- **Page Numbers**: Click specific page numbers to jump directly

**Advanced Navigation:**
- **Quick Jump**: For datasets with >5 pages, use the "Go to Page" input
- **Search Integration**: Search results are paginated with preserved search terms

#### Search Functionality:
1. **Search Bar**: Search by patient name, email, or patient number
2. **Real-time Results**: Results are paginated automatically
3. **Clear Search**: Reset search and return to page 1
4. **Search Persistence**: Search terms maintained across page navigation

#### Performance Benefits:
- **Faster Loading**: Only 100 patients loaded at a time
- **Reduced Memory Usage**: Efficient database queries
- **Better Responsiveness**: Optimized for large patient databases
- **Mobile Friendly**: Responsive pagination controls

### Patient Information Display

#### Patient List Columns:
- **Patient Number**: Unique identifier badge
- **Name**: With avatar initials
- **Mobile Number**: Contact information
- **City**: Location information
- **Actions**: View details, history, and create appointment buttons

#### Patient Details Modal:
Access comprehensive patient information through the "View Details" button:
- Personal information (name, email, mobile)
- Medical details (gender, date of birth)
- Address information
- Direct edit patient link

### Patient Actions

#### Available Actions per Patient:
1. **View Details**: Quick overview in modal popup
2. **Patient History**: Complete medical history and appointments
3. **New Appointment**: Direct appointment creation for the patient
4. **Edit Patient**: Modify patient information (receptionist access)

---

## 📅 Appointment Management

### Creating Appointments

#### For Admin & Receptionist Users:
1. **Navigate to Appointments**: Click "Appointments" in the navigation menu
2. **Create New**: Click the "New Appointment" button
3. **Search Patient**: Use the patient search field to find the patient
   - Search by name, phone number, or patient ID
   - Select from the dropdown results
4. **Set Priority**: Choose appointment priority:
   - 🔴 **High Priority**: Urgent cases needing immediate attention
   - 🟡 **Medium Priority**: Regular appointments (default)
   - ⚪ **Low Priority**: Routine follow-ups
5. **Select Doctor**: Choose the attending doctor from the dropdown
6. **Pick Date & Time**: Select date and available time slot
7. **Add Notes**: Include any administrative notes or special instructions
8. **Submit**: Click "Create Appointment" to save

#### For Doctor Users:
1. **Navigate to Appointments**: Click "Appointments" in the navigation menu
2. **Create New**: Click "New Appointment" button (shows "For yourself" note)
3. **Search Patient**: Find and select the patient you want to see
4. **Set Priority**: Choose appropriate priority level
5. **Pick Date & Time**: Select from your available time slots
6. **Add Details**: Include appointment notes and remarks
7. **Submit**: Click "Create Appointment" to save

#### For Patient Users:
1. **Navigate to Appointments**: Access through the dashboard
2. **Create New**: Click "New Appointment" button
3. **Select Doctor**: Choose from available doctors
4. **Pick Date & Time**: Select from available slots
5. **Add Notes**: Include reason for visit or special requests
6. **Submit**: Click "Create Appointment" to save

### Viewing Appointments

#### Appointment List Features:
- **Filter Options**:
  - Status: All, Scheduled, Completed, Cancelled
  - Patient Type: All, New Patients, Existing Patients
  - Priority: All, High, Medium, Low
  - Date: Select specific date

- **Information Displayed**:
  - Date & Time
  - Patient name and ID
  - Patient type badge (New/Existing)
  - Priority level with color coding
  - Doctor name and specialization
  - Status badge
  - Administrative notes

#### Color Coding System:
- **Priority Levels**:
  - 🔴 Red badge: High Priority
  - 🟡 Yellow badge: Medium Priority
  - ⚪ Gray badge: Low Priority

- **Patient Types**:
  - 🟢 Green badge: New Patient
  - 🔵 Blue badge: Existing Patient

- **Status Indicators**:
  - 🟡 Yellow: Scheduled
  - 🟢 Green: Completed
  - 🔴 Red: Cancelled

### Editing Appointments

#### Permission Matrix:
| Appointment Status | Admin | Receptionist | Doctor (Assigned) | Doctor (Other) | Patient |
|-------------------|-------|--------------|------------------|---------------|---------|
| Scheduled | ✅ Full Edit | ✅ Full Edit | ✅ Full Edit | ❌ | ❌ |
| Completed | ✅ Full Edit | ❌ | ✅ Full Edit | ❌ | ❌ |
| Cancelled | ✅ Full Edit | ✅ Full Edit | ✅ Full Edit | ❌ | ❌ |

#### How to Edit:
1. **Access Edit**: Click the edit (pencil) icon in the actions column
2. **Modify Details**: Update appointment information as needed
3. **Change Priority**: Select new priority level if required
4. **Update Status**: Change appointment status (if permitted)
5. **Add Remarks**: Include doctor's remarks or updated notes
6. **Save Changes**: Click "Save Changes" to update

#### Quick Actions:
- **Mark Complete**: Click the checkmark icon for scheduled appointments
- **Cancel Appointment**: Click the X icon to cancel
- **Delete**: Admin users can permanently delete appointments

---

## 🎯 Priority System

### Understanding Priority Levels

#### 🔴 High Priority
- **Use Case**: Emergency appointments, urgent medical issues
- **Response Time**: Immediate attention required
- **Examples**: 
  - Severe pain or discomfort
  - Follow-up after emergency treatment
  - Critical test results review

#### 🟡 Medium Priority (Default)
- **Use Case**: Regular scheduled appointments
- **Response Time**: Standard scheduling
- **Examples**:
  - Routine check-ups
  - Regular consultations
  - Prescription renewals

#### ⚪ Low Priority
- **Use Case**: Non-urgent, routine appointments
- **Response Time**: Flexible scheduling
- **Examples**:
  - Annual health screenings
  - Preventive care visits
  - Administrative consultations

### Setting Priority

#### When Creating Appointments:
1. Select appropriate priority level from dropdown
2. Priority is required for all new appointments
3. Default selection is "Medium Priority"

#### When Editing Appointments:
1. Only authorized users can change priority
2. Consider patient condition and urgency
3. Document reason for priority changes in notes

#### Priority-Based Filtering:
1. Use priority filter to view specific priority appointments
2. Helpful for managing daily schedules
3. Prioritize high-priority appointments in planning

---

## 👥 User Roles & Permissions

### Admin Users
**Full System Access**
- ✅ Create, edit, delete all appointments
- ✅ Manage all user accounts
- ✅ Access all system features
- ✅ View system analytics and reports
- ✅ Configure system settings

### Receptionist Users
**Patient & Appointment Management**
- ✅ Create appointments for any doctor
- ✅ Edit scheduled and cancelled appointments
- ❌ Edit completed appointments
- ✅ Manage patient information
- ✅ View all appointments
- ✅ Delete scheduled appointments only

### Doctor Users
**Medical Practice Management**
- ✅ Create appointments for themselves only
- ✅ Edit their own appointments (any status)
- ✅ View their assigned appointments only
- ✅ Add medical remarks and observations
- ✅ Update appointment status
- ❌ Delete appointments

### Patient Users
**Personal Appointment Access**
- ✅ Create their own appointments
- ✅ View their own appointments only
- ❌ Edit appointments
- ❌ Change appointment priority
- ✅ Cancel their own appointments (through request)

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Patient List Issues

**Problem**: Pagination not working or showing incorrect page counts
**Solutions**:
- Refresh the page (F5 or Ctrl+R)
- Clear browser cache and cookies
- Check if you have patients in the database
- Contact admin if issue persists

**Problem**: Search results not paginated correctly
**Solutions**:
- Clear search and try again
- Ensure search term is at least 2 characters
- Try searching with different criteria (name vs email)
- Check for special characters in search term

**Problem**: "Go to Page" not working
**Solutions**:
- Ensure page number is within valid range (1 to max pages)
- Check that you're entering numbers only
- Try using pagination buttons instead
- Contact support if feature is completely broken

#### 2. Cannot Create Appointment
**Problem**: "New Appointment" button not visible
**Solutions**:
- Verify you're logged in with appropriate role
- Check if you have appointment creation permissions
- Contact admin if you should have access

#### 3. No Available Time Slots
**Problem**: Time dropdown shows "No available slots"
**Solutions**:
- Try different date
- Check doctor's availability schedule
- Contact admin to update doctor availability

#### 4. Priority Not Showing
**Problem**: Priority column/filter not visible
**Solutions**:
- Run database migration: `python add_priority_migration.py`
- Clear browser cache
- Contact system administrator

#### 5. Edit Button Missing
**Problem**: Cannot edit appointments
**Solutions**:
- Check appointment status (completed appointments have restricted access)
- Verify your role permissions
- Ensure you're assigned to the appointment (for doctors)

#### 6. Patient Search Not Working
**Problem**: Patient search returns no results
**Solutions**:
- Check spelling and try partial names
- Search by phone number or patient ID
- Verify patient exists in system
- Ensure patient is active

#### 7. Page Not Loading After Browser Back
**Problem**: Previous page shows blank or doesn't load
**Solutions**:
- Refresh the page (F5 or Ctrl+R)
- Clear browser cache
- Try using navigation menu instead of back button

### Contact Support

#### For Technical Issues:
- Email: admin@clinicmanagement.com
- Phone: +1-234-567-8900

#### For Training & Usage:
- Schedule training session with admin
- Check documentation at: `/help`
- Contact your supervisor or IT support

---

## 📱 Mobile Usage Tips

### Responsive Design
- System works on tablets and smartphones
- Touch-friendly buttons and forms
- Optimized layouts for smaller screens

### Best Practices:
1. Use landscape mode for better appointment list viewing
2. Tap and hold for context menus
3. Use search filters to quickly find appointments
4. Bookmark frequently used pages

---

## 🔄 Workflow Recommendations

### Patient Management for Receptionists:
1. **Daily Review**: Check patient list for new registrations
2. **Search Efficiently**: Use patient number or partial names for quick lookups
3. **Page Navigation**: Use page jump for large patient databases (>500 patients)
4. **Patient Verification**: Always verify patient details before creating appointments
5. **Regular Updates**: Keep patient contact information current

### Daily Routine for Receptionists:
1. **Morning**: Review high-priority appointments for the day
2. **Check-in**: Use filters to view today's scheduled appointments
3. **Updates**: Monitor appointment status changes throughout day
4. **End of Day**: Review completed appointments and prepare for next day

### Best Practices for Doctors:
1. **Planning**: Filter to view your appointments by priority
2. **Documentation**: Add remarks after each appointment
3. **Follow-up**: Create follow-up appointments during visits
4. **Emergency**: Use high priority for urgent appointments

### Patient Guidelines:
1. **Booking**: Book appointments in advance when possible
2. **Changes**: Contact reception for appointment modifications
3. **Preparation**: Arrive early for high-priority appointments
4. **Communication**: Provide accurate contact information

---

*Last Updated: December 2024*
*Version: 2.1.0* 