# Texas DPS Scheduler - Quick Reference Guide

## Form Fields Locators Quick Look

### By Field ID (Most Reliable)
```javascript
#input-52      → Texas Card Number
#input-55      → First Name
#input-58      → Last Name
#dob           → Date of Birth
#last4Ssn      → Last four of SSN
#input-70      → Cell Phone Radio Button
#input-72      → Email Radio Button
#input-120     → Cell Phone Number
#email         → Email Address
#verifyEmail   → Verify Email Address
```

### By Role (Most Accessible)
```javascript
textbox "First Name"
textbox "Last Name"
textbox "Date of Birth (mm/dd/yyyy)"
textbox "Cell Phone"
textbox "Email"
textbox "Verify Email"

radio "Cell Phone"
radio "Email"

button "Log On"
button "English"
button "Español"
button "Previous"
button "VERIFY"

spinbutton "Texas Card Number (DL, ID, EIC)"
spinbutton "Last four of SSN"
```

---

## Complete Playwright Code Snippets

### 1. Navigate to Website
```javascript
await page.goto('https://www.txdpsscheduler.com/');
```

### 2. Select Language (English)
```javascript
await page.getByRole('button', { name: 'English' }).click();
```

### 3. Fill Complete Login Form (Cell Phone Method)
```javascript
// Optional: Texas Card Number
await page.locator('#input-52').fill('1234567890');

// Required: First Name
await page.getByRole('textbox', { name: 'First Name' }).fill('John');

// Required: Last Name
await page.getByRole('textbox', { name: 'Last Name' }).fill('Doe');

// Required: Date of Birth (format: mm/dd/yyyy)
await page.locator('#dob').fill('01/15/1990');

// Required: Last four of SSN
await page.locator('#last4Ssn').fill('1234');

// Required: Select Cell Phone (default)
await page.locator('#input-70').check();

// Required: Cell Phone Number (format: (###)###-####)
await page.locator('#input-120').fill('(512)555-1234');

// Submit
await page.getByRole('button', { name: 'Log On' }).click();
```

### 4. Fill Complete Login Form (Email Method)
```javascript
// Optional: Texas Card Number
await page.locator('#input-52').fill('1234567890');

// Required: First Name
await page.locator('#input-55').fill('Jane');

// Required: Last Name
await page.locator('#input-58').fill('Smith');

// Required: Date of Birth (format: mm/dd/yyyy)
await page.locator('#dob').fill('03/20/1985');

// Required: Last four of SSN
await page.locator('#last4Ssn').fill('5678');

// Required: Select Email
await page.locator('#input-72').click();

// Required: Email Address
await page.locator('#email').fill('user@example.com');

// Required: Verify Email Address
await page.locator('#verifyEmail').fill('user@example.com');

// Submit
await page.getByRole('button', { name: 'Log On' }).click();
```

### 5. OTP Verification
```javascript
// Fill OTP field
await page.locator('input[type="text"]').first().fill('123456');

// Click VERIFY button
await page.getByRole('button', { name: 'VERIFY' }).click();
```

### 6. Navigate Services
```javascript
// Click Previous button
await page.getByRole('button', { name: 'Previous' }).click();

// Click New Appointment
await page.getByRole('button', { name: 'New Appointment' }).click();

// Click Existing Appointment
await page.getByRole('button', { name: 'Existing Appointment' }).click();
```

### 7. Select Service
```javascript
// Driver License Services
await page.getByRole('button', { 
  name: 'Apply for first time Texas DL/Permit' 
}).click();

// ID Services
await page.getByRole('button', { 
  name: 'Apply for first time Texas ID' 
}).click();

// CDL Services
await page.getByRole('button', { 
  name: 'Apply for first time Texas CLP/CDL' 
}).click();

// Non-Domicile CDL
await page.getByRole('button', { 
  name: 'Apply/Renew Non-Domicile CDL' 
}).click();

// Other Services
await page.getByRole('button', { 
  name: 'Apply for Election Identification Certificate' 
}).click();

await page.getByRole('button', { 
  name: 'Schedule a home-bound visit' 
}).click();
```

---

## Form Field Properties

### Texas Card Number (DL, ID, EIC)
- **ID**: `input-52`
- **Type**: Number / Spinbutton
- **Required**: ❌ No
- **Placeholder**: (none)

### First Name
- **ID**: `input-55`
- **Type**: Text
- **Required**: ✅ Yes
- **Placeholder**: (none)
- **Validation**: "First name is required"

### Last Name
- **ID**: `input-58`
- **Type**: Text
- **Required**: ✅ Yes
- **Placeholder**: (none)

### Date of Birth
- **ID**: `dob`
- **Type**: Tel
- **Format**: mm/dd/yyyy
- **Required**: ✅ Yes
- **Placeholder**: (none)

### Last Four of SSN
- **ID**: `last4Ssn`
- **Type**: Number / Spinbutton
- **Required**: ✅ Yes
- **Placeholder**: (none)

### Contact Method
- **Radio Group Name**: `radio-69`
- **Options**:
  - Cell Phone (ID: `input-70`, value: "phone") - Default
  - Email (ID: `input-72`, value: "email")
- **Required**: ✅ Yes

### Cell Phone Number (Conditional)
- **ID**: `input-120`
- **Type**: Text
- **Format**: (###)###-####
- **Required**: ✅ Yes (if Cell Phone selected)
- **Placeholder**: (###)###-####
- **Shows When**: Cell Phone radio is selected

### Email (Conditional)
- **ID**: `email`
- **Type**: Text
- **Required**: ✅ Yes (if Email selected)
- **Placeholder**: (none)
- **Shows When**: Email radio is selected
- **Validation**: "Email is required"

### Verify Email (Conditional)
- **ID**: `verifyEmail`
- **Type**: Text
- **Required**: ✅ Yes (if Email selected)
- **Placeholder**: (none)
- **Shows When**: Email radio is selected
- **Validation**: "Verify Email is required"

### reCAPTCHA
- **ID**: `g-recaptcha-response-100000`
- **Type**: Hidden
- **Required**: ✅ Yes
- **Auto-handled**: By Google's reCAPTCHA widget

### One-Time Passcode (OTP Page)
- **Type**: Text
- **Required**: ✅ Yes
- **Max Attempts**: 5
- **Location**: Sent to phone or email used during login

---

## Button Reference

| Button | Locator | Method | Status |
|--------|---------|--------|--------|
| English | `getByRole('button', { name: 'English' })` | Click | Always Enabled |
| Español | `getByRole('button', { name: 'Español' })` | Click | Always Enabled |
| Log On | `getByRole('button', { name: 'Log On' })` | Click | Disabled until form complete |
| VERIFY | `getByRole('button', { name: 'VERIFY' })` | Click | Disabled until OTP entered |
| Previous | `getByRole('button', { name: 'Previous' })` | Click | Always Enabled |
| New Appointment | `getByRole('button', { name: 'New Appointment' })` | Click | Enabled |
| Existing Appointment | `getByRole('button', { name: 'Existing Appointment' })` | Click | May be Disabled |
| Apply for first time Texas DL/Permit | `getByRole('button', { name: 'Apply for first time Texas DL/Permit' })` | Click | Enabled |
| Apply for first time Texas ID | `getByRole('button', { name: 'Apply for first time Texas ID' })` | Click | Enabled |
| Apply for first time Texas CLP/CDL | `getByRole('button', { name: 'Apply for first time Texas CLP/CDL' })` | Click | Enabled |

---

## Page Navigation Flow

```
┌─────────────────┐
│  Language       │
│  Selection      │
└────────┬────────┘
         │ Select English/Spanish
         ▼
┌─────────────────┐
│  Log On Form    │──── Fill form with credentials
│  (Login)        │     - First Name, Last Name
│                 │     - Date of Birth, Last 4 SSN
│                 │     - Cell Phone OR Email
└────────┬────────┘
         │ Valid credentials + reCAPTCHA
         ▼
┌─────────────────┐
│  OTP            │──── Enter One-Time Passcode
│  Verification   │     (Sent via SMS/Email)
└────────┬────────┘
         │ Valid OTP
         ▼
┌─────────────────┐
│  Appointment    │
│  Options        │──── Choose New or Existing
│                 │     Appointment
└────────┬────────┘
         │ Select New Appointment
         ▼
┌─────────────────┐
│  Service        │
│  Selection      │──── Choose service type:
│                 │     - Driver License
│                 │     - ID Card
│                 │     - CDL
│                 │     - Road Skills Test
│                 │     - Other Services
└─────────────────┘
```

---

## Common Issues & Solutions

### Issue: Log On button is disabled
**Cause**: Not all required fields are filled
**Solution**: Fill First Name, Last Name, DOB, Last 4 SSN, and either Phone or Email

### Issue: Cell Phone field not visible
**Cause**: Email radio button is selected
**Solution**: Click Cell Phone radio button to show phone field

### Issue: Email fields not visible
**Cause**: Cell Phone radio button is selected
**Solution**: Click Email radio button to show email fields

### Issue: Form fields showing validation errors
**Cause**: Fields were filled incorrectly or are empty
**Solution**: Follow the format requirements (e.g., DOB = mm/dd/yyyy)

### Issue: VERIFY button disabled on OTP page
**Cause**: OTP field is empty
**Solution**: Enter the 6-digit code sent to your phone/email

### Issue: reCAPTCHA appears broken
**Cause**: Browser security or iframe issues
**Solution**: Use browser with proper security context, ensure iframes are loaded

---

## Testing Checklist

- [ ] Language toggle works (English/Español)
- [ ] All form fields display correctly
- [ ] Cell Phone/Email conditional display works
- [ ] Form validation shows appropriate errors
- [ ] Log On button only enabled with complete form
- [ ] Date format validation works (mm/dd/yyyy)
- [ ] Phone format displays correctly ((###)###-####)
- [ ] reCAPTCHA loads and displays
- [ ] OTP field accepts input
- [ ] Navigation buttons work (Previous)
- [ ] Service selection buttons are clickable
- [ ] Progress bar updates on page navigation
- [ ] Support email link is clickable
- [ ] Page title displays correctly
- [ ] All buttons have proper labels and roles
- [ ] Form is responsive on mobile devices

---

## Accessibility Notes

✅ **Good Accessibility Practices Found**:
- Proper use of `role="button"` attributes
- Form labels associated with inputs
- Radio buttons in fieldset with legend
- Alert messages for validation errors
- Navigation buttons with clear labels
- reCAPTCHA iframe included

⚠️ **Potential Improvements**:
- Consider aria-required on all required fields
- Add more descriptive aria-labels where missing
- Ensure error messages have proper ARIA roles
- Test with screen readers for full compatibility

