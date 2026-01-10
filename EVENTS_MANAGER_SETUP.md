# 🎯 How to Create Events Manager from Admin Panel

## ✨ Automatic Process (NEW!)

Now you can create an Events Manager user completely from the Django admin without any manual steps!

### Step 1: Go to Users Admin
1. Login to `http://localhost:8000/admin/` with your **superuser account**
2. Click **Users** in the left sidebar

### Step 2: Add New User
1. Click **+ Add User**
2. Fill in:
   - **Username**: `events_manager_name`
   - **Password**: Create a strong password
3. Click **Save**

### Step 3: Add to Events Manager Group (THIS IS THE MAGIC STEP!)
1. On the user detail page, scroll down to **Permissions** section
2. In **Groups**, select **"Events Manager"**
3. Click the arrow `→` to add it to "Chosen groups"
4. Click **Save**

### ✅ That's It!
The signal automatically:
- ✅ Enables **is_staff = True**
- ✅ Sets all 8 permissions (Events & Attendance)
- ✅ User can now login to admin

---

## 🔍 How It Works Behind the Scenes

**What changed:**
1. Added a Django signal `auto_staff_on_events_manager()` in `models.py`
2. When a user is added to the "Events Manager" group, the signal automatically sets `is_staff = True`
3. Customized User admin to show a helpful tip about the Events Manager group
4. No manual command needed anymore!

---

## 📝 Example Workflow

1. **Create User**: `john_events_manager`
2. **Set Password**: `SecurePass123!`
3. **Add to Group**: Select "Events Manager" → Save
4. **Result**: John can now:
   - ✅ Login at `/admin/`
   - ✅ Create, edit, delete Events
   - ✅ View and manage Attendance Records
   - ✅ Assign crews to events
   - ❌ Cannot access Users, Profiles, Reimbursements, etc.

---

## 🚀 Test It

1. As superuser, create a new test user: `test_manager`
2. Add to "Events Manager" group
3. Logout and login as `test_manager`
4. You should see ONLY:
   - ✅ Events
   - ✅ Attendance Records

---

## 💡 Pro Tips

- **Bulk Create**: You can create multiple Events Managers this way
- **Easy Management**: Edit users anytime by adding/removing from the group
- **No Manual Steps**: No need to run commands anymore
- **Staff Status**: Automatically enabled when added to the group

---

## 🔐 Permission Details

When a user is in the "Events Manager" group, they get:
```
- attendance.add_event
- attendance.change_event
- attendance.delete_event
- attendance.view_event
- attendance.add_attendancerecord
- attendance.change_attendancerecord
- attendance.delete_attendancerecord
- attendance.view_attendancerecord
```

That's all they can access in the admin!
