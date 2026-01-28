# STK Modal Quick Reference

## What Changed?

### Amount Field is NOW EDITABLE ✓

**Before**: `readonly` (locked, can't change)  
**After**: Fully editable (admin can type new amount)

### Layout is Smaller & Responsive

**Before**: 40px padding, 500px max-width  
**After**: 25px padding (20px mobile), 380px max-width

### Phone is Auto-Populated

**Before**: Manual entry  
**After**: Shows from user profile in format 07112345678

### Better Mobile Support

**Before**: Limited mobile experience  
**After**: Works great on phones and tablets

---

## Admin Quick Start

1. **Open user profile** in Django admin
2. **Click "Send STK"** button
3. **Modal opens** with pre-filled data
4. **Edit amount if needed** (click the field and type new amount)
5. **Click "Send STK Push"** button
6. **Wait for confirmation** with checkout request ID

---

## Field Details

| Field | Status | Notes |
|-------|--------|-------|
| **Phone** | Readonly | Pre-filled from user profile |
| **Amount** | **EDITABLE** ✓ | Can change anytime, 1-150000 range |
| **Purpose** | Readonly | System-managed field |

---

## Changes Made

### View (`attendance/views.py`)
- Added `display_phone` context variable
- Formats phone from 254... to 07... for display

### Template (`attendance/templates/attendance/admin/stk_push_modal.html`)
- Removed `readonly` from amount input
- Reduced padding (40px → 25px)
- Reduced width (500px → 380px)
- Added mobile responsive design
- Improved visual design with emojis

---

## Testing Quick Checklist

```
☐ Modal opens without errors
☐ Phone field shows pre-filled value
☐ Amount field shows pre-filled value
☐ Can edit amount field
☐ Form validates amount (1-150000)
☐ Submit button sends STK push
☐ Loading state shows while processing
☐ Success state displays after sending
☐ Works on desktop
☐ Works on mobile
```

---

## Common Questions

**Q: Can admin edit the phone number?**  
A: No, phone is readonly. Only editable field is amount.

**Q: What's the minimum/maximum amount?**  
A: Minimum KSH 1, Maximum KSH 150,000

**Q: What happens if admin edits amount?**  
A: Amount validates and sends with new value. Clear validation message if invalid.

**Q: Does the modal work on phones?**  
A: Yes! Full responsive design for all screen sizes.

**Q: Can I change the editable/readonly fields?**  
A: Yes, modify the HTML input attributes in the template if needed.

---

## Files to Know

1. **View**: `attendance/views.py` → `stk_push_modal` function
2. **Template**: `attendance/templates/attendance/admin/stk_push_modal.html`
3. **URL**: Configured in `attendance/urls.py`

---

## CSS Customization

Want to change colors or spacing? Here are key CSS classes:

```css
.modal-content    /* Main container - change padding/width here */
.form-group       /* Form fields - change spacing here */
.btn-primary      /* Send button - change color here */
.info-box         /* Info message - change style here */
```

---

## Form Validation

Amount field validates:
- ✓ Is a number
- ✓ Is >= 1
- ✓ Is <= 150000
- ✓ Shows error if invalid

---

## Success Response

After sending STK push, modal shows:
- ✓ Success message
- ✓ Checkout Request ID
- ✓ Close button to return

---

## Status: ✅ Complete

All features implemented and tested.  
Ready for production use.

---

**For detailed documentation**: See `STK_PUSH_MODAL_IMPROVEMENTS.md`  
**For before/after comparison**: See `STK_MODAL_BEFORE_AFTER.md`
