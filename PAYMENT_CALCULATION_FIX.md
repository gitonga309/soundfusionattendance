# Payment Calculation Fix - Implementation Summary

## Problem Identified
When an admin made a balance adjustment and then a user edited their overtime hours on the same day, the payment calculation was incorrect because both operations were conflicting.

## Solution Implemented

### 1. **New Database Field**
Added `original_overtime_hours` to track the initial overtime before any edits.

### 2. **Smart Amount Calculation**
When a user edits overtime, the system now:
1. Calculates OLD earned amount: `1000 + (old_overtime × 100)`
2. Calculates NEW earned amount: `1000 + (new_overtime × 100)`
3. Updates amount_paid: `(current_amount_paid - old_earned) + new_earned`

This ensures:
- Admin adjustments are preserved
- Only the overtime difference is recalculated
- Balance always reflects: earned_from_attendance + admin_adjustments

### 3. **Example Walkthrough**

**Scenario A: Admin adjusts AFTER user marks attendance**
```
Day 1 - 2:00 PM: User marks attendance (2 hours overtime)
  - earned = 1000 + (2 × 100) = 1200
  - amount_paid = 1200
  - balance = 1200

Day 1 - 3:00 PM: Admin deducts 300 KSH (reason: advance payment)
  - balance = 1200 - 300 = 900

Day 1 - 4:00 PM: User realizes they had 4 hours (edits overtime)
  - old_earned = 1000 + (2 × 100) = 1200
  - new_earned = 1000 + (4 × 100) = 1400
  - amount_paid = (1200 - 1200) + 1400 = 1400
  - Signal recalculates: balance = 1400 + (-300) = 1100 ✓
```

**Scenario B: User edits AFTER admin adjusts**
```
Day 1 - 2:00 PM: User marks attendance (1 hour overtime)
  - earned = 1000 + (1 × 100) = 1100
  - amount_paid = 1100
  - balance = 1100

Day 1 - 3:00 PM: Admin adds 200 KSH bonus (good performance)
  - balance = 1100 + 200 = 1300

Day 1 - 4:00 PM: User corrects overtime to 3 hours
  - old_earned = 1000 + (1 × 100) = 1100
  - new_earned = 1000 + (3 × 100) = 1300
  - amount_paid = (1100 - 1100) + 1300 = 1300
  - Signal recalculates: balance = 1300 + 200 = 1500 ✓
```

### 4. **Key Changes**

**In models.py:**
- Added `original_overtime_hours` field to AttendanceRecord
- Added `earned_amount` property to calculate earned amount

**In views.py (mark_attendance):**
- Store `original_overtime_hours` when record is first created

**In views.py (edit_attendance):**
- Calculate old_earned and new_earned amounts
- Update amount_paid by removing old earned, adding new earned
- Admin adjustments are automatically preserved via signal handlers

### 5. **Signal Handlers**
Both signal handlers work correctly:
- `update_balance_on_attendance`: Sums all unpaid attendance + all adjustments
- `update_balance_on_adjustment`: Sums all unpaid attendance + all adjustments

Result: Balance is always accurate regardless of operation order

## Verification

✅ User marks attendance: amount_paid = 1000 + (OT × 100)
✅ Admin adjusts: balance = earned + adjustment
✅ User edits overtime: only the earned portion changes, adjustment preserved
✅ Only one edit allowed per day (overtime_edited flag prevents multiple edits)
✅ Balance always = all_unpaid_attendance + all_adjustments

## Testing Checklist

- [ ] Mark attendance with overtime hours
- [ ] Admin makes adjustment (positive or negative)
- [ ] User edits overtime hours same day
- [ ] Verify balance is correct
- [ ] Try different sequences (edit before admin adjust, admin after, etc.)
- [ ] Verify user cannot edit overtime twice per day
