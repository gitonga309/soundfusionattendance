# 🎵 Sound Fusion Limited - QUICK REFERENCE GUIDE

## ⚡ START THE SYSTEM

### On Windows (PowerShell)
```powershell
cd C:\Users\alexk\Desktop\SoundFusionLimited
python manage.py runserver 0.0.0.0:8000
```

### Then Access:
- **Home:** http://127.0.0.1:8000/
- **Register:** http://127.0.0.1:8000/register
- **Login:** http://127.0.0.1:8000/login
- **Admin Dashboard:** http://127.0.0.1:8000/admin-dashboard

---

## 👤 FOR STAFF (Casuals/Workers)

### Daily Workflow
1. **Login** → Username & Password
2. **View Dashboard** → See today's status & balance
3. **Mark Attendance** → Select Event + Overtime Hours
4. **Check Balance** → Shows KES amount
5. **Edit (Optional)** → Change overtime once per day
6. **Logout** → End session

### Payments
- **Base Pay:** KES 1,000 per day
- **Overtime:** KES 100 per hour
- **Example:** 3 hours overtime = 1,000 + (3×100) = KES 1,300

### How Balance Works
- Balance = All unpaid attendance payments + adjustments
- Admin can add/subtract money
- Reasons tracked for all adjustments

---

## 👨‍💼 FOR ADMIN (Manager/Owner)

### Setup (First Time Only)
```bash
python manage.py createsuperuser
# Enter username, email, password
```

### Daily Tasks
1. **Check Dashboard** → /admin-dashboard
2. **View Unpaid Records** → See who owes what
3. **Manage Balances** → Add adjustments (pay, deductions, etc.)
4. **Approve Events** → Create/edit events for tracking
5. **Log Equipment** → Record items taken to events

### Common Operations

**Mark Someone as Paid:**
- Go to Admin Dashboard
- Find the person
- Adjust balance to 0 (subtract what they earned)
- Add note: "Paid via [method]"

**Add Emergency Balance:**
- Admin Dashboard → Manage Balances
- Search for person
- Enter positive amount
- Reason: e.g., "Advance payment"

**Track Equipment:**
- Create event first
- After event, log all equipment:
  - What was taken (cables, screens, etc.)
  - Condition (good, damaged, etc.)
  - Who logged it

---

## 🔑 URL REFERENCE

| Page | URL | Who |
|------|-----|-----|
| Home | / | Everyone |
| Register | /register | New users |
| Login | /login | Everyone |
| Dashboard | /dashboard | Logged-in staff |
| Mark Attendance | /attendance/mark | Logged-in staff |
| View Records | /view-attendance | Logged-in staff |
| Edit Attendance | /edit-attendance/{id} | Logged-in staff |
| Admin Dashboard | /admin-dashboard | Admin only |
| Manage Balances | /manage-balances | Admin only |
| Logout | /logout | Logged-in users |

---

## 🐛 TROUBLESHOOTING

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
# If used, kill the process or use different port:
python manage.py runserver 0.0.0.0:8001
```

### Database errors
```bash
# Check migrations
python manage.py showmigrations attendance

# Apply missing migrations
python manage.py migrate

# Test database
python system_test.py
```

### Login not working
- Check username is correct
- Check CAPS LOCK
- If account is new, wait 10 seconds for database

### Balance not updating
- Try logging out and in again
- Admin can manually adjust if needed

---

## 📊 DATABASE BACKUP

### Before important operations
```bash
# Backup database (creates copy of db.sqlite3)
copy db.sqlite3 db.sqlite3.backup
```

### Restore from backup
```bash
# If something goes wrong
copy db.sqlite3.backup db.sqlite3
```

---

## 🔧 MAINTENANCE

### Weekly
- Check for pending balance adjustments
- Verify all attendance records are accurate
- Review equipment logs for damage/missing items

### Monthly
- Export attendance reports
- Reconcile payments
- Archive old events

---

## 💡 TIPS & BEST PRACTICES

1. **Always Logout** after each session
2. **Double-check Overtime** before submitting (only editable once)
3. **Record Equipment Immediately** after event, while fresh
4. **Add Context** to balance adjustments (why was money added/deducted)
5. **Keep Passwords Safe** - don't share accounts
6. **Screenshot Confirmations** after recording attendance

---

## 🚨 EMERGENCY CONTACTS

If system goes down:
1. Restart server: `Ctrl+C` then run `python manage.py runserver 0.0.0.0:8000`
2. Check database: `python system_test.py`
3. If still broken: Database might be corrupted
4. Last resort: Restore from backup

---

## 📱 MOBILE ACCESS

The system is mobile-friendly. You can:
- Access from any phone/tablet browser
- Mark attendance from site
- Check balance on phone
- Works with WiFi or mobile data

**URL on mobile:** http://[your-computer-ip]:8000/

---

## 🎯 KEY NUMBERS TO REMEMBER

- **Base Pay:** KES 1,000
- **Overtime Rate:** KES 100/hour
- **Max Overtime:** 24 hours
- **Supper Threshold:** 9 hours (future enhancement)
- **Server Port:** 8000

---

**Last Updated:** December 14, 2025  
**Status:** ✅ PRODUCTION READY
