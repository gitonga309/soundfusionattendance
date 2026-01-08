# Expense Reimbursement System - Quick User Guide

## For Regular Users

### How to Submit a Reimbursement Request

1. **Log in** to your Sound Fusion account
2. Go to **Dashboard**
3. Click **"Request Reimbursement"** button (bottom of page)
   - Or use navbar: **Reimbursements** → **New Request**

4. **Fill the form**:
   - **Event** (optional): Select the event this expense is related to
   - **Expense Type**: Choose from:
     - Transport (Uber/Bolt)
     - Purchase (Equipment/Supplies)
     - Airtime
     - Meal/Food
     - Other
   - **Amount**: Enter the amount in KSH (max 50,000)
   - **Description**: Explain what the expense was for
   - **Receipt Photo** (optional): Upload proof/receipt image

5. **Click Submit**
   - You'll see: "Reimbursement request submitted! Awaiting admin approval."

### How to Track Your Requests

1. Go to **Dashboard**
2. Click **"Reimbursements"** in navbar
   - Or click **"View Records"** → navigate to reimbursements

3. **View your status**:
   - 🟡 **Pending** (yellow) = Waiting for approval
   - 🟢 **Approved** (green) = Done! Balance updated
   - 🔴 **Rejected** (red) = Not approved, check reason below

4. **For Rejected Requests**: Scroll down to see the rejection reason
   - Contact admin if you have questions

---

## For Admin/Accountant

### How to Review & Approve Requests

1. **Log in** to your admin account
2. Go to **Admin Dashboard**
3. Click **"Reimbursements"** in top navbar

4. **See pending requests** (first tab):
   - Shows count of pending requests
   - Each card displays:
     - User name and email
     - Amount (in green highlight)
     - Expense type
     - Event name
     - Description
     - Receipt link (if uploaded)

5. **To Approve**:
   - Click green **"Approve"** button
   - Done! User balance automatically updated
   - Request moves to "Approved" tab

6. **To Reject**:
   - Click red **"Reject"** button
   - Fill in rejection reason (required)
   - Explain why (e.g., "No receipt provided" / "Amount too high")
   - Click **"Reject Request"**
   - User will see reason in their history

### View Approved/Rejected History

1. Click **"Approved"** or **"Rejected"** tab
2. **For Approved**: See who approved and when
3. **For Rejected**: See rejection reason
4. Use for audit and reporting

### Alternative: Admin Interface

1. Go to **Django Admin** (`/admin/`)
2. Navigate to **Reimbursements**
3. Can bulk change status or filter by date/type
4. But **recommended way is the Reimbursements Dashboard** for better UX

---

## Key Rules

### Amount Limits
- **Minimum**: Any positive amount
- **Maximum**: KSH 50,000 per request
- Larger amounts must be split into multiple requests

### Approved vs Approved Balance
- When request is **approved**, amount is **immediately added to user balance**
- User can see new balance in their dashboard
- User can check "My Reimbursements" to see all transactions

### Rejection Reasons
- Always provide a reason when rejecting
- Be specific: "No receipt", "Missing description", "Amount too high", etc.
- User can then resubmit with corrections

### Receipt Photos
- **Optional** but recommended for amounts > 5,000 KSH
- Helps prevent fraud
- Can be any image format (JPG, PNG, etc.)
- Keep file size reasonable for uploads

---

## Common Questions

**Q: What if I submitted wrong amount?**
A: Request will be rejected. The reason will explain. Resubmit with correct amount.

**Q: How long does approval take?**
A: Check with your accountant. Usually within 1-2 days.

**Q: Can I upload multiple receipts?**
A: Currently, only 1 receipt per request. For multiple items, submit separate requests or combine into one description.

**Q: What if balance still not updated after approval?**
A: Check "My Reimbursements" to confirm status is "Approved". If yes, contact admin.

**Q: Can I cancel a request?**
A: Contact admin. Cannot cancel via system currently.

**Q: Why is my amount rejected as invalid?**
A: Could be:
- Negative or zero amount
- Amount > 50,000 KSH (system limit)
- Non-numeric characters in amount field

---

## Balance Calculation

Your total balance = Attendance fees + Admin adjustments + Approved reimbursements

Example:
```
Attendance records:      5,000 KSH
Admin adjustment:        +500 KSH (bonus)
Approved reimbursement:  +300 KSH (transport)
─────────────────────────────────
Total Balance:           5,800 KSH
```

---

## Workflow Diagram

```
USER SUBMITS REQUEST
        ↓
 [Form Submission]
        ↓
  Validation Check
   (Amount ≤ 50k)
        ↓
  Request Saved
  Status: PENDING
        ↓
  ADMIN REVIEWS
        ↓
     APPROVE          REJECT
        ↓                ↓
  Balance            Provide
  Updated            Reason
        ↓                ↓
  User Notified    User Notified
  Next Login       See Reason
        ↓                ↓
   APPROVED      User Can
   Status      Resubmit
```

---

## Integration with Dashboard

Your reimbursement requests are part of your **overall balance** shown in the dashboard.

- Check dashboard anytime to see current total balance
- This includes all approved reimbursements
- Updates automatically when admin approves

---

## Security & Privacy

✅ Only admins can approve/reject
✅ Each user only sees their own requests
✅ All transactions logged and audited
✅ Receipt photos stored securely
✅ No balance changes without audit trail

---

## Support

If you have issues:
1. Check this guide
2. Contact your administrator
3. Or check the system for error messages

---

**Last Updated**: 2025
**System**: Sound Fusion Attendance & Reimbursement
