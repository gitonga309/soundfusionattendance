# M-Pesa Testing Quick Reference

## Configuration Summary ✓

Your M-Pesa setup is now configured to work with your hosted app!

```
App URL:        https://sound-fusion-attendance.onrender.com/
Callback URL:   https://sound-fusion-attendance.onrender.com/api/mpesa/callback/
Shortcode:      174379 (SAF Default Test)
Environment:    Sandbox (Testing)
```

## To Test M-Pesa Payments:

### 1. Push Code to Render
```bash
git add -A
git commit -m "Configure M-Pesa with hosted callback URL and SAF test shortcode"
git push
```

### 2. Test Payment Flow
1. Open: https://sound-fusion-attendance.onrender.com/
2. Login or create account
3. Go to Payment section
4. Click "Pay with M-Pesa"
5. Enter test phone: `254708374149` or `254717123456`
6. Enter amount: `100` (KSH)
7. Click "Confirm Payment"

### 3. When STK Prompt Appears
- PIN: `123456`
- Press OK

### 4. Check Payment Status
- Payment will complete automatically
- Status updates in database
- Confirmation email sent to user
- Receipt appears in admin panel

## Test Credentials

| Item | Value |
|------|-------|
| **Shortcode** | 174379 |
| **Test Phone 1** | 254708374149 |
| **Test Phone 2** | 254717123456 |
| **Test PIN** | 123456 |
| **Min Amount** | 1 KSH |
| **Max Amount** | 150,000 KSH |
| **Pass Key** | bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919 |

## Where to Check Results

### Admin Panel
- URL: https://sound-fusion-attendance.onrender.com/admin/
- Go to "M-Pesa Payments"
- View all payment records and statuses

### User Dashboard  
- URL: https://sound-fusion-attendance.onrender.com/dashboard/
- View payment history
- Check balance updates

### Database
- Table: `attendance_mpesapayment`
- Fields: status, receipt_number, result_code, transaction_date

## When You Get Your Own Safaricom Account

Update these Render environment variables:
1. `MPESA_BUSINESS_SHORT_CODE` = Your shortcode
2. `MPESA_PASS_KEY` = Your pass key
3. `MPESA_CONSUMER_KEY` = Your consumer key
4. `MPESA_CONSUMER_SECRET` = Your consumer secret
5. `MPESA_ENVIRONMENT` = `production`

The callback URL will continue to work automatically!

## Troubleshooting

| Issue | Solution |
|-------|----------|
| STK not appearing | Check phone number format (should start with 254) |
| Payment fails | Verify amount is 1-150,000 KSH |
| Callback not received | Check MPESA_CALLBACK_URL in settings.py |
| No confirmation email | Check EMAIL settings in settings.py |
| Can't see payments in admin | Check user has is_staff or is_superuser |

## API Endpoints

```
POST   /api/mpesa/request-payment/      → Initiate STK push
POST   /api/mpesa/callback/              → Receive M-Pesa callbacks
GET    /api/mpesa/payment-status/        → Check payment status
GET/POST /payment/stk-push/              → Manual STK push modal
GET    /api/stk-status/                  → Check STK request status
```

## Files Modified

- [soundfusion_attendance/settings.py](soundfusion_attendance/settings.py) - Added hosted callback URL and test credentials

---

Your app is ready to receive M-Pesa payments! 🎉
