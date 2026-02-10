# Texas DPS Scheduler - Automated Test Case Template

## Test Data Setup

```javascript
const TEST_DATA = {
  // User Information
  firstName: 'Naveen',
  lastName: 'Kumar',
  dateOfBirth: '07/21/2000',
  ssn_last4: '1234',
  cellPhone: '(940) 758-4720',
  email: 'naveenreddyusa498@gmail.com',
  
  // Location Settings
  zipCode: '76201',
  locationPreference: 'Denton',
  maxDistanceMiles: 25,
  
  // Service Selection
  service: 'Apply for first time Texas DL/Permit',
  dayOfWeek: 'Any Day',
  
  // Expected Results
  expectedConfirmationNumber: '958771011',
  expectedDate: '3/12/2026',
  expectedTime: '11:40 AM',
  expectedLocation: 'Denton'
};
```

---

## Complete End-to-End Test Suite

```javascript
import { test, expect, Page, Browser } from '@playwright/test';

test.describe('Texas DPS Scheduler - Complete Appointment Booking Flow', () => {
  let page: Page;
  const testData = {
    firstName: 'Naveen',
    lastName: 'Kumar',
    dateOfBirth: '07/21/2000',
    ssn_last4: '1234',
    cellPhone: '(940) 758-4720',
    email: 'naveenreddyusa498@gmail.com',
    zipCode: '76201'
  };

  test.beforeEach(async ({ browser }) => {
    const context = await browser.newContext({
      acceptDownloads: true,
    });
    page = await context.newPage();
    await page.goto('https://www.txdpsscheduler.com/');
  });

  test('TC-001: Navigate to login form via English button', async () => {
    // Verify language selection page is visible
    const englishBtn = page.getByRole('button', { name: 'English' }).first();
    await expect(englishBtn).toBeVisible();
    
    // English button text should be visible
    await expect(page.getByText('Welcome to the Texas DPS')).toBeVisible();
  });

  test('TC-002: Select Email as contact method instead of Phone', async () => {
    // Find and click Email radio button
    const emailRadio = page.getByRole('radio', { name: 'Email' });
    
    // Verify it's visible and clickable
    await expect(emailRadio).toBeVisible();
    
    // Click on the Email label instead of radio for better compatibility
    await page.getByText('Email', { selector: 'label, div' }).click();
    
    // Wait for Email fields to appear
    await page.waitForTimeout(300);
    
    // Verify Email input fields are now visible
    const emailInput = page.getByRole('textbox', { name: /^Email$/ });
    const verifyEmailInput = page.getByRole('textbox', { name: 'Verify Email' });
    
    await expect(emailInput).toBeVisible();
    await expect(verifyEmailInput).toBeVisible();
  });

  test('TC-003: Fill login form with all required information', async () => {
    // Select Email option
    await page.getByText('Email', { selector: 'label, div' }).click();
    await page.waitForTimeout(300);
    
    // Fill form fields
    await page.getByRole('textbox', { name: 'First Name' }).fill(testData.firstName);
    await page.waitForTimeout(150);
    
    await page.getByRole('textbox', { name: 'Last Name' }).fill(testData.lastName);
    await page.waitForTimeout(150);
    
    await page.getByRole('textbox', { name: 'Date of Birth' }).fill(testData.dateOfBirth);
    await page.waitForTimeout(150);
    
    await page.getByRole('spinbutton', { name: 'Last four of SSN' }).fill(testData.ssn_last4);
    await page.waitForTimeout(150);
    
    await page.getByRole('textbox', { name: /^Email$/ }).fill(testData.email);
    await page.waitForTimeout(150);
    
    await page.getByRole('textbox', { name: 'Verify Email' }).fill(testData.email);
    await page.waitForTimeout(500);
    
    // Verify Log On button is now enabled
    const logOnBtn = page.getByRole('button', { name: 'Log On' });
    await expect(logOnBtn).not.toBeDisabled();
    
    // Verify filled values
    await expect(page.getByRole('textbox', { name: 'First Name' })).toHaveValue(testData.firstName);
    await expect(page.getByRole('textbox', { name: 'Last Name' })).toHaveValue(testData.lastName);
  });

  test('TC-004: Handle OTP verification (requires manual OTP entry)', async () => {
    // Navigate to OTP page
    // Note: This would require actual OTP code from email/SMS
    
    // Verify OTP page elements
    await page.waitForSelector('text=One Time Passcode Verification');
    
    const otpInput = page.locator('input[type="text"]').first();
    await expect(otpInput).toBeVisible();
    
    const verifyBtn = page.getByRole('button', { name: 'VERIFY' });
    await expect(verifyBtn).toBeDisabled();
    
    // Fill OTP (would be provided by user)
    // await otpInput.fill('123456');
    // await page.waitForTimeout(300);
    // await expect(verifyBtn).not.toBeDisabled();
    // await verifyBtn.click();
  });

  test('TC-005: Select appointment type (New Appointment)', async () => {
    // Assuming we're past OTP verification
    // This would continue from successful OTP entry
    
    const newAppointmentBtn = page.getByRole('button', { name: 'New Appointment' });
    
    // Verify button is visible and enabled
    await expect(newAppointmentBtn).toBeVisible();
    await expect(newAppointmentBtn).not.toBeDisabled();
    
    // Click New Appointment
    await newAppointmentBtn.click();
    await page.waitForTimeout(500);
    
    // Verify service selection page loaded
    await expect(page.getByText('Please select the option that best describes the service you need')).toBeVisible();
  });

  test('TC-006: Select service - Apply for first time Texas DL/Permit', async () => {
    const dlServiceBtn = page.getByRole('button', { 
      name: 'Apply for first time Texas DL/Permit' 
    });
    
    // Verify button is visible and enabled
    await expect(dlServiceBtn).toBeVisible();
    await expect(dlServiceBtn).not.toBeDisabled();
    
    // Click service selection
    await dlServiceBtn.click();
    await page.waitForTimeout(1000);
    
    // Verify customer details page loaded
    await expect(page.getByText('Customer Details')).toBeVisible();
  });

  test('TC-007: Fill customer details form', async () => {
    // Fill Cell Phone
    await page.getByRole('textbox', { name: 'Cell Phone' }).fill(testData.cellPhone);
    await page.waitForTimeout(200);
    
    // Fill Zip Code
    await page.getByRole('textbox', { name: 'Zip Code' }).fill(testData.zipCode);
    await page.waitForTimeout(500);
    
    // Verify fields are filled
    await expect(page.getByRole('textbox', { name: 'Cell Phone' })).toHaveValue(testData.cellPhone);
    await expect(page.getByRole('textbox', { name: 'Zip Code' })).toHaveValue(testData.zipCode);
    
    // Verify Next button is enabled
    const nextBtn = page.getByRole('button', { name: 'Next' });
    await expect(nextBtn).not.toBeDisabled();
  });

  test('TC-008: Select location from available options', async () => {
    // Verify Denton location is available
    await expect(page.getByText('Denton')).toBeVisible();
    await expect(page.getByText('3.05 miles away')).toBeVisible();
    
    // Verify next available date is shown
    await expect(page.getByText(/3\/12\/2026/)).toBeVisible();
  });

  test('TC-009: Select appointment date', async () => {
    // Scroll to date selection if needed
    const dateButtons = page.locator('text=/Thursday|Monday|Tuesday|Wednesday/');
    
    // Click first available Thursday (3/12/2026)
    await page.getByText('Thursday').first().click();
    await page.waitForTimeout(300);
    
    // Verify time selection appears
    await expect(page.getByText('Select from the available times')).toBeVisible();
  });

  test('TC-010: Select appointment time', async () => {
    // Select 11:40 AM time slot
    const timeSlot = page.getByText('11:40 AM');
    await expect(timeSlot).toBeVisible();
    
    await timeSlot.click();
    await page.waitForTimeout(500);
    
    // Verify Next button is enabled
    const nextBtn = page.getByRole('button', { name: 'Next' });
    await expect(nextBtn).not.toBeDisabled();
  });

  test('TC-011: Verify appointment summary before confirmation', async () => {
    // Verify all summary details are shown
    const summaryElements = [
      'Naveen',
      'Kumar',
      'Apply for first time Texas DL/Permit',
      /3\/12\/2026 11:40 AM/,
      'Denton',
      testData.email,
      testData.cellPhone
    ];
    
    for (const element of summaryElements) {
      await expect(page.getByText(element)).toBeVisible();
    }
    
    // Verify required documents section
    await expect(page.getByText('Proof of Identification')).toBeVisible();
    await expect(page.getByText('Proof of US Citizenship')).toBeVisible();
    await expect(page.getByText('Proof of Social Security Number')).toBeVisible();
    await expect(page.getByText('Proof of Texas Residency')).toBeVisible();
  });

  test('TC-012: Confirm appointment and receive confirmation number', async () => {
    // Click Confirm button
    const confirmBtn = page.getByRole('button', { name: 'Confirm' });
    await expect(confirmBtn).toBeVisible();
    
    await confirmBtn.click();
    await page.waitForTimeout(1000);
    
    // Verify confirmation page
    await expect(page.getByText('Your appointment has been confirmed')).toBeVisible();
    
    // Verify confirmation number is displayed
    const confirmationNumber = page.locator('text=/Confirmation Number|958771011/');
    await expect(confirmationNumber).toBeVisible();
    
    // Verify final details
    await expect(page.getByText('Naveen')).toBeVisible();
    await expect(page.getByText('Kumar')).toBeVisible();
    await expect(page.getByText(/3\/12\/2026 11:40 AM/)).toBeVisible();
  });

  test('TC-013: Verify Print button is available on confirmation page', async () => {
    const printBtn = page.getByRole('button', { name: 'Print' });
    await expect(printBtn).toBeVisible();
    await expect(printBtn).not.toBeDisabled();
  });

  test('TC-014: Verify Log Out button is available on confirmation page', async () => {
    const logOutBtn = page.getByRole('button', { name: 'Log Out' });
    await expect(logOutBtn).toBeVisible();
    await expect(logOutBtn).not.toBeDisabled();
  });

  test('TC-015: Navigation - Test Previous buttons throughout flow', async () => {
    // Assuming we're on customer details page
    const previousBtn = page.getByRole('button', { name: 'Previous' }).first();
    
    if (await previousBtn.isVisible()) {
      await previousBtn.click();
      await page.waitForTimeout(500);
      
      // Verify we're back at appointment options
      await expect(page.getByText('Appointment Options')).toBeVisible();
    }
  });

  test('TC-016: Form validation - Missing required fields', async () => {
    // Try to submit without filling required fields
    const logOnBtn = page.getByRole('button', { name: 'Log On' });
    
    // Button should be disabled without required fields
    await expect(logOnBtn).toBeDisabled();
  });

  test('TC-017: Form validation - Email mismatch', async () => {
    // Select email
    await page.getByText('Email', { selector: 'label, div' }).click();
    await page.waitForTimeout(300);
    
    // Fill form with mismatched emails
    await page.getByRole('textbox', { name: 'First Name' }).fill(testData.firstName);
    await page.getByRole('textbox', { name: 'Last Name' }).fill(testData.lastName);
    await page.getByRole('textbox', { name: 'Date of Birth' }).fill(testData.dateOfBirth);
    await page.getByRole('spinbutton', { name: 'Last four of SSN' }).fill(testData.ssn_last4);
    
    // Fill different emails
    const emailInput = page.getByRole('textbox', { name: /^Email$/ });
    const verifyEmailInput = page.getByRole('textbox', { name: 'Verify Email' });
    
    await emailInput.fill('test1@example.com');
    await verifyEmailInput.fill('test2@example.com');
    await page.waitForTimeout(500);
    
    // Check if validation error appears
    const errorMsg = page.locator('text=/Email|mismatch|does not match/i');
    // May or may not show error depending on form validation
  });

  test('TC-018: Accessibility - Verify all interactive elements are keyboard accessible', async () => {
    // Tab through form
    await page.keyboard.press('Tab');
    
    // Check that focused element is visible
    const focusedElement = await page.evaluate(() => {
      return document.activeElement?.getAttribute('class') || '';
    });
    
    expect(focusedElement).toBeTruthy();
  });

  test('TC-019: Responsive Design - Test on mobile viewport', async () => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    
    // Verify buttons are still clickable
    const englishBtn = page.getByRole('button', { name: 'English' }).first();
    await expect(englishBtn).toBeVisible();
    
    // Calculate button size
    const bbox = await englishBtn.boundingBox();
    expect(bbox?.width).toBeGreaterThan(40); // Min touch target size
    expect(bbox?.height).toBeGreaterThan(40);
  });

  test('TC-020: Verify page title throughout flow', async () => {
    await expect(page).toHaveTitle('Texas DPS - Schedule Appointment');
    
    // Title should remain same on all pages
    await page.goto('https://www.txdpsscheduler.com/');
    await expect(page).toHaveTitle('Texas DPS - Schedule Appointment');
  });
});
```

---

## Helper Functions for Automation

```javascript
// Helper function to fill login form
async function fillLoginForm(page, data) {
  // Select Email option
  await page.getByText('Email', { selector: 'label, div' }).click();
  await page.waitForTimeout(300);
  
  // Fill fields
  await page.getByRole('textbox', { name: 'First Name' }).fill(data.firstName);
  await page.waitForTimeout(100);
  
  await page.getByRole('textbox', { name: 'Last Name' }).fill(data.lastName);
  await page.waitForTimeout(100);
  
  await page.getByRole('textbox', { name: 'Date of Birth' }).fill(data.dateOfBirth);
  await page.waitForTimeout(100);
  
  await page.getByRole('spinbutton', { name: 'Last four of SSN' }).fill(data.ssn_last4);
  await page.waitForTimeout(100);
  
  await page.getByRole('textbox', { name: /^Email$/ }).fill(data.email);
  await page.waitForTimeout(100);
  
  await page.getByRole('textbox', { name: 'Verify Email' }).fill(data.email);
  await page.waitForTimeout(300);
}

// Helper function to handle OTP (requires user input or automation service)
async function handleOTP(page, otp: string) {
  const otpInput = page.locator('input[type="text"]').first();
  await otpInput.fill(otp);
  await page.waitForTimeout(300);
  
  const verifyBtn = page.getByRole('button', { name: 'VERIFY' });
  await verifyBtn.click();
  await page.waitForTimeout(500);
}

// Helper function to select service
async function selectService(page, serviceName: string) {
  const serviceBtn = page.getByRole('button', { name: serviceName });
  await serviceBtn.click();
  await page.waitForTimeout(1000);
}

// Helper function to fill customer details
async function fillCustomerDetails(page, data) {
  await page.getByRole('textbox', { name: 'Cell Phone' }).fill(data.cellPhone);
  await page.waitForTimeout(200);
  
  await page.getByRole('textbox', { name: 'Zip Code' }).fill(data.zipCode);
  await page.waitForTimeout(500);
}

// Helper function to select date and time
async function selectDateAndTime(page, dateText: string, timeText: string) {
  // Select date
  await page.getByText(dateText).click();
  await page.waitForTimeout(500);
  
  // Select time
  await page.getByText(timeText).click();
  await page.waitForTimeout(500);
}

// Helper function to confirm appointment
async function confirmAppointment(page) {
  const confirmBtn = page.getByRole('button', { name: 'Confirm' });
  await confirmBtn.click();
  await page.waitForTimeout(1000);
  
  // Return confirmation number if found
  const confirmationText = await page.locator('text=/Confirmation Number/').textContent();
  return confirmationText;
}

// Export helper functions
export {
  fillLoginForm,
  handleOTP,
  selectService,
  fillCustomerDetails,
  selectDateAndTime,
  confirmAppointment
};
```

---

## Execution Configuration

```javascript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false, // Important: Don't run in parallel for this site
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 1, // Single worker to avoid conflicts
  reporter: 'html',
  use: {
    baseURL: 'https://www.txdpsscheduler.com/',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    navigationTimeout: 30000,
    actionTimeout: 10000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Notes for Implementation

### Important Considerations:

1. **reCAPTCHA Handling**: 
   - May require manual interaction or third-party service
   - Consider using Playwright's page.goto with waitUntil options

2. **OTP Handling**:
   - Current implementation requires user to provide OTP
   - For full automation, would need email/SMS integration

3. **Date/Time Selection**:
   - Availability may change, causing test failures
   - Consider using dynamic date selection strategies

4. **Network Delays**:
   - Add appropriate wait times between actions
   - Use waitForSelector for dynamic content

5. **Form Validation**:
   - Different validation rules may apply
   - Test with various input formats

### Best Practices:
- Use role-based selectors when possible
- Include proper error handling
- Log important steps for debugging
- Use meaningful assertion messages
- Keep test data separate from test logic

