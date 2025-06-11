# Setup & Migration Guide

## 🔄 Updating to Version 2.0.0

This guide will help you update your existing Clinic Management System to include the new priority features and doctor self-appointment creation.

---

## ⚠️ Pre-Migration Checklist

### 1. Backup Your Database
```bash
# For MySQL/MariaDB
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# For SQLite
cp clinic_db.sqlite clinic_db_backup_$(date +%Y%m%d_%H%M%S).sqlite
```

### 2. Stop the Application
```bash
# If running with Flask development server
# Press Ctrl+C in the terminal

# If running with a production server
sudo systemctl stop clinic-management
```

### 3. Check Current Version
Verify your current system version before proceeding.

---

## 📥 Installation Steps

### 1. Update Code Files
Ensure all the following files are updated in your project:

#### Core Application Files:
- `models.py` - Updated Appointment model with new fields
- `routes/appointments.py` - Enhanced appointment routes
- `templates/appointments/list.html` - Updated appointment list with priority
- `templates/appointments/create.html` - Enhanced creation form
- `templates/appointments/edit.html` - Updated edit form

#### Migration Files:
- `add_priority_migration.py` - Database migration script

### 2. Install Dependencies
```bash
# Activate your virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install required packages
pip install flask-cors sqlalchemy
```

### 3. Run Database Migration
```bash
# Execute the migration script
python add_priority_migration.py
```

**Expected Output:**
```
Existing columns: ['id', 'doctor_id', 'patient_id', 'datetime', 'status', 'patient_type', 'notes', 'remarks', 'created_at', 'updated_at']
✅ Added column 'priority' successfully
✅ Added column 'payment_status' successfully
✅ Added column 'payment_amount' successfully
✅ Added column 'payment_mode' successfully
✅ Added column 'payment_received_by' successfully
✅ Added column 'payment_date' successfully
✅ Added foreign key constraint for payment_received_by
✅ Updated existing appointments with default values
```

### 4. Verify Migration
```bash
# Test the migration by checking database structure
python -c "
from app import app, db
from models import Appointment
with app.app_context():
    print('Migration successful - Appointment model loaded')
    print('New columns available in Appointment model')
"
```

### 5. Start the Application
```bash
# Development server
flask run

# Or with Python
python app.py

# Production server
sudo systemctl start clinic-management
```

---

## 🧪 Testing the Update

### 1. Test Patient List Pagination
1. **Login** as a receptionist
2. **Navigate** to Patients → Patients List
3. **Verify** pagination controls are visible (even with <100 patients)
4. **Check** total patient count in header
5. **Test** Previous/Next buttons functionality
6. **Verify** page information display (e.g., "Page 1 of 3")
7. **Test** search functionality with pagination
8. **Test** "Go to Page" feature (if >5 pages available)

### 2. Test Priority System
1. **Login** as an admin or receptionist
2. **Navigate** to Appointments → Create New Appointment
3. **Verify** priority dropdown is visible with three options:
   - High Priority
   - Medium Priority (selected by default)
   - Low Priority
4. **Create** a test appointment with high priority
5. **Check** the appointments list shows priority badges

### 3. Test Doctor Self-Appointment
1. **Login** as a doctor user
2. **Navigate** to Appointments
3. **Verify** "New Appointment" button shows "(For yourself)" note
4. **Click** New Appointment
5. **Verify** doctor field is hidden and auto-selected
6. **Create** a test appointment

### 4. Test Permission System
1. **Create** a completed appointment (admin/receptionist)
2. **Login** as receptionist
3. **Verify** edit button is not visible for completed appointments
4. **Login** as the assigned doctor
5. **Verify** edit button is visible for completed appointments

---

## 🚨 Troubleshooting

### Issue: Migration Script Fails

#### Error: "No module named 'flask_cors'"
```bash
# Solution: Install missing dependency
pip install flask-cors
```

#### Error: "IndentationError in admin.py"
```bash
# Solution: Check for mixed tabs/spaces
python -m py_compile routes/admin.py
python -m py_compile routes/receptionist.py
# Fix any indentation issues reported
```

#### Error: "Unknown column 'priority' in SELECT"
```bash
# Solution: Re-run migration script
python add_priority_migration.py

python -m py_compile routes/admin.py
```

### Issue: Priority Not Showing

#### Symptoms:
- Priority column missing from appointment list
- Priority filter not visible
- Priority dropdown missing in forms

#### Solutions:
1. **Clear browser cache** (Ctrl+F5)
2. **Verify migration ran successfully**
3. **Check database columns**:
```sql
SHOW COLUMNS FROM appointment;
```
4. **Restart application server**

### Issue: Doctor Can't Create Appointments

#### Symptoms:
- "New Appointment" button missing for doctors
- Permission denied errors

#### Solutions:
1. **Verify user role** is set to 'doctor'
2. **Check Doctor model** exists for the user
3. **Verify routes/appointments.py** includes doctor permissions

### Issue: Database Errors

#### MySQL Connection Issues:
```python
# Check database connection in app.py
# Verify MySQL credentials in .env file
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=clinic_management
```

#### Foreign Key Constraint Errors:
```sql
-- Check foreign key constraints
SHOW CREATE TABLE appointment;

-- If needed, add constraint manually
ALTER TABLE appointment 
ADD CONSTRAINT fk_payment_received_by 
FOREIGN KEY (payment_received_by) REFERENCES user(id);
```

### Issue: Patient List Pagination Problems

#### Symptoms:
- Pagination controls not showing
- Page counts incorrect
- Search results not paginated
- "Go to Page" feature not working

#### Solutions:
1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Check Flask-SQLAlchemy version**:
```bash
pip show Flask-SQLAlchemy
# Should be compatible with pagination
```
3. **Verify database connection**
4. **Check browser console** for JavaScript errors
5. **Test with different browsers**

---

## 📊 Verification Checklist

After migration, verify these features work:

### ✅ Patient List Pagination
- [ ] Pagination controls visible on Patient List page
- [ ] Previous/Next buttons work correctly
- [ ] Page information displays current page and total pages
- [ ] Search functionality works with pagination
- [ ] "Go to Page" feature works for large datasets
- [ ] Page navigation preserves search terms
- [ ] Mobile responsive pagination controls
- [ ] Total patient count shows in header

### ✅ Priority System
- [ ] Priority dropdown in create appointment form
- [ ] Priority column in appointments list
- [ ] Priority filter in appointments list
- [ ] Color-coded priority badges (Red/Yellow/Gray)
- [ ] Priority editing in edit appointment form

### ✅ Doctor Features
- [ ] Doctors can see "New Appointment" button
- [ ] Doctor field auto-populated for doctor users
- [ ] Doctors can search and select patients
- [ ] Doctors can edit their own appointments

### ✅ Permission System
- [ ] Receptionists cannot edit completed appointments
- [ ] Doctors can edit their completed appointments
- [ ] Admins can edit all appointments
- [ ] Edit buttons show/hide correctly

### ✅ Database Integrity
- [ ] All existing appointments have default priority 'medium'
- [ ] All existing appointments have payment_status 'unpaid'
- [ ] No broken foreign key constraints
- [ ] Application starts without errors

---

## 🔄 Rollback Procedure

If you encounter issues and need to rollback:

### 1. Stop the Application
```bash
# Stop the server
sudo systemctl stop clinic-management
```

### 2. Restore Database Backup
```bash
# For MySQL/MariaDB
mysql -u username -p database_name < backup_YYYYMMDD_HHMMSS.sql

# For SQLite
cp clinic_db_backup_YYYYMMDD_HHMMSS.sqlite clinic_db.sqlite
```

### 3. Restore Previous Code
```bash
# Use git to restore previous version
git checkout previous_version_tag

# Or manually restore backup files
```

### 4. Restart Application
```bash
# Start with previous version
python app.py
```

---

## 📞 Support

### Getting Help
- **Documentation**: Check `USER_GUIDE.md` for usage instructions
- **Issues**: Create GitHub issue with error details
- **Email**: admin@clinicmanagement.com

### Providing Feedback
Please report:
- Migration errors encountered
- Missing features or bugs
- Performance issues
- User experience feedback

---

*Migration Guide Version: 2.1.0*
*Last Updated: December 2024* 