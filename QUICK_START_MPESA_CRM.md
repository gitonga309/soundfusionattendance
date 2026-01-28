# 🚀 Quick Start Guide - M-Pesa & CRM Features

**For**: Sound Fusion Admin  
**Duration**: 5-10 minutes to get started  
**Prerequisites**: Admin access to Django admin panel

---

## 🎯 Quick Actions

### 1️⃣ First Time Setup (5 minutes)

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Migrations
```bash
python manage.py migrate
```

#### Create Admin User (if not existing)
```bash
python manage.py createsuperuser
```

#### Start Development Server
```bash
python manage.py runserver
```

Then access: http://localhost:8000/admin/

---

### 2️⃣ Send Your First M-Pesa Payment (3 minutes)

**In Admin Panel:**

1. Click **Attendance** → **M-Pesa Payments**
2. Click **Add M-Pesa Payment** (top right)
3. Fill in:
   - **User**: Select employee
   - **Phone Number**: `254700123456` (employee's M-Pesa number)
   - **Amount**: `500` (KSH)
   - **Payment Purpose**: `Salary Payment`
4. Click **Save**

**Result:**
- STK push sent to employee's phone
- Employee enters M-PIN on their phone
- Payment completes automatically
- Status changes to "completed"

---

### 3️⃣ Assign Crew to Event (3 minutes)

**In Admin Panel:**

1. Click **Attendance** → **Events**
2. Create or select an event
3. Go to **Attendance** → **Event Crew**
4. Click **Add Event Crew**
5. Fill in:
   - **Event**: Select event from step 2
   - **User**: Select crew member
   - **Role**: `Sound Engineer` (or their role)
   - **Notes**: Add any special instructions (optional)
6. Click **Save**

**Next Step:** Send invitation (see next section)

---

### 4️⃣ Send Crew Invitations (2 minutes)

**In Admin Panel:**

1. Go to **Attendance** → **Event Crew**
2. Filter by Event (if many records)
3. **Select** the crew members you want to invite
4. In **Action** dropdown, select **"Send Invitations to Selected Crew"**
5. Click **Go**

**What Happens:**
- Email invitation sent to crew members
- They receive email with event details
- They can confirm from their **"My Crew Assignments"** page
- You see status update in admin immediately

---

### 5️⃣ Send Event Reminders (2 minutes)

**Do this**: 1 day before event

**In Admin Panel:**

1. Go to **Attendance** → **Event Crew**
2. Filter: **Status** = `confirmed`, **Event** = your event
3. Select confirmed crew members
4. Action dropdown: **"Send Reminders to Confirmed Crew"**
5. Click **Go**

**What Crew Receives:**
- Email reminder with:
  - Event date & time
  - Location
  - Their role
  - Special instructions

---

## 📱 Employee Self-Service

### For Crew Members:

1. Login to dashboard
2. Click **"My Crew Assignments"** (in menu)
3. See all pending invitations
4. Click **Confirm** or **Decline**
5. See confirmed assignments
6. Check reminders before events

**URL**: `/crew/assignments/`

---

## 📊 Admin Dashboard Features

### M-Pesa Payments (`/admin/attendance/mpesapayment/`)

**Quick Actions:**
- 🔍 **Search** by phone or username
- 🏷️ **Filter** by status (pending, completed, failed)
- 🔄 **Resend STK Push** - Button on each pending payment
- 📋 **Bulk Action** - Select multiple → "Initiate M-Pesa STK Push"

**View Payment Details:**
- Click any payment to see full details
- Check M-Pesa receipt number
- View transaction date
- See all timestamps

### Event Crew (`/admin/attendance/eventcrew/`)

**Quick Actions:**
- 🔍 **Search** by name, email, or event
- 🏷️ **Filter** by status (invited, confirmed, declined)
- ✉️ **Send Invitations** - Bulk action
- 📢 **Send Reminders** - Bulk action
- ✅ **Mark as Confirmed** - Bulk action

### Email Notifications (`/admin/attendance/emailnotification/`)

**Quick Actions:**
- 📧 **View** all sent emails
- ❌ **Monitor** failed emails
- 🔄 **Resend** failed notifications
- 🔍 **Filter** by type (crew_invitation, payment_approved, etc.)

---

## 🔧 Configuration (One-Time)

### For M-Pesa (IMPORTANT!)

Add to your `.env` file or environment variables:

```bash
# Get these from Safaricom Developer Portal
MPESA_CONSUMER_KEY=your_key_here
MPESA_CONSUMER_SECRET=your_secret_here
MPESA_BUSINESS_SHORT_CODE=174379  # for sandbox
MPESA_PASS_KEY=your_pass_key_here
MPESA_ENVIRONMENT=sandbox  # Change to 'production' when live
MPESA_CALLBACK_URL=http://localhost:8000/api/mpesa/callback/
```

**For Production:**
```bash
MPESA_ENVIRONMENT=production
MPESA_BUSINESS_SHORT_CODE=your_production_code
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/
```

### For Email (Optional)

Add to your `.env`:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password  # Not regular password!
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate "App Password" at https://myaccount.google.com/apppasswords
3. Use the app password in EMAIL_HOST_PASSWORD

---

## 🎓 Common Tasks

### Task 1: Pay an Employee via M-Pesa

1. Go to M-Pesa Payments admin
2. Click "Add M-Pesa Payment"
3. Fill: Employee, Phone, Amount, Purpose
4. Click Save → STK sent to phone
5. Employee enters M-PIN
6. Payment completes
7. Status shows "completed" in admin
8. Notification email sent to employee

⏱️ **Time**: 2 minutes

---

### Task 2: Setup Event with Crew

1. Create event (in Events admin)
2. Assign crew members (Event Crew admin)
3. Send invitations (bulk action)
4. Wait for confirmations (in Event Crew list)
5. Send reminders next day (bulk action)
6. Event happens
7. Mark crew as completed (status change)

⏱️ **Time**: 5 minutes spread over event duration

---

### Task 3: Monitor Payments

1. Go to M-Pesa Payments admin
2. Filter by status = "pending"
3. Check when payment initiated
4. If stuck: Click "Resend STK Push"
5. If failed: Delete and create new

⏱️ **Time**: 1 minute

---

### Task 4: Check Email Status

1. Go to Email Notifications admin
2. Filter by is_sent = False (failed)
3. Select failed emails
4. Action: "Resend Failed Notifications"
5. Emails resent automatically

⏱️ **Time**: 1 minute

---

## 🐛 Troubleshooting

### "STK Push not working?"

✅ **Check:**
1. Phone number format: Must be `254XXXXXXXXX` (starts with 254)
2. M-Pesa credentials: Correct key and secret from Safaricom
3. Environment: "sandbox" for testing, "production" for live
4. Network: Check internet connectivity

---

### "Crew not receiving invitations?"

✅ **Check:**
1. Crew member has email in profile
2. EMAIL_BACKEND configured
3. EMAIL_HOST_USER and PASSWORD correct
4. For Gmail: Using "App Password" not regular password
5. Check Email Notifications admin for failed emails

---

### "Payment stuck in 'pending'?"

✅ **Solutions:**
1. User didn't complete STK prompt on phone
2. Click "Resend STK Push" button
3. Wait 5 minutes and refresh
4. Check M-Pesa logs on Safaricom portal
5. User may have insufficient funds

---

## 📞 Support

### For M-Pesa Issues:
- Contact: Safaricom Developer Support
- Documentation: https://developer.safaricom.co.ke/docs

### For Django Issues:
- Check: `QUALITY_IMPLEMENTATION_SUMMARY.md`
- Read: `MPESA_CRM_IMPLEMENTATION.md`
- Django Docs: https://docs.djangoproject.com/

### For System Issues:
- Check Django logs: `/tmp/django.log`
- Check M-Pesa callbacks in admin
- Verify environment variables are set

---

## ✨ Pro Tips

💡 **Tip 1**: Always test in sandbox first before going to production

💡 **Tip 2**: Send invitations at least 2-3 days before events

💡 **Tip 3**: Send reminders the day before, not hours before

💡 **Tip 4**: Keep phone numbers in format 254XXXXXXXXX (no +, no 0)

💡 **Tip 5**: Check Email Notifications regularly for delivery issues

💡 **Tip 6**: Use "Search" in admin to find specific payments/crew quickly

---

## 🎯 Next Steps

1. ✅ Install requirements.txt
2. ✅ Run migrations
3. ✅ Configure M-Pesa credentials
4. ✅ Configure email backend
5. ✅ Test M-Pesa payment in sandbox
6. ✅ Test crew invitations
7. ✅ Test reminders
8. ✅ Deploy to production

---

## 📊 Success Metrics

Track these to ensure system is working well:

| Metric | Target | Current |
|--------|--------|---------|
| M-Pesa Payment Success Rate | > 95% | __ |
| Email Delivery Rate | > 99% | __ |
| Crew Confirmation Rate | > 80% | __ |
| Average Response Time | < 2s | __ |
| System Uptime | > 99% | __ |

---

**Ready to get started?** 🚀

1. Install dependencies
2. Run migrations
3. Configure credentials
4. Send your first payment
5. Assign your first crew

**Questions?** See `MPESA_CRM_IMPLEMENTATION.md` for detailed guides.

---

**Last Updated**: January 26, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
