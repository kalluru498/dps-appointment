"""
Refactored Booking Engine for the DPS Agent Booking System.
Wraps the existing Playwright automation and adds auto-booking capability,
dynamic service selection, and status callback hooks.

FIXED VERSION: Improved email field detection and filling on Customer Details page (Page 6)
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
        # Debug trace screenshots:
        # - screenshot_trace: capture screenshots throughout workflow
        # - screenshot_on_emit: attach a screenshot for each status update
        self.screenshot_trace = bool(self.config.get("screenshot_trace", True))
        self.screenshot_on_emit = bool(self.config.get("screenshot_on_emit", True))
        self._screenshot_counter = 0

    def _sanitize_name(self, value: str, max_len: int = 64) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", (value or "").strip().lower())
        cleaned = cleaned.strip("_")
        if not cleaned:
            cleaned = "step"
        return cleaned[:max_len]

    async def _emit(self, level: str, message: str, screenshot_path: Optional[str] = None):
        """Emit a status update through the callback."""
        if self.screenshot_trace and self.screenshot_on_emit and screenshot_path is None and self.page:
            screenshot_path = await self._save_screenshot(
                f"trace_{level}_{self._sanitize_name(message)}"
            )
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
            self._screenshot_counter += 1
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            safe_name = self._sanitize_name(name, max_len=80)
            os.makedirs('screenshots', exist_ok=True)
            filepath = f"screenshots/{self._screenshot_counter:04d}_{safe_name}_{timestamp}.png"
            if self.page:
                await self.page.screenshot(path=filepath) # type: ignore
            return filepath
        except Exception as e:
            logger.debug(f"Screenshot error: {e}")
            return None

    async def _capture_step(self, name: str) -> Optional[str]:
        """Capture a debug screenshot for a specific step/action."""
        if not self.screenshot_trace or not self.page:
            return None
        return await self._save_screenshot(name)

    # ─── Step 1: Navigate to Scheduler ───────────────────────────

    async def navigate_to_scheduler(self) -> bool:
        """Navigate to the DPS scheduler and select English."""
        try:
            if not self.page:
                return False
            await self._emit("info", f"Navigating to {self.base_url}...")
            await self._capture_step("navigate_before_goto")
            await self.page.goto(self.base_url, wait_until='networkidle', timeout=30000) # type: ignore
            await self._capture_step("navigate_after_goto")
            
            await self.page.wait_for_selector("button:has-text('ENGLISH')", timeout=10000) # type: ignore
            await self._capture_step("navigate_before_click_english")
            await self.page.click("button:has-text('ENGLISH')") # type: ignore
            await self._capture_step("navigate_after_click_english")
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
            await self._capture_step("login_before_form_fill")
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
            await self._capture_step("login_after_form_fill")

            # ── Click LOG ON ──
            await self._capture_step("login_before_submit")
            await self._click_button_by_text(['log on', 'submit', 'continue', 'next'])  # type: ignore
            await self._emit("info", "Submitted login form")  # type: ignore
            await self._capture_step("login_after_submit")

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
            await self._capture_step("otp_phase_start")
            
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
            await self._capture_step("otp_page_detected")
            
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

            await self._capture_step("otp_before_fill")
            await otp_field.click()
            await asyncio.sleep(0.3)
            await otp_field.fill("")
            await otp_field.type(otp_code, delay=50)
            await self._capture_step("otp_after_fill")

            # Click verify
            await self._capture_step("otp_before_click_verify")
            await self._click_button_by_text(['verify'])
            await self._capture_step("otp_after_click_verify")
            await asyncio.sleep(2)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except PlaywrightTimeout:
                pass

            await self._emit("success", "OTP verification completed")
            await self._capture_step("otp_completed")
            return True

        except Exception as e:
            ss = await self._save_screenshot('otp_error')
            await self._emit("error", f"OTP error: {str(e)}", ss) # type: ignore
            return False

    # ─── Step 4: Select Service Type (DYNAMIC) ───────────────────

    async def _dismiss_blocking_dialogs(self, page: Page) -> bool:
        """Dismiss transient overlays/popups that can block clicks."""
        dismissed = False
        patterns = [
            re.compile(r"^ok$", re.I),
            re.compile(r"^okay$", re.I),
            re.compile(r"^close$", re.I),
            re.compile(r"^got it$", re.I),
            re.compile(r"^continue$", re.I),
            re.compile(r"^accept$", re.I),
            re.compile(r"^i understand$", re.I),
            re.compile(r"^proceed$", re.I),
        ]

        for pattern in patterns:
            loc = None
            try:
                loc = page.get_by_role("button", name=pattern)
                count = await loc.count()
            except Exception:
                count = 0
            if loc is None:
                continue
            for i in range(min(count, 4)):
                btn = loc.nth(i)
                try:
                    if not await btn.is_visible():
                        continue
                    btxt = (await btn.text_content() or "popup_button").strip()
                    await self._capture_step(f"click_before_{self._sanitize_name(btxt)}")
                    await btn.click(timeout=2000)
                    await asyncio.sleep(0.3)
                    await self._capture_step(f"click_after_{self._sanitize_name(btxt)}")
                    dismissed = True
                except Exception:
                    continue

        try:
            dialog = page.locator("[role='dialog'], .modal, .MuiDialog-root, .cdk-overlay-container").first
            if await dialog.count() > 0 and await dialog.is_visible():
                ok_btn = dialog.locator("button").filter(has_text=re.compile(r"ok|close|continue|accept", re.I)).first
                if await ok_btn.count() > 0 and await ok_btn.is_visible():
                    btxt = (await ok_btn.text_content() or "popup_ok").strip()
                    await self._capture_step(f"click_before_{self._sanitize_name(btxt)}")
                    await ok_btn.click(timeout=2000)
                    await asyncio.sleep(0.3)
                    await self._capture_step(f"click_after_{self._sanitize_name(btxt)}")
                    dismissed = True
        except Exception:
            pass

        if dismissed:
            await self._emit("info", "Dismissed blocking popup/dialog")
        return dismissed

    async def _is_on_service_selection_step(self, page: Page) -> bool:
        """Detect Service Selection page using stable heading/category text."""
        markers = [
            re.compile(r"Please select the option that best describes the service you need", re.I),
            re.compile(r"Service Selection", re.I),
            re.compile(r"Driver License Services|Identification Card Services|Commercial Driver License Services", re.I),
        ]
        for marker in markers:
            try:
                loc = page.get_by_text(marker).first
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _is_on_customer_details_step(self, page: Page) -> bool:
        """Detect Page 6 (Customer Details / ZIP input) where service is already selected."""
        try:
            zip_selector = "input[placeholder='#####'], input[id*='zip'], #zipCode"
            zip_loc = page.locator(zip_selector).first
            if await zip_loc.count() > 0 and await zip_loc.is_visible():
                return True
        except Exception:
            pass

        markers = [
            re.compile(r"Please enter your contact information", re.I),
            re.compile(r"Customer Details", re.I),
            re.compile(r"ZIP Code|City/Town", re.I),
        ]
        for marker in markers:
            try:
                loc = page.get_by_text(marker).first
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def select_service_type(self, button_keywords: Optional[List[str]] = None) -> bool:
        """
        Select 'New Appointment' and the appropriate service type.
        """
        page = self.page
        if not page:
            return False

        try:
            await self._emit("info", "Phase: Service Selection - Locating appointment buttons...")
            await asyncio.sleep(2)
            await self._dismiss_blocking_dialogs(page)

            # Force the expected service unless explicitly overridden.
            if not button_keywords:
                button_keywords = [
                    "apply for first time texas dl/permit",
                    "first time texas dl",
                    "dl/permit",
                    "dl permit",
                ]

            # Appointment Options -> Service Selection
            if not await self._is_on_service_selection_step(page):
                moved_to_service = False
                for _ in range(3):
                    await self._dismiss_blocking_dialogs(page)
                    clicked = False
                    try:
                        new_appt = page.get_by_role("button", name=re.compile(r"^New Appointment$", re.I)).first
                        if await new_appt.count() > 0 and await new_appt.is_visible():
                            await self._capture_step("service_before_click_new_appointment")
                            await new_appt.click(timeout=5000)
                            await self._capture_step("service_after_click_new_appointment")
                            await self._emit("info", "Clicked 'New Appointment'")
                            clicked = True
                    except Exception:
                        pass

                    if not clicked:
                        clicked = await self._click_button_by_text(["new appointment"])

                    await asyncio.sleep(1.5)
                    await self._dismiss_blocking_dialogs(page)
                    if await self._is_on_service_selection_step(page):
                        moved_to_service = True
                        break

                if not moved_to_service and not await self._is_on_service_selection_step(page):
                    ss = await self._save_screenshot("service_transition_blocked")
                    await self._emit("error", "Could not reach Service Selection page after clicking New Appointment", ss)
                    return False

            await asyncio.sleep(1)
            await self._dismiss_blocking_dialogs(page)

            service_clicked = False
            preferred_patterns = [
                re.compile(r"Apply for first time Texas DL/Permit", re.I),
            ]

            for pattern in preferred_patterns:
                try:
                    btn = page.get_by_role("button", name=pattern).first
                    if await btn.count() > 0 and await btn.is_visible():
                        txt = (await btn.text_content() or "service_button").strip()
                        await self._capture_step(f"service_before_click_{self._sanitize_name(txt)}")
                        await btn.click(timeout=5000)
                        await self._capture_step(f"service_after_click_{self._sanitize_name(txt)}")
                        await self._dismiss_blocking_dialogs(page)
                        # In "Appointment Exists" flow, OK may move us directly to Customer Details.
                        if await self._is_on_customer_details_step(page):
                            await self._emit("success", "Selected service and moved to Customer Details")
                            return True
                        await self._emit("success", f"Selected service: {txt}")
                        service_clicked = True
                        break
                except Exception:
                    continue

            if not service_clicked:
                buttons = await page.query_selector_all("button") # type: ignore
                for btn in buttons:
                    text = (await btn.text_content() or "").lower()
                    if any(kw in text for kw in button_keywords):
                        await btn.click()
                        await self._dismiss_blocking_dialogs(page)
                        if await self._is_on_customer_details_step(page):
                            await self._emit("success", "Selected service and moved to Customer Details")
                            return True
                        await self._emit("success", f"Selected service: {text.strip()}")
                        service_clicked = True
                        break

            if not service_clicked:
                buttons = await page.query_selector_all("button") # type: ignore
                for btn in buttons:
                    text = (await btn.text_content() or "").lower()
                    if (
                        len(text) > 10
                        and "previous" not in text
                        and ("dl" in text or "license" in text or "permit" in text)
                    ):
                        await btn.click()
                        await self._dismiss_blocking_dialogs(page)
                        if await self._is_on_customer_details_step(page):
                            await self._emit("success", "Selected service and moved to Customer Details")
                            return True
                        await self._emit("warning", f"Fallback service selection: {text.strip()}")
                        service_clicked = True
                        break

            if not service_clicked:
                # Some flows land on an intermediate step with only Previous/Next.
                # Try one forward navigation and re-check known states.
                if not await self._is_on_customer_details_step(page):
                    advanced = await self._click_next(page)
                    if advanced:
                        await asyncio.sleep(1.5)
                        await self._dismiss_blocking_dialogs(page)
                        if await self._is_on_customer_details_step(page):
                            await self._emit("info", "Advanced with Next to Customer Details step.")
                            return True
                        if await self._is_on_service_selection_step(page):
                            # Retry one quick service click pass after transition.
                            buttons = await page.query_selector_all("button") # type: ignore
                            for btn in buttons:
                                text = (await btn.text_content() or "").lower()
                                if any(kw in text for kw in button_keywords):
                                    await btn.click()
                                    await self._emit("success", f"Selected service: {text.strip()}")
                                    service_clicked = True
                                    break

            if not service_clicked:
                if await self._is_on_customer_details_step(page):
                    await self._emit(
                        "info",
                        "Service options not visible, but Customer Details step is already active. Continuing."
                    )
                    return True
                try:
                    buttons = await page.query_selector_all("button") # type: ignore
                    names: List[str] = []
                    for btn in buttons[:25]:
                        t = (await btn.text_content() or "").strip()
                        if t:
                            names.append(t)
                    if names:
                        await self._emit("warning", f"Visible buttons at failure: {', '.join(names[:12])}")
                except Exception:
                    pass
                ss = await self._save_screenshot("service_not_found")
                await self._emit("error", "Could not find service type button", ss)
                return False

            await asyncio.sleep(2)
            return True

        except Exception as e:
            ss = await self._save_screenshot('service_error')
            await self._emit("error", f"Service selection error: {str(e)}", ss)
            return False

    # ─── Step 5: Search Location ─────────────────────────────────

    async def search_location(self) -> bool:
        """Fill Cell Phone + Email + Verify Email, then ZIP, then click Next to go to Select Location."""
        page = self.page
        if not page:
            return False

        try:
            await self._emit("info", "Phase: Location Search - Filling required contact fields...")
            await self._fill_customer_details_required_fields(page)

            await self._emit("info", "Entering ZIP Code...")
            await self._capture_step("location_before_zip_fill")

            zip_selector = "input[placeholder='#####'], input[id*='zip' i], #zipCode, input[name*='zip' i]"
            await page.wait_for_selector(zip_selector, timeout=10000)

            zip_value = str(self.config.get("zip_code") or "76201").strip()
            zip_digits = re.sub(r"\D", "", zip_value)[:5] or "76201"

            await page.fill(zip_selector, "")
            await page.type(zip_selector, zip_digits, delay=40)

            zip_input = page.locator(zip_selector).first
            try:
                await zip_input.evaluate(
                    "el => {"
                    "el.dispatchEvent(new Event('input', { bubbles:true }));"
                    "el.dispatchEvent(new Event('change', { bubbles:true }));"
                    "el.blur();"
                    "}"
                )
            except Exception:
                pass

            await page.keyboard.press("Tab")
            await asyncio.sleep(0.2)

            await self._capture_step("location_after_zip_fill")

            # ✅ Next button: tolerate "NEXT →"
            next_btn = page.get_by_role("button", name=re.compile(r"\bNext\b", re.I)).first
            await next_btn.wait_for(state="visible", timeout=10000)

            # Wait briefly for enablement after validation
            for _ in range(10):
                try:
                    aria_disabled = (await next_btn.get_attribute("aria-disabled")) or ""
                except Exception:
                    aria_disabled = ""
                enabled = False
                try:
                    enabled = await next_btn.is_enabled()
                except Exception:
                    enabled = False

                if enabled and aria_disabled.lower() != "true":
                    break
                await asyncio.sleep(0.3)

            # Click Next (with fallback)
            try:
                await self._capture_step("location_before_click_next")
                await next_btn.click(timeout=5000)
                await self._capture_step("location_after_click_next")
            except Exception:
                await self._emit("warning", "Normal Next click failed; using JS click fallback")
                await page.evaluate("(btn) => btn.click()", await next_btn.element_handle())

            await self._emit("info", "Searching for nearby locations...")
            await page.wait_for_load_state("networkidle", timeout=15000)

            try:
                await page.get_by_text(re.compile(r"Select Location|available dates", re.I)).first.wait_for(
                    state="visible", timeout=10000
                )
            except Exception:
                pass

            await self._emit("success", "Location search complete")
            return True

        except PlaywrightTimeout:
            ss = await self._save_screenshot("location_timeout")
            await self._emit("error", "Timeout searching for locations", ss)
            return False
        except Exception as e:
            await self._emit("error", f"Location search error: {str(e)}")
            return False


    
      
    async def _fill_customer_details_required_fields(self, page: Page) -> None:
        """
            Customer Details (Page 6):
            Fill ONLY: Cell Phone, Email, Verify Email.
            Do NOT scan all inputs (can hit ZIP). Keep it deterministic.
        """
        try:
            email_val = str(self.config.get("email") or "").strip()
            if not email_val:
                await self._emit("warning", "No email configured; cannot fill Email/Verify Email")
                return

            cell_val_raw = str(self.config.get("cell_phone") or self.config.get("phone") or "").strip()
            cell_digits = re.sub(r"\D", "", cell_val_raw)

            await self._emit("info", "Filling Customer Details: Cell Phone, Email, Verify Email...")
            await asyncio.sleep(0.8)

            async def _fill(loc, value: str, label: str) -> bool:
                try:
                    if await loc.count() == 0:
                        return False
                    if not await loc.first.is_visible(timeout=1500):
                        return False

                    el = loc.first
                    # Skip if already filled with something real
                    cur = (await el.input_value()).strip()
                    if cur and "###" not in cur and cur != "#####":
                        await self._emit("info", f"{label} already filled")
                        return True

                    await el.click()
                    await asyncio.sleep(0.15)
                    await el.fill("")
                    await asyncio.sleep(0.1)
                    await el.type(value, delay=35)

                    # Trigger reactive validation
                    try:
                        await el.evaluate(
                            "el => {"
                            "el.dispatchEvent(new Event('input', { bubbles:true }));"
                            "el.dispatchEvent(new Event('change', { bubbles:true }));"
                            "el.blur();"
                            "}"
                        )
                    except Exception:
                        pass

                    await page.keyboard.press("Tab")
                    await asyncio.sleep(0.15)
                    await self._emit("success", f"✓ Filled {label}")
                    return True
                except Exception as e:
                    await self._emit("debug", f"Fill {label} failed: {e}")
                    return False

            # --- Cell Phone (by label / role / id/name) ---
            if cell_digits:
                cell_locators = [
                    page.get_by_label(re.compile(r"Cell\s*Phone|Mobile", re.I)),
                    page.get_by_role("textbox", name=re.compile(r"Cell\s*Phone|Mobile", re.I)),
                    page.locator("input[id*='cell' i], input[name*='cell' i], input[id*='mobile' i], input[name*='mobile' i]"),
                ]
                cell_ok = False
                for loc in cell_locators:
                    if await _fill(loc, cell_digits, "Cell Phone"):
                        cell_ok = True
                        break
                if not cell_ok:
                    await self._emit("warning", "Could not fill Cell Phone (label/id not found)")
            else:
                await self._emit("warning", "No cell phone configured; Next may remain disabled if Cell Phone is required")

            # --- Email ---
            email_locators = [
                page.get_by_label(re.compile(r"^\s*Email\s*$|Email\s*Address", re.I)),
                page.get_by_role("textbox", name=re.compile(r"^\s*Email\s*$|Email\s*Address", re.I)),
                page.locator("input[type='email'], input[id='email'], input[name='email'], input[id*='email' i]:not([id*='verify' i]):not([id*='confirm' i])"),
            ]
            email_ok = False
            for loc in email_locators:
                if await _fill(loc, email_val, "Email"):
                    email_ok = True
                    break
            if not email_ok:
                await self._emit("warning", "Could not fill Email field (label/id not found)")

            # --- Verify Email ---
            verify_locators = [
                page.get_by_label(re.compile(r"Verify\s*Email|Confirm\s*Email|Re-?enter\s*Email", re.I)),
                page.get_by_role("textbox", name=re.compile(r"Verify\s*Email|Confirm\s*Email|Re-?enter\s*Email", re.I)),
                page.locator("input[id*='verify' i][id*='email' i], input[name*='verify' i][name*='email' i], input[id*='confirm' i][id*='email' i]"),
            ]
            verify_ok = False
            for loc in verify_locators:
                if await _fill(loc, email_val, "Verify Email"):
                    verify_ok = True
                    break
            if not verify_ok:
                await self._emit("warning", "Could not fill Verify Email field (label/id not found)")

            await self._capture_step("customer_details_after_contact_fill")

        except Exception as e:
            await self._emit("error", f"Customer Details fill error: {e}")
            await self._save_screenshot("customer_details_fill_error")

    # ─── Step 6: Get Available Appointments ──────────────────────

    async def _extract_date_cards(self, page: Page) -> List[str]:
        """
        Extract date candidates from clickable date cards on Page 7.
        This avoids polluting candidates with 'Next Available Date' from location cards.
        """
        dates: List[str] = []
        seen = set()
        date_pattern = re.compile(r"\b(\d{1,2}/\d{1,2}(?:/\d{4})?)\b")

        # Prefer buttons in date-selection area.
        locators = [
            page.locator("button, [role='button']").filter(
                has_text=re.compile(r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday", re.I)
            ),
            page.locator("button, [role='button']").filter(has_text=re.compile(r"\d{1,2}/\d{1,2}", re.I)),
        ]

        for loc in locators:
            try:
                count = await loc.count()
            except Exception:
                count = 0
            for i in range(min(count, 30)):
                try:
                    el = loc.nth(i)
                    if not await el.is_visible():
                        continue
                    text = (await el.text_content() or "").strip()
                    if not text or "Next Available Date" in text:
                        continue
                    matches = date_pattern.findall(text)
                    for match in matches:
                        normalized = match.strip()
                        if len(normalized.split("/")) == 2:
                            continue
                        if normalized not in seen:
                            seen.add(normalized)
                            dates.append(normalized)
                except Exception:
                    continue

        # Fallback: parse any full dates from page HTML.
        if not dates:
            try:
                page_content = await page.content()
                for d in re.findall(r"\d{1,2}/\d{1,2}/\d{4}", page_content):
                    if d not in seen:
                        seen.add(d)
                        dates.append(d)
            except Exception:
                pass

        try:
            dates.sort(key=lambda x: datetime.strptime(x, "%m/%d/%Y"))
        except Exception:
            pass
        return dates

    async def get_available_appointments(self) -> Optional[Dict]:
        """Extract available appointment information from the Select Location page."""
        page = self.page
        if not page:
            return None
        try:
            await self._emit("info", "Checking available appointment slots...")
            await asyncio.sleep(3)

            page_text = await page.locator("body").text_content() or ""  # type: ignore

            # Find location
            location_found = None
            for kw in ['denton', 'arlington', 'dallas', 'houston', 'austin', 'fort worth',
                        'san antonio', 'plano', 'mckinney', 'lewisville', 'carrollton']:
                if kw in page_text.lower():
                    location_found = kw.title()
                    break

            # Pull dates from clickable date cards first.
            date_candidates = await self._extract_date_cards(page)
            if not date_candidates and not location_found:
                await self._emit("info", "No appointments currently available")
                return None

            if date_candidates:
                result = {
                    'location': location_found or self.config.get('location_preference', 'Unknown'),
                    'zip_code': self.config.get('zip_code', '76201'),
                    'next_available': date_candidates[0],
                    'available_dates': date_candidates[:15],
                    'total_slots': len(date_candidates),
                    'checked_at': datetime.now().isoformat()
                }
                await self._emit("success",
                    f"Found {len(date_candidates)} slots! Next: {date_candidates[0]} at {result['location']}")
                return result

            await self._emit("info", "No appointment dates found on page")
            return None

        except Exception as e:
            ss = await self._save_screenshot('appointments_error')
            await self._emit("error", f"Error getting appointments: {str(e)}", ss)
            return None

    # ─── Step 7: Auto-Book a Slot ────────────────────────────────

    def _build_candidate_dates(self, target_date: Optional[str], available_dates: Optional[List[str]]) -> List[str]:
        """Build ordered list of dates to try: target first, then rest of available_dates."""
        candidates = []
        if target_date:
            candidates.append(target_date)
        if available_dates:
            for d in available_dates:
                if d and d not in candidates:
                    candidates.append(d)
        return candidates[:20]  # cap to avoid runaway

    def _date_variants(self, date_text: str) -> List[str]:
        """Build UI date variants (MM/DD/YYYY and MM/DD forms)."""
        variants: List[str] = []
        if date_text:
            variants.append(date_text.strip())
        try:
            dt = datetime.strptime(date_text.strip(), "%m/%d/%Y")
            variants.extend(
                [
                    f"{dt.month}/{dt.day}/{dt.year}",
                    f"{dt.month:02d}/{dt.day:02d}/{dt.year}",
                    f"{dt.month}/{dt.day}",
                    f"{dt.month:02d}/{dt.day:02d}",
                ]
            )
        except Exception:
            pass

        seen = set()
        unique = []
        for value in variants:
            value = value.strip()
            if value and value not in seen:
                seen.add(value)
                unique.append(value)
        return unique

    async def _is_on_time_or_confirm_step(self, page: Page) -> bool:
        """Detect whether we are on a step where 'Previous' should exist."""
        markers = [
            re.compile(r"Select Time|available times|choose a time", re.I),
            re.compile(r"\bConfirm\b|appointment details", re.I),
        ]
        for marker in markers:
            try:
                loc = page.get_by_text(marker).first
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _is_on_time_step(self, page: Page) -> bool:
        markers = [
            re.compile(r"Select Time|available times|choose a time", re.I),
        ]
        for marker in markers:
            try:
                loc = page.get_by_text(marker).first
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _is_on_confirm_step(self, page: Page) -> bool:
        markers = [
            re.compile(r"Confirm Appointment|Time Remaining to Confirm|\bConfirm\b", re.I),
        ]
        for marker in markers:
            try:
                loc = page.get_by_text(marker).first
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _click_date_on_page(self, page: Page, d: str) -> bool:
        """Try to click a date on the current page (date carousel). Prefer buttons to avoid clicking 'Next Available Date' in location cards."""
        variants = self._date_variants(d)
        if not variants:
            return False

        date_regex = re.compile("|".join(re.escape(v) for v in variants), re.I)

        async def _try_click(locator) -> bool:
            try:
                count = await locator.count()
            except Exception:
                return False
            for i in range(min(count, 20)):
                candidate = locator.nth(i)
                try:
                    if not await candidate.is_visible():
                        continue
                    parent_txt = await candidate.evaluate(
                        "el => el.closest('button, [role=button], div, li')?.textContent || ''"
                    )
                    if "Next Available Date" in (parent_txt or ""):
                        continue
                    ctext = (await candidate.text_content() or "date").strip()
                    await self._capture_step(f"click_before_{self._sanitize_name(ctext)}")
                    await candidate.scroll_into_view_if_needed(timeout=3000)
                    await candidate.click(timeout=5000)
                    await self._capture_step(f"click_after_{self._sanitize_name(ctext)}")
                    return True
                except Exception:
                    continue
            return False

        # Strategy 0: Prefer date-looking buttons.
        btns = page.locator("button, [role='button']").filter(has_text=date_regex)
        if await _try_click(btns):
            return True

        # Strategy 1: Scope under date-selection section.
        try:
            section = page.locator("[class*='date'], [class*='carousel'], section, div").filter(
                has_text=re.compile(r"Select from the available dates", re.I)
            ).first
            if await section.count() > 0:
                in_section = section.locator("button, [role='button'], div, span").filter(has_text=date_regex)
                if await _try_click(in_section):
                    return True
        except Exception:
            pass

        # Strategy 2: Try exact variants.
        for variant in variants:
            if await _try_click(page.get_by_text(variant, exact=True)):
                return True

        # Strategy 3: weekday + date card text.
        try:
            dt = datetime.strptime(d, "%m/%d/%Y")
            weekday = dt.strftime("%A")
            weekday_loc = page.locator("button, [role='button'], div, span").filter(
                has_text=re.compile(re.escape(weekday), re.I)
            ).filter(has_text=date_regex)
            if await _try_click(weekday_loc):
                return True
        except Exception:
            pass

        return False

    async def _find_and_click_time_slot(self, page: Page) -> bool:
        """Find and click a time slot on Select Time page. Reference: getByText(':40 AM')."""
        # Wait for Select Time page specifically (avoid matching "Select from the available dates" on date page)
        try:
            await page.get_by_text(re.compile(r"Select Time|Select from the available times", re.I)).first.wait_for(
                state="visible", timeout=10000
            )
        except Exception:
            pass
        await asyncio.sleep(2)

        # Reference: getByText(':40 AM') - partial time match; format "11:40 AM"
        time_regex = re.compile(r"\d{1,2}\s*:\s*\d{2}\s*(AM|PM)", re.I)
        time_regex_loose = re.compile(r"\d{1,2}:\d{2}\s*[AP]M", re.I)
        time_partial = re.compile(r":\d{2}\s*[AP]M", re.I)  # :40 AM per doc

        # Prefer buttons (time slots are often buttons)
        strategies = [
            page.locator("button, [role='button']").filter(has_text=time_regex_loose),
            page.get_by_text(time_partial),
            page.get_by_text(time_regex),
            page.get_by_text(time_regex_loose),
            page.locator("button").filter(has_text=time_regex_loose),
            page.locator("[role='button']").filter(has_text=time_regex_loose),
            page.locator("div, span, button").filter(has_text=time_regex_loose),
        ]
        for time_loc in strategies:
            try:
                cnt = await time_loc.count()
                for i in range(min(cnt, 15)):
                    el = time_loc.nth(i)
                    try:
                        if not await el.is_visible():
                            continue
                        t_text = (await el.text_content() or "").strip()
                        if not t_text or len(t_text) > 30:  # avoid full sentence/label
                            continue
                        # Skip if this is date text (e.g. "3/23/2026") not time
                        if re.search(r"\d{1,2}/\d{1,2}/\d{4}", t_text):
                            continue
                        if re.search(r"\d{1,2}\s*:\s*\d{2}", t_text) and (
                            "AM" in t_text.upper() or "PM" in t_text.upper()
                        ):
                            await self._capture_step(f"click_before_time_{self._sanitize_name(t_text)}")
                            await el.scroll_into_view_if_needed(timeout=3000)
                            await asyncio.sleep(0.3)
                            await el.click(timeout=5000)
                            await self._capture_step(f"click_after_time_{self._sanitize_name(t_text)}")
                            await self._emit("success", f"Selected time slot: {t_text}")
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
        # No time found: save screenshot for debugging
        await self._save_screenshot("booking_no_time_found")
        return False
    async def _click_previous(self, page: Page) -> bool:
        """Click Previous to go back one step. Returns True if clicked."""
        candidates = [
            page.get_by_role("button", name=re.compile(r"(?:<-)?\s*previous\b", re.I)),
            page.locator("button, [role='button'], a").filter(has_text=re.compile(r"\bprevious\b", re.I)),
        ]
        for loc in candidates:
            try:
                count = await loc.count()
            except Exception:
                count = 0
            for i in range(min(count, 5)):
                btn = loc.nth(i)
                try:
                    if not await btn.is_visible():
                        continue
                    btxt = (await btn.text_content() or "previous").strip()
                    await self._capture_step(f"click_before_{self._sanitize_name(btxt)}")
                    await btn.scroll_into_view_if_needed(timeout=3000)
                    await btn.click(timeout=5000)
                    await self._capture_step(f"click_after_{self._sanitize_name(btxt)}")
                    return True
                except Exception:
                    continue
        return await self._click_button_by_text(["previous", "<- previous"])
    async def _click_next(self, page: Page) -> bool:
        """Click Next. Reference: getByRole('button', { name: 'Next' })."""
        candidates = [
            page.get_by_role("button", name=re.compile(r"^Next$", re.I)),
            page.locator("button").filter(has_text=re.compile(r"^Next$", re.I)),
        ]
        for loc in candidates:
            try:
                count = await loc.count()
            except Exception:
                count = 0
            for i in range(min(count, 5)):
                btn = loc.nth(i)
                try:
                    if not await btn.is_visible() or not await btn.is_enabled():
                        continue
                    btxt = (await btn.text_content() or "next").strip()
                    await self._capture_step(f"click_before_{self._sanitize_name(btxt)}")
                    await btn.scroll_into_view_if_needed(timeout=3000)
                    await btn.click(timeout=5000)
                    await self._capture_step(f"click_after_{self._sanitize_name(btxt)}")
                    return True
                except Exception:
                    continue
        return await self._click_button_by_text(["next"])

    async def auto_book_slot(
        self, target_date: Optional[str] = None, available_dates: Optional[List[str]] = None
    ) -> bool:
        """
        Auto-book per TX DPS reference flow:
        Page 7 Select Location: location already selected -> select BEST date from carousel ->
        Next (enabled after date) -> Page 8 Select Time -> select time slot ->
        Next (enabled after time) -> Page 9 Confirm -> Confirm.
        If no time for this date, Previous and try next date.
        """
        page = self.page
        if not page:
            return False

        candidate_dates = self._build_candidate_dates(target_date, available_dates)
        if not candidate_dates:
            await self._emit("warning", "No dates to try for booking")
            return False

        try:
            await self._emit("info", "Phase: Booking - Selecting slot and confirming...")
            await self._emit("info", f"Selecting best date first, then trying up to {len(candidate_dates)} date(s).")
            await asyncio.sleep(1)

            for date_index, d in enumerate(candidate_dates):
                is_best = date_index == 0 and target_date and d == target_date
                await self._emit("info", f"Trying date {date_index + 1}/{len(candidate_dates)}: {d}" + (" (best slot)" if is_best else "") + "...")

                if date_index > 0:
                    await self._emit("info", "Going back to select another date...")
                    if await self._is_on_time_or_confirm_step(page):
                        if await self._click_previous(page):
                            await asyncio.sleep(2)
                        else:
                            await self._emit("warning", "Could not click Previous to try another date")
                    else:
                        await self._emit("info", "Already on date selection step; no Previous click needed")

                # 1) Select date on Page 7 (date carousel; reference: getByText('Thursday3/12/'))
                date_clicked = await self._click_date_on_page(page, d)
                if not date_clicked:
                    if await self._is_on_time_or_confirm_step(page):
                        await self._emit("info", f"Date {d} not clickable here; trying Previous and retrying once...")
                        if await self._click_previous(page):
                            await asyncio.sleep(2)
                            date_clicked = await self._click_date_on_page(page, d)
                    if not date_clicked:
                        await self._emit("warning", f"Could not click date {d}, skipping")
                        continue
                await self._emit("info", f"Selected date: {d}")
                await asyncio.sleep(2)

                # 2) Next -> Page 8 Select Time (reference: Next enabled after date selected)
                if not await self._click_next(page):
                    await self._emit("warning", f"Could not click Next after selecting date {d}, trying next date")
                    continue
                await self._emit("info", "Clicked Next (after date)")
                await asyncio.sleep(3.5)
                if not await self._is_on_time_step(page):
                    await self._emit("warning", "Did not reach Select Time step after clicking Next")
                    continue

                # 3) Select time slot (reference: getByText(':40 AM'))
                time_slot_clicked = await self._find_and_click_time_slot(page)
                if not time_slot_clicked:
                    await self._emit("warning", f"No time slots for {d}; will try another date")
                    continue

                await asyncio.sleep(1)

                # 4) Next -> Page 9 Confirm (reference: Next enabled after time selected)
                if not await self._click_next(page):
                    await self._emit("warning", f"Could not click Next after selecting time for {d}")
                    continue
                await self._emit("info", "Clicked Next (after time)")
                await asyncio.sleep(2)
                if not await self._is_on_confirm_step(page):
                    await self._emit("warning", "Did not reach Confirm step after selecting time")
                    continue

                # 5) Confirm (reference: getByRole('button', { name: 'Confirm' }))
                confirm_btn = page.get_by_role("button", name="Confirm").first
                if await confirm_btn.count() > 0 and await confirm_btn.is_enabled():
                    await confirm_btn.click()
                    await self._emit("info", "Clicked Confirm")
                else:
                    await self._click_button_by_text(["confirm", "book", "schedule", "submit"])
                await asyncio.sleep(3)

                ss = await self._save_screenshot("booking_confirmation")
                final_content = await page.content()
                if any(
                    k in final_content.lower()
                    for k in [
                        "confirmation number",
                        "your appointment has been confirmed",
                        "appointment has been confirmed",
                        "has been confirmed",
                    ]
                ):
                    await self._emit("success", "Booking CONFIRMED! Verification details visible in screenshot.", ss)
                    return True
                await self._emit("warning", "Confirm clicked but confirmation screen not detected. Check screenshot.", ss)
                return False

            await self._emit("warning", "Tried all dates but no time slots were available for any of them.")
            await self._save_screenshot("booking_no_time_any_date")
            return False

        except Exception as e:
            ss = await self._save_screenshot("booking_error")
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
                # Pass all available dates so auto_book_slot can retry with another date if no time slots
                booked = await self.auto_book_slot(best_date, appointments.get('available_dates'))
                appointments['booking_confirmed'] = booked

                if booked:
                    await self._emit("success", f"Appointment BOOKED for {best_date}!")
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
                    name = self._sanitize_name(text or "button")
                    await self._capture_step(f"click_before_{name}")
                    await self._emit("info", f"Clicking button: {text[:80]}")
                    try:
                        await page.evaluate("el => el.click()", btn) # type: ignore
                    except:
                        await btn.click(force=True, timeout=5000) # type: ignore
                    await self._capture_step(f"click_after_{name}")
                    await self._emit("info", f"Clicked button: {text[:80]}")
                    return True
                except:
                    continue
        return False