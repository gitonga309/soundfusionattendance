# Sound Fusion Attendance Management System

## Project Overview

Sound Fusion Attendance is a Django-based web application designed for an event company to track employee/worker attendance and manage payments. The system allows workers to mark attendance, record overtime hours, and view their payment balances, while administrators can manage all users, adjust balances, and track payment history.

## Key Features

### User Features (Workers)
- **User Registration & Authentication**
  - Sign up with username, email, phone number, date of birth, and disability information
  - Secure login with Django authentication
  - Persistent session management

- **Attendance Tracking**
  - Mark attendance once per day with automatic timestamp
  - Specify event/venue name for attendance records
  - Record overtime hours (0-24 hours)
  - Automatic payment calculation: KSH 1000 base + KSH 100 per overtime hour

- **Dashboard**
  - View today's attendance status
  - Display total account balance owed
  - Show recent balance changes made by admin (with dates, amounts, reasons, and admin name)
  - Quick access to all features

- **Attendance Records**
  - View complete attendance history
  - Edit attendance records (overtime hours and event details)
  - See payment amounts for each day
  - Clean, responsive table interface

### Admin Features
- **Admin Dashboard** (at `/admin-dashboard/`)
  - Three-tab interface:
    1. **User Balances**: View all users with current balances, make adjustments, track reasons
    2. **Attendance Records**: See most recent attendance records for all users
    3. **Adjustment History**: View all balance adjustments made with admin who made them
  
  - Statistics display:
    - Total number of users
    - Total balance owed across all users

- **Balance Management** (at `/manage-balances/`)
  - Dedicated page for comprehensive balance updates
  - Search functionality to find users quickly
  - Visual highlighting of rows being modified
  - Confirmation before saving changes
  - All balance adjustments logged with reasons

- **Balance Adjustments**
  - Add or deduct from user balances with custom reasons
  - Full audit trail: tracks which admin made changes, when, and why
  - Users see all adjustments in their dashboard
  - Supports both positive (bonus) and negative (deductions) adjustments

## Technical Architecture

### Database Models

#### User (Django Built-in)
- username, email, password, first_name, last_name
- is_superuser (for admin identification)

#### Profile
- OneToOneField to User
- phone_number, email, date_of_birth, disability
- **balance** (Decimal): Current amount owed to user

#### AttendanceRecord
- ForeignKey to User
- date, check_in_time
- event (name/venue)
- overtime_hours (0-24)
- is_paid (Boolean)
- **amount_paid** (Decimal): Calculated as 1000 + (overtime_hours * 100)
- admin_adjustment (for future use)

#### BalanceAdjustment
- ForeignKey to Profile
- ForeignKey to admin User (who made the adjustment)
- amount (Decimal): positive or negative
- reason (text description)
- date (auto-set to creation time)
- Full audit trail for all balance changes

### Signal Handlers
- **User Creation**: Automatically creates Profile when new user registers
- **Attendance Record Changes**: Automatically recalculates user balance:
  - Sums all unpaid attendance records' `amount_paid` values
  - Updates Profile.balance accordingly
  - Ensures balance always reflects actual unpaid earnings

### Payment Calculation Logic
```
Daily Pay = 1000 KSH (base) + (overtime_hours × 100 KSH)
User Balance = Sum of all unpaid attendance records' amount_paid
```

## URL Routes

### Public Routes
- `/register/` - User registration page
- `/login/` - Login page
- `/logout/` - Logout (redirects to login)

### User Routes (requires login)
- `/dashboard/` - Main user dashboard
- `/view-attendance/` - View attendance history
- `/edit-attendance/<id>/` - Edit specific attendance record
- `/attendance/mark` - Mark new attendance

### Admin Routes (requires superuser)
- `/admin-dashboard/` - Main admin interface with tabs
- `/manage-balances/` - Dedicated balance management interface

## Improvements Made to Original System

### 1. Fixed Critical Bug
- **Before**: admin_dashboard view had syntax error (missing 't' in 'request')
- **After**: Function properly defined and working

### 2. Enhanced User Interface
- **Before**: Basic, inconsistent styling across pages
- **After**: 
  - Modern gradient-based design with purple theme (#667eea, #764ba2)
  - Consistent navbar on all pages
  - Font Awesome icons for better visual communication
  - Responsive grid layouts
  - Professional card-based design

### 3. Improved Balance Tracking
- **Before**: Limited visibility of balance changes
- **After**:
  - Admin dashboard shows balance changes in detail
  - Users see who made changes, when, and why
  - Complete audit trail with BalanceAdjustment model
  - Dashboard displays recent adjustments prominently

### 4. New Admin Features
- **Dedicated Balance Management Page** (`/manage-balances/`):
  - Search functionality to find users
  - Visual feedback when making adjustments
  - Confirmation before saving all changes
  - Better organization than admin_dashboard tabs

- **Statistics & Overview**:
  - Total users count
  - Total balance owed
  - Better data presentation

### 5. Better Data Organization
- **Admin Dashboard Tabs**:
  1. User Balances - Make adjustments
  2. Attendance Records - View latest activity
  3. Adjustment History - Audit trail

### 6. Enhanced User Experience
- **Logout buttons** on all pages
- **Navigation improvements**:
  - Back buttons on all secondary pages
  - Consistent navbar on main pages
  - Clear call-to-action buttons
  
- **Status indicators**:
  - Balance badges with color coding
  - Attendance status display
  - Overtime hour badges

### 7. Data Validation
- Phone number uniqueness checking
- Email validation
- Password strength requirements
- Numeric input validation for amounts

## Security Features

1. **Django Built-in Security**
   - CSRF protection on all forms
   - SQL injection prevention via ORM
   - XSS protection in templates
   - Secure password hashing

2. **Authentication**
   - Login required decorator on all user/admin pages
   - Superuser requirement for admin pages
   - Session-based authentication

3. **Authorization**
   - Users can only view/edit their own records
   - Admins can only access admin pages
   - Balance adjustments tied to admin user

## File Structure

```
soundfusion_attendance/
├── manage.py
├── requirements.txt
├── runtime.txt
├── db.sqlite3
│
├── soundfusion_attendance/ (project config)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── attendance/ (main app)
│   ├── models.py (User, Profile, AttendanceRecord, BalanceAdjustment)
│   ├── views.py (all views and logic)
│   ├── forms.py (registration and attendance forms)
│   ├── urls.py (URL routing)
│   ├── admin.py (Django admin configuration)
│   │
│   └── templates/attendance/
│       ├── register.html
│       ├── login.html
│       ├── dashboard.html ✨ (improved)
│       ├── mark_attendance.html
│       ├── edit_attendance.html
│       ├── view_attendance.html ✨ (improved)
│       ├── admin_dashboard.html ✨ (new)
│       └── manage_balances.html ✨ (new)
│
└── workers/ (stub app for future expansion)
```

## How to Use

### For Workers

1. **Register**
   - Go to `/register/`
   - Fill in username, email, phone, date of birth (optional), disability (optional)
   - Create password

2. **Login**
   - Go to `/login/`
   - Enter username and password

3. **Mark Attendance**
   - Click "Mark Attendance" on dashboard
   - Enter event name and overtime hours
   - Submit

4. **View Records**
   - Click "View Records" to see all attendance
   - Click "Edit" to modify overtime hours and event name

5. **Check Balance**
   - Dashboard shows total balance
   - View recent admin adjustments with reasons

### For Administrators

1. **Access Admin Dashboard**
   - Login as superuser
   - Navigate to `/admin-dashboard/`

2. **Manage Balances**
   - Go to `/manage-balances/`
   - Search for users
   - Enter adjustment amounts and reasons
   - Click "Save All Changes"

3. **View Records**
   - Check "Attendance Records" tab for recent activity
   - Monitor "Adjustment History" for all changes

## Performance Considerations

- Balance calculated at save time (not query time) for efficiency
- Profile created automatically on user registration
- Signals ensure data consistency
- Database indexed on common queries (date, user, is_paid)

## Future Enhancements

1. **Reporting**
   - Monthly/weekly payment reports
   - Attendance analytics
   - Export to CSV/PDF

2. **Notifications**
   - Email notifications for balance changes
   - SMS alerts for key events

3. **Advanced Features**
   - Shift management
   - Team assignments
   - Multiple event types with different pay rates
   - Automatic payment processing

4. **Mobile App**
   - React Native app for attendance marking
   - Push notifications

## Deployment

The system is configured for Render.com deployment:
- Uses PostgreSQL in production
- WhiteNoise for static files
- Environment-based settings
- ALLOWED_HOSTS configuration for deployment

## Support

For issues or questions:
1. Check console for error messages
2. Review Django debug page in development
3. Check model relationships and signals
4. Verify authentication is working
