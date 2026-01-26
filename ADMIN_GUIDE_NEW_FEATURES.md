# Admin Guide - New Feature Management

## Overview of Enhancements

This guide explains how to use and manage the new features in the Sound Fusion Attendance system.

---

## 1. Salaried Employee Self-Onboarding Management

### Admin Dashboard Location
**Admin Panel → Attendance → Employee Onboarding**

### What You'll See
- List of all onboarding applications
- Color-coded status badges:
  - 🟡 **Yellow**: Pending Review
  - 🔵 **Blue**: Accepted
  - 🟤 **Grey**: Completed
  - 🔴 **Red**: Rejected

### How to Review an Application

1. **Click on any application** to view full details
2. **Check applicant information**:
   - Personal details (name, DOB, ID)
   - Employment info (job role, salary)
   - Contact info (email, phone)
   - Documents submitted (if any)

3. **Approve the Application**:
   - Change Status to: "Accepted" or "Completed"
   - Click Save
   - Employee profile is updated with their submitted details
   - They can now log in and use the system

4. **Reject the Application** (if needed):
   - Change Status to: "Rejected"
   - Add Rejection Reason (explain why)
   - Click Save
   - Employee receives notification
   - They can resubmit after fixing issues

### Key Fields
- **Status**: pending → accepted → completed (or rejected)
- **Reviewed By**: Auto-filled with your username
- **Reviewed At**: Auto-set timestamp
- **Rejection Reason**: Only shown if status is "Rejected"

### Tips
- Review applications regularly (check email notifications)
- Verify documents are proper before approving
- Provide clear rejection reasons for resubmissions
- Completed status means employee is fully onboarded

---

## 2. Event Type Management

### Where Users Can Create Custom Events
- When marking attendance (if event not in list)
- When editing attendance
- When submitting reimbursement requests

### Events Auto-Created
- System automatically creates new events when employees type custom names
- Event name = what employee typed
- Date = today's date
- Location = "Custom Event"

### Manual Event Management
**Admin Panel → Attendance → Events**

- View all events (custom and predefined)
- Create events manually via "Add Event" button
- Edit event details (name, date, location, etc.)
- Assign crew members to events

---

## 3. Reimbursement Management (Enhanced)

### Admin Dashboard Location
**Admin Panel → Attendance → Expense Reimbursement**

### New Features in List View

#### Quick Actions Dropdown
- **For each pending reimbursement**:
  - Click dropdown with "-- Choose Action --"
  - Select: **Approve** or **Reject**
  - Status updates immediately

#### Status Badges
- ✓ **Green**: Approved
- ✗ **Red**: Rejected
- ⏳ **Grey**: Pending

#### Bulk Actions
- **Select multiple reimbursements** with checkboxes
- Choose from Action dropdown at bottom:
  - "Approve selected reimbursements"
  - "Reject selected reimbursements"
  - "Mark as paid"
- Click "Go" button

### How to Review a Reimbursement

1. **Click on any reimbursement** to view details
2. **See the information**:
   - User who submitted
   - Expense type
   - Amount
   - Description
   - Receipt image (if uploaded)
   - Date requested

3. **View Receipt** (if submitted):
   - Receipt photo is shown with preview
   - Can download full image
   - Check it matches claim

4. **Approve or Reject**:
   - **To Approve**:
     - Change Status to "approved"
     - Click Save
     - User's balance automatically increased
     - Approved_by and Approved_at auto-filled
   
   - **To Reject**:
     - Change Status to "rejected"
     - Enter Rejection Reason
     - Click Save
     - User gets notification

### Balance Updates
- **When you approve**: User's balance += reimbursement amount
- **When you reject**: Balance unchanged
- **Automatic**: No manual balance adjustment needed
- **Tracked**: BalanceChange record created automatically

### Reimbursement without Receipt
- Receipt is now optional
- Can approve based on description alone
- Receipt is recommended for verification
- Same approval process

### Reimbursement without Event
- Event field is optional
- Can approve without linked event
- Same approval process

---

## 4. Balance Management (Enhanced)

### New Payment Recording System

**Admin Panel → Attendance → Payment Records**

- Shows all payments users marked
- Read-only list for tracking
- Fields: user, amount, method, reference, date
- Can't edit or delete (audit trail)

### Balance Change Tracking

**Admin Panel → Attendance → Balance Changes**

- Complete audit trail of all balance modifications
- Shows every transaction affecting user balances
- Read-only for security

#### Change Types Logged
| Type | Description | Amount |
|------|-------------|---------|
| `attendance` | Attendance recorded | +KSH earned |
| `attendance_edit` | Attendance modified | ± difference |
| `admin_adjustment` | Admin manual adjustment | ± amount |
| `reimbursement` | Reimbursement approved | +KSH amount |
| `salary_payment` | Salary paid | +KSH amount |
| `payment_marked` | User marked payment | -KSH amount |

### Manual Balance Adjustments
**Admin Panel → Attendance → Profile**

1. Select user from list
2. Click on their profile
3. Edit "Balance" field to adjust
4. Click Save
5. BalanceAdjustment record auto-created
6. BalanceChange record auto-created

### Viewing Balance History
See section 6 below: "View User's Complete History"

---

## 5. Attendance Management (Enhanced)

### Admin Dashboard Location
**Admin Panel → Attendance → Attendance Records**

### New Feature: View User History Link
- Each attendance record now has a **"View History"** button
- Clicking it shows:
  - All attendance records for that user
  - Complete balance change log
  - All transactions affecting their balance

---

## 6. View User's Complete History (NEW FEATURE)

### How to Access
**Admin Panel → Attendance → Attendance Records**

1. Find any attendance record for the user
2. Click **"View History"** button in the Actions column

### What You'll See

#### User Information Section
- Username
- Email
- Employment type
- Current balance (with color badge)

#### Attendance Records Table
- Date of each record
- Event name
- Overtime hours worked
- Supper allowance (if applicable)
- Amount paid
- Payment status (Paid/Unpaid)

#### Balance Change History
Each entry shows:
- **Change Type**: Icon + label (Attendance, Adjustment, Reimbursement, etc.)
- **Amount Changed**: 
  - Green badge: +KSH (income)
  - Red badge: -KSH (payment)
- **Balance Impact**: Previous → New balance
- **Timestamp**: Date and time
- **Made By**: Who made the change (for admin-made changes)
- **Description**: What exactly happened

### Use Cases
1. **Audit Trail**: Verify all changes to user's balance
2. **Dispute Resolution**: Show user complete history
3. **Salary Review**: Check all payments and adjustments
4. **Compliance**: Document all financial transactions

---

## 7. Dashboard Changes (What Users See)

### New Dashboard Sections

#### Balance Changes Log
- Shows last 10 balance changes
- Color-coded for quick scanning
- Helps users verify their balance

#### Payment Records
- Shows last 5 payments marked by user
- Amount, method, date, reference
- Users can verify their payments were recorded

#### Mark Payment Button
- New button on dashboard
- Users can mark payments directly
- Reduces manual balance management

---

## Security & Access Control

### Permission Checks
- Only superusers/admin can:
  - Approve/reject reimbursements
  - View user history
  - Make balance adjustments
  - Create events (via Events Manager group)

- Regular users can:
  - Submit reimbursement requests
  - Mark attendance
  - Mark payments
  - View their own history

### Audit Trail
- All changes logged automatically
- Changed_by user tracked
- Timestamp recorded
- Read-only history in admin panel
- No deletion of change records

---

## Workflow Examples

### Example 1: Approve Employee Reimbursement
1. Go to Admin → Expense Reimbursement
2. See pending reimbursement from John (KSH 2,500 transport)
3. Review receipt image (looks valid)
4. Click status dropdown: Select "Approve"
5. Status changes to ✓ Approved
6. John's balance increases by KSH 2,500
7. John sees updated balance on his dashboard
8. BalanceChange record created automatically

### Example 2: Adjust User Balance (Error Correction)
1. Admin notices user balance is wrong
2. Go to Admin → Profile
3. Search for user's profile
4. Click edit
5. Change balance to correct amount
6. Click Save
7. BalanceAdjustment record created
8. BalanceChange record logged
9. User can see the change in their history

### Example 3: Investigate User Payment Discrepancy
1. User claims they paid but balance didn't decrease
2. Go to Admin → Attendance Records
3. Find any record for that user
4. Click "View History"
5. See all balance changes
6. Find the payment in the list
7. Verify timestamp, amount, and payment method
8. Check PaymentRecord table for details
9. Compare with user's claim

---

## Best Practices

### For Reimbursement Approvals
1. ✓ Review receipts when available
2. ✓ Approve quickly to keep employees satisfied
3. ✓ Use bulk actions for multiple approvals
4. ✓ Document rejection reasons clearly
5. ✓ Check reimbursements weekly

### For Balance Management
1. ✓ Use view history regularly
2. ✓ Document adjustment reasons
3. ✓ Avoid manual adjustments (let system calculate)
4. ✓ Use audit trail for verification
5. ✓ Verify payment records match user claims

### For Onboarding
1. ✓ Review applications promptly
2. ✓ Request additional docs if needed
3. ✓ Provide clear rejection reasons
4. ✓ Keep records organized
5. ✓ Verify documents before approving

---

## Troubleshooting

### Balance Won't Update
- Check BalanceChange history for the change
- Verify reimbursement status is "approved"
- Check for conflicting adjustments
- Contact development if still wrong

### Can't Find User History
- Go to Attendance Records admin
- Search for any record by username
- Click "View History" on any record found
- Or search in BalanceChange table by user

### Reimbursement Stuck
- Check status in list view
- Make sure you saved changes
- Try page refresh
- Check browser console for errors

### User Payment Not Recorded
- Check PaymentRecord table
- Verify user marked payment successfully
- Check BalanceChange for payment entry
- Ask user to retry if failed

---

## Reports & Analytics

### Useful Admin Queries
- **Pending Reimbursements**: Filter status = "pending"
- **Total Paid Out**: Sum of approved reimbursements
- **User Balances**: View Profile list, sorted by balance
- **Payment History**: View PaymentRecord table
- **Change History**: View BalanceChange with filters

### Data Export
- Can select records and export to CSV
- Use Django admin's built-in export
- Useful for reporting to management

---

## User Support Tips

When users ask about:

**"Why did my balance change?"**
- → Show them their Balance Change history
- → Explain each transaction type
- → Point to specific record

**"Can I resubmit my reimbursement?"**
- → Check if it was rejected
- → Explain why it was rejected
- → Resubmit via new form

**"How do I mark a payment?"**
- → Direct to dashboard
- → Click "Mark Payment" button
- → Fill in details
- → Takes effect immediately

**"Where's my receipt image?"**
- → Reimbursement record shows it
- → Admin can see preview
- → Can download full image

---

## Technical Notes

- New models: PaymentRecord, BalanceChange
- Migrations applied: 0022_balancechange_paymentrecord
- No breaking changes to existing functionality
- All changes tracked automatically via signals
- Read-only audit tables (BalanceChange)

---

**Last Updated**: January 23, 2026
**Version**: 2.0 - With New Features
**Status**: Ready for Production
