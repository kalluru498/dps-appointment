# Texas DPS Scheduler - Complete Interaction Log

**Website**: https://www.txdpsscheduler.com/  
**Date**: January 29, 2026  
**Status**: ✅ **APPOINTMENT SUCCESSFULLY SCHEDULED**

---

## Appointment Confirmation Details

| Field | Value |
|-------|-------|
| **Confirmation Number** | 958771011 |
| **First Name** | Naveen |
| **Last Name** | Kumar |
| **Service Type** | Apply for first time Texas DL/Permit |
| **Appointment Date** | 3/12/2026 |
| **Appointment Time** | 11:40 AM |
| **Location** | Denton, TX (4020 E McKinney Denton, 76208) |
| **Email** | naveenreddyusa498@gmail.com |
| **Cell Phone** | (940) 758-4720 |
| **Distance from Zip** | 3.05 miles away |

---

## Complete Page-by-Page Flow

### Page 1: Language Selection
**URL**: https://www.txdpsscheduler.com/

**Content**:
- Welcome message in English and Spanish
- Two language buttons available

**Buttons**:
- English (ref: e10/e32)
- Español (ref: e12/e34)

**HTML Structure**:
```html
<div class="language-selection">
  <p>Welcome to the Texas DPS appointment scheduling system...</p>
  <button>English</button>
  <button>Español</button>
</div>
```

---

### Page 2: Log On (Login Form)

**Progress**: Select Option

**Form Fields Captured**:

| Field Name | Input ID | Type | Required | Value Entered |
|-----------|----------|------|----------|---------------|
| Texas Card Number | input-52 | Spinbutton | ❌ No | (empty) |
| First Name | input-55 | Textbox | ✅ Yes | Naveen |
| Last Name | input-58 | Textbox | ✅ Yes | Kumar |
| Date of Birth | dob | Tel | ✅ Yes | 07/21/2000 |
| Last Four SSN | last4Ssn | Spinbutton | ✅ Yes | 1234 |
| Contact Method (Radio) | radio-69 | Radiogroup | ✅ Yes | Email (selected) |
| Email | email | Textbox | ✅ Yes | naveenreddyusa498@gmail.com |
| Verify Email | verifyEmail | Textbox | ✅ Yes | naveenreddyusa498@gmail.com |

**Conditional Elements**:
- When "Email" radio selected: Email & Verify Email fields appear
- When "Cell Phone" radio selected: Cell Phone field appears

**Buttons**:
- Log On (ref: e143) - Initially disabled, enabled after form completion
- English (header)
- Español (header)

**HTML Content Summary**:
```html
<form>
  <h2>Log On</h2>
  <p>Please complete the fields below...</p>
  
  <input id="input-52" type="number" label="Texas Card Number" />
  <input id="input-55" type="text" label="First Name" required />
  <input id="input-58" type="text" label="Last Name" required />
  <input id="dob" type="tel" label="Date of Birth" required />
  <input id="last4Ssn" type="number" label="Last four of SSN" required />
  
  <fieldset>
    <input id="input-70" type="radio" value="phone" name="radio-69" />
    <input id="input-72" type="radio" value="email" name="radio-69" checked />
  </fieldset>
  
  <input id="email" type="text" label="Email" required />
  <input id="verifyEmail" type="text" label="Verify Email" required />
  
  <button type="submit">Log On</button>
</form>

<div class="recaptcha"><!-- Google reCAPTCHA --></div>
```

---

### Page 3: One-Time Passcode (OTP) Verification

**Progress**: Verify Identity

**Description**: "Additional verification is required to continue to the appointment scheduling process. A One-Time Passcode (OTP) was sent to the cell phone number or email address provided. Please enter this passcode below then click Verify. Max 5 attempts."

**Form Fields**:
- OTP Input (ref: e167) - Textbox for 6-digit code

**Buttons**:
- VERIFY (ref: button after OTP field) - Initially disabled, enabled when OTP entered
- Previous (ref: e175) - Navigate back

**HTML Structure**:
```html
<div class="otp-verification">
  <h2>One Time Passcode Verification</h2>
  <p>A One-Time Passcode (OTP) was sent...</p>
  <input type="text" placeholder="Enter OTP" />
  <button disabled>VERIFY</button>
  <button>Previous</button>
</div>
```

---

### Page 4: Appointment Options

**Progress**: Select Option

**Title**: "Appointment Options"

**Description**: 
- **New Appointment**: "Use this option to schedule a new appointment. For each card you hold, you may have one active appointment scheduled for each service."
- **Existing Appointment**: "Use this option to: View Appointment, Cancel an Existing Appointment, Reschedule an Existing Appointment"

**Content Note**:
"Commercial Driver License (CDL) drivers: Entry Level Driver Training (ELDT) requirements began Feb. 7, 2022..."
[Link to more info](https://www.dps.texas.gov/section/driver-license/how-do-i-apply-commercial-driver-license)

**Buttons**:
- New Appointment (ref: e198) - Enabled ✅
- Existing Appointment (ref: e201) - Disabled ❌
- Previous (ref: e215) - Enabled ✅

**Action Taken**: Clicked "New Appointment"

---

### Page 5: Service Selection

**Progress**: Select Service

**Heading**: "Please select the option that best describes the service you need."

**Service Categories & Available Buttons**:

#### Driver License Services
- ✅ Apply for first time Texas DL/Permit (ref: e226) - **SELECTED**
- ❌ Change, replace or renew Texas DL/Permit (disabled)
- ❌ Returning to take a computer or written test (disabled)
- ❌ Driver License Address Change (disabled)

#### Identification Card Services
- ✅ Apply for first time Texas ID (ref: e232)
- ❌ Change, replace or renew Texas ID (disabled)
- ❌ ID Address Change (disabled)

#### Commercial Driver License Services
- ✅ Apply for first time Texas CLP/CDL (ref: e237)
- ✅ Apply/Renew Non-Domicile CDL (ref: e242)
- ❌ Renew Texas CLP/CDL (disabled)
- ❌ Upgrade Texas CDL (disabled)
- ❌ Downgrade Texas CDL (disabled)
- ❌ Add or Remove Restriction (disabled)
- ❌ Change or replace Texas CLP/CDL (disabled)
- ❌ Returning to take computer/written test (disabled)
- ❌ Update Medical Certificate (disabled)

#### Road Skills Tests
- ❌ CDL (disabled)
- ❌ Class C (disabled)
- ❌ Class M (disabled)
- ❌ RV (disabled)
- ❌ Public Safety (disabled)
- ❌ Non-CDL Class A/Class B (disabled)

#### Other Services
- ✅ Apply for Election Identification Certificate (ref: e256)
- ✅ Schedule a home-bound visit (ref: e260)
- ✅ Service not listed or my license is not eligible (ref: e263)
- ✅ I am required to take a road test (ref: e265)
- ❌ Change or replace EIC (disabled)
- ❌ I received a correction no fee letter from DPS (disabled)
- ❌ Lawful Presence Verification Complete (disabled)

**Buttons**:
- Previous (ref: e272)
- All service selection buttons above

**Action Taken**: Clicked "Apply for first time Texas DL/Permit"

---

### Page 6: Customer Details

**Progress**: Customer Details

**Description**: "Please enter your contact information, review the type of service you are scheduling, then enter the ZIP Code or select the City/Town of the area where you would like to schedule your appointment. When making multiple appointments, please use the same phone number."

**Section 1: Appointment Information**

| Field Name | Input ID | Type | Pre-filled? | Value |
|-----------|----------|------|-------------|-------|
| First Name | e288 | Textbox | ✅ Yes | Naveen |
| Last Name | e296 | Textbox | ✅ Yes | Kumar |
| Date of Birth | e305 | Textbox | ✅ Yes | 07/21/2000 |
| Home Phone | e314 | Textbox | ❌ No | (empty) |
| Cell Phone | e322 | Textbox | ❌ No | (940) 758-4720 |
| Email | e331 | Textbox | ✅ Yes | naveenreddyusa498@gmail.com |
| Verify Email | e340 | Textbox | ✅ Yes | naveenreddyusa498@gmail.com |

**Checkboxes**:
- "I prefer to receive notifications via text message" (ref: e349) - Unchecked
- "Send selected notifications in Spanish" (ref: e358) - Unchecked
- "ADA Accommodation Required" (ref: e367) - Unchecked

**Section 2: Service Type & Location Selection**

**Service Type Display**: "Apply for first time Texas DL/Permit"

**Day of Week Filter**:
- Button: "Day of Week Any Day" (ref: e383)
- Dropdown with options: Any Day (default)

**Location Selection**:
- ZIP Code Input (ref: e401) - Filled: **76201**
- OR City/Town Dropdown (ref: e411) - Not used

**Buttons**:
- Previous (ref: e426)
- Next (ref: e433) - Disabled until ZIP code entered, then enabled

**HTML Structure Example**:
```html
<form>
  <section>
    <h3>Appointment Information</h3>
    <input id="input-288" type="text" value="Naveen" label="First Name" />
    <input id="input-296" type="text" value="Kumar" label="Last Name" />
    <!-- More fields... -->
  </section>
  
  <section>
    <h3>Service Type: Apply for first time Texas DL/Permit</h3>
    <button>Day of Week: Any Day</button>
    <input id="zipCode" type="text" placeholder="#####" value="76201" />
    <!-- OR City/Town dropdown -->
  </section>
  
  <button>Previous</button>
  <button>Next</button>
</form>
```

**Action Taken**: Filled Cell Phone and ZIP Code, clicked Next

---

### Page 7: Select Location

**Progress**: Select Location

**Selected Location (Primary)**:
- **City**: Denton
- **Address**: 4020 E McKinney Denton, 76208
- **Distance**: 3.05 miles away
- **Next Available Date**: 3/12/2026
- **Map Link**: [Google Maps](http://maps.google.com/?saddr=&daddr=33.210213,-97.083480)

**Suggested Locations (Other Options)**:

1. **Flower Mound**
   - Address: 6200 Canyon Falls Drive Ste. 400, Flower Mound 76226
   - Distance: 11.59 miles away
   - Next Available: 4/27/2026
   - Select Button (ref: e478)

2. **Lewisville**
   - Address: 400 N Valley Pkwy Suite 2072 Lewisville, 75067
   - Distance: 14.08 miles away
   - Next Available: 4/1/2026
   - Select Button (ref: e491)

3. **Carrollton Mega Center**
   - Address: 4600 State Hwy 121 Carrollton, 75010
   - Distance: 17.9 miles away
   - Next Available: 3/12/2026
   - Select Button (ref: e504)

4. **Plano**
   - Address: 825 Ohio Dr. Plano, 75093
   - Distance: 24.96 miles away
   - Next Available: 3/4/2026
   - Select Button (ref: e517)

**Available Dates Display** (for Denton - 3/12/2026 selected):
- Thursday 3/12/2026
- Monday 3/16/2026
- Tuesday 3/17/2026
- Wednesday 3/18/2026
- Thursday 3/19/2026

**Navigation Elements**:
- Previous/Next arrows for date carousel
- Clickable date cards

**Buttons**:
- Previous (ref: e557)
- Next (ref: disabled until date selected)

**Action Taken**: Selected Thursday 3/12/2026 from date carousel

---

### Page 8: Select Time

**Progress**: Select Time

**Location**: Denton - Apply for first time Texas DL/Permit for 3/12/2026

**Available Time Slots**:
- 11:40 AM (ref: e635) - **SELECTED**

**Navigation Elements**:
- Previous/Next arrows for time carousel
- Currently showing: 11:40 AM (single slot visible)

**Buttons**:
- Previous (ref: e643)
- Next (ref: e647) - Enabled after time selection

**Action Taken**: Clicked 11:40 AM time slot

---

### Page 9: Confirm Appointment

**Progress**: Confirm Appointment

**Timer**: "Time Remaining to Confirm: 04:49" (countdown timer)

**Summary Section**:

| Field | Value |
|-------|-------|
| First Name | Naveen |
| Last Name | Kumar |
| Service Type | Apply for first time Texas DL/Permit |
| Appointment Date/Time | 3/12/2026 11:40 AM |
| Confirmation Number | (Not yet assigned) |
| Notification Language | English |
| Home Phone | N/A |
| Cell Phone | (940) 758-4720 |
| Email | naveenreddyusa498@gmail.com |
| DL Location | Denton, 4020 E McKinney Denton, 76208 |

**Required Documents Section**:
Listed documents needed to complete transaction in office:
1. Proof of Identification - [Link to acceptable documents](https://www.dps.texas.gov/DriverLicense/identificationrequirements.htm)
2. Proof of US Citizenship or Lawful Presence - [Link to acceptable documents](https://www.dps.texas.gov/DriverLicense/LawfulStatusDLID.htm)
3. Proof of Social Security Number - [Link to acceptable documents](https://www.dps.texas.gov/DriverLicense/ssn.htm)
4. Proof of Texas Residency - [Link to acceptable documents](https://www.dps.texas.gov/DriverLicense/residencyReqNonCDL.htm)

**Important Notes**:
- "You must click "Confirm" below to complete your appointment."
- "Please arrive early to complete required forms. You may not check in more than 30 minutes prior to your appointment."
- "If you are more than 30 minutes late, your appointment will be cancelled."
- "Note: If you have a Not Eligible card status you may not be able to complete your appointment."

**Buttons**:
- Previous (ref: e719)
- Confirm (ref: e723) - Enabled

**Action Taken**: Clicked "Confirm" button

---

### Page 10: Appointment Confirmation (Final)

**Progress**: Appointment Confirmation

**Status**: ✅ **YOUR APPOINTMENT HAS BEEN CONFIRMED**

**Final Confirmation Details**:

| Field | Value |
|-------|-------|
| Confirmation Number | **958771011** |
| First Name | Naveen |
| Last Name | Kumar |
| Service Type | Apply for first time Texas DL/Permit |
| Appointment Date/Time | 3/12/2026 11:40 AM |
| Notification Language | English |
| Home Phone | N/A |
| Cell Phone | 9407584720 |
| Email | naveenreddyusa498@gmail.com |
| DL Location | Denton |
| Address | 4020 E McKinney Denton, 76208 |

**Required Documents** (Same as Page 9):
1. Proof of Identification
2. Proof of US Citizenship or Lawful Presence
3. Proof of Social Security Number
4. Proof of Texas Residency

**Important Reminders**:
- Please arrive early to complete required forms
- You may not check in more than 30 minutes prior to your appointment
- If you are more than 30 minutes late, your appointment will be cancelled
- If you have a Not Eligible card status you may not be able to complete your appointment

**Final Buttons**:
- Log Out (ref: e791)
- Print (ref: e794) - For printing confirmation

---

## Summary of All Interactive Elements

### Total Pages Navigated: 10

### Total Form Fields: 15+
- Text inputs
- Number/Spinbutton inputs
- Radio buttons
- Checkboxes
- Dropdowns/Comboboxes
- Date selectors
- Time selectors

### Total Buttons/Links: 40+
- Language toggles
- Form submission buttons
- Navigation buttons (Previous/Next)
- Service selection buttons (30+ available)
- Location selection buttons
- Date/Time selection buttons
- Final confirmation buttons

### Conditional Elements Encountered:
- ✅ Email vs Cell Phone selection affecting visible fields
- ✅ Service selection enabling different flow
- ✅ ZIP code enabling Next button
- ✅ Date selection enabling Next button
- ✅ Time selection enabling Next button

### Progressive Disclosure Pattern:
The site uses a multi-step wizard pattern with:
1. Authentication (Login + OTP)
2. Appointment Type Selection
3. Service Selection
4. Customer Information
5. Location & Date Selection
6. Time Selection
7. Confirmation
8. Final Confirmation

---

## All Locators Used

### Playwright Selectors Used:

```javascript
// Language
page.getByRole('button', { name: 'English' })
page.getByRole('button', { name: 'Español' })

// Login Form
page.getByRole('textbox', { name: 'First Name' })
page.getByRole('textbox', { name: 'Last Name' })
page.getByRole('textbox', { name: 'Date of Birth' })
page.getByRole('spinbutton', { name: 'Last four of SSN' })
page.getByRole('radio', { name: 'Email' })
page.getByRole('textbox', { name: /^Email$/ })

// Navigation
page.getByRole('button', { name: 'Next' })
page.getByRole('button', { name: 'Previous' })

// Service Selection
page.getByRole('button', { name: 'Apply for first time Texas DL/Permit' })

// Date/Time Selection
page.getByText('Thursday3/12/')
page.getByText(':40 AM')

// Final Actions
page.getByRole('button', { name: 'Confirm' })
page.getByRole('button', { name: 'Print' })
```

---

## Key Data Points Collected

### User Information Provided:
```
FIRST_NAME: Naveen
LAST_NAME: Kumar
DOB: 07/21/2000
SSN_LAST4: 1234
PHONE: (940) 758-4720
EMAIL: naveenreddyusa498@gmail.com
ZIP_CODE: 76201
LOCATION_PREFERENCE: Denton
```

### Appointment Details Generated:
```
CONFIRMATION_NUMBER: 958771011
SERVICE: Apply for first time Texas DL/Permit
DATE: 3/12/2026
TIME: 11:40 AM
LOCATION: Denton, TX
ADDRESS: 4020 E McKinney Denton, 76208
DISTANCE: 3.05 miles from ZIP code
```

---

## HTML Content Breakdown

### Total HTML Size: ~32,517+ bytes (growing with each page)

### Key HTML Elements by Page:
- Language page: Simple button selection
- Login page: Form with conditional elements
- OTP page: Single input with timer
- Option page: Two primary buttons
- Service page: 30+ service buttons organized in categories
- Customer details page: Multi-field form with checkboxes
- Location page: Table with location cards and selection buttons
- Date page: Carousel with clickable date buttons
- Time page: Carousel with clickable time buttons
- Confirmation pages: Summary display with documentation links

### Common HTML Patterns Found:
- Fieldsets for radio button groups
- Tables for displaying multiple options
- Alert/notification elements for messages
- Links with external resources
- Progress bar/stepper component
- Modal/dialog patterns for selections

---

## Browser Compatibility & Features

### Accessibility Features:
- Proper ARIA labels (role attributes)
- Tab navigation support
- Screen reader compatible structure
- Form validation with error messages
- Progress indicator for multi-step process

### Responsive Design:
- Mobile-friendly layout
- Touch-friendly buttons
- Scrollable tables for location/time selection

### Advanced Features:
- Google reCAPTCHA for security
- Timer countdown for confirmation deadline
- Map integration for location display
- Email notification support
- Multi-language support (English/Spanish)

---

## Notes for Future Automation

### Key Challenges:
1. **reCAPTCHA** - Requires special handling (may need manual solving or service)
2. **OTP Verification** - Requires receiving email/SMS with code
3. **Dynamic Availability** - Appointment slots may vary by date/location
4. **Network Delays** - Some pages have slight loading delays

### Recommended Waits:
- After form submission: 500-1000ms
- After selection: 300-500ms
- After page navigation: 500-1000ms
- Before button clicks: 200-300ms

### Best Practices for Testing:
1. Always wait for reCAPTCHA to be ready
2. Verify all required fields before form submission
3. Handle conditional field visibility
4. Use explicit waits for dynamic content
5. Test with various ZIP codes for different locations
6. Validate confirmation number is generated

---

**End of Report**

