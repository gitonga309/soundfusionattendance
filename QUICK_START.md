# Sound Fusion Attendance System - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 5.1.4
- PostgreSQL (production) or SQLite (development)

### Installation

1. **Clone and Setup**
```bash
cd c:\Users\alexk\Desktop\SoundFusionLimited
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Setup**
```bash
python manage.py migrate
```

4. **Create Admin User**
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

5. **Run Development Server**
```bash
python manage.py runserver
```

6. **Access the Application**
- Open browser: http://localhost:8000/login/

---

## 📱 User Workflow

### 1. Registration
- Go to: http://localhost:8000/register/
- Fill in:
  - Username (unique)
  - Email (unique)
  - Phone number (unique)
  - Date of birth (optional)
  - Disability info (optional)
  - Password (twice for confirmation)
- Click "Register"

### 2. Login
- Go to: http://localhost:8000/login/
- Enter username and password
- Click "Login"

### 3. Mark Attendance
- Click "Mark Attendance" on dashboard
- Enter:
  - Event name (e.g., "Wedding at Nairobi Hilton")
  - Overtime hours (0-24)
- Click "Submit Attendance"
- **Note**: Can only mark once per day

### 4. View Records
- Click "View Records" on dashboard
- See all attendance history
- Click "Edit" on any day to modify overtime hours

### 5. Check Balance
- Dashboard shows current balance owed
- Shows recent admin adjustments
- View who made changes and why

---

## 👨‍💼 Admin Workflow

### 1. Admin Login
- Use superuser account created during setup
- Login at: http://localhost:8000/login/

### 2. Access Admin Tools
Once logged in as admin, two options available:

#### Option A: Admin Dashboard (Quick Overview)
- Navigate to: `/admin-dashboard/`
- Use tabs:
  - **User Balances**: Quick balance adjustments
  - **Attendance Records**: View recent activity
  - **Adjustment History**: See all changes

#### Option B: Manage Balances (Comprehensive)
- Navigate to: `/manage-balances/`
- Better for bulk updates
- Features:
  - Search for users
  - Enter adjustment amounts
  - Add reasons for adjustments
  - Confirm before saving

### 3. Making Balance Adjustments

**Method 1: Quick Adjustment (Admin Dashboard)**
1. Go to User Balances tab
2. Find user in list
3. Enter adjustment amount (positive or negative)
4. Enter reason
5. Click "Save All Adjustments"

**Method 2: Comprehensive (Manage Balances)**
1. Go to /manage-balances/
2. Use search box to find user
3. Enter adjustment amount
4. Enter reason (e.g., "Cash advance", "Bonus", "Deduction")
5. Visual rows highlight in yellow when modified
6. Click "Save All Changes"
7. Confirm in popup

### 4. View Audit Trail
- User Balances tab → "Recent Adjustments" column
- Adjustment History tab → Full change history
- Shows: date, amount, reason, admin who made change

---

## 💰 Payment System Details

### Daily Payment Calculation
```
Daily Pay = 1000 KSH (base) + (overtime_hours × 100 KSH)

Examples:
- 0 overtime = 1000 KSH
- 2 overtime = 1200 KSH
- 5 overtime = 1500 KSH
- 12 overtime = 2200 KSH
```

### User Balance
- **Definition**: Total amount owed to user for unpaid days
- **Calculation**: Sum of all unpaid attendance records
- **Updates**: Automatically when attendance is marked/edited

### Balance Adjustments
- Can be positive (bonus) or negative (deduction)
- Must have a reason (required field)
- Tracked with admin who made it
- Users see all adjustments in their dashboard

---

## 🔑 Key Features Overview

### For Workers ✓
- [x] Register and create account
- [x] Mark attendance daily
- [x] Edit overtime hours same day
- [x] View all attendance records
- [x] See current balance owed
- [x] Check recent balance changes
- [x] See who adjusted balance and why
- [x] Logout securely

### For Admins ✓
- [x] Login with superuser account
- [x] View all users and their balances
- [x] Make quick balance adjustments
- [x] Comprehensive balance management
- [x] Search for specific users
- [x] View recent attendance activity
- [x] Complete audit trail of changes
- [x] Statistics and overview
- [x] Manage multiple users efficiently

---

## 🎨 Interface Guide

### Dashboard (User View)
- **Top Section**: Welcome message and navigation
- **Stats Cards**: Today's status, total balance, today's pay
- **Profile Section**: User details for the day
- **Balance History**: Recent admin adjustments
- **Action Buttons**: Mark Attendance, View Records

### Admin Dashboard
- **Tab 1**: User Balances (adjustment form)
- **Tab 2**: Attendance Records (recent activity)
- **Tab 3**: Adjustment History (audit trail)
- **Stats**: Total users, total balance owed

### Manage Balances
- **Header**: Total balance owed display
- **Search**: Real-time user filtering
- **Table**: All users with edit inputs
- **Color Coding**: Highlighted rows show modifications
- **Actions**: Save with confirmation

---

## 📊 Reports Available

### Admin Can View:
1. **User List** with current balances
2. **Attendance Records** with payment amounts
3. **Balance Change History** with reasons
4. **User Statistics** (total count, total balance)

### Worker Can View:
1. **Personal Balance** on dashboard
2. **Attendance History** with all details
3. **Recent Adjustments** with dates and reasons
4. **Daily Payment** amounts

---

## 🔒 Security Notes

### Passwords
- Minimum requirements enforced by Django
- Stored securely with hashing
- Never displayed anywhere

### User Data
- Users can only see their own records
- Admins see all user data
- Phone numbers and emails are private
- Balance adjustments are transparent

### Audit Trail
- Every balance change is logged
- Shows who made the change
- Reason is recorded
- Date and time are tracked

---

## ⚠️ Important Rules

### Attendance Rules
- **One per day**: Can only mark one attendance record per day
- **Same day editing**: Can edit overtime hours on the same day
- **Event required**: Must enter event/venue name
- **Overtime limits**: 0-24 hours (reasonable limit)

### Balance Rules
- **Non-negative payments**: All daily payments are positive (1000+ KSH)
- **Adjustment reasons required**: All admin changes must have a reason
- **Automatic calculation**: Balance auto-updates when attendance changes
- **Audit trail**: All changes are tracked and visible

### Admin Rules
- **Superuser only**: Only accounts with is_superuser=True can access admin pages
- **Changes visible**: Workers see all balance adjustments
- **Reason required**: Every adjustment needs explanation
- **No deletion**: Records are kept forever for auditing

---

## 🛠️ Troubleshooting

### User Can't Login
- Check username spelling
- Verify account was created (check registration page)
- Reset password if forgotten
- Check if account is active

### Can't Mark Attendance
- Attendance already marked today (edit it instead)
- Not logged in (go to login page)
- Try refreshing page if form unresponsive

### Balance Not Showing
- Refresh page (browser cache issue)
- Check attendance was saved (go to view records)
- Verify is_paid field is False in database

### Admin Features Not Visible
- Login with superuser account (check is_superuser=True)
- Not admin account? Contact system administrator
- Try logging out and back in

### Search Not Working
- Check spelling of username
- Try email instead
- Clear search box and try again

---

## 📞 Support

### Getting Help
1. Check SYSTEM_DOCUMENTATION.md for complete details
2. Review IMPROVEMENTS_SUMMARY.md for recent changes
3. Check this Quick Start Guide
4. Look at existing user examples in dashboard

### Common Questions

**Q: Can workers see other workers' balances?**
A: No, only their own balance on their dashboard

**Q: Can admin see all workers?**
A: Yes, admin dashboard shows all workers and their balances

**Q: Is there a limit to overtime hours?**
A: Yes, 0-24 hours per day (reasonable work limit)

**Q: Can attendance be marked multiple times per day?**
A: No, one record per day. Use Edit to change it.

**Q: Are balance adjustments reversible?**
A: No, but you can make an offsetting adjustment (e.g., +2000 to reverse -2000)

**Q: Who can see adjustment reasons?**
A: Both workers (on dashboard) and admins (in history)

---

## 🚀 Next Steps

1. **Create Test Users**: Register a few test accounts
2. **Test Workflows**: Mark attendance, edit records
3. **Test Admin**: Try making balance adjustments
4. **Check Dashboard**: See how data displays
5. **Review Reports**: Check admin views and history

---

## 📝 Useful Commands

```bash
# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check database
python manage.py dbshell

# Collect static files (production)
python manage.py collectstatic

# Create backup
python manage.py dumpdata > backup.json

# Restore from backup
python manage.py loaddata backup.json
```

---

## ✅ System Health Check

To verify everything is working:

1. **Can register new user**
   - Go to /register/, create account
   - Should see success message

2. **Can login**
   - Go to /login/, enter credentials
   - Should see dashboard

3. **Can mark attendance**
   - Click "Mark Attendance"
   - Enter event and hours
   - Should see confirmation

4. **Admin can access tools**
   - Login as superuser
   - Navigate to /admin-dashboard/
   - Should see user list and tabs

5. **Balance updates**
   - Mark attendance with 2 hours overtime
   - Balance should be 1200 KSH
   - Dashboard should reflect this

---

## 🎓 Learning Resources

### Understanding the System
- **Models**: See models.py for data structure
- **Views**: See views.py for business logic
- **Templates**: See templates/ for UI
- **Database**: See migrations/ for schema

### Django Concepts Used
- User Authentication (built-in)
- OneToOne/ForeignKey relationships
- Signal handlers
- Template inheritance
- Forms and validation
- Decorators for permissions

---

## 📈 Scaling Considerations

As the company grows:
1. Migrate to PostgreSQL (production DB)
2. Add more admin users for load sharing
3. Implement caching for large datasets
4. Consider mobile app for attendance marking
5. Add reporting module for analytics
6. Implement batch payment processing

---

## 🎉 You're All Set!

Your Sound Fusion Attendance System is ready to use. 

**Key Points to Remember:**
- Workers mark attendance daily
- Can edit same day if needed
- Admins manage balances with reasons
- All changes are auditable
- Balance = sum of unpaid earnings
- Pay = 1000 + (OT hours × 100)

**Happy tracking!**
