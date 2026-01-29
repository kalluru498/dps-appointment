#!/usr/bin/env python3
"""
Texas DPS Appointment Monitor
Checks for available appointments and sends notifications
"""

import os
import sys
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class DPSAppointmentChecker:
    def __init__(self):
        self.base_url = "https://www.txdpsscheduler.com"
        self.driver = None
        
        # Your information (from screenshots)
        self.first_name = os.getenv('FIRST_NAME', 'Naveen')
        self.last_name = os.getenv('LAST_NAME', 'Kumar')
        self.dob = os.getenv('DOB', '07/21/2000')
        self.ssn_last4 = os.getenv('SSN_LAST4', '')  # Set this in GitHub Secrets
        self.phone = os.getenv('PHONE', '(940) 977-2486')
        self.email = os.getenv('EMAIL', 'kaumarnaveen@gmail.com')
        self.zip_code = os.getenv('ZIP_CODE', '76201')
        
        # Notification settings
        self.notify_email = os.getenv('NOTIFY_EMAIL', self.email)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        
    def setup_driver(self):
        """Setup Chrome WebDriver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def send_notification(self, subject, message, available_dates=None):
        """Send email notification when appointments are found"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.notify_email
            
            # Create HTML message
            html = f"""
            <html>
              <body>
                <h2>🎉 Texas DPS Appointment Available!</h2>
                <p>{message}</p>
                
                {f'<h3>Available Dates:</h3><ul>{"".join([f"<li>{date}</li>" for date in available_dates])}</ul>' if available_dates else ''}
                
                <p><strong>Book now at:</strong> <a href="{self.base_url}">{self.base_url}</a></p>
                
                <p style="color: #666; font-size: 12px;">
                  Checked at: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}
                </p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(message, 'plain'))
            msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            print(f"✅ Notification sent to {self.notify_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send notification: {str(e)}")
            return False
    
    def check_appointments(self):
        """Main function to check for appointments"""
        try:
            self.setup_driver()
            print(f"🔍 Starting appointment check at {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
            
            # Navigate to the scheduler
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Click English
            english_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ENGLISH')]"))
            )
            english_button.click()
            time.sleep(2)
            
            # Fill in login information
            print("📝 Filling in login information...")
            
            # First name
            first_name_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='First Name' or contains(@id, 'first')]"))
            )
            first_name_field.clear()
            first_name_field.send_keys(self.first_name)
            
            # Last name
            last_name_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Last Name' or contains(@id, 'last')]")
            last_name_field.clear()
            last_name_field.send_keys(self.last_name)
            
            # DOB
            dob_field = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Date of Birth') or contains(@id, 'dob')]")
            dob_field.clear()
            dob_field.send_keys(self.dob)
            
            # SSN last 4
            ssn_field = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Last four of SSN') or contains(@id, 'ssn')]")
            ssn_field.clear()
            ssn_field.send_keys(self.ssn_last4)
            
            # Phone
            phone_field = self.driver.find_element(By.XPATH, "//input[@type='tel' or contains(@id, 'phone')]")
            phone_field.clear()
            phone_field.send_keys(self.phone)
            
            # Click Log On
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOG ON')]"))
            )
            login_button.click()
            time.sleep(3)
            
            # Handle OTP if needed (you'll need to handle this manually or skip for automation)
            try:
                otp_field = self.driver.find_element(By.XPATH, "//input[@type='text' and contains(@placeholder, 'passcode')]")
                print("⚠️ OTP verification required - this step cannot be automated")
                print("💡 For automated monitoring, you may need to use a different approach")
                return None
            except NoSuchElementException:
                pass
            
            # Click "New Appointment"
            new_appt_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'NEW APPOINTMENT')]"))
            )
            new_appt_button.click()
            time.sleep(2)
            
            # Select service type - "Apply for first time Texas DL/Permit"
            service_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'APPLY FOR FIRST TIME TEXAS DL/PERMIT')]"))
            )
            service_button.click()
            time.sleep(2)
            
            # Enter ZIP code
            zip_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='#####' or contains(@id, 'zip')]"))
            )
            zip_field.clear()
            zip_field.send_keys(self.zip_code)
            
            # Click Next
            next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'NEXT')]")
            next_button.click()
            time.sleep(3)
            
            # Check for Denton location
            print("🔍 Checking Denton location...")
            denton_section = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Denton')]"))
            )
            
            # Get the next available date
            next_date_element = self.driver.find_element(
                By.XPATH, 
                "//div[contains(text(), 'Denton')]/following::div[contains(text(), 'Next Available Date')]/following-sibling::div"
            )
            next_available_date = next_date_element.text
            
            print(f"📅 Next available date in Denton: {next_available_date}")
            
            # Click on Denton to see all available dates
            select_button = self.driver.find_element(
                By.XPATH,
                "//div[contains(text(), 'Denton')]/following::button[contains(text(), 'Select')]"
            )
            select_button.click()
            time.sleep(2)
            
            # Get all available dates
            date_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'date') or contains(text(), '/202')]")
            available_dates = [elem.text for elem in date_elements if elem.text.strip()]
            
            print(f"✅ Found {len(available_dates)} available dates!")
            
            if available_dates:
                # Send notification
                message = f"Appointments are available in Denton! Next available: {next_available_date}"
                self.send_notification(
                    subject="🎉 DPS Appointment Available in Denton!",
                    message=message,
                    available_dates=available_dates[:10]  # Send first 10 dates
                )
                
                # Save to file for GitHub Actions artifact
                with open('appointments_found.json', 'w') as f:
                    json.dump({
                        'found': True,
                        'location': 'Denton',
                        'next_available': next_available_date,
                        'available_dates': available_dates[:10],
                        'checked_at': datetime.now().isoformat()
                    }, f, indent=2)
                
                return True
            else:
                print("❌ No appointments currently available")
                return False
                
        except TimeoutException as e:
            print(f"⏱️ Timeout waiting for element: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error during check: {str(e)}")
            self.driver.save_screenshot('error_screenshot.png')
            return None
        finally:
            if self.driver:
                self.driver.quit()

def main():
    checker = DPSAppointmentChecker()
    result = checker.check_appointments()
    
    if result is True:
        print("✅ Appointments found and notification sent!")
        sys.exit(0)  # Success
    elif result is False:
        print("ℹ️ No appointments available at this time")
        sys.exit(0)  # No error, just no appointments
    else:
        print("⚠️ Check could not be completed")
        sys.exit(1)  # Error occurred

if __name__ == "__main__":
    main()
