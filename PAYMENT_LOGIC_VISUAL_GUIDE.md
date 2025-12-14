# Payment Calculation Logic - Visual Guide

## How the Payment System Works

### Formula
```
BALANCE = Sum(all_unpaid_attendance.amount_paid) + Sum(all_admin_adjustments.amount)
```

### For Each Day's Attendance
```
amount_paid = 1000 + (overtime_hours × 100)
```

---

## Step-by-Step Example: Complete Day

### Initial State
User has no records
```
Balance = 0
```

---

### Step 1: User Marks Attendance (2:00 PM)
User works 2 hours overtime

**Database Update:**
```
AttendanceRecord:
  - user_id: 5
  - date: 2025-11-15
  - overtime_hours: 2
  - original_overtime_hours: 2
  - amount_paid: 1000 + (2 × 100) = 1200
  - overtime_edited: FALSE

Signal Handler Runs:
  - total_attendance = 1200
  - total_adjustments = 0
  - NEW BALANCE = 1200 + 0 = 1200 ✓
```

---

### Step 2: Admin Makes Adjustment (3:00 PM)
Admin deducts 300 KSH (advance payment given)

**Database Update:**
```
BalanceAdjustment:
  - profile_id: 5
  - admin_id: 1
  - amount: -300
  - reason: "Advance payment"
  - date: 2025-11-15 15:00

Signal Handler Runs:
  - total_attendance = 1200 (unchanged - still showing what they earned)
  - total_adjustments = -300 (the deduction)
  - NEW BALANCE = 1200 + (-300) = 900 ✓
```

---

### Step 3: User Edits Overtime (4:00 PM)
User realizes they actually worked 4 hours

**Before Edit:**
```
amount_paid = 1200  (from 2 hours)
```

**Calculation:**
```
old_earned = 1000 + (2 × 100) = 1200
new_earned = 1000 + (4 × 100) = 1400
new_amount_paid = (1200 - 1200) + 1400 = 1400
```

**Database Update:**
```
AttendanceRecord:
  - overtime_hours: 4 (CHANGED)
  - original_overtime_hours: 2 (unchanged - for reference)
  - amount_paid: 1400 (updated)
  - overtime_edited: TRUE (prevent further edits)

Signal Handler Runs:
  - total_attendance = 1400 (now reflects 4 hours)
  - total_adjustments = -300 (admin adjustment still applies)
  - NEW BALANCE = 1400 + (-300) = 1100 ✓
```

---

## Key Points

### ✓ What Stays the Same
- Admin adjustments are **never removed**
- Once set, they persist through overtime edits

### ✓ What Changes
- Only the earned amount (1000 + OT × 100) changes
- This is deducted from current amount_paid, then new earned amount is added

### ✓ Order Independence
Works correctly regardless of sequence:
- User edits THEN admin adjusts? ✓ Works
- Admin adjusts THEN user edits? ✓ Works
- Repeat adjustments? ✓ Works (admin can adjust multiple times)
- User can only edit once? ✓ Enforced by overtime_edited flag

---

## Formula Breakdown

When user edits overtime on a day where admin already adjusted:

```
new_amount_paid = (old_amount_paid - old_earned) + new_earned
                = (old_amount_paid - old_earned) + new_earned
                
Where:
  old_earned = 1000 + (old_overtime × 100)
  new_earned = 1000 + (new_overtime × 100)
```

**Why this works:**
- `old_amount_paid` includes both earned amount AND any adjustments
- Subtracting `old_earned` removes just the earned portion
- Adding `new_earned` puts in the new earned portion
- Adjustments stay intact because they're not touched

---

## Examples

### Example 1: No Admin Adjustment
```
Mark: 3 OT → amount_paid = 1300, balance = 1300
Edit: 5 OT → new_amount_paid = (1300 - 1300) + 1500 = 1500, balance = 1500
```

### Example 2: Admin Adds Bonus
```
Mark: 2 OT → amount_paid = 1200, balance = 1200
Admin: +500 bonus → balance = 1700
Edit: 3 OT → amount_paid = (1200 - 1200) + 1300 = 1300
        Signal: balance = 1300 + 500 = 1800 ✓
```

### Example 3: Admin Deducts, User Reduces Hours
```
Mark: 5 OT → amount_paid = 1500, balance = 1500
Admin: -400 penalty → balance = 1100
Edit: 2 OT → amount_paid = (1500 - 1500) + 1200 = 1200
       Signal: balance = 1200 + (-400) = 800 ✓
```

### Example 4: Multiple Admin Adjustments
```
Mark: 2 OT → amount_paid = 1200, balance = 1200
Admin 1: -200 → balance = 1000
Admin 2: +150 → balance = 1150
Admin 3: -50 → balance = 1100
Edit: 3 OT → amount_paid = (1200 - 1200) + 1300 = 1300
       Signal: balance = 1300 + (-200 + 150 - 50) = 1300 - 100 = 1200 ✓
```

---

## Technical Implementation

### File: `models.py`
- Added `original_overtime_hours` field
- Added `earned_amount` property
- Signal handlers sum amounts correctly

### File: `views.py` - `mark_attendance()`
- On first creation: `original_overtime_hours = overtime_hours`

### File: `views.py` - `edit_attendance()`
- Calculate: `old_earned = 1000 + (old_overtime × 100)`
- Calculate: `new_earned = 1000 + (new_overtime × 100)`
- Update: `amount_paid = (amount_paid - old_earned) + new_earned`
- Set: `overtime_edited = TRUE`

---

## Testing

To verify the system works correctly:

1. **Test Case 1**: Mark → Admin Adjust → Edit
2. **Test Case 2**: Mark → Edit → Admin Adjust
3. **Test Case 3**: Mark → Admin Adjust → Admin Adjust Again → Edit
4. **Test Case 4**: Try to edit twice (should fail on second attempt)

All balances should be accurate in all cases.
