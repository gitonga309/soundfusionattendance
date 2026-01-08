# Expense Reimbursement System - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SOUND FUSION ATTENDANCE SYSTEM                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      USER LAYER (Frontend)                       │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  Regular User                    │  Admin/Accountant           │  │
│  │  ├─ Dashboard                    │  ├─ Admin Dashboard        │  │
│  │  ├─ Submit Request               │  ├─ Reimbursement List     │  │
│  │  │  (submit_reimbursement.html)  │  │  (admin_reimbursements) │  │
│  │  ├─ View History                 │  ├─ Approve Requests       │  │
│  │  │  (view_reimbursements.html)   │  ├─ Reject Requests        │  │
│  │  └─ Track Balance                │  │  (reject_reimbursement)  │  │
│  │                                   │  └─ Admin Interface        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                   VIEW LAYER (Django Views)                      │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  submit_reimbursement()        [POST Request]           │   │  │
│  │  │  ├─ Validates form (amount ≤ 50k)                       │   │  │
│  │  │  ├─ Creates ExpenseReimbursement object                 │   │  │
│  │  │  ├─ Sets user = request.user                            │   │  │
│  │  │  └─ Redirects to view_reimbursements                    │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  view_reimbursements()        [GET]                     │   │  │
│  │  │  ├─ Filters by user = request.user                      │   │  │
│  │  │  ├─ Orders by date (newest first)                       │   │  │
│  │  │  └─ Renders template with list                          │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  admin_reimbursements()       [GET]                     │   │  │
│  │  │  ├─ Filters by status (pending/approved/rejected)       │   │  │
│  │  │  ├─ Counts for each status                              │   │  │
│  │  │  ├─ Renders tabbed admin dashboard                      │   │  │
│  │  │  └─ Only accessible to admin users                      │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  approve_reimbursement(id)    [POST]                    │   │  │
│  │  │  ├─ Gets reimbursement object                           │   │  │
│  │  │  ├─ Sets status = 'approved'                            │   │  │
│  │  │  ├─ Sets approved_by = request.user                     │   │  │
│  │  │  ├─ Sets approved_at = timezone.now()                   │   │  │
│  │  │  └─ Triggers signal → Balance update                    │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  reject_reimbursement(id)     [GET/POST]                │   │  │
│  │  │  ├─ GET: Show rejection form                            │   │  │
│  │  │  ├─ POST: Set status = 'rejected'                       │   │  │
│  │  │  ├─ Store rejection_reason from form                    │   │  │
│  │  │  └─ No balance change (not approved)                    │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               BUSINESS LOGIC LAYER (Forms & Signals)             │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌──────────────────────────┐   ┌──────────────────────────┐   │  │
│  │  │ ExpenseReimbursementForm │   │ Signal Handlers          │   │  │
│  │  ├──────────────────────────┤   ├──────────────────────────┤   │  │
│  │  │ Fields:                  │   │ on_reimbursement_save:   │   │  │
│  │  │ ├─ event (optional)      │   │ ├─ If status='approved'  │   │  │
│  │  │ ├─ expense_type (req)    │   │ │  ├─ Recalculate user   │   │  │
│  │  │ ├─ amount (req)          │   │ │  │  balance             │   │  │
│  │  │ ├─ description (opt)     │   │ │  ├─ Formula:            │   │  │
│  │  │ └─ receipt_photo (opt)   │   │ │  │  balance =           │   │  │
│  │  │                          │   │ │  │  + attendance        │   │  │
│  │  │ Validation:              │   │ │  │  + adjustments       │   │  │
│  │  │ ├─ amount > 0            │   │ │  │  + reimbursements    │   │  │
│  │  │ └─ amount ≤ 50,000       │   │ │  └─ Update Profile      │   │  │
│  │  └──────────────────────────┘   │ └──────────────────────────┘   │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER (Models & ORM)                     │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐    │  │
│  │  │ ExpenseReimbursement Model                             │    │  │
│  │  ├────────────────────────────────────────────────────────┤    │  │
│  │  │ Fields:                                                │    │  │
│  │  │ ├─ user (FK → User) [required]                         │    │  │
│  │  │ ├─ event (FK → Event) [nullable]                       │    │  │
│  │  │ ├─ expense_type (choices) [required]                   │    │  │
│  │  │ │  ├─ transport                                        │    │  │
│  │  │ │  ├─ purchase                                         │    │  │
│  │  │ │  ├─ airtime                                          │    │  │
│  │  │ │  ├─ meal                                             │    │  │
│  │  │ │  └─ other                                            │    │  │
│  │  │ ├─ amount (Decimal, max_digits=10) [required]          │    │  │
│  │  │ ├─ description (TextField) [optional]                  │    │  │
│  │  │ ├─ receipt_photo (ImageField) [optional]               │    │  │
│  │  │ ├─ status (choices, default='pending')                 │    │  │
│  │  │ │  ├─ pending                                          │    │  │
│  │  │ │  ├─ approved                                         │    │  │
│  │  │ │  └─ rejected                                         │    │  │
│  │  │ ├─ requested_at (DateTimeField, auto_now_add) [audit]  │    │  │
│  │  │ ├─ approved_by (FK → User) [nullable, audit]           │    │  │
│  │  │ ├─ approved_at (DateTimeField) [nullable, audit]       │    │  │
│  │  │ └─ rejection_reason (TextField) [optional]             │    │  │
│  │  │                                                         │    │  │
│  │  │ Relationships:                                         │    │  │
│  │  │ ├─ User (creator of request)                           │    │  │
│  │  │ ├─ User (approver)                                     │    │  │
│  │  │ └─ Event (optional context)                            │    │  │
│  │  │                                                         │    │  │
│  │  │ Methods:                                               │    │  │
│  │  │ └─ __str__: Returns readable request summary           │    │  │
│  │  │                                                         │    │  │
│  │  │ Meta:                                                  │    │  │
│  │  │ └─ ordering: ['-requested_at'] (newest first)          │    │  │
│  │  └────────────────────────────────────────────────────────┘    │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────┐    │  │
│  │  │ Related Models (Already Existing)                      │    │  │
│  │  ├────────────────────────────────────────────────────────┤    │  │
│  │  │ Profile Model:                                         │    │  │
│  │  │ └─ balance (calculated field)                          │    │  │
│  │  │    = sum(AttendanceRecord.amount_paid, is_paid=False)  │    │  │
│  │  │    + sum(BalanceAdjustment.amount)                     │    │  │
│  │  │    + sum(ExpenseReimbursement.amount, status='approved')    │  │
│  │  │                                                         │    │  │
│  │  │ User Model (Django):                                   │    │  │
│  │  │ └─ Has many ExpenseReimbursement objects               │    │  │
│  │  │                                                         │    │  │
│  │  │ Event Model (Already Existing):                        │    │  │
│  │  │ └─ Optional relation to ExpenseReimbursement           │    │  │
│  │  └────────────────────────────────────────────────────────┘    │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                │                                        │
│                                ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                   DATABASE LAYER (PostgreSQL)                    │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  Table: attendance_expensereimbursement                         │  │
│  │  ├─ id (PK)                                                    │  │
│  │  ├─ user_id (FK)                                               │  │
│  │  ├─ event_id (FK, nullable)                                    │  │
│  │  ├─ expense_type (varchar)                                     │  │
│  │  ├─ amount (decimal)                                           │  │
│  │  ├─ description (text)                                         │  │
│  │  ├─ receipt_photo (varchar)                                    │  │
│  │  ├─ status (varchar)                                           │  │
│  │  ├─ requested_at (timestamp)                                   │  │
│  │  ├─ approved_by_id (FK, nullable)                              │  │
│  │  ├─ approved_at (timestamp, nullable)                          │  │
│  │  └─ rejection_reason (text)                                    │  │
│  │                                                                  │  │
│  │  Indices:                                                      │  │
│  │  ├─ PRIMARY KEY (id)                                           │  │
│  │  ├─ FOREIGN KEY (user_id)                                      │  │
│  │  ├─ FOREIGN KEY (event_id)                                     │  │
│  │  ├─ INDEX (status)                                             │  │
│  │  └─ INDEX (requested_at)                                       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Submission Flow
```
User Fills Form
      ↓
[submit_reimbursement.html]
      ↓
Django Form Validation
├─ Amount > 0? ✓
├─ Amount ≤ 50,000? ✓
├─ Expense type selected? ✓
└─ Required fields filled? ✓
      ↓
submit_reimbursement() View
      ↓
Create ExpenseReimbursement object
├─ user = request.user
├─ status = 'pending'
├─ requested_at = now()
└─ Save to database
      ↓
Success Message
      ↓
Redirect to view_reimbursements
```

### Approval Flow
```
Admin sees Pending Request
      ↓
[admin_reimbursements.html] Pending Tab
      ↓
Admin Clicks "Approve"
      ↓
approve_reimbursement() View [POST]
      ↓
Update ExpenseReimbursement
├─ status = 'approved'
├─ approved_by = request.user
├─ approved_at = timezone.now()
└─ Save to database
      ↓
SIGNAL TRIGGERED: post_save
      ↓
Signal Handler: update_balance_on_reimbursement_approval()
      ├─ Get user profile
      ├─ Recalculate balance:
      │  = sum(attendance)
      │  + sum(adjustments)
      │  + sum(approved reimbursements)
      ├─ Update Profile.balance
      └─ Save profile
      ↓
Redirect to admin_reimbursements
      ↓
User sees updated balance on next login
```

### Rejection Flow
```
Admin sees Pending Request
      ↓
[admin_reimbursements.html] Pending Tab
      ↓
Admin Clicks "Reject"
      ↓
reject_reimbursement() View [GET]
      ↓
Show [reject_reimbursement.html] Form
├─ Display request details
├─ Show warning message
└─ Provide reason textarea
      ↓
Admin Fills Rejection Reason
      ↓
Admin Clicks "Reject Request"
      ↓
reject_reimbursement() View [POST]
      ↓
Update ExpenseReimbursement
├─ status = 'rejected'
├─ rejection_reason = form_input
└─ Save to database
      ↓
NO SIGNAL (status != 'approved')
      ↓
Balance NOT updated
      ↓
Redirect to admin_reimbursements
      ↓
User sees rejection reason in [view_reimbursements.html]
```

## Component Interaction Matrix

```
┌─────────────────┬─────────────┬──────────────────┬──────────────┐
│ Component       │ Reads From  │ Writes To        │ Triggers     │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ Form            │ User Input  │ Validation       │ POST Request │
│                 │ Database    │                  │              │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ View (submit)   │ Form Data   │ Database         │ Signal       │
│                 │ User Info   │                  │              │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ View (admin)    │ Database    │ N/A              │ Template     │
│                 │ Counts      │                  │ Render       │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ View (approve)  │ Request ID  │ Database         │ Signal       │
│                 │ User Info   │ (reimbursement)  │              │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ Signal Handler  │ Database    │ Profile.balance  │ Balance      │
│                 │ Aggregates  │ (database)       │ Update       │
├─────────────────┼─────────────┼──────────────────┼──────────────┤
│ Template        │ Context     │ HTML             │ Browser      │
│                 │ Data        │ Output           │ Display      │
└─────────────────┴─────────────┴──────────────────┴──────────────┘
```

## Database Transaction Flow

```
User Submits Request:
  BEGIN TRANSACTION
  ├─ INSERT into attendance_expensereimbursement (...)
  ├─ COMMIT
  └─ Success

Admin Approves Request:
  BEGIN TRANSACTION
  ├─ UPDATE attendance_expensereimbursement SET status='approved', ...
  ├─ Signal fires
  ├─ SELECT SUM(amount) FROM attendance_attendancerecord
  ├─ SELECT SUM(amount) FROM attendance_balanceadjustment
  ├─ SELECT SUM(amount) FROM attendance_expensereimbursement WHERE status='approved'
  ├─ UPDATE attendance_profile SET balance = (calculated_sum)
  ├─ COMMIT
  └─ Success (user sees new balance next login)
```

## Integration Points

```
Existing System Components Used:
├─ Django User Model
│  └─ Referenced by ExpenseReimbursement.user and approved_by
├─ Event Model
│  └─ Optional reference from ExpenseReimbursement
├─ Profile Model
│  └─ Balance calculation includes reimbursements
├─ BalanceAdjustment Model
│  └─ Coexists with reimbursement amounts
├─ AttendanceRecord Model
│  └─ Coexists in balance calculation
├─ Admin Framework
│  └─ ExpenseReimbursementAdmin registered
├─ Authentication System
│  └─ @login_required, @user_passes_test decorators
└─ Templates Framework
   └─ All templates extend existing style/structure
```

---

**This architecture ensures:**
- ✅ Separation of concerns (views, forms, models)
- ✅ Data integrity (validation at form and model level)
- ✅ Automatic balance updates (signal handlers)
- ✅ Security (permission decorators)
- ✅ Auditability (timestamps and approver tracking)
- ✅ Scalability (proper indexing and query optimization)
