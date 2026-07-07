# Clinic Management System - Changelog

---

## Version 2.5.0 — Jul 7, 2026

### 💊 Medicine Orders — Payment Tracking
- Added **Payment Status** (`unpaid` / `paid`) and **Payment Amount** (₹) to every medicine order
- Added **Payment Mode** field: Cash, Online, UPI, Card, NEFT/RTGS
- Receptionist can set payment via an inline ₹ panel on the manage page
- **Payment is locked** once the order reaches `Ready`, `Delivered`, or `Cancelled` — amount cannot be changed
- Customers see a **payment card** on the tracking/status page once order is Ready or Delivered (green if paid, amber if unpaid with clinic-pay prompt)

### 💊 Medicine Orders — Status Rules
- Orders marked as **Delivered** are now permanently locked — status cannot be reverted to any previous state
- Backend enforces the lock server-side (not just UI)
- UI shows a `🔒 Delivered` badge in place of the status dropdown for delivered orders

### 📄 Appointments — Pagination
- Appointments list now shows **20 per page** (previously loaded all records)
- All active filters (status, date, doctor, patient type, priority) are preserved across page navigation
- Record count shown: "Showing X–Y of Z appointments"

### 🏥 Public Landing — `/public_scanner`
- New kiosk-style landing page to choose between Book Appointment, Order Medicines, and Track Order
- Three large tap-friendly cards, green leaf theme, mobile/tablet/kiosk optimised

### 🐛 Bug Fixes
- **Race condition** in order/request number generation — replaced sequential ID lookup with `flush()`-then-assign pattern; DB auto-increment guarantees unique IDs even under concurrent requests
- **Empty mobile guard** — existing-patient appointment submit path now validates mobile before saving
- **Dead payment collapse panel** removed for locked orders (Ready/Delivered/Cancelled) — no orphaned DOM
- **`colspan` mismatch** in medicine manage table fixed (8 → 9 after Payment column added)
- **Unused `Doctor` import** removed from `public_appointments.py`
- **Unused `func` import** removed from `routes/medicines.py`

### 🗄️ Database
- Added `payment_status`, `payment_amount`, `payment_mode` columns to `medicine_order` table
- Added `migration_v261.sql` — upgrade script for version-8 → version-26.1 (safe, idempotent)
- Added `schema_v261_full.sql` — complete fresh-deployment schema for all 12 tables

### 📦 Dependencies
- Upgraded `Flask-Migrate` from `4.0.5` → `4.0.7` in `requirements-linux.txt`

---

## Version 2.4.0 — Jul 4, 2026

### 🆕 New Modules

#### 1. 💊 Order Medicines (Public)
- **New public module** at `/medicines/order` — no login required
- Patients can place medicine orders with:
  - Mobile number + optional Patient ID
  - Duration selection: 15 / 30 / 45 days (chip-style radio buttons)
  - Delivery type: **Self Pickup** (with preferred pickup date) or **Courier** (with delivery address)
  - Additional notes field
- Auto-links order to patient record if mobile/Patient ID matches existing account
- Order IDs generated in `MED-XXXXX` format
- **Track Orders** at `/medicines/track` — search by mobile + Order ID or Patient ID
- **Order Status page** at `/medicines/track/<order_number>` with live progress tracker (Placed → Processing → Ready → Delivered)
- **Courier Tracking** for receptionist:
  - Add courier company (Delhivery, BlueDart, DTDC, Ekart, etc.), AWB number, and tracking URL
  - Patients see AWB + direct "Track on Courier Website" button on status page
  - Auto-promotes status from `pending` → `processing` when AWB is saved
- **Staff Management** at `/medicines/manage` (receptionist / admin only):
  - Stats cards for each status
  - Filter by status
  - Update order status via inline dropdown
  - Inline courier details form per courier order
- New DB table: `medicine_order`

#### 2. 👨‍⚕️ Book Appointment (Public)
- **New public module** at `/book/` — no login required
- Landing page with New Patient / Existing Patient selection
- **New Patient** (`/book/new`):
  - Name, mobile, email, gender
  - Preferred date + time slot (chip selection)
  - Reason / concern notes
  - Request reference generated in `APTRQ-XXXXX` format
- **Existing Patient** (`/book/existing`):
  - Search by mobile number OR Patient ID
  - Patient record auto-filled on find
  - Book appointment with preferred date/time and notes
- **Staff Request Management** at `/book/requests` (receptionist / admin only):
  - Stats: Pending / Confirmed / Cancelled
  - Confirm or Cancel requests with one click
  - **Create Appointment** button pre-fills patient info, patient type, and notes into the appointment form
- New DB table: `appointment_request`

### ✨ Improvements

#### Appointment Form Pre-fill
- Clicking "Create Appointment" from an appointment request now pre-fills:
  - Patient (auto-selected, no search needed)
  - Patient Type (New / Existing from the request)
  - Notes from the request
- Patient selection is preserved across form validation failures (req_id + patient_id passed in redirect)

#### Admin Sidebar
- Admin role now has a proper sidebar with: Dashboard, Manage Users, Appointments, Medicine Orders, Appt Requests

#### Flash Messages
- Fixed raw HTML tags appearing in toast notifications (`| safe` filter applied)

### 🎨 UI / UX — Green Leaf Theme
- All public pages (`/medicines/*`, `/book/*`) redesigned with a **light green leaf theme**
- Material Design / iOS / Windows-inspired components:
  - **Floating label inputs** — label rises on focus/fill
  - **Chip-style radio buttons** — full-tap-area pill selection
  - **Card-style delivery selector** with animated icon circle
  - **Gradient buttons** with ripple effect and hover lift
  - **Fixed floating submit bar** on mobile screens (iOS bottom bar style)
  - **Progress tracker** with connected dot steps
  - **Patient found bar** with avatar initial
  - Brand header with decorative gradient + overlay circle
- Font stack: `-apple-system / Roboto / Segoe UI` for native feel
- `cubic-bezier(0.4,0,0.2,1)` easing (Google Material standard)
- Mobile-first: `inputmode` attributes for correct mobile keyboards

### 🗄️ Database
- Added `medicine_order` table (MariaDB/MySQL)
- Added `appointment_request` table (MariaDB/MySQL)
- Added `courier_name`, `courier_awb`, `courier_tracking_url` columns to `medicine_order`
- Fixed `preferred_time` column size (`VARCHAR(10)` → `VARCHAR(30)`) to fit time range values like `11:00-13:00`

---

## Version 2.4.1 — Jul 4, 2026

### 🆕 New Page

#### Public Scanner / Kiosk Landing (`/public_scanner`)
- New public landing page designed for reception kiosks, QR code links, and shared tablets
- No login required — fully public
- Three large tap-friendly action cards:
  - 📅 **Book Appointment** → `/book/`
  - 💊 **Order Medicines** → `/medicines/order`
  - 📦 **Track My Order** → `/medicines/track`
- Vertically centered full-screen layout — works on mobile, tablet, and kiosk screens
- Card lift + scale animation on hover / tap
- Green leaf theme consistent with all public pages
- Security note footer ("Your information is safe and secure")

---

## Version 2.0.0 - Recent Updates

### 🚀 New Features

#### 1. Patient List Pagination System
- **Performance Optimization**: Implemented pagination for Patients List with maximum 100 patients per page
- **Database Efficiency**: Reduced server load by limiting query results and implementing proper LIMIT/OFFSET
- **Enhanced Navigation**: 
  - Always-visible pagination controls (even for single page)
  - Previous/Next buttons with clear text labels
  - Page jump functionality for quick navigation
  - Smart page range calculation with ellipsis for large datasets
- **Visual Improvements**:
  - Total patient count and page information in header
  - Pagination summary showing current position
  - Responsive design for mobile devices
  - Enhanced styling with purple theme consistency

#### 2. Appointment Priority System
- **Priority Levels**: Added three priority levels for appointments:
  - 🔴 **High Priority** - For urgent cases requiring immediate attention
  - 🟡 **Medium Priority** - For regular appointments (default)
  - ⚪ **Low Priority** - For routine follow-ups
- **Visual Indicators**: Color-coded badges in appointment lists
- **Priority Filter**: Added filter option in appointments list to filter by priority
- **Form Integration**: Priority selection in both create and edit appointment forms

#### 3. Doctor Self-Appointment Creation
- **Enhanced Permissions**: Doctors can now create appointments for themselves
- **Streamlined UI**: Simplified appointment creation form for doctors
- **Auto-Assignment**: Doctor field is automatically set when doctors create appointments
- **Patient Search**: Doctors can search and select patients for appointments

#### 4. Advanced Permission System
- **Status-Based Editing**: 
  - ✅ **Completed Appointments**: Only doctors and admins can edit
  - ✅ **Active Appointments**: Receptionists, admins, and assigned doctors can edit
- **Role-Based Access**: Enhanced permission matrix for different user roles
- **Visual Feedback**: Clear indication of edit permissions in the UI

#### 5. Database Enhancements
- **New Appointment Fields**:
  - `priority` (VARCHAR(10)) - High/Medium/Low priority levels
  - `payment_status` (VARCHAR(20)) - Payment tracking capability
  - `payment_amount` (FLOAT) - Payment amount storage
  - `payment_mode` (VARCHAR(20)) - Cash/Online payment modes
  - `payment_received_by` (INT) - Staff member who received payment
  - `payment_date` (DATETIME) - Payment timestamp
- **Improved Timestamps**: Better datetime handling with UTC support

### 🔧 Technical Improvements

#### 1. Patient List Performance Enhancement
- **Pagination Implementation**: Flask-SQLAlchemy paginate() method for efficient data loading
- **Query Optimization**: 100 patients per page limit with proper indexing
- **Memory Management**: Reduced memory usage by avoiding large dataset loads
- **Search Integration**: Paginated search results with maintained search terms across pages
- **Error Handling**: Graceful fallback for pagination errors with user feedback

#### 2. Enhanced Appointment Management
- **Patient Type Indicators**: Visual badges for New vs Existing patients
- **Improved Filtering**: Multiple filter options (status, patient type, priority, date)
- **Better Search**: Enhanced patient search functionality
- **Responsive Design**: Mobile-friendly appointment lists and forms

#### 3. User Interface Enhancements
- **Modern Color Scheme**: Improved visual hierarchy and contrast
- **Icon Integration**: FontAwesome icons for better UX
- **Loading States**: Better feedback during form submissions
- **Validation**: Enhanced client-side and server-side validation

#### 4. Backend Improvements
- **Database Migrations**: Automatic schema updates
- **Error Handling**: Improved error messages and logging
- **Transaction Safety**: Better database transaction management
- **API Endpoints**: Enhanced REST API structure

### 📊 Appointment Features Matrix

| Feature | Admin | Receptionist | Doctor | Patient |
|---------|-------|--------------|---------|---------|
| Create Appointment | ✅ (Any doctor) | ✅ (Any doctor) | ✅ (Self only) | ✅ (Select doctor) |
| Edit Active Appointment | ✅ | ✅ | ✅ (If assigned) | ❌ |
| Edit Completed Appointment | ✅ | ❌ | ✅ (If assigned) | ❌ |
| Set Priority | ✅ | ✅ | ✅ | ❌ |
| Delete Appointment | ✅ | ✅ (Scheduled only) | ❌ | ❌ |
| View All Appointments | ✅ | ✅ | ✅ (Own only) | ✅ (Own only) |

### 🎨 UI/UX Improvements

#### 1. Patient List Page Enhancements
```
Features Added:
- Pagination controls with Previous/Next navigation
- Total patient count and page information display
- Smart page range with ellipsis for large datasets
- Quick jump-to-page functionality for datasets >5 pages
- Always-visible pagination (even for single page)
- Search term preservation across pages
- Mobile-responsive pagination controls
- Enhanced card header with page statistics
```

#### 2. Appointment List Page
```
Features Added:
- Priority column with color-coded badges
- Patient type indicators
- Enhanced action buttons with conditional logic
- Improved filter section with priority filter
- Better responsive design for mobile devices
```

#### 3. Create Appointment Form
```
Features Added:
- Priority selection dropdown
- Doctor-specific form layout
- Patient search with autocomplete
- Visual confirmation for selected patients
- Better form validation and error messages
```

#### 4. Edit Appointment Form
```
Features Added:
- Priority editing capability
- Current appointment details display
- Role-based field visibility
- Permission-based access control
- Quick action buttons for status changes
```

### 🔧 Installation & Migration

#### Database Migration
Run the following script to update existing databases:
```bash
python add_priority_migration.py
```

This script will:
- Add priority column to appointments table
- Add payment-related columns
- Set default values for existing records
- Create necessary foreign key constraints

#### Required Dependencies
Ensure these packages are installed:
```bash
pip install flask-cors
pip install sqlalchemy
```

### 📝 Configuration Changes

#### Environment Variables
No new environment variables required for basic functionality.

#### Database Schema Changes
```sql
-- New columns added to appointment table:
ALTER TABLE appointment ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE appointment ADD COLUMN payment_status VARCHAR(20) DEFAULT 'unpaid';
ALTER TABLE appointment ADD COLUMN payment_amount FLOAT;
ALTER TABLE appointment ADD COLUMN payment_mode VARCHAR(20);
ALTER TABLE appointment ADD COLUMN payment_received_by INT;
ALTER TABLE appointment ADD COLUMN payment_date DATETIME;
```

### 🚦 Known Issues & Fixes

#### Fixed Issues:
- ✅ Browser back button navigation issues
- ✅ Time slot management in user creation
- ✅ Modal functionality for doctor availability
- ✅ Database column compatibility with MySQL/MariaDB
- ✅ Indentation errors in admin routes

#### Compatibility:
- ✅ MySQL/MariaDB support
- ✅ SQLite support (development)
- ✅ Python 3.8+ compatibility
- ✅ Flask 2.x compatibility

### 📚 API Documentation

#### New Endpoints:
```
GET /patients/ - List patients with pagination and search
GET /appointments/ - List appointments with filters
POST /appointments/create - Create new appointment
PUT /appointments/{id}/edit - Edit appointment
POST /appointments/{id}/complete - Mark appointment complete
POST /appointments/{id}/cancel - Cancel appointment
DELETE /appointments/{id} - Delete appointment (admin/receptionist only)
```

#### Patient List Query Parameters:
```
?page=1 - Page number (default: 1)
?search=query - Search by name, email, or patient number
```

#### Appointment Query Parameters:
```
?status=scheduled|completed|cancelled
?patient_type=new|existing
?priority=high|medium|low
?date=YYYY-MM-DD
```

### 🔄 Workflow Updates

#### New Appointment Creation Workflow:
1. User selects role-appropriate form
2. Priority level selection (required)
3. Patient search/selection
4. Doctor assignment (auto for doctors)
5. Date/time selection with availability check
6. Form submission with validation

#### Appointment Management Workflow:
1. Filter appointments by priority/status/type
2. Edit permissions based on appointment status and user role
3. Status updates with proper authorization
4. Payment tracking (future enhancement)

### 🎯 Future Enhancements

#### Planned Features:
- 💳 **Payment Processing**: Complete payment workflow implementation
- 📧 **Email Notifications**: Appointment confirmations and reminders
- 📱 **Mobile App Integration**: REST API for mobile applications
- 📊 **Analytics Dashboard**: Appointment metrics and reporting
- 🔔 **Real-time Notifications**: WebSocket-based notifications

#### Technical Roadmap:
- 🔒 **Enhanced Security**: Two-factor authentication
- 🌐 **Multi-language Support**: Internationalization
- 📈 **Performance Optimization**: Database indexing and caching
- 🧪 **Testing Suite**: Comprehensive unit and integration tests

---

## Version History

### v2.5.0 (Current) — Jul 7, 2026
- Payment tracking (status, amount, mode) on medicine orders with lock-after-Ready rule
- Delivered status permanently locked — no revert
- Appointments list pagination (20/page, filters preserved)
- Race-condition-safe order/request number generation
- Production migration scripts (`migration_v261.sql`, `schema_v261_full.sql`)

### v2.4.1 — Jul 4, 2026
- Public Scanner/Kiosk landing page at /public_scanner
- Three-option card layout for appointment booking, medicine orders, and order tracking

### v2.4.0 — Jul 4, 2026
- Medicine Order module (public) with courier tracking
- Book Appointment module (public) for new & existing patients
- Green Leaf theme with Material/iOS-style UI on all public pages
- Appointment form pre-fill from request data
- Admin sidebar added
- Flash message HTML rendering fix

### v2.1.0 (Previous)
- Patient List pagination system (100 patients per page)
- Performance optimization for large patient databases
- Enhanced navigation with always-visible pagination controls
- Quick page jump functionality for large datasets
- Mobile-responsive pagination design
- Search integration with pagination

### v2.0.0 (Previous)
- Priority system for appointments
- Doctor self-appointment creation
- Enhanced permission system
- Payment system foundation
- UI/UX improvements

### v1.0.0 (Initial)
- Basic appointment management
- User management system
- Doctor availability scheduling
- Role-based access control
- Basic dashboard functionality

---

*Last Updated: July 7, 2026*