# M-Pesa STK Push & CRM Implementation Guide

## Overview

This document details the implementation of **M-Pesa STK Push payment integration** and **Event Crew CRM system** for Sound Fusion Attendance Application. These features enable high-quality payment processing and professional event management.

---

## 1. M-Pesa STK Push Payment Integration

### 1.1 Features Implemented

- **STK Push Requests**: Initiate Lipa Na M-Pesa Online payments via STK (Sim Toolkit)
- **Automated Callbacks**: Receive and process M-Pesa payment confirmations
- **Payment Tracking**: Store and track all M-Pesa transactions with status
- **Admin Dashboard**: Easy payment management and resend functionality
- **Balance Updates**: Automatic balance reduction when payment is confirmed

### 1.2 Setup Instructions

#### Step 1: Get M-Pesa API Credentials

1. Register with **Safaricom Developer** at: https://developer.safaricom.co.ke/
2. Create an application and get:
   - **Consumer Key**
   - **Consumer Secret**
   - **Business Short Code** (for sandbox: 174379, for production: your assigned code)
   - **Pass Key** (Lipa Na M-Pesa Online - Passkey)

#### Step 2: Configure Environment Variables

Set these in your production environment:

```bash
# M-Pesa Credentials
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_BUSINESS_SHORT_CODE=174379  # Use 174379 for sandbox
MPESA_PASS_KEY=your_pass_key
MPESA_INITIATOR_NAME=api_operationID
MPESA_INITIATOR_PASSWORD=your_initiator_password
MPESA_ENVIRONMENT=sandbox  # Use 'production' in production

# Callback URL (must be accessible from internet)
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/
```

#### Step 3: Email Configuration

Set these for email notifications:

```bash
# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 1.3 Admin Usage

#### Requesting M-Pesa Payment

1. Go to **Django Admin** → **M-Pesa Payments**
2. Click **Add M-Pesa Payment**
3. Fill in:
   - Employee/User
   - Phone Number (format: 254xxxxxxxxx)
   - Amount (KSH)
   - Payment Purpose
4. Click **Save**
5. The STK push will be initiated automatically
6. Employee receives USSD prompt on their phone

#### Resending STK Push

1. In M-Pesa Payments list, find the payment with status "Pending"
2. Click the **"Resend STK Push"** button in the Action column
3. Or select multiple payments and use **"Initiate M-Pesa STK Push"** action

#### Viewing Payment History

- Status shows: `initiated` → `pending` → `completed` or `failed`
- Receipt number automatically captured when payment completes
- Timestamps track initiation and completion

### 1.4 API Endpoints

#### Request M-Pesa Payment
```
POST /api/mpesa/request-payment/
Content-Type: application/json

{
  "amount": 500.00,
  "phone": "254700123456",
  "purpose": "Salary Payment"
}

Response:
{
  "success": true,
  "payment_id": 123,
  "checkout_request_id": "...",
  "message": "STK push initiated successfully"
}
```

#### Check Payment Status
```
GET /api/mpesa/payment-status/?payment_id=123

Response:
{
  "payment_id": 123,
  "status": "completed",
  "amount": "500.00",
  "receipt_number": "ABC123XYZ",
  "completed_at": "2026-01-26T14:30:00Z"
}
```

#### M-Pesa Callback (Safaricom → Your Server)
```
POST /api/mpesa/callback/

Callback processed automatically. No manual action required.
```

### 1.5 Database Models

**MpesaPayment Model:**
- `user`: ForeignKey to User
- `phone_number`: Recipient's phone number
- `amount`: Payment amount in KSH
- `payment_purpose`: Description of payment
- `checkout_request_id`: Unique M-Pesa request ID
- `status`: Current payment status (initiated, pending, completed, failed, cancelled)
- `receipt_number`: M-Pesa transaction receipt
- `transaction_date`: When payment was completed
- `initiated_at`: Timestamp of request
- `completed_at`: Timestamp of completion

### 1.6 Files Modified/Created

- `soundfusion_attendance/settings.py` - Added M-Pesa configuration
- `attendance/mpesa_utils.py` - NEW: M-Pesa API client and callback processor
- `attendance/models.py` - Added MpesaPayment model
- `attendance/admin.py` - Added MpesaPaymentAdmin with actions
- `attendance/views.py` - Added M-Pesa payment and callback views
- `attendance/urls.py` - Added M-Pesa API routes
- `requirements.txt` - Added requests, celery, redis

---

## 2. Event Crew CRM System

### 2.1 Features Implemented

- **Crew Assignments**: Assign crew members to events with specific roles
- **Automated Invitations**: Send email invitations to assigned crew
- **Confirmation Tracking**: Track crew confirmation status
- **Crew Reminders**: Send reminders before event date
- **Setup Briefings**: Distribute detailed setup instructions
- **Communication History**: Log all communications sent to crew

### 2.2 CRM Workflow

#### Step 1: Create Event and Assign Crew

1. Go to **Events** → **Create Event**
2. Fill in event details (name, date, location, etc.)
3. After creating event, go to **Django Admin** → **Event Crew**
4. Click **Add Event Crew**
5. Select:
   - Event
   - User (crew member)
   - Role (e.g., "Sound Engineer", "Lighting Tech", "Setup Lead")
   - Add any special instructions in Notes

#### Step 2: Send Crew Invitations

**Method 1: Admin Action**
1. Go to **Django Admin** → **Event Crew**
2. Filter by specific event
3. Select crew with `invitation_sent = False`
4. Action dropdown → **"Send Invitations to Selected Crew"**
5. Click Go

**Method 2: Individual Send**
1. Click on an EventCrew record
2. Click **"Send Invite"** button if invitation not yet sent
3. Email sent immediately

#### Step 3: Track Confirmations

1. Crew members see assignments in **"My Crew Assignments"** page
2. They can click **"Confirm"** or **"Decline"**
3. Admin sees status update in real-time in EventCrew list
4. Filter by `status=confirmed` to see confirmed crew

#### Step 4: Send Reminders

1. One day before event, select confirmed crew
2. Go to **Event Crew** list
3. Select crew with `status=confirmed` and `reminder_sent=False`
4. Action dropdown → **"Send Reminders to Confirmed Crew"**
5. Click Go

#### Step 5: Send Setup Briefing

1. Before event day, go to **Event Crew** list
2. Filter by event
3. Select all confirmed crew
4. Use admin actions to send setup briefing
5. Crew receives detailed instructions with:
   - Event details
   - Complete crew roster
   - Special instructions
   - Contact information

### 2.3 Email Templates

#### Crew Invitation Email
```
Subject: You are invited to work on: [Event Name]

Dear [Crew Member Name],

You are invited to work as a [Role] for the following event:

Event: [Event Name]
Date: [Event Date]
Location: [Event Location]

[Special Instructions if any]

Please confirm your participation as soon as possible.

[Confirmation Link]

Thank you,
Sound Fusion Team
```

#### Event Reminder Email
```
Subject: Reminder: [Event Name] - [Event Date]

Dear [Crew Member Name],

This is a friendly reminder about the upcoming event:

Event: [Event Name]
Date: [Event Date] at [Event Time]
Location: [Event Location]
Your Role: [Role]

[Special Instructions]

Please ensure you arrive on time and bring all necessary equipment.
```

#### Setup Briefing Email
```
Subject: Setup Briefing: [Event Name]

Dear [Crew Member Name],

Setup Briefing for: [Event Name]
[Event Details]
[Crew List]
[Special Instructions]

Please confirm receipt and report any issues immediately.
```

### 2.4 Admin Interface Enhancements

**EventCrew Admin Features:**
- List display with inline editing
- Status filtering (invited, confirmed, declined, completed)
- Bulk actions for sending invitations and reminders
- Communication tracking (invitation_sent, reminder_sent, timestamps)
- Search by crew name, email, event, or role

**Email Notification Admin:**
- Track all emails sent
- View failed notifications
- Resend failed emails
- Filter by notification type and status

### 2.5 Database Models

**EventCrew Model:**
- `event`: ForeignKey to Event
- `user`: ForeignKey to User (crew member)
- `role`: Job title/role in event
- `status`: Current status (invited, confirmed, declined, completed)
- `invitation_sent`: Boolean flag + timestamp
- `reminder_sent`: Boolean flag + timestamp
- `notes`: Special instructions

**EmailNotification Model:**
- `recipient`: Email address
- `user`: ForeignKey to User (nullable)
- `notification_type`: Type of notification (event_created, crew_assignment, etc.)
- `subject`: Email subject
- `message`: Email body
- `is_sent`: Boolean flag
- `sent_at`: Timestamp
- `failed_attempts`: Counter for retries
- `last_error`: Error message if failed

### 2.6 Crew Member Portal

Visit `/crew/assignments/` to see:
- **Pending Invitations**: Events you haven't confirmed yet
- **Confirmed Assignments**: Events you've committed to
- **Completed Events**: Past events you worked on
- **Declined Assignments**: Events you declined

Actions:
- Click **"Confirm"** to accept assignment
- Click **"Decline"** to reject assignment

### 2.7 Files Modified/Created

- `attendance/models.py` - Added EventCrew and EmailNotification models
- `attendance/email_utils.py` - NEW: CRM email notification system
- `attendance/admin.py` - Added EventCrewAdmin, EmailNotificationAdmin
- `attendance/views.py` - Added crew assignment views
- `attendance/urls.py` - Added crew assignment routes
- `attendance/templates/attendance/crew_assignments.html` - NEW: Crew portal template

---

## 3. Quality Standards Implementation

### 3.1 Code Standards

✅ **Database Indexes**
- Added indexes on frequently queried fields
- Example: `(event, status)`, `(user, status)`, `(checkout_request_id)`

✅ **Error Handling**
- Try-catch blocks in all external API calls
- Graceful fallback if M-Pesa service is down
- Error logging with timestamps

✅ **Security**
- CSRF protection on all forms
- User permission checks (login_required, user_passes_test)
- Sensitive credentials stored in environment variables

✅ **Performance**
- select_related() for foreign key queries
- Caching for frequently accessed data
- Async email sending (optional with Celery)

✅ **Logging**
- All payment operations logged
- All email sends logged
- Error tracking for debugging

### 3.2 Admin Interface Standards

✅ **User Experience**
- Organized admin sections (M-Pesa, Crew, Notifications)
- Bulk actions for common tasks
- Quick action buttons (Resend, Send Invite)
- Status indicators and badges
- Search and filter capabilities

✅ **Data Integrity**
- Readonly fields for system-generated data (IDs, timestamps)
- Proper field ordering in forms
- Validation at model and form levels

### 3.3 API Standards

✅ **RESTful Design**
- Proper HTTP methods (POST, GET, DELETE)
- JSON request/response format
- Appropriate status codes (200, 400, 404, 500)

✅ **Error Responses**
```json
{
  "error": "Error message here",
  "status": "failed",
  "code": "ERROR_CODE"
}
```

✅ **Success Responses**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

---

## 4. Configuration Checklist

- [ ] Set up M-Pesa Developer account and get credentials
- [ ] Configure environment variables in production
- [ ] Set up email backend (Gmail, SendGrid, etc.)
- [ ] Update MPESA_CALLBACK_URL to your production domain
- [ ] Test M-Pesa in sandbox first
- [ ] Configure Redis for Celery (optional but recommended)
- [ ] Set up log files for monitoring
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser if needed: `python manage.py createsuperuser`
- [ ] Test payment flow end-to-end
- [ ] Test email notifications

---

## 5. Production Deployment

### Security Checklist

- [ ] Change `MPESA_ENVIRONMENT` to `production`
- [ ] Update `MPESA_BUSINESS_SHORT_CODE` to production code
- [ ] Enable SSL/HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Set `DEBUG = False`
- [ ] Use strong SECRET_KEY
- [ ] Store credentials in `.env` file or secrets manager
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up regular backups
- [ ] Monitor M-Pesa callback failures

### Monitoring

- Check M-Pesa payment status in admin daily
- Monitor failed email notifications
- Review error logs for issues
- Track payment success rates

---

## 6. Troubleshooting

### M-Pesa Issues

**Q: STK push not appearing on phone**
- A: Verify phone number format (must start with 254)
- A: Check if M-Pesa API credentials are correct
- A: Ensure you're in sandbox/production correctly

**Q: Callback not received**
- A: Verify MPESA_CALLBACK_URL is publicly accessible
- A: Check firewall/CORS settings
- A: Monitor logs for incoming POST requests

**Q: Payment stuck in "pending" status**
- A: Check M-Pesa logs on Safaricom portal
- A: User may not have completed STK prompt
- A: Try "Resend STK Push" action

### Email Issues

**Q: Crew invitations not being sent**
- A: Check EMAIL_BACKEND is configured correctly
- A: Verify EMAIL_HOST_USER has permission
- A: Check logs for SMTP errors
- A: For Gmail, use "App Password" not regular password

**Q: Emails going to spam**
- A: Add SPF, DKIM, DMARC records for domain
- A: Use consistent FROM email address
- A: Avoid spam trigger words in templates

---

## 7. Support & Updates

For issues or updates:
1. Check error logs in Django admin
2. Review M-Pesa callback responses
3. Test with sandbox credentials first
4. Monitor email delivery status in EmailNotification admin

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production Ready
