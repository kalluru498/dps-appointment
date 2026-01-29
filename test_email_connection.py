#!/usr/bin/env python3
"""
Test script to verify IMAP email connection
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.otp_handler import OTPHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_email_connection():
    """Test IMAP connection to Gmail"""
    
    # Load environment variables
    load_dotenv()
    
    email = os.getenv('EMAIL')
    password = os.getenv('SMTP_PASSWORD')
    
    logger.info(f"Testing email connection for: {email}")
    logger.info(f"Password provided: {'Yes' if password else 'No'}")
    
    if not email or not password:
        logger.error("EMAIL or SMTP_PASSWORD not configured in .env")
        return False
    
    # Initialize OTP handler
    otp_handler = OTPHandler(
        email_address=email,
        smtp_password=password
    )
    
    # Test connection
    logger.info("Attempting IMAP connection...")
    
    try:
        otp = otp_handler._fetch_latest_otp()
        
        if otp:
            logger.info(f"[SUCCESS] Latest OTP found: {otp}")
        else:
            logger.info("[INFO] No OTP found in latest email (this is normal if no OTP email exists yet)")
        
        logger.info("[SUCCESS] Email connection established!")
        return True
        
    except Exception as e:
        logger.error(f"[FAILED] Email connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email_connection()
    sys.exit(0 if success else 1)
