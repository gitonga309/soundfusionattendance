# M-Pesa Configuration - Final Reference

## Current Configuration (Active Now)

```python
# File: soundfusion_attendance/settings.py
# Lines 196-203

# M-Pesa API Credentials
MPESA_CONSUMER_KEY = 'FiT4hg3x50VAokkOpxAbADAjK17q4TpVrO1bpeYnCwwj0l3o'
MPESA_CONSUMER_SECRET = 'qpYvdPTfB3vZpSLXRJiY12xw0YDEtuZGWHxu2IyjGHfPQGAy5W4hkku4eAlWN2R8'

# SAF (Safaricom) default test shortcode - 174379
MPESA_BUSINESS_SHORT_CODE = '174379'
MPESA_PASS_KEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

MPESA_ENVIRONMENT = 'sandbox'  # sandbox or production

# M-Pesa callback URL - Point to your hosted domain
MPESA_CALLBACK_URL = 'https://sound-fusion-attendance.onrender.com/api/mpesa/callback/'
```

---

## How M-Pesa Payment Flow Works

```
┌─────────────────┐
│  User Opens App │
│   sound-fusion  │
│  onrender.com   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│   User Clicks "Pay"      │
│  Enters Phone & Amount   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  App Calls: initiate_stk_push()              │
│  Sends request to:                           │
│  https://sandbox.safaricom.co.ke/mpesa/      │
│  stkpush/v1/processrequest                   │
│  With:                                        │
│  - BusinessShortCode: 174379                 │
│  - Amount: User amount                       │
│  - CallBackURL: https://...onrender.com/     │
│    api/mpesa/callback/                       │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  STK Prompt Appears on Phone   │
│  (M-Pesa Push Notification)    │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  User Enters PIN: 123456       │
│  Confirms Payment              │
└────────┬───────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  M-Pesa Processes Payment                    │
│  Calls App Callback URL:                     │
│  POST https://sound-fusion-attendance.       │
│      onrender.com/api/mpesa/callback/        │
│                                              │
│  With payment result:                        │
│  - CheckoutRequestID                         │
│  - ResultCode: 0 (success)                   │
│  - MpesaReceiptNumber                        │
│  - TransactionDate                           │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  App Callback Handler Processes              │
│  process_mpesa_callback()                    │
│  - Finds payment record                      │
│  - Updates status to "completed"             │
│  - Stores receipt number                     │
│  - Saves transaction date                    │
│  - Sends confirmation email                  │
└────────┬─────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Payment Complete ✓                │
│  User sees confirmation            │
│  Admin sees payment in dashboard   │
│  Email sent to user                │
└────────────────────────────────────┘
```

---

## Configuration Breakdown

### 1. Consumer Key & Secret
```
MPESA_CONSUMER_KEY = 'FiT4hg3x50VAokkOpxAbADAjK17q4TpVrO1bpeYnCwwj0l3o'
MPESA_CONSUMER_SECRET = 'qpYvdPTfB3vZpSLXRJiY12xw0YDEtuZGWHxu2IyjGHfPQGAy5W4hkku4eAlWN2R8'
```
- **Purpose**: Authenticate with M-Pesa sandbox API
- **Used for**: Getting access tokens for API calls
- **Mode**: Sandbox (for testing)

### 2. Business Shortcode
```
MPESA_BUSINESS_SHORT_CODE = '174379'
```
- **Purpose**: Unique identifier for your business in M-Pesa
- **Value**: SAF (Safaricom) default test shortcode
- **Sandbox Only**: This is for testing, not production
- **How It Works**: When STK push is sent, M-Pesa knows which business is requesting payment

### 3. Pass Key
```
MPESA_PASS_KEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
```
- **Purpose**: Encrypt password for API requests
- **Used for**: Generating password in STK push requests
- **Format**: Encodes timestamp + shortcode + passkey as base64
- **Sandbox Only**: This is SAF's default test pass key

### 4. Environment
```
MPESA_ENVIRONMENT = 'sandbox'
```
- **sandbox**: Uses test API endpoints
- **production**: Uses real API endpoints
- **Current**: sandbox (testing mode)

### 5. Callback URL
```
MPESA_CALLBACK_URL = 'https://sound-fusion-attendance.onrender.com/api/mpesa/callback/'
```
- **Purpose**: Tell M-Pesa where to send payment results
- **When M-Pesa Calls This**: After user enters PIN and payment is processed
- **What M-Pesa Sends**: JSON with payment result (success/failed)
- **Your App Does**: Updates database, sends email, shows confirmation

---

## API Endpoints in Your App

### 1. Request Payment
```
POST /api/mpesa/request-payment/
```
- **Triggers**: STK push to user's phone
- **Sends**: Phone number, amount, purpose
- **Returns**: Checkout request ID
- **Called by**: Frontend when user clicks "Pay"

### 2. Callback Endpoint
```
POST /api/mpesa/callback/
```
- **Called by**: M-Pesa (not your users)
- **Receives**: Payment result from M-Pesa
- **Does**: Process payment, update database, send email
- **Returns**: Success/fail response to M-Pesa
- **CSRF**: Exempted (M-Pesa can't provide CSRF token)

### 3. Check Payment Status
```
GET /api/mpesa/payment-status/?payment_id=123
```
- **Called by**: Frontend to check if payment completed
- **Returns**: Current payment status
- **Statuses**: initiated, pending, completed, failed, cancelled

### 4. Manual STK Push
```
GET/POST /payment/stk-push/
```
- **Called by**: Admin for manual payment collection
- **Modal**: Shows form to enter phone/amount
- **Triggers**: STK push if submitted

---

## Test Workflow

### To Test Payments:

1. **Go to app**: https://sound-fusion-attendance.onrender.com/
2. **Login**: Use your credentials
3. **Start payment**: Click payment button
4. **Enter details**:
   - Phone: `254708374149` or `254717123456`
   - Amount: `100` KSH
5. **Submit**: Click "Pay with M-Pesa"
6. **Enter PIN**: When prompted, enter `123456`
7. **Confirm**: Payment processes
8. **See callback**: App receives result
9. **Check status**: Payment marked as completed
10. **Check admin**: See payment in admin panel

---

## Database Storage

### Payment Records
```sql
Table: attendance_mpesapayment

Columns:
- id (primary key)
- user_id (foreign key)
- phone_number: '254708374149'
- amount: 100.00
- payment_purpose: 'balance_payment'
- checkout_request_id: 'ws_CO_28_04_2023_093518' (unique)
- merchant_request_id: '29115-34620561-1'
- status: 'completed' (initiated, pending, completed, failed)
- receipt_number: 'LGR7S7LR43' (from M-Pesa)
- transaction_date: 20230428093519 (from M-Pesa)
- result_code: 0 (0=success, other=error)
- result_description: 'The service request...'
- initiated_at: 2023-04-28 09:35:18
- completed_at: 2023-04-28 09:35:25
```

---

## Logging

All M-Pesa operations are logged to help debug:

```
[2023-04-28 09:35:18] INFO: STK push initiated for user_1
[2023-04-28 09:35:20] DEBUG: Access token obtained
[2023-04-28 09:35:21] INFO: M-Pesa API response: CheckoutRequestID=ws_CO_...
[2023-04-28 09:35:25] INFO: Callback received for checkout_1
[2023-04-28 09:35:25] INFO: Payment marked as completed
[2023-04-28 09:35:26] INFO: Confirmation email sent to user
```

Check Render logs:
- Go to https://dashboard.render.com
- Select service → Logs
- Search for "mpesa" or "M-Pesa"

---

## When You Get Your Own Safaricom Account

Update these settings on Render:

| Variable | Get From |
|----------|----------|
| MPESA_BUSINESS_SHORT_CODE | Safaricom dashboard |
| MPESA_PASS_KEY | Safaricom dashboard |
| MPESA_CONSUMER_KEY | Safaricom dashboard |
| MPESA_CONSUMER_SECRET | Safaricom dashboard |
| MPESA_ENVIRONMENT | Set to "production" |

The callback URL stays the same:
```
https://sound-fusion-attendance.onrender.com/api/mpesa/callback/
```

---

## Files to Review

1. **Settings**: [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py#L192-L203)
   - M-Pesa configuration

2. **Views**: [attendance/views.py](attendance/views.py#L1096)
   - Callback handler
   - Payment initiation
   - Status checking

3. **Utils**: [attendance/mpesa_utils.py](attendance/mpesa_utils.py)
   - M-Pesa client (API calls)
   - Callback processing
   - Email notifications

4. **Models**: [attendance/models.py](attendance/models.py#L490)
   - MpesaPayment model
   - Payment fields

5. **URLs**: [attendance/urls.py](attendance/urls.py#L34-L43)
   - API endpoints

---

## Troubleshooting Quick Reference

| Problem | Check | Solution |
|---------|-------|----------|
| No STK prompt | Phone number format | Must be 254XXXXXXXXX |
| Payment fails | Amount range | Must be 1-150,000 KSH |
| Callback not received | Callback URL | Check MPESA_CALLBACK_URL in settings |
| No confirmation email | Email config | Check EMAIL settings in settings.py |
| Can't see payments | Admin permission | User must have is_staff=True |
| Logs not showing | Debug mode | Check DEBUG=True in settings |

---

## Summary

✅ **Callback URL**: https://sound-fusion-attendance.onrender.com/api/mpesa/callback/
✅ **Business Shortcode**: 174379
✅ **Pass Key**: Configured
✅ **Environment**: Sandbox (testing)
✅ **All Endpoints**: Ready
✅ **Payment Model**: Ready
✅ **Email**: Ready
✅ **Logging**: Ready

**Your M-Pesa integration is complete and ready to test!** 🎉
