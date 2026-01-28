# M-Pesa Configuration Setup for Production

## Date: January 28, 2026

### Changes Made

Your M-Pesa integration has been configured for your hosted app on Render:

#### 1. **Business Shortcode**
- **Default SAF Test Shortcode**: `174379`
- This is the Safaricom-provided default shortcode for sandbox testing
- Location: [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py#L193)

#### 2. **Pass Key**
- **Default SAF Test Pass Key**: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`
- This is the default test pass key from Safaricom
- Location: [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py#L194)

#### 3. **Callback URL**
- **Production Callback URL**: `https://sound-fusion-attendance.onrender.com/api/mpesa/callback/`
- This URL will receive M-Pesa payment callbacks
- When M-Pesa processes a payment, it will send the response to this endpoint
- Location: [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py#L202)

#### 4. **Environment Settings**
- **Environment**: `sandbox` (default)
- **Consumer Key & Secret**: Already configured from SAF
- These are configured in settings and use environment variables for production

### How It Works

1. **Payment Initiation Flow**:
   - User initiates STK push payment via the app
   - App calls M-Pesa Sandbox API at: `https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest`
   - STK prompt appears on customer's phone

2. **Callback Processing**:
   - When user enters M-Pesa PIN and completes payment, M-Pesa sends callback
   - Callback is received at: `https://sound-fusion-attendance.onrender.com/api/mpesa/callback/`
   - App processes the callback and updates payment status in database
   - Confirmation email is sent to user

### Endpoints

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/api/mpesa/request-payment/` | Initiate STK push payment | POST |
| `/api/mpesa/callback/` | Receive M-Pesa callbacks | POST |
| `/api/mpesa/payment-status/` | Check payment status | GET |
| `/payment/stk-push/` | STK push modal UI | GET/POST |

### Testing the Setup

#### Test Phone Numbers (from SAF):
- `254708374149`
- `254717123456`

#### Test PIN:
- `123456`

#### Valid Test Amounts:
- Between KSH 1 and KSH 150,000

#### Testing Steps:
1. Navigate to a payment page in your app
2. Enter a test phone number (without +254 prefix, app adds it)
3. Enter amount (1-150,000 KSH)
4. Click "Pay with M-Pesa"
5. M-Pesa STK prompt appears
6. Enter test PIN: `123456`
7. Payment processes and callback is received
8. Payment status updates to "completed"

### Important Notes

1. **Sandbox vs Production**:
   - Currently using **SANDBOX** mode
   - For production, you'll need:
     - Your actual Safaricom business shortcode
     - Your actual Safaricom pass key
     - Set `MPESA_ENVIRONMENT` to `production`

2. **Environment Variables**:
   - All credentials can be overridden via environment variables on Render:
     - `MPESA_BUSINESS_SHORT_CODE`
     - `MPESA_PASS_KEY`
     - `MPESA_CONSUMER_KEY`
     - `MPESA_CONSUMER_SECRET`
     - `MPESA_CALLBACK_URL`
     - `MPESA_ENVIRONMENT`

3. **CSRF Token**:
   - The callback view has `@csrf_exempt` decorator to allow M-Pesa callbacks
   - This is safe since M-Pesa validates requests separately

4. **Payment Records**:
   - All payments are tracked in the `MpesaPayment` model
   - Status flow: initiated → pending → completed/failed
   - Receipt numbers and transaction dates are captured

### Configuration Files Updated

- [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py#L192-L202)

### Next Steps

When you get your own Safaricom business account:
1. Get your business shortcode from Safaricom
2. Get your pass key from Safaricom
3. Update environment variables on Render:
   - Set `MPESA_BUSINESS_SHORT_CODE` to your shortcode
   - Set `MPESA_PASS_KEY` to your pass key
   - Optionally set `MPESA_ENVIRONMENT` to `production`

The callback URL will automatically work with your Render-hosted app.
