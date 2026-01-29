"""
Texas DPS Appointment Monitor - Playwright Version
Main checker module for monitoring appointment availability
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeout
from utils.notifier import EmailNotifier
from utils.logger import setup_logger
from utils.otp_handler import OTPHandler

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = setup_logger(__name__)


class DPSAppointmentChecker:
    """
    Main class for checking DPS appointment availability using Playwright
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the checker with configuration
        
        Args:
            config: Optional configuration dictionary. If not provided, reads from environment.
        """
        self.config = config or self._load_config_from_env()
        self.base_url = "https://www.txdpsscheduler.com"
        self.notifier = EmailNotifier(self.config)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    def _load_config_from_env(self) -> Dict:
        """Load configuration from environment variables"""
        return {
            # Personal Information
            'first_name': os.getenv('FIRST_NAME', ''),
            'last_name': os.getenv('LAST_NAME', ''),
            'dob': os.getenv('DOB', ''),
            'ssn_last4': os.getenv('SSN_LAST4', ''),
            'phone': os.getenv('PHONE', ''),
            'email': os.getenv('EMAIL', ''),
            'zip_code': os.getenv('ZIP_CODE', '76201'),
            
            # Notification Settings
            'notify_email': os.getenv('NOTIFY_EMAIL', os.getenv('EMAIL', '')),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            
            # Search Settings
            'location_preference': os.getenv('LOCATION_PREFERENCE', 'Denton'),
            'max_distance_miles': int(os.getenv('MAX_DISTANCE_MILES', '20')),
            
            # Browser Settings
            'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
            'screenshot_on_error': os.getenv('SCREENSHOT_ON_ERROR', 'true').lower() == 'true',
        }
    
    async def setup_browser(self):
        """Setup Playwright browser instance"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.config['headless'],
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            self.page = await context.new_page()
            logger.info("Browser setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {str(e)}")
            raise
    
    async def navigate_to_scheduler(self) -> bool:
        """Navigate to the appointment scheduler"""
        try:
            logger.info(f"Navigating to {self.base_url}")
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            
            # Click English button
            await self.page.wait_for_selector("button:has-text('ENGLISH')", timeout=10000)
            await self.page.click("button:has-text('ENGLISH')")
            logger.info("Selected English language")
            
            await self.page.wait_for_load_state('networkidle')
            return True
            
        except PlaywrightTimeout:
            logger.error("Timeout while navigating to scheduler")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('navigation_timeout')
            return False
        except Exception as e:
            logger.error(f"Error navigating to scheduler: {str(e)}")
            return False
    
    async def fill_login_form(self) -> bool:
        """Fill in the login form with user information"""
        try:
            logger.info("Filling login form")
            
            # First, wait for the page to settle
            await asyncio.sleep(3)
            
            # Save a screenshot to see what we're working with
            await self._save_screenshot('form_before_fill')
            
            # Wait for form to be visible - check for any inputs
            logger.info("Waiting for input fields...")
            await self.page.wait_for_selector("input", timeout=30000)
            await asyncio.sleep(2)
            
            # STEP 1: Get initial form fields and fill First, Last, DOB, SSN BEFORE selecting email
            logger.info("Step 1: Filling initial form fields (First Name, Last Name, DOB, SSN Last 4)...")
            
            # Wait longer to ensure all fields are loaded
            await asyncio.sleep(2)
            
            inputs = await self.page.query_selector_all("input")
            logger.info(f"Found {len(inputs)} input fields initially")
            
            # Log ALL fields found to understand the form structure
            for idx, input_field in enumerate(inputs):
                placeholder = await input_field.get_attribute("placeholder")
                input_type = await input_field.get_attribute("type")
                input_id = await input_field.get_attribute("id")
                
                # Try to find the label for this field
                label_text = ""
                if input_id:
                    label = await self.page.query_selector(f"label[for='{input_id}']")
                    if label:
                        label_text = await label.text_content()
                
                logger.info(f"Initial Input {idx}: type={input_type}, label='{label_text}', placeholder='{placeholder}'")
            
            filled_count = 0
            
            # First pass: fill First, Last, DOB, SSN
            for input_field in inputs:
                placeholder = await input_field.get_attribute("placeholder") or ""
                input_id = await input_field.get_attribute("id") or ""
                input_name = await input_field.get_attribute("name") or ""
                input_type = await input_field.get_attribute("type") or ""
                
                # Skip radio buttons, checkboxes, and other non-form-field inputs
                if input_type in ["radio", "checkbox", "hidden"]:
                    continue
                
                # Get associated label if exists
                label_text = ""
                if input_id:
                    label = await self.page.query_selector(f"label[for='{input_id}']")
                    if label:
                        label_text = await label.text_content()
                
                label_lower = label_text.lower()
                placeholder_lower = placeholder.lower()
                name_lower = input_name.lower()
                
                logger.info(f"Initial field: label='{label_text}', placeholder='{placeholder}'")
                
                # Check if field is already filled
                current_value = await input_field.input_value()
                if current_value and current_value.strip():
                    logger.info(f"Field '{label_text}' already filled with: {current_value}")
                    continue
                
                # Determine what to fill based on field matching
                value_to_fill = None
                field_name = None
                
                # Check for SSN first (before Last Name) since it contains "last"
                if 'last four' in label_lower or 'last 4' in label_lower or 'ssn' in label_lower:
                    value_to_fill = self.config.get('ssn_last4', '')
                    field_name = 'SSN Last 4'
                elif 'first' in label_lower or 'first' in name_lower:
                    value_to_fill = self.config.get('first_name', '')
                    field_name = 'First Name'
                elif 'last' in label_lower or 'last' in name_lower:
                    value_to_fill = self.config.get('last_name', '')
                    field_name = 'Last Name'
                elif ('date' in label_lower or 'birth' in label_lower or 'dob' in label_lower or 
                      'mm/dd/yyyy' in placeholder_lower):
                    value_to_fill = self.config.get('dob', '')
                    field_name = 'Date of Birth'
                
                # Fill the field if we determined a value
                if value_to_fill:
                    try:
                        await input_field.click()
                        await asyncio.sleep(0.3)
                        await input_field.fill("")
                        await asyncio.sleep(0.2)
                        await input_field.type(value_to_fill, delay=30)
                        logger.info(f"[OK] Filled {field_name}: {value_to_fill}")
                        filled_count += 1
                    except Exception as e:
                        logger.warning(f"Error filling {field_name}: {e}")
            
            logger.info(f"Successfully filled {filled_count} initial fields")
            await asyncio.sleep(1)
            
            # STEP 2: Now select Email radio button (this changes form to show Email fields instead of DOB/SSN)
            logger.info("Step 2: Selecting Email option for contact method...")
            try:
                # Wait for the email radio to be in the DOM
                await self.page.wait_for_selector("input[type='radio'][value='email']", timeout=10000)
                
                # Find the email radio button by its value attribute
                email_radio = await self.page.query_selector("input[type='radio'][value='email']")
                
                if email_radio:
                    # Check if it's checked using aria-checked attribute
                    aria_checked = await email_radio.get_attribute("aria-checked")
                    logger.info(f"Email radio aria-checked: {aria_checked}")
                    
                    if aria_checked == "false":
                        # Click the radio to show email fields - use JavaScript click
                        try:
                            # Try using JavaScript click first
                            await self.page.evaluate("el => el.click()", email_radio)
                            logger.info("[OK] Clicked Email radio button via JavaScript")
                            await asyncio.sleep(2)  # Wait for form to update and show email fields
                        except Exception as js_error:
                            logger.warning(f"JavaScript click failed: {js_error}, trying Playwright click...")
                            try:
                                await email_radio.click(force=True, timeout=5000)
                                logger.info("[OK] Clicked Email radio button via Playwright")
                                await asyncio.sleep(2)
                            except Exception as pw_error:
                                logger.warning(f"Playwright click also failed: {pw_error}")
                    else:
                        logger.info("Email option already selected")
                else:
                    logger.warning("Could not find email radio button")
                    
            except Exception as e:
                logger.warning(f"Error selecting email radio: {e}")
            
            # STEP 3: Get fresh set of input fields after Email selection (should now show Email fields)
            logger.info("Step 3: Filling email fields after radio selection...")
            inputs = await self.page.query_selector_all("input")
            logger.info(f"Found {len(inputs)} input fields after email selection")
            
            # Log all input fields to see what's now available
            for idx, input_field in enumerate(inputs):
                placeholder = await input_field.get_attribute("placeholder")
                input_type = await input_field.get_attribute("type")
                input_id = await input_field.get_attribute("id")
                
                # Try to find the label for this field
                label_text = ""
                if input_id:
                    label = await self.page.query_selector(f"label[for='{input_id}']")
                    if label:
                        label_text = await label.text_content()
                
                logger.debug(f"Input {idx}: type={input_type}, label='{label_text}', placeholder='{placeholder}'")
            
            # Second pass: fill Email and Verify Email (these only appear after email radio is selected)
            for input_field in inputs:
                placeholder = await input_field.get_attribute("placeholder") or ""
                input_id = await input_field.get_attribute("id") or ""
                input_type = await input_field.get_attribute("type") or ""
                
                # Skip radio buttons, checkboxes, and other non-form-field inputs
                if input_type in ["radio", "checkbox", "hidden", "number", "tel"]:
                    continue
                
                # Get associated label if exists
                label_text = ""
                if input_id:
                    label = await self.page.query_selector(f"label[for='{input_id}']")
                    if label:
                        label_text = await label.text_content()
                
                label_lower = label_text.lower()
                
                logger.info(f"Email field check: label='{label_text}'")
                
                # Check if field is already filled
                current_value = await input_field.input_value()
                if current_value and current_value.strip():
                    logger.info(f"Field '{label_text}' already filled with: {current_value}")
                    continue
                
                # Only fill email fields here (these appear AFTER email radio is selected)
                value_to_fill = None
                field_name = None
                
                if 'email' in label_lower and 'verify' not in label_lower:
                    value_to_fill = self.config.get('email', '')
                    field_name = 'Email'
                elif 'verify' in label_lower and 'email' in label_lower:
                    value_to_fill = self.config.get('email', '')
                    field_name = 'Verify Email'
                
                # Fill the field if we determined a value
                if value_to_fill:
                    try:
                        await input_field.click()
                        await asyncio.sleep(0.3)
                        await input_field.fill("")
                        await asyncio.sleep(0.2)
                        await input_field.type(value_to_fill, delay=30)
                        logger.info(f"[OK] Filled {field_name}: {value_to_fill}")
                        filled_count += 1
                    except Exception as e:
                        logger.warning(f"Error filling {field_name}: {e}")
            
            logger.info(f"Total fields filled: {filled_count}")
            await asyncio.sleep(1)
            
            # Save screenshot before submitting
            await self._save_screenshot('form_before_submit')
            logger.info("Step 4: Looking for LOG ON button...")
            submit_clicked = False
            
            buttons = await self.page.query_selector_all("button")
            logger.info(f"Found {len(buttons)} buttons on page:")
            
            for idx, btn in enumerate(buttons):
                btn_text = await btn.text_content()
                logger.info(f"  Button {idx}: text='{btn_text}'")
            
            # Find the LOG ON button specifically
            for btn in buttons:
                btn_text = await btn.text_content()
                if btn_text and 'log on' in btn_text.lower():
                    try:
                        # Try JavaScript click first
                        try:
                            await self.page.evaluate("el => el.click()", btn)
                            logger.info(f"[OK] Clicked LOG ON button via JavaScript")
                            submit_clicked = True
                            break
                        except Exception as js_error:
                            logger.debug(f"JavaScript click failed: {js_error}")
                            # Fallback to Playwright click with force
                            await btn.click(force=True, timeout=5000)
                            logger.info(f"[OK] Clicked LOG ON button via Playwright")
                            submit_clicked = True
                            break
                    except Exception as e:
                        logger.warning(f"Error clicking LOG ON button: {e}")
            
            if not submit_clicked:
                logger.warning("Could not find LOG ON button - trying any submit-like button")
                for btn in buttons:
                    btn_text = await btn.text_content()
                    if btn_text:
                        btn_text_lower = btn_text.lower().strip()
                        if any(keyword in btn_text_lower for keyword in ['submit', 'continue', 'next', 'ok', 'accept']):
                            try:
                                await self.page.evaluate("el => el.click()", btn)
                                logger.info(f"[OK] Clicked button: {btn_text.strip()}")
                                submit_clicked = True
                                break
                            except Exception as e:
                                logger.warning(f"Error clicking button: {e}")
            
            if not submit_clicked:
                logger.warning("Could not find and click submit button")
            
            # Save screenshot after form submission attempt
            await self._save_screenshot('form_after_submit')
            
            # Wait briefly for page to respond and load OTP page if required
            logger.info("Waiting for page to load after form submission...")
            try:
                await asyncio.sleep(3)  # Give page time to load
                # Try to get current URL to see where we are
                current_url = self.page.url
                logger.info(f"Current URL after LOG ON: {current_url}")
                
                # Try to wait for load state
                await self.page.wait_for_load_state('networkidle', timeout=5000)
            except PlaywrightTimeout:
                logger.info("Page did not reach networkidle - continuing anyway")
                await asyncio.sleep(2)
            
            return True
            
        except PlaywrightTimeout as e:
            logger.error(f"Timeout while filling login form: {str(e)}")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('login_form_timeout')
            return False
        except Exception as e:
            logger.error(f"Error filling login form: {str(e)}")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('login_form_error')
            return False
    
    async def handle_otp_verification(self) -> bool:
        """
        Handle OTP verification by reading from email and filling the form
        
        Returns:
            True if OTP was successfully verified or not required, False otherwise
        """
        try:
            logger.info("Checking for OTP verification requirement...")
            await asyncio.sleep(2)
            
            # Get current page info
            current_url = self.page.url
            logger.info(f"Current URL: {current_url}")
            
            # Save screenshot to see current state
            await self._save_screenshot('otp_check')
            
            # Wait a bit more for page to fully load - OTP field might appear after form submission
            logger.info("Waiting for potential OTP field to appear...")
            try:
                await self.page.wait_for_load_state('networkidle', timeout=8000)
            except PlaywrightTimeout:
                logger.info("Page still loading, continuing...")
            
            await asyncio.sleep(1)
            
            # List all input fields to see what's available
            inputs = await self.page.query_selector_all("input")
            logger.info(f"Found {len(inputs)} input fields on page")
            for idx, inp in enumerate(inputs):
                inp_type = await inp.get_attribute("type")
                inp_id = await inp.get_attribute("id")
                inp_placeholder = await inp.get_attribute("placeholder")
                logger.info(f"  Input {idx}: type='{inp_type}', id='{inp_id}', placeholder='{inp_placeholder}'")
            
            # Check if OTP field exists on page - look for common patterns
            otp_selectors = [
                "input[type='text'][placeholder*='pass']",
                "input[type='text'][placeholder*='code']", 
                "input[id*='otp']",
                "input[id*='passcode']",
                "input[placeholder*='passcode']",
                "input[placeholder*='code']",
                "input[type='text']",  # Any text input as fallback
            ]
            
            otp_field = None
            for selector in otp_selectors:
                otp_field = await self.page.query_selector(selector)
                if otp_field:
                    logger.info(f"Found OTP field with selector: {selector}")
                    break
            
            if not otp_field:
                logger.info("No OTP field found - proceeding without OTP")
                return True
            
            logger.info("OTP verification required - reading OTP from email...")
            
            try:
                # Initialize OTP handler
                otp_handler = OTPHandler(
                    email_address=self.config.get('email', ''),
                    smtp_password=self.config.get('smtp_password', '')
                )
                
                # Get OTP from email (wait up to 120 seconds)
                otp_code = await otp_handler.get_otp_from_email(timeout=120, check_interval=5)
                
                if not otp_code:
                    logger.error("Could not retrieve OTP from email")
                    return False
                
                logger.info(f"[OK] OTP retrieved: {otp_code}")
                
                # Fill OTP field
                await otp_field.click()
                await asyncio.sleep(0.3)
                await otp_field.fill("")
                await asyncio.sleep(0.2)
                await otp_field.type(otp_code, delay=50)
                
                logger.info(f"[OK] Filled OTP field: {otp_code}")
                
                # Save screenshot before clicking verify
                await self._save_screenshot('otp_before_verify')
                
                # Click Verify button
                verify_button = await self.page.query_selector("button:has-text('VERIFY'), button:has-text('Verify')")
                if verify_button:
                    await verify_button.click()
                    logger.info("[OK] Clicked VERIFY button")
                else:
                    # Try to find verify button by other means
                    buttons = await self.page.query_selector_all("button")
                    for btn in buttons:
                        btn_text = await btn.text_content()
                        if btn_text and 'verify' in btn_text.lower():
                            await btn.click()
                            logger.info(f"[OK] Clicked button: {btn_text.strip()}")
                            break
                
                # Wait for verification to complete
                await asyncio.sleep(2)
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=10000)
                except PlaywrightTimeout:
                    logger.info("Page did not reach networkidle after OTP - continuing")
                
                logger.info("[OK] OTP verification completed")
                return True
                
            except Exception as otp_error:
                logger.error(f"Error during OTP verification: {str(otp_error)}")
                return False
            
        except Exception as e:
            logger.error(f"Error handling OTP verification: {str(e)}")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('otp_error')
            return False
    
    
    async def select_appointment_type(self) -> bool:
        """Select 'New Appointment' and service type"""
        try:
            # First, let's see what buttons are available
            buttons = await self.page.query_selector_all("button")
            logger.info(f"Found {len(buttons)} buttons on page:")
            for idx, btn in enumerate(buttons):
                btn_text = await btn.text_content()
                logger.info(f"  Button {idx}: '{btn_text}'")
            
            # Wait for page to load
            await asyncio.sleep(1)
            
            # Try to find and click "New Appointment" button
            new_appt_clicked = False
            for btn in buttons:
                btn_text = await btn.text_content()
                if btn_text and 'new' in btn_text.lower() and 'appointment' in btn_text.lower():
                    try:
                        await btn.click()
                        logger.info(f"Clicked 'New Appointment' button")
                        new_appt_clicked = True
                        break
                    except Exception as e:
                        logger.warning(f"Error clicking button: {e}")
            
            if not new_appt_clicked:
                logger.error("Could not find and click 'New Appointment' button")
                return False
            
            await asyncio.sleep(2)
            
            # Wait for service type options to appear
            buttons = await self.page.query_selector_all("button")
            logger.info(f"Found {len(buttons)} buttons after New Appointment:")
            
            # Try to find and click service type button
            service_clicked = False
            for btn in buttons:
                btn_text = await btn.text_content()
                if btn_text and 'apply' in btn_text.lower() and 'texas' in btn_text.lower():
                    try:
                        await btn.click()
                        logger.info(f"Clicked service type button: '{btn_text.strip()}'")
                        service_clicked = True
                        break
                    except Exception as e:
                        logger.warning(f"Error clicking service button: {e}")
            
            if not service_clicked:
                # Try a more generic approach
                logger.info("Could not find 'Apply for first time Texas DL/PERMIT' - trying any service button")
                for idx, btn in enumerate(buttons):
                    btn_text = await btn.text_content() or ""
                    if len(btn_text) > 10 and 'dl' in btn_text.lower():  # Looks like a service option
                        try:
                            await btn.click()
                            logger.info(f"Clicked service button {idx}: '{btn_text.strip()}'")
                            service_clicked = True
                            break
                        except Exception as e:
                            logger.warning(f"Error clicking service button: {e}")
            
            if not service_clicked:
                logger.error("Could not find service type button")
                return False
            
            await asyncio.sleep(2)
            return True
            
        except PlaywrightTimeout:
            logger.error("Timeout while selecting appointment type")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('appointment_type_timeout')
            return False
        except Exception as e:
            logger.error(f"Error selecting appointment type: {str(e)}")
            return False
    
    async def search_location(self) -> bool:
        """Enter ZIP code and search for locations"""
        try:
            # Fill ZIP code
            await self.page.wait_for_selector("input[placeholder='#####'], input[id*='zip']", timeout=10000)
            await self.page.fill("input[placeholder='#####'], input[id*='zip']", self.config['zip_code'])
            logger.info(f"Entered ZIP code: {self.config['zip_code']}")
            
            # Click Next
            await self.page.click("button:has-text('NEXT')")
            logger.info("Searching for locations...")
            
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            return True
            
        except PlaywrightTimeout:
            logger.error("Timeout while searching location")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('location_search_timeout')
            return False
        except Exception as e:
            logger.error(f"Error searching location: {str(e)}")
            return False
    
    async def get_available_appointments(self) -> Optional[Dict]:
        """
        Extract available appointment information from the page
        
        Returns:
            Dictionary with location and appointment details, or None if not found
        """
        try:
            logger.info("Waiting for appointment slots page to load...")
            await asyncio.sleep(3)
            
            # Take screenshot to see what we're working with
            await self._save_screenshot('slots_page')
            
            # Get page content
            page_text = await self.page.locator("body").text_content()
            page_content = await self.page.content()
            
            logger.info(f"Page content preview: {page_text[:200]}")
            
            # Look for any location name in the page (not just "Denton")
            # The page might show different location names
            location_found = None
            
            # Check if we have any recognizable location keywords
            location_keywords = ['denton', 'arlington', 'dallas', 'houston', 'austin', 'san antonio']
            for keyword in location_keywords:
                if keyword in page_text.lower():
                    location_found = keyword.title()
                    logger.info(f"Found location keyword: {location_found}")
                    break
            
            # If no specific location found, check if page has appointment slots at all
            if not location_found:
                # Check for any date patterns which indicate appointments exist
                import re
                date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
                dates = re.findall(date_pattern, page_content)
                
                if dates:
                    logger.info(f"Found appointment dates even without location name")
                    location_found = "Available Location"
                else:
                    logger.info("No location or appointments found on page")
                    return None
            
            logger.info(f"Location: {location_found}")
            
            # Look for all buttons and try to click Select
            buttons = await self.page.query_selector_all("button")
            logger.info(f"Found {len(buttons)} buttons on appointments page")
            
            # Try to find and click Select button for the first location
            select_clicked = False
            for btn in buttons:
                btn_text = await btn.text_content() or ""
                if "select" in btn_text.lower():
                    try:
                        await btn.click(timeout=5000)
                        logger.info("Clicked Select button for appointments")
                        await asyncio.sleep(2)
                        select_clicked = True
                        break
                    except Exception as e:
                        logger.debug(f"Could not click select button: {e}")
            
            # Extract date information from page
            import re
            date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
            dates = re.findall(date_pattern, page_content)
            unique_dates = list(set(dates))
            
            # Sort dates if possible
            try:
                from datetime import datetime as dt
                unique_dates = sorted(unique_dates, key=lambda x: dt.strptime(x, '%m/%d/%Y'))
            except:
                pass  # If sorting fails, just use them as-is
            
            if unique_dates:
                logger.info(f"Found {len(unique_dates)} available dates: {unique_dates[:5]}...")
                return {
                    'location': location_found or self.config['location_preference'],
                    'zip_code': self.config['zip_code'],
                    'next_available': unique_dates[0] if unique_dates else 'Unknown',
                    'available_dates': unique_dates[:15],
                    'total_slots': len(unique_dates),
                    'checked_at': datetime.now().isoformat()
                }
            else:
                logger.info("No date slots found on appointments page - appointments may not be available")
                return None
                
        except asyncio.TimeoutError as e:
            logger.warning(f"Timeout getting available appointments: {str(e)}")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('get_appointments_timeout')
            return None
        except Exception as e:
            logger.error(f"Error getting available appointments: {str(e)}")
            if self.config['screenshot_on_error']:
                await self._save_screenshot('get_appointments_error')
            return None
    
    async def _save_screenshot(self, name: str):
        """Save screenshot for debugging"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshots/{name}_{timestamp}.png"
            os.makedirs('screenshots', exist_ok=True)
            await self.page.screenshot(path=filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {str(e)}")
    
    async def check_appointments(self) -> Optional[Dict]:
        """
        Main method to check for appointments
        
        Returns:
            Dictionary with appointment information if found, None otherwise
        """
        try:
            logger.info("="*60)
            logger.info("Starting DPS Appointment Check")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
            logger.info("="*60)
            
            await self.setup_browser()
            
            # Navigate to scheduler
            if not await self.navigate_to_scheduler():
                logger.error("Failed to navigate to scheduler")
                return None
            
            # Fill login form
            if not await self.fill_login_form():
                logger.error("Failed to fill login form")
                return None
            
            # Handle OTP verification if required
            if not await self.handle_otp_verification():
                logger.error("OTP verification failed")
                return None
            
            # Select appointment type
            if not await self.select_appointment_type():
                logger.error("Failed to select appointment type")
                return None
            
            # Search for location
            if not await self.search_location():
                logger.error("Failed to search location")
                return None
            
            # Get available appointments
            appointments = await self.get_available_appointments()
            
            if appointments:
                logger.info("Appointments found!")
                logger.info(f"Location: {appointments['location']}")
                logger.info(f"Next available: {appointments['next_available']}")
                logger.info(f"Total slots: {appointments['total_slots']}")
                
                # Send notification
                await self.notifier.send_notification(
                    subject=f"DPS Appointments Available in {appointments['location']}!",
                    appointments=appointments
                )
                
                # Save to file
                self._save_results(appointments)
                
                return appointments
            else:
                logger.info("No appointments currently available")
                return None
                
        except Exception as e:
            logger.error(f"Error during appointment check: {str(e)}")
            if self.config['screenshot_on_error'] and self.page:
                await self._save_screenshot('check_error')
            return None
        finally:
            await self.cleanup()
    
    def _save_results(self, appointments: Dict):
        """Save appointment results to JSON file"""
        try:
            os.makedirs('results', exist_ok=True)
            filename = f"results/appointments_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(appointments, f, indent=2)
            
            logger.info(f"Results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
    
    async def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self.page:
                try:
                    await self.page.close()
                except Exception as e:
                    logger.debug(f"Error closing page: {e}")
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.debug(f"Error closing browser: {e}")
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.debug(f"Error during cleanup: {str(e)}")


async def main():
    """Main entry point"""
    checker = DPSAppointmentChecker()
    try:
        result = await checker.check_appointments()
        
        if result:
            logger.info("Check completed - Appointments found!")
            return 0
        else:
            logger.info("Check completed - No appointments available")
            return 1
    finally:
        # Ensure cleanup happens
        await checker.cleanup()


if __name__ == "__main__":
    # Suppress ResourceWarning about unclosed pipes in asyncio
    import warnings
    import sys
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    # Suppress asyncio-related warnings
    if sys.platform == 'win32':
        # On Windows, suppress the proactor transport warnings
        warnings.filterwarnings("ignore", message=".*unclosed transport.*")
    
    exit_code = asyncio.run(main())
    exit(exit_code)