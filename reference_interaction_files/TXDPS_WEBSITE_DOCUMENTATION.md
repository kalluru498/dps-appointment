# Texas DPS Scheduler Website - Complete Documentation

**Website**: https://www.txdpsscheduler.com/  
**Page Title**: Texas DPS - Schedule Appointment  
**Last Updated**: January 29, 2026

---

## Table of Contents
1. [Website Structure & Tabs](#website-structure--tabs)
2. [Page 1: Language Selection](#page-1-language-selection)
3. [Page 2: Login / Log On](#page-2-login--log-on)
4. [Page 3: OTP Verification](#page-3-otp-verification)
5. [Page 4: Appointment Options](#page-4-appointment-options)
6. [Page 5: Service Selection](#page-5-service-selection)
7. [All Form Fields - Complete Reference](#all-form-fields---complete-reference)
8. [All Buttons - Complete Reference](#all-buttons---complete-reference)
9. [Playwright Locators](#playwright-locators)

---

## Website Structure & Tabs

### Navigation Tabs/Sections:
The website has a **progress bar** with the following sections:
1. **Language Selection** - Initial page
2. **Log On** - Login credentials
3. **OTP Verification** - One-Time Passcode verification
4. **Appointment Options** - Choose between New/Existing appointments
5. **Service Selection** - Select the service you need
6. **Further pages** - Depending on service selection

### Header Navigation:
- **Language Toggle**: English / Español buttons (available in header)
- **Log Out Button**: Appears after initial login
- **Version Number**: V-25.3.0.1 (bottom right)

---

## Page 1: Language Selection

**Purpose**: User selects preferred language (English or Spanish)

### Buttons:
| Button Text | Type | Locator | Purpose |
|-----------|------|---------|---------|
| English | Button | `ref=e10` / Accessible via `getByRole('button', { name: 'English' })` | Select English language |
| Español | Button | `ref=e12` / Accessible via `getByRole('button', { name: 'Español' })` | Select Spanish language |

### HTML Structure:
```html
<div class="language-selection">
  <p>Welcome to the Texas DPS appointment scheduling system. Please select your preferred language to continue:</p>
  <p>Bienvenido al sistema de programación de citas DPS de Texas. Por favor seleccione su idioma preferido para continuar:</p>
  <button>English</button>
  <button>Español</button>
</div>
```

---

## Page 2: Login / Log On

**Purpose**: User enters credentials to log into their account

### Form Fields:

| Field Name | Type | Input ID | HTML Attributes | Placeholder | Required | Notes |
|-----------|------|----------|-----------------|-------------|----------|-------|
| Texas Card Number (DL, ID, EIC) | Number/Spinbutton | `input-52` | type="number" | N/A | ❌ No | Optional field |
| First Name | Text | `input-55` | type="text" | N/A | ✅ Yes | Required field (marked with *) |
| Last Name | Text | `input-58` | type="text" | N/A | ✅ Yes | Required field (marked with *) |
| Date of Birth | Telephone | `dob` | type="tel" | N/A | ✅ Yes | Format: mm/dd/yyyy, Required field |
| Last four of SSN | Number/Spinbutton | `last4Ssn` | type="number" | N/A | ✅ Yes | Required field (marked with *) |
| Contact Method - Radio Group | Radio | `radio-69` (parent) | name="radio-69" | N/A | ✅ Yes | Two options: Cell Phone OR Email |
| &nbsp;&nbsp;Cell Phone (Option 1) | Radio | `input-70` | type="radio", value="phone" | N/A | - | Default selected |
| &nbsp;&nbsp;Email (Option 2) | Radio | `input-72` | type="radio", value="email" | N/A | - | Alternate option |
| **CONDITIONAL - If Cell Phone Selected:** |
| Cell Phone Number | Text | `input-120` | type="text" | (###)###-#### | ✅ Yes | Shows only when Cell Phone is selected |
| **CONDITIONAL - If Email Selected:** |
| Email Address | Text | `email` | type="text" | N/A | ✅ Yes | Shows only when Email is selected |
| Verify Email | Text | `verifyEmail` | type="text" | N/A | ✅ Yes | Shows only when Email is selected |
| reCAPTCHA | Hidden | `g-recaptcha-response-100000` | type="hidden" | N/A | ✅ Yes | Google reCAPTCHA token |

### Buttons:

| Button Text | Button ID | Status | Purpose |
|-----------|----------|--------|---------|
| Log On | `ref=e126` | Disabled until form complete | Submit login credentials |
| English | `ref=e32` | Enabled | Change language to English |
| Español | `ref=e34` | Enabled | Change language to Spanish |

### Form Validation Notes:
- **First Name**: Required validation shown with alert "First name is required"
- **Email**: Required validation shown with alert "Email is required" (when Email radio selected)
- **Verify Email**: Required validation shown with alert "Verify Email is required" (when Email radio selected)
- **Log On Button**: Disabled until all required fields are filled
- **Message**: "Please provide a valid cell phone number or email address to log in."

### Contact Information:
- **Support Email**: TXScheduler@dps.texas.gov

### HTML Structure (Simplified):
```html
<div class="login-form">
  <h2>Log On</h2>
  <p>Please complete the fields below. A Texas Card Number is not required...</p>
  
  <form>
    <input id="input-52" type="number" label="Texas Card Number (DL, ID, EIC)" />
    <input id="input-55" type="text" label="First Name" required />
    <input id="input-58" type="text" label="Last Name" required />
    <input id="dob" type="tel" label="Date of Birth (mm/dd/yyyy)" required />
    <input id="last4Ssn" type="number" label="Last four of SSN" required />
    
    <fieldset name="radio-69">
      <label>
        <input id="input-70" type="radio" name="radio-69" value="phone" checked />
        Cell Phone
      </label>
      <label>
        <input id="input-72" type="radio" name="radio-69" value="email" />
        Email
      </label>
    </fieldset>
    
    <!-- Shows when Cell Phone selected -->
    <input id="input-120" type="text" label="Cell Phone" placeholder="(###)###-####" />
    
    <!-- Shows when Email selected -->
    <input id="email" type="text" label="Email" />
    <input id="verifyEmail" type="text" label="Verify Email" />
    
    <button type="submit">Log On</button>
  </form>
</div>
```

---

## Page 3: OTP Verification

**Purpose**: User enters One-Time Passcode (OTP) received via SMS or Email

### Form Fields:

| Field Name | Type | Input ID | Placeholder | Required | Notes |
|-----------|------|----------|-------------|----------|-------|
| One-Time Passcode (OTP) | Text | Unknown (auto-focus field) | N/A | ✅ Yes | Sent to phone or email |

### Buttons:

| Button Text | Button ID | Status | Purpose |
|-----------|----------|--------|---------|
| VERIFY | ref=e164 | Disabled until OTP entered | Submit OTP for verification |
| Previous | ref=e171 | Enabled | Go back to login page |

### Additional Info:
- **Title**: One Time Passcode Verification
- **Description**: "Additional verification is required to continue to the appointment scheduling process. A One-Time Passcode (OTP) was sent to the cell phone number or email address provided. Please enter this passcode below then click Verify. Max 5 attempts."
- **Max Attempts**: 5

### HTML Structure:
```html
<div class="otp-verification">
  <h2>One Time Passcode Verification</h2>
  <p>A One-Time Passcode (OTP) was sent... Max 5 attempts.</p>
  
  <form>
    <input type="text" placeholder="Enter OTP" autofocus />
    <button type="button" disabled>VERIFY</button>
    <button type="button">Previous</button>
  </form>
</div>
```

---

## Page 4: Appointment Options

**Purpose**: User chooses whether to create a new appointment or manage existing one

### Buttons:

| Button Text | Button ID | Status | Purpose |
|-----------|----------|--------|---------|
| New Appointment | ref=e196 | Enabled | Create a new appointment |
| Existing Appointment | ref=e201 | Disabled | View/Manage/Reschedule existing appointment (not available for this session) |
| Previous | ref=e213 | Enabled | Go back to previous page |

### Progress Bar:
- Current Step: "Select Option"
- Visual progress indicator showing completion status

### Description:
**New Appointment**: "Use this option to schedule a new appointment. For each card you hold, you may have one active appointment scheduled for each service."

**Existing Appointment**: "Use this option to:
- **View Appointment**: View the date, time and location of your existing appointment.
- **Cancel an Existing Appointment**: If you cancel your appointment, there may be a delay in the availability of a new appointment.
- **Reschedule an Existing Appointment**: You may have only one active appointment scheduled for each service."

### Additional Info:
- System message: "A limited number of additional appointments will be available at most driver license offices daily. These additional appointments are made available throughout the day and can be scheduled online, eliminating the need to visit the driver license office in-person."

### HTML Structure:
```html
<div class="appointment-options">
  <h2>Appointment Options</h2>
  
  <button>New Appointment</button>
  <p>Use this option to schedule a new appointment...</p>
  
  <button disabled>Existing Appointment</button>
  <p>Use this option to:
    <strong>View Appointment</strong>...
  </p>
  
  <button>Previous</button>
</div>
```

---

## Page 5: Service Selection

**Purpose**: User selects the type of service they need

### Heading:
"Please select the option that best describes the service you need."

**Note**: "Do not see the service you need? Please select 'Service Not Listed or My License Is Not Eligible'."

### Service Categories & Buttons:

#### 1. Driver License Services
| Button Text | Button ID | Status |
|-----------|----------|--------|
| Apply for first time Texas DL/Permit | ref=e224 | Enabled |
| Change, replace or renew Texas DL/Permit | ref=e225 | Disabled |
| Returning to take a computer or written test | ref=e226 | Disabled |
| Driver License Address Change | ref=e227 | Disabled |

#### 2. Identification Card Services
| Button Text | Button ID | Status |
|-----------|----------|--------|
| Apply for first time Texas ID | ref=e230 | Enabled |
| Change, replace or renew Texas ID | ref=e231 | Disabled |
| ID Address Change | ref=e232 | Disabled |

#### 3. Commercial Driver License Services
| Button Text | Button ID | Status |
|-----------|----------|--------|
| Apply for first time Texas CLP/CDL | ref=e235 | Enabled |
| Renew Texas CLP/CDL | ref=e236 | Disabled |
| Upgrade Texas CDL (Class or Endorsements) | ref=e237 | Disabled |
| Downgrade Texas CDL to DL | ref=e238 | Disabled |
| Apply/Renew Non-Domicile CDL | ref=e240 | Enabled |
| Add or Remove Restriction | ref=e241 | Disabled |
| Change or replace Texas CLP/CDL | ref=e242 | Disabled |
| Returning to take a computer or written test | ref=e243 | Disabled |
| Update Medical Certificate | ref=e244 | Disabled |

#### 4. Road Skills Tests
| Button Text | Button ID | Status |
|-----------|----------|--------|
| CDL | ref=e246 | Disabled |
| Class C | ref=e247 | Disabled |
| Class M | ref=e248 | Disabled |
| RV | ref=e249 | Disabled |
| Public Safety | ref=e250 | Disabled |
| Non-CDL Class A/Class B | ref=e251 | Disabled |

#### 5. Other Services
| Button Text | Button ID | Status |
|-----------|----------|--------|
| Apply for Election Identification Certificate | ref=e254 | Enabled |
| Change or replace EIC | ref=e255 | Disabled |
| I received a correction no fee letter from DPS | ref=e256 | Disabled |
| Schedule a home-bound visit | ref=e258 | Enabled |
| Lawful Presence Verification Complete | ref=e259 | Disabled |
| Service not listed or my license is not eligible | ref=e261 | Enabled |
| I am required to take a road test | ref=e263 | Enabled |

### Other Buttons:
| Button Text | Button ID | Status |
|-----------|----------|--------|
| Previous | ref=e270 | Enabled |

### Important CDL Notice:
"Commercial Driver License (CDL) drivers: Entry Level Driver Training (ELDT) requirements began Feb. 7, 2022. Anyone applying for a Class A or B CDL for the first time, upgrading an existing CDL to a Class A or B, or obtaining a school bus (S), passenger (P) or hazardous materials (H) endorsement for the first time must meet ELDT requirements. For more information, please visit our website [here](https://www.dps.texas.gov/section/driver-license/how-do-i-apply-commercial-driver-license)."

### HTML Structure:
```html
<div class="service-selection">
  <h2>Please select the option that best describes the service you need.</h2>
  
  <section class="service-category">
    <h3>Driver License Services</h3>
    <button>Apply for first time Texas DL/Permit</button>
    <button disabled>Change, replace or renew Texas DL/Permit</button>
    <!-- ... more buttons ... -->
  </section>
  
  <!-- ... more service categories ... -->
  
  <button>Previous</button>
</div>
```

---

## All Form Fields - Complete Reference

### Fields by Page:

#### Login Page (Page 2) - All Input Elements:
```json
[
  {
    "fieldName": "Texas Card Number (DL, ID, EIC)",
    "fieldId": "input-52",
    "fieldType": "number",
    "required": false,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A"
  },
  {
    "fieldName": "First Name",
    "fieldId": "input-55",
    "fieldType": "text",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A"
  },
  {
    "fieldName": "Last Name",
    "fieldId": "input-58",
    "fieldType": "text",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A"
  },
  {
    "fieldName": "Date of Birth (mm/dd/yyyy)",
    "fieldId": "dob",
    "fieldType": "tel",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A"
  },
  {
    "fieldName": "Last four of SSN",
    "fieldId": "last4Ssn",
    "fieldType": "number",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A"
  },
  {
    "fieldName": "Cell Phone (Option 1)",
    "fieldId": "input-70",
    "fieldType": "radio",
    "required": true,
    "name": "radio-69",
    "value": "phone",
    "ariaLabel": "N/A",
    "conditional": "Show if selected"
  },
  {
    "fieldName": "Email (Option 2)",
    "fieldId": "input-72",
    "fieldType": "radio",
    "required": true,
    "name": "radio-69",
    "value": "email",
    "ariaLabel": "N/A",
    "conditional": "Show if selected"
  },
  {
    "fieldName": "Cell Phone Number",
    "fieldId": "input-120",
    "fieldType": "text",
    "required": true,
    "placeholder": "(###)###-####",
    "name": "N/A",
    "ariaLabel": "N/A",
    "conditional": "Only shows when 'Cell Phone' radio is selected"
  },
  {
    "fieldName": "Email Address",
    "fieldId": "email",
    "fieldType": "text",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A",
    "conditional": "Only shows when 'Email' radio is selected"
  },
  {
    "fieldName": "Verify Email",
    "fieldId": "verifyEmail",
    "fieldType": "text",
    "required": true,
    "placeholder": "N/A",
    "name": "N/A",
    "ariaLabel": "N/A",
    "conditional": "Only shows when 'Email' radio is selected"
  },
  {
    "fieldName": "reCAPTCHA Token",
    "fieldId": "g-recaptcha-response-100000",
    "fieldType": "hidden",
    "required": true,
    "name": "g-recaptcha-response",
    "ariaLabel": "N/A"
  }
]
```

#### OTP Page (Page 3):
```json
[
  {
    "fieldName": "One-Time Passcode",
    "fieldType": "text",
    "required": true,
    "placeholder": "Enter OTP",
    "notes": "Max 5 attempts allowed"
  }
]
```

---

## All Buttons - Complete Reference

### Master Button List:

```json
[
  {
    "page": "All Pages",
    "buttonText": "English",
    "buttonId": "e32 or e10",
    "type": "Language Toggle",
    "accessible": "getByRole('button', { name: 'English' })",
    "status": "Enabled"
  },
  {
    "page": "All Pages",
    "buttonText": "Español",
    "buttonId": "e34 or e12",
    "type": "Language Toggle",
    "accessible": "getByRole('button', { name: 'Español' })",
    "status": "Enabled"
  },
  {
    "page": "Page 2 - Login",
    "buttonText": "Log On",
    "buttonId": "e126",
    "type": "Submit",
    "accessible": "getByRole('button', { name: 'Log On' })",
    "status": "Disabled until form complete"
  },
  {
    "page": "Page 3 - OTP",
    "buttonText": "VERIFY",
    "buttonId": "e164",
    "type": "Submit",
    "accessible": "getByRole('button', { name: 'VERIFY' })",
    "status": "Disabled until OTP entered"
  },
  {
    "page": "Page 3 - OTP",
    "buttonText": "Previous",
    "buttonId": "e171",
    "type": "Navigation",
    "accessible": "getByRole('button', { name: 'Previous' })",
    "status": "Enabled"
  },
  {
    "page": "Page 4 - Appointment Options",
    "buttonText": "New Appointment",
    "buttonId": "e196",
    "type": "Action",
    "accessible": "getByRole('button', { name: 'New Appointment' })",
    "status": "Enabled"
  },
  {
    "page": "Page 4 - Appointment Options",
    "buttonText": "Existing Appointment",
    "buttonId": "e201",
    "type": "Action",
    "accessible": "getByRole('button', { name: 'Existing Appointment' })",
    "status": "Disabled"
  },
  {
    "page": "Page 4 - Appointment Options",
    "buttonText": "Previous",
    "buttonId": "e213",
    "type": "Navigation",
    "accessible": "getByRole('button', { name: 'Previous' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Apply for first time Texas DL/Permit",
    "buttonId": "e224",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Apply for first time Texas DL/Permit' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Apply for first time Texas ID",
    "buttonId": "e230",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Apply for first time Texas ID' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Apply for first time Texas CLP/CDL",
    "buttonId": "e235",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Apply for first time Texas CLP/CDL' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Apply/Renew Non-Domicile CDL",
    "buttonId": "e240",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Apply/Renew Non-Domicile CDL' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Apply for Election Identification Certificate",
    "buttonId": "e254",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Apply for Election Identification Certificate' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Schedule a home-bound visit",
    "buttonId": "e258",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Schedule a home-bound visit' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Service not listed or my license is not eligible",
    "buttonId": "e261",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'Service not listed or my license is not eligible' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "I am required to take a road test",
    "buttonId": "e263",
    "type": "Service Selection",
    "accessible": "getByRole('button', { name: 'I am required to take a road test' })",
    "status": "Enabled"
  },
  {
    "page": "Page 5 - Service Selection",
    "buttonText": "Previous",
    "buttonId": "e270",
    "type": "Navigation",
    "accessible": "getByRole('button', { name: 'Previous' })",
    "status": "Enabled"
  }
]
```

---

## Playwright Locators

### Recommended Playwright Selectors:

#### By Role (Preferred Method - Most Accessible):
```javascript
// Language Selection Buttons
await page.getByRole('button', { name: 'English' }).click();
await page.getByRole('button', { name: 'Español' }).click();

// Login Form Fields
await page.getByRole('spinbutton', { name: 'Texas Card Number' }).fill('123456');
await page.getByRole('textbox', { name: 'First Name' }).fill('John');
await page.getByRole('textbox', { name: 'Last Name' }).fill('Doe');
await page.getByRole('textbox', { name: 'Date of Birth' }).fill('01/15/1990');
await page.getByRole('spinbutton', { name: 'Last four of SSN' }).fill('1234');

// Radio Button Selection
await page.getByRole('radio', { name: 'Cell Phone' }).check();
await page.getByRole('radio', { name: 'Email' }).check();

// Conditional Fields
await page.getByRole('textbox', { name: 'Cell Phone' }).fill('(512)555-1234');
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
await page.getByRole('textbox', { name: 'Verify Email' }).fill('user@example.com');

// Submit Button
await page.getByRole('button', { name: 'Log On' }).click();

// OTP Verification
await page.getByRole('textbox').first().fill('123456');
await page.getByRole('button', { name: 'VERIFY' }).click();

// Navigation
await page.getByRole('button', { name: 'Previous' }).click();

// Appointment Selection
await page.getByRole('button', { name: 'New Appointment' }).click();
await page.getByRole('button', { name: 'Existing Appointment' }).click();

// Service Selection
await page.getByRole('button', { name: 'Apply for first time Texas DL/Permit' }).click();
await page.getByRole('button', { name: 'Apply for first time Texas ID' }).click();
```

#### By ID:
```javascript
// Texas Card Number
await page.locator('#input-52').fill('123456');

// First Name
await page.locator('#input-55').fill('John');

// Last Name
await page.locator('#input-58').fill('Doe');

// Date of Birth
await page.locator('#dob').fill('01/15/1990');

// Last Four SSN
await page.locator('#last4Ssn').fill('1234');

// Cell Phone Radio
await page.locator('#input-70').check();

// Email Radio
await page.locator('#input-72').check();

// Cell Phone Number
await page.locator('#input-120').fill('(512)555-1234');

// Email
await page.locator('#email').fill('user@example.com');

// Verify Email
await page.locator('#verifyEmail').fill('user@example.com');

// reCAPTCHA (normally auto-filled by Google)
await page.locator('#g-recaptcha-response-100000').fill('token');
```

#### By Placeholder Text:
```javascript
// Cell Phone (on Email selection tab)
await page.getByPlaceholder('(###)###-####').fill('(512)555-1234');
```

#### By Label Text:
```javascript
await page.getByLabel('Texas Card Number').fill('123456');
await page.getByLabel('First Name').fill('John');
await page.getByLabel('Last Name').fill('Doe');
await page.getByLabel('Date of Birth').fill('01/15/1990');
await page.getByLabel('Last four of SSN').fill('1234');
await page.getByLabel('Cell Phone').fill('(512)555-1234');
await page.getByLabel('Email').fill('user@example.com');
```

---

## Additional HTML Content Information

### Total HTML Size: ~32,517 bytes

### Key HTML Elements by Category:

#### Header Section:
- `img` - DPS Logo
- `h1` or similar - "Schedule Appointment" title
- Language toggle buttons (English/Español)
- Version number display (V-25.3.0.1)
- Log Out button (appears after login)

#### Main Form Section:
- `<form>` container for login
- `<fieldset>` for radio buttons (contact method)
- Multiple `<input>` elements with various types
- `<button>` elements for actions
- `<alert>` elements for validation messages

#### Footer Section:
- Support email link: `mailto:TXScheduler@dps.texas.gov`
- `<iframe>` for reCAPTCHA
- Privacy & Terms links (Google)

#### Progress Bar:
- Visual indicator of current step in process
- Dynamically updates with page transitions

---

## Summary

This website uses a **multi-step wizard pattern** for appointment scheduling:

1. **Language Selection** - 2 buttons
2. **Login/Authentication** - 10+ form fields, conditional display
3. **OTP Verification** - 1 input field, 2 buttons
4. **Appointment Type Selection** - 2 service buttons
5. **Service Category Selection** - 30+ service option buttons

**Total Interactive Elements**: 
- ~35+ Buttons
- ~12 Form Fields (with conditional display)
- 2 Language Options
- Multiple validation states

**Key Features**:
- Responsive design (Mobile-friendly)
- Accessibility considerations (ARIA labels, Role attributes)
- Progressive disclosure (conditional form fields)
- Form validation with error messages
- reCAPTCHA protection
- Multi-language support (English/Spanish)

