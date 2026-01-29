#!/usr/bin/env python3
"""
Texas DPS Appointment Monitor - Simplified Version (No Login Required)
This version checks appointment availability without logging in
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

class SimpleDPSChecker:
    """Simplified checker that doesn't require login"""
    
    def __init__(self):
        self.base_url = "https://www.txdpsscheduler.com"
        self.driver = None
        
        # Notification settings only
        self.zip_code = os.getenv('ZIP_CODE', '76201')
        self.notify_email = os.getenv('NOTIFY_EMAIL', '')
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
        
    def send_notification(self, subject, message, next_available=None):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.notify_email
            
            html = f"""
            <html>
              <body>
                <h2>🎉 Texas DPS Appointment Availability Update!</h2>
                <p>{message}</p>
                
                {f'<h3>Next Available Date: {next_available}</h3>' if next_available else ''}
                
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
    
    def check_appointments_simple(self):
        """
        Simplified check - navigates to location selection without login
        and checks if appointments are available
        """
        try:
            self.setup_driver()
            print(f"🔍 Starting simplified check at {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
            
            # Navigate to the scheduler
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Click English
            english_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ENGLISH')]"))
            )
            english_button.click()
            time.sleep(2)
            
            # Look for "Schedule a driver license appointment" button
            # This button should be visible without logging in
            try:
                schedule_button = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//button[contains(text(), 'Schedule a driver license appointment')] | //a[contains(text(), 'Schedule a driver license appointment')]")
                    )
                )
                
                if schedule_button.is_displayed() and schedule_button.is_enabled():
                    print("✅ Schedule button is accessible")
                    
                    # Try to access the page to see if we can check availability
                    # without full login
                    schedule_button.click()
                    time.sleep(3)
                    
                    # Check if we can see location selector
                    try:
                        # Try to detect if locations are shown
                        location_elements = self.driver.find_elements(
                            By.XPATH, 
                            "//div[contains(text(), 'Denton')] | //button[contains(text(), 'Denton')]"
                        )
                        
                        if location_elements:
                            print(f"✅ Found {len(location_elements)} Denton location references")
                            
                            # Try to get availability info
                            date_elements = self.driver.find_elements(
                                By.XPATH,
                                "//div[contains(text(), '/')and contains(text(), '202')]"
                            )
                            
                            if date_elements:
                                dates = [elem.text for elem in date_elements if elem.text.strip()]
                                print(f"✅ Found dates: {dates}")
                                
                                # Send notification
                                message = f"Appointments may be available in Denton! Please check the website."
                                self.send_notification(
                                    subject="🎉 DPS Appointments May Be Available!",
                                    message=message,
                                    next_available=dates[0] if dates else None
                                )
                                
                                return True
                            else:
                                print("ℹ️ Could not detect specific dates without login")
                                return False
                        else:
                            print("ℹ️ Login may be required to see location details")
                            return None
                            
                    except NoSuchElementException:
                        print("ℹ️ Location information requires login")
                        return None
                        
                else:
                    print("⚠️ Schedule button not accessible")
                    return None
                    
            except TimeoutException:
                print("⚠️ Could not find schedule button")
                return None
                
        except Exception as e:
            print(f"❌ Error during simplified check: {str(e)}")
            if self.driver:
                self.driver.save_screenshot('error_screenshot_simple.png')
            return None
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """
    Main function for simplified checker
    Note: This version has limitations as it can't access detailed
    appointment information without logging in
    """
    print("="*60)
    print("SIMPLIFIED DPS APPOINTMENT CHECKER")
    print("Note: Limited information without login")
    print("="*60)
    
    checker = SimpleDPSChecker()
    result = checker.check_appointments_simple()
    
    if result is True:
        print("✅ Possible appointments detected!")
        sys.exit(0)
    elif result is False:
        print("ℹ️ No clear appointment information available")
        sys.exit(0)
    else:
        print("⚠️ Check requires login for detailed information")
        print("💡 Consider using the manual checking strategy instead")
        sys.exit(1)

if __name__ == "__main__":
    main()
