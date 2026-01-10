# Quick Testing Guide - Salaried Employee Features

## How to Test the New Features

### Test 1: Salaried Employee Salary Calculation
**Setup:**
1. Login to admin panel
2. Go to Users and create a new user as "salaried" employee
3. Complete onboarding with a job role and monthly salary (e.g., KSH 50,000)

**Test Steps:**
1. Login as the salaried employee
2. Go to Dashboard - **Should see:**
   - ✨ Clarity Non Stop ✨ (animated motto on home page)
   - Salary Information card showing job role and monthly salary
   - Current balance

3. Mark attendance with 3 hours overtime
   - **Expected:** Amount Paid = 3 × 100 = **KSH 300** (NO base 1000!)
   - Check balance increased by 300

4. For hourly employee (casual laborer), mark same attendance
   - **Expected:** Amount Paid = 1000 + (3 × 100) = **KSH 1300**

---

### Test 2: Admin Balance Adjustment Visibility
**Setup:**
1. Have a salaried employee logged in
2. Admin user logged in separately

**Test Steps (Admin):**
1. Go to Profile admin
2. Find the salaried employee
3. Adjust their balance by +500 or -200
4. Add reason: "Bonus" or "Adjustment"

**Test Steps (Employee):**
1. Refresh Dashboard
2. Scroll to "Balance Adjustments" section
3. **Should see:**
   - Date and time of adjustment
   - Amount (+500 or -200 with color coding)
   - Reason: "Bonus" or "Adjustment"
   - Admin name who made the change

---

### Test 3: Edit Attendance Recalculation
**Setup:**
1. Salaried employee marks attendance with 2 hours overtime
   - Amount = 2 × 100 = 200

**Test Steps:**
1. Edit the attendance to 5 hours overtime
   - **Expected:** New Amount = 5 × 100 = **KSH 500**
   - Balance should reflect difference (+300)

2. For hourly employee with same edit:
   - Old: 1000 + (2 × 100) = 1200
   - New: 1000 + (5 × 100) = 1500
   - **Expected:** Difference = +300

---

### Test 4: Home Page Motto Display
**Test Steps:**
1. Go to home page (before login)
2. Look at hero section
3. **Should see:**
   - "✨ Clarity Non Stop ✨" text
   - Green color (#2ecc71)
   - Pulsing/fading animation
   - Positioned above the main heading

---

### Test 5: Dashboard Features
**Test Steps (Salaried Employee):**
1. Login and go to Dashboard
2. **Verify all sections load:**
   - [x] Salary Information (if salaried)
   - [x] Current Balance
   - [x] Today's Attendance
   - [x] Balance Adjustments (Audit Trail)
   - [x] Recent Attendance Records
   - [x] Quick Action Buttons

3. **Check Quick Actions:**
   - Mark Attendance button → navigates to mark_attendance
   - View Records button → navigates to view_attendance
   - Submit Expense button → navigates to submit_reimbursement

---

## Expected Behavior Summary

| Feature | Hourly Worker | Salaried Worker |
|---------|--------------|-----------------|
| Base Amount | KSH 1000 | None |
| Overtime Rate | KSH 100/hr | KSH 100/hr |
| Example: 2 hrs OT | 1000 + 200 = 1200 | 0 + 200 = 200 |
| Example: 5 hrs OT | 1000 + 500 = 1500 | 0 + 500 = 500 |
| Dashboard Shows | Attendance & Balance | Attendance, Balance, **Salary Info** |
| Audit Trail | Admin adjustments visible | Admin adjustments visible |

---

## Troubleshooting

**Dashboard not showing?**
- Ensure user is logged in (@login_required decorator)
- Check database has Profile record for user
- Check employment_type is set correctly

**Salary info not showing?**
- Verify employment_type = 'salaried'
- Check onboarding was completed with job_role and monthly_salary
- Check Profile has these fields populated

**Motto not animating?**
- Clear browser cache (Ctrl+Shift+Del)
- Check CSS is loaded (F12 → Elements → search for .motto)
- Verify home.html has the motto div

**Balance adjustment not visible?**
- Check BalanceAdjustment records exist in admin
- Ensure user relationship is correct
- Verify recent_adjustments query returns results

---

## Files to Check

- `attendance/views.py` - Logic for salary calculations
- `templates/attendance/dashboard.html` - New dashboard template
- `templates/attendance/home.html` - Home page with motto
- `attendance/models.py` - EmployeeOnboarding model (should have optional job_role, monthly_salary)

---

## Database Queries to Verify

```sql
-- Check if user has salaried employment type
SELECT * FROM attendance_profile WHERE user_id = ? AND employment_type = 'salaried';

-- Check if onboarding has job_role and salary
SELECT * FROM attendance_employeeonboarding WHERE user_id = ?;

-- Check balance adjustments
SELECT * FROM attendance_balanceadjustment WHERE user_id = ? ORDER BY date DESC;

-- Check attendance amounts for salaried vs hourly
SELECT user_id, amount_paid, overtime_hours FROM attendance_attendancerecord LIMIT 10;
```

---

## Success Criteria ✅

- [ ] Salaried employees don't get base KSH 1000
- [ ] Hourly employees still get base + overtime
- [ ] Dashboard shows salary info for salaried employees
- [ ] Admin adjustments are visible to employees (audit trail)
- [ ] Motto appears on home page with animation
- [ ] Edit attendance recalculates correctly for both types
- [ ] All forms submit without errors
- [ ] No database migrations needed

---

**Implementation Date:** January 8, 2026
**Status:** Ready for Testing ✅
