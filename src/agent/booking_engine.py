"""
Refactored Booking Engine for the DPS Agent Booking System.
Wraps the existing Playwright automation and adds auto-booking capability,
dynamic service selection, and status callback hooks.
"""

import os
import json
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, List, Callable, Awaitable
from dotenv import load_dotenv  # type: ignore
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout  # type: ignore

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.notifier import EmailNotifier  # type: ignore
from utils.logger import setup_logger  # type: ignore
from utils.otp_handler import OTPHandler  # type: ignore

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

logger = setup_logger(__name__)

# Type alias for status callbacks
StatusCallback = Callable[[str, str, Optional[str]], Awaitable[None]]


class BookingEngine:
    """
    Autonomous booking engine that can:
    - Navigate the DPS scheduler site
    - Fill forms with user data
    - Handle OTP verification
    - Dynamically select service type based on AI engine output
    - Auto-select the best time slot and confirm booking
    - Report progress via status callbacks
    """

    def __init__(self, config: Dict, on_status: Optional[StatusCallback] = None):
        """
        Initialize the booking engine.

        Args:
            config: User configuration dictionary.
            on_status: Async callback for status updates — fn(level, message, screenshot_path)
        """
        self.config = config
        self.base_url = "https://www.txdpsscheduler.com"
        self.on_status = on_status
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def _emit(self, level: str, message: str, screenshot_path: Optional[str] = None):
        """Emit a status update through the callback."""
        logger.info(f"[{level.upper()}] {message}")
        if self.on_status:
            try:
                await self.on_status(level, message, screenshot_path)  # type: ignore
            except Exception as e:
                logger.warning(f"Status callback error: {e}")

    # ─── Browser Lifecycle ───────────────────────────────────────

    async def setup_browser(self):
        """Launch Playwright browser."""
        await self._emit("info", "Launching browser...")
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(  # type: ignore
            headless=self.config.get("headless", True),
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        self.context = await self.browser.new_context(  # type: ignore
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()  # type: ignore
        await self._emit("success", "Browser launched successfully")

    async def cleanup(self):
        """Close browser and all resources."""
        try:
            # On Windows, closing resources can sometimes trigger 'closed pipe' errors from asyncio
            if self.page:
                try: 
                    await self.page.close() # type: ignore
                except: 
                    pass
                self.page = None

            if self.context:
                try: 
                    await self.context.close() # type: ignore
                except: 
                    pass
                self.context = None

            if self.browser:
                try: 
                    await self.browser.close() # type: ignore
                except: 
                    pass
                self.browser = None

            if self._playwright:
                try: 
                    await self._playwright.stop() # type: ignore
                except: 
                    pass
                self._playwright = None

            await self._emit("info", "Browser cleaned up")
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")

    # ─── Screenshot Helper ───────────────────────────────────────

    async def _save_screenshot(self, name: str) -> Optional[str]:
        """Save a screenshot and return the file path."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.makedirs('screenshots', exist_ok=True)
            filepath = f"screenshots/{name}_{timestamp}.png"
            if self.page:
                await self.page.screenshot(path=filepath) # type: ignore
            return filepath
        except Exception as e:
            logger.debug(f"Screenshot error: {e}")
            return None

    # ─── Step 1: Navigate to Scheduler ───────────────────────────

    async def navigate_to_scheduler(self) -> bool:
        """Navigate to the DPS scheduler and select English."""
        try:
            if not self.page:
                return False
            await self._emit("info", f"Navigating to {self.base_url}...")
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000) # type: ignore
            
            await self.page.wait_for_selector("button:has-text('ENGLISH')", timeout=10000) # type: ignore
            await self.page.click("button:has-text('ENGLISH')") # type: ignore
            await self._emit("success", "Selected English language")
            
            await self.page.wait_for_load_state('networkidle') # type: ignore
            return True
        except PlaywrightTimeout:
            ss = await self._save_screenshot('navigation_timeout')
            await self._emit("error", "Timeout navigating to scheduler", ss)
            return False
        except Exception as e:
            await self._emit("error", f"Navigation error: {str(e)}")
            return False

    # ─── Step 2: Fill Login Form ─────────────────────────────────

    async def fill_login_form(self) -> bool:
        """Fill the login form with user personal information."""
        page = self.page
        if not page:
            return False
            
        try:
            await self._emit("info", "Filling login form...")
            await self._emit("info", "Phase: Login - Waiting for form to load...")
            await asyncio.sleep(3)
            
            await page.wait_for_selector("input", timeout=30000) # type: ignore
            await asyncio.sleep(2)

            # ── Fill initial fields (First, Last, DOB, SSN) ──
            inputs = await page.query_selector_all("input")  # type: ignore
            filled_count: int = 0

            for input_field in inputs:
                input_type = await input_field.get_attribute("type") or ""
                if input_type in ["radio", "checkbox", "hidden"]:
                    continue

                input_id = await input_field.get_attribute("id") or ""
                input_name = await input_field.get_attribute("name") or ""
                placeholder = await input_field.get_attribute("placeholder") or ""
                label_text = ""
                if input_id:
                    label = await page.query_selector(f"label[for='{input_id}']") # type: ignore
                    if label:
                        label_text = await label.text_content() or ""

                ll = label_text.lower()
                pl = placeholder.lower()
                nl = input_name.lower()

                current = await input_field.input_value()
                if current and current.strip():
                    continue

                value, field_name = None, None
                if 'last four' in ll or 'last 4' in ll or 'ssn' in ll:
                    value, field_name = self.config.get('ssn_last4', ''), 'SSN Last 4'
                elif 'first' in ll or 'first' in nl:
                    value, field_name = self.config.get('first_name', ''), 'First Name'
                elif 'last' in ll or 'last' in nl:
                    value, field_name = self.config.get('last_name', ''), 'Last Name'
                elif 'date' in ll or 'birth' in ll or 'dob' in ll or 'mm/dd/yyyy' in pl:
                    value, field_name = self.config.get('dob', ''), 'Date of Birth'

                if value:
                    try:
                        await input_field.click()
                        await asyncio.sleep(0.3)
                        await input_field.fill("")
                        await asyncio.sleep(0.2)
                        await input_field.type(value, delay=30)
                        filled_count += 1  # type: ignore
                        await self._emit("info", f"Filled {field_name}")
                    except Exception as e:
                        await self._emit("warning", f"Error filling {field_name}: {e}")

            # ── Select Email radio button ──
            try:
                await page.wait_for_selector("input[type='radio'][value='email']", timeout=10000)
                email_radio = await page.query_selector("input[type='radio'][value='email']")
                if email_radio:
                    aria = await email_radio.get_attribute("aria-checked")
                    if aria == "false":
                        await page.evaluate("el => el.click()", email_radio)
                        await self._emit("info", "Selected Email contact method")
                        await asyncio.sleep(2)
            except Exception as e:
                await self._emit("warning", f"Email radio selection: {e}") # type: ignore

            # ── Fill Email fields (appear after radio selection) ──
            inputs = await page.query_selector_all("input") # type: ignore
            for input_field in inputs:
                input_type = await input_field.get_attribute("type") or ""
                if input_type in ["radio", "checkbox", "hidden", "number", "tel"]:
                    continue
                input_id = await input_field.get_attribute("id") or ""
                label_text = ""
                if input_id:
                    label = await page.query_selector(f"label[for='{input_id}']") # type: ignore
                    if label:
                        label_text = await label.text_content() or ""
                ll = label_text.lower() # type: ignore
                current = await input_field.input_value()
                if current and current.strip():
                    continue

                value, field_name = None, None
                if 'email' in ll and 'verify' not in ll:
                    value, field_name = self.config.get('email', ''), 'Email' # type: ignore
                elif 'verify' in ll and 'email' in ll:
                    value, field_name = self.config.get('email', ''), 'Verify Email' # type: ignore

                if value:
                    try:
                        await input_field.click()
                        await asyncio.sleep(0.3)
                        await input_field.fill("")
                        await asyncio.sleep(0.2)
                        await input_field.type(value, delay=30)
                        filled_count += 1  # type: ignore
                        await self._emit("info", f"Filled {field_name}") # type: ignore
                    except Exception as e:
                        await self._emit("warning", f"Error filling {field_name}: {e}") # type: ignore

            await self._emit("success", f"Login form filled ({filled_count} fields)") # type: ignore

            # ── Click LOG ON ──
            await self._click_button_by_text(['log on', 'submit', 'continue', 'next'])  # type: ignore
            await self._emit("info", "Submitted login form")  # type: ignore

            await asyncio.sleep(3)
            try:
                await page.wait_for_load_state('networkidle', timeout=5000) # type: ignore
            except PlaywrightTimeout:
                await asyncio.sleep(2)

            return True

        except PlaywrightTimeout:
            ss = await self._save_screenshot('login_timeout')
            await self._emit("error", "Timeout filling login form", ss) # type: ignore
            return False
        except Exception as e:
            ss = await self._save_screenshot('login_error')
            await self._emit("error", f"Login form error: {str(e)}", ss) # type: ignore
            return False

    # ─── Step 3: Handle OTP ──────────────────────────────────────

    async def handle_otp(self) -> bool:
        """Handle OTP verification by reading from email."""
        page = self.page
        if not page:
            return False
            
        try:
            await self._emit("info", "Phase: OTP - Checking for OTP verification page...")
            
            # Wait for either OTP screen or the next screen (Appointment Options)
            try:
                # Use a combined locator to wait for either state
                target = page.locator("text=/One Time Passcode Verification/i, button:has-text('New Appointment'), button:has-text('NEW APPOINTMENT')").first
                await target.wait_for(state='visible', timeout=15000)
            except:
                pass

            # Check if we are already on the next page (Appointment Options)
            if (await page.locator("button:has-text('New Appointment')").count() > 0) or \
               (await page.locator("button:has-text('NEW APPOINTMENT')").count() > 0):
                await self._emit("info", "Already on appointment options page — OTP skipped/passed")
                return True

            # If not on next page, check for OTP header
            header = page.locator("text=/One Time Passcode Verification/i")
            if await header.count() == 0:
                await self._emit("info", "No OTP page detected — proceeding")
                return True

            await self._emit("info", "OTP verification page detected")
            
            # Find the OTP input field
            otp_field = page.locator("input[type='text'], input:not([type='radio']):not([type='hidden'])").first
            
            if not await otp_field.is_visible(timeout=5000):
                await self._emit("warning", "OTP header found but input field not visible")
                return True

            await self._emit("info", "OTP verification required — reading email...")

            otp_handler = OTPHandler(
                email_address=self.config.get('email', ''),
                smtp_password=self.config.get('smtp_password', '')
            )

            otp_code = await otp_handler.get_otp_from_email(timeout=120, check_interval=5)

            if not otp_code:
                await self._emit("warning", "Could not retrieve OTP from email — waiting 30s for manual entry or bypass...")
                try:
                    # Check if we navigate away from OTP page anyway
                    await page.wait_for_selector("button:has-text('New Appointment'), button:has-text('NEW APPOINTMENT')", timeout=30000)
                    await self._emit("success", "Navigation detected — OTP resolved externally")
                    return True
                except:
                    ss = await self._save_screenshot('otp_failed')
                    await self._emit("error", "Could not retrieve OTP and no navigation detected", ss)
                    return False

            await self._emit("success", f"OTP retrieved: {otp_code}")

            await otp_field.click()
            await asyncio.sleep(0.3)
            await otp_field.fill("")
            await otp_field.type(otp_code, delay=50)

            # Click verify
            await self._click_button_by_text(['verify'])
            await asyncio.sleep(2)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except PlaywrightTimeout:
                pass

            await self._emit("success", "OTP verification completed")
            return True

        except Exception as e:
            ss = await self._save_screenshot('otp_error')
            await self._emit("error", f"OTP error: {str(e)}", ss) # type: ignore
            return False

    # ─── Step 4: Select Service Type (DYNAMIC) ───────────────────

    async def select_service_type(self, button_keywords: Optional[List[str]] = None) -> bool:
        """
        Select 'New Appointment' and the appropriate service type.

        Args:
            button_keywords: List of keywords to match against service buttons.
                           If None, defaults to 'apply' + 'texas' (first-time DL).
        """
        page = self.page
        if not page:
            return False
            
        try:
            await self._emit("info", "Phase: Service Selection - Locating appointment buttons...")
            await asyncio.sleep(2)
            
            if not button_keywords:
                button_keywords = ["apply", "first time", "texas dl"]

            # Click "New Appointment"
            try:
                await page.wait_for_selector("button", timeout=10000)
            except:
                pass
                
            buttons = await page.query_selector_all("button") # type: ignore
            new_appt_clicked = False
            for btn in buttons:
                text = (await btn.text_content() or "").lower()
                if 'new' in text and 'appointment' in text:
                    await btn.click()
                    await self._emit("info", "Clicked 'New Appointment'")
                    new_appt_clicked = True
                    break

            if not new_appt_clicked:
                # Try fallback for "New Appointment"
                await self._click_button_by_text(['new appointment', 'new'])
                new_appt_clicked = True # Assume success if _click_button_by_text returns

            await asyncio.sleep(2)

            # Click service type button using AI-determined keywords
            buttons = await page.query_selector_all("button") # type: ignore
            service_clicked = False

            for btn in buttons:
                text = (await btn.text_content() or "").lower()
                # Check if ANY of the keywords match
                if any(kw in text for kw in button_keywords):
                    await btn.click()
                    await self._emit("success", f"Selected service: {text.strip()}")
                    service_clicked = True
                    break

            if not service_clicked:
                # Fallback: try buttons that look like service options
                for btn in buttons:
                    text = (await btn.text_content() or "").lower()
                    if len(text) > 10 and ('dl' in text or 'license' in text or 'permit' in text):
                        await btn.click()
                        await self._emit("warning", f"Fallback service selection: {text.strip()}")
                        service_clicked = True
                        break

            if not service_clicked:
                await self._emit("error", "Could not find service type button")
                return False

            await asyncio.sleep(2)
            return True

        except Exception as e:
            ss = await self._save_screenshot('service_error')
            await self._emit("error", f"Service selection error: {str(e)}", ss)
            return False

    # ─── Step 5: Search Location ─────────────────────────────────

    async def search_location(self) -> bool:
        """Enter ZIP code and search for locations."""
        page = self.page
        if not page:
            return False
        try:
            await self._emit("info", "Phase: Location Search - Entering Zip Code...")
            
            zip_selector = "input[placeholder='#####'], input[id*='zip']"
            await page.wait_for_selector(zip_selector, timeout=10000) # type: ignore
            await page.fill(zip_selector, self.config.get('zip_code', '76201')) # type: ignore

            await page.click("button:has-text('NEXT')") # type: ignore
            await self._emit("info", "Searching for nearby locations...")
            
            await page.wait_for_load_state('networkidle', timeout=15000) # type: ignore
            await self._emit("success", "Location search complete")
            return True

        except PlaywrightTimeout:
            ss = await self._save_screenshot('location_timeout')
            await self._emit("error", "Timeout searching for locations", ss)
            return False
        except Exception as e:
            await self._emit("error", f"Location search error: {str(e)}")
            return False

    # ─── Step 6: Get Available Appointments ──────────────────────

    async def get_available_appointments(self) -> Optional[Dict]:
        """Extract available appointment information from the page."""
        page = self.page
        if not page:
            return None
        try:
            await self._emit("info", "Checking available appointment slots...")
            
            # Wait for content or "no slots" message to appear
            await asyncio.sleep(3)
            page_content = await page.content() # type: ignore
            page_text = await page.locator("body").text_content() # type: ignore

            # Find location
            location_found = None
            for kw in ['denton', 'arlington', 'dallas', 'houston', 'austin', 'fort worth',
                        'san antonio', 'plano', 'mckinney', 'lewisville', 'carrollton']:
                if kw in page_text.lower():
                    location_found = kw.title()
                    break

            import re
            date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
            dates = re.findall(date_pattern, page_content)
            unique_dates = list(set(dates))

            try:
                unique_dates.sort(key=lambda x: datetime.strptime(x, '%m/%d/%Y'))
            except:
                pass

            if not unique_dates and not location_found:
                await self._emit("info", "No appointments currently available")
                return None

            # Try clicking Select button
            buttons = await self.page.query_selector_all("button") # type: ignore
            for btn in buttons:
                text = (await btn.text_content() or "").lower()
                if "select" in text:
                    try:
                        await btn.click(timeout=5000)
                        await self._emit("info", "Selected first available location")
                        await asyncio.sleep(2)
                    except:
                        pass
                    break

            if unique_dates:
                result = {
                    'location': location_found or self.config.get('location_preference', 'Unknown'),
                    'zip_code': self.config.get('zip_code', '76201'),
                    'next_available': unique_dates[0],
                    'available_dates': unique_dates[:15],  # type: ignore
                    'total_slots': len(unique_dates),
                    'checked_at': datetime.now().isoformat()
                }
                await self._emit("success",
                    f"Found {len(unique_dates)} slots! Next: {unique_dates[0]} at {result['location']}")
                return result

            await self._emit("info", "No appointment dates found on page")
            return None

        except Exception as e:
            ss = await self._save_screenshot('appointments_error')
            await self._emit("error", f"Error getting appointments: {str(e)}", ss)
            return None

    # ─── Step 7: Auto-Book a Slot ────────────────────────────────

    async def auto_book_slot(self, target_date: Optional[str] = None) -> bool:
        """
        Attempt to auto-book the best available appointment slot.
        """
        page = self.page
        if not page:
            return False
            
        try:
            await self._emit("info", "Phase: Booking - Selecting slot and confirming...")

            # 1. Identify all available date buttons
            # Localize dates: they are often in grid or carousel items
            date_buttons = page.locator("button, div[role='button'], div.v-btn").filter(has_text=re.compile(r'\d{1,2}/\d{1,2}/\d{4}'))
            count = await date_buttons.count()
            await self._emit("info", f"Found {count} date buttons on page")

            candidate_dates = []
            if target_date:
                candidate_dates.append(target_date)
            
            # Fallback to other visible dates if primary fails
            for i in range(min(count, 3)):
                date_text = await date_buttons.nth(i).text_content()
                if date_text:
                    match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', date_text)
                    if match and match.group(0) not in candidate_dates:
                        candidate_dates.append(match.group(0))

            time_slot_clicked = False
            for d in candidate_dates:
                await self._emit("info", f"Trying to select date: {d}...")
                
                # Click the date button
                d_btn = page.locator(f"text='{d}'").first
                if await d_btn.count() > 0:
                    await d_btn.click()
                    await asyncio.sleep(2.5) # Wait for times to load
                    
                    # 2. Look for time slot buttons
                    # They might contain AM/PM or HH:MM
                    time_buttons = page.locator("button").filter(has_text=re.compile(r'(\d{1,2}:\d{2}|AM|PM)', re.IGNORECASE))
                    time_count = await time_buttons.count()
                    
                    if time_count > 0:
                        # Select the first available time slot
                        for t_idx in range(time_count):
                            t_btn = time_buttons.nth(t_idx)
                            t_text = (await t_btn.text_content() or "").strip()
                            
                            # Check if button is enabled
                            if await t_btn.is_enabled():
                                await t_btn.click()
                                await self._emit("success", f"Selected time slot: {t_text} for date {d}")
                                time_slot_clicked = True
                                break
                    
                    if time_slot_clicked:
                        break
                else:
                    await self._emit("warning", f"Date button {d} not clickable")

            if not time_slot_clicked:
                await self._emit("warning", "Could not find or select any specific time slots")
                # Attempt to proceed anyway as some pages auto-select or have a different layout
                await self._save_screenshot("booking_no_time_found")

            await asyncio.sleep(1)

            # 3. Click confirm/book/next button
            # Usually 'NEXT', 'SUBMIT', 'CONFIRM', or 'BOOK'
            await self._emit("info", "Attempting to click final confirmation button...")
            
            # Check if NEXT is enabled first
            next_btn = page.locator("button:has-text('NEXT'), button:has-text('CONTINUE'), button:has-text('SUBMIT')").first
            if await next_btn.count() > 0:
                if not await next_btn.is_enabled():
                    await self._emit("warning", "The 'NEXT' button is disabled (maybe time slot wasn't registered)")
                
                await next_btn.click(force=True)
                await self._emit("info", "Clicked validation button")
            else:
                await self._click_button_by_text(['confirm', 'book', 'schedule', 'submit', 'next', 'continue'])

            await asyncio.sleep(3)
            ss = await self._save_screenshot('booking_confirmation')
            
            # Final verification: Did we reach a confirmation screen?
            # Look for keywords like "Confirmation", "Success", "Appointment Number"
            final_content = await page.content()
            if any(k in final_content.lower() for k in ['confirmation', 'success', 'appointment number', 'id:', 'booked']):
                await self._emit("success", "🎉 Booking CONFIRMED! Verification details visible in screenshot.", ss)
                return True
            else:
                await self._emit("warning", "Attempted booking, but confirmation screen not detected. Check screenshot.", ss)
                return False

        except Exception as e:
            ss = await self._save_screenshot('booking_error')
            await self._emit("error", f"Auto-book error: {str(e)}", ss)
            return False

    # ─── Full Check & Book Flow ──────────────────────────────────

    async def run_check_and_book(self,
                                  button_keywords: Optional[List[str]] = None,
                                  auto_book: bool = True,
                                  slot_ranker=None) -> Optional[Dict]:
        """
        Run the full appointment check and optionally auto-book.

        Args:
            button_keywords: Keywords for service type button matching.
            auto_book: Whether to attempt auto-booking.
            slot_ranker: Optional function(dates, priority) -> ranked slots.

        Returns:
            Appointment dict if found, None otherwise.
        """
        try:
            await self._emit("info", "=" * 50)
            await self._emit("info", f"Starting DPS Appointment Check — {datetime.now().strftime('%I:%M:%S %p')}")

            await self.setup_browser()

            # Step 1: Navigate
            if not await self.navigate_to_scheduler():
                return None

            # Step 2: Login
            if not await self.fill_login_form():
                return None

            # Step 3: OTP
            if not await self.handle_otp():
                return None

            # Step 4: Service type
            if not await self.select_service_type(button_keywords):
                return None

            # Step 5: Location search
            if not await self.search_location():
                return None

            # Step 6: Get appointments
            appointments = await self.get_available_appointments()

            if not appointments:
                await self._emit("info", "No appointments available at this time")
                return None

            # Step 7: Auto-book if enabled
            if auto_book and appointments.get('available_dates'):
                best_date = appointments['available_dates'][0]

                # Use slot ranker if provided
                if slot_ranker:
                    priority = self.config.get('slot_priority', 'any')
                    ranked = slot_ranker(appointments['available_dates'], priority)
                    if ranked:
                        best_date = ranked[0]['date']
                        await self._emit("info",
                            f"AI ranked best slot: {best_date} (score: {ranked[0]['score']})")

                appointments['booking_attempted'] = True
                appointments['target_date'] = best_date
                booked = await self.auto_book_slot(best_date)
                appointments['booking_confirmed'] = booked

                if booked:
                    await self._emit("success", f"🎉 Appointment BOOKED for {best_date}!")
                else:
                    await self._emit("warning",
                        "Auto-booking could not confirm. Please book manually ASAP!")

            return appointments

        except Exception as e:
            ss = await self._save_screenshot('check_error')
            await self._emit("error", f"Check flow error: {str(e)}", ss)
            return None
        finally:
            await self.cleanup()

    # ─── Utility ─────────────────────────────────────────────────

    async def _click_button_by_text(self, keywords: List[str]) -> bool:
        """Find and click a button matching any of the given keywords."""
        page = self.page
        if not page:
            return False
        buttons = await page.query_selector_all("button") # type: ignore
        for btn in buttons:
            text = (await btn.text_content() or "").lower().strip()
            if any(kw in text for kw in keywords):
                try:
                    try:
                        await page.evaluate("el => el.click()", btn) # type: ignore
                    except:
                        await btn.click(force=True, timeout=5000) # type: ignore
                    return True
                except:
                    continue
        return False
