"""
OTP Handler - Reads OTP from email and extracts the code
"""

import imaplib
import email
import asyncio
import re
from email.header import decode_header
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OTPHandler:
    """Handle OTP verification by reading from email"""
    
    def __init__(self, email_address: str, smtp_password: str, smtp_server: str = "smtp.gmail.com"):
        """
        Initialize OTP Handler
        
        Args:
            email_address: Email address to read OTP from
            smtp_password: Email password (or app-specific password for Gmail)
            smtp_server: IMAP server (default: Gmail)
        """
        self.email_address = email_address
        self.smtp_password = smtp_password
        self.imap_server = smtp_server.replace("smtp", "imap")
        logger.info(f"OTP Handler initialized for {email_address}")
    
    async def get_otp_from_email(self, timeout: int = 120, check_interval: int = 5) -> Optional[str]:
        """
        Read OTP from the most recent email (async wrapper)
        
        Args:
            timeout: Maximum time to wait for OTP in seconds
            check_interval: How often to check for new emails in seconds
            
        Returns:
            OTP code if found, None otherwise
        """
        import time as time_module
        
        start_time = time_module.time()
        
        while time_module.time() - start_time < timeout:
            try:
                # Run blocking I/O in executor to avoid blocking event loop
                loop = asyncio.get_event_loop()
                otp = await loop.run_in_executor(None, self._fetch_latest_otp)
                
                if otp:
                    logger.info(f"[OK] OTP found: {otp}")
                    return otp
                
                elapsed = time_module.time() - start_time
                logger.info(f"Waiting for OTP... ({elapsed:.0f}s elapsed)")
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"Error checking email: {str(e)}")
                await asyncio.sleep(check_interval)
        
        logger.error(f"Timeout: OTP not received within {timeout} seconds")
        return None
    
    def _fetch_latest_otp(self) -> Optional[str]:
        """Fetch OTP from the latest email (blocking, runs in executor)"""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.smtp_password)
            
            # Select inbox
            mail.select("INBOX")
            
            # Search for recent emails
            status, messages = mail.search(None, "ALL")
            
            if status != "OK" or not messages[0]:
                logger.debug("No emails found")
                mail.close()
                mail.logout()
                return None
            
            # Get the latest email
            email_ids = messages[0].split()
            latest_email_id = email_ids[-1]
            
            # Fetch the email
            status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
            
            if status != "OK":
                logger.debug("Could not fetch email")
                mail.close()
                mail.logout()
                return None
            
            # Parse email
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Extract OTP from email body
            otp = self._extract_otp_from_message(msg)
            
            mail.close()
            mail.logout()
            
            return otp
            
        except imaplib.IMAP4.error as e:
            logger.warning(f"IMAP error: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching email: {str(e)}")
            return None
    
    def _extract_otp_from_message(self, msg) -> Optional[str]:
        """Extract OTP code from email message"""
        try:
            # Get email body
            body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            logger.debug(f"Email body preview: {body[:200]}")
            
            # Look for common OTP patterns
            # Pattern 1: "passcode is XXXXXX" or "code is XXXXXX"
            patterns = [
                r'passcode[:\s]+([0-9]{4,6})',
                r'code[:\s]+([0-9]{4,6})',
                r'otp[:\s]+([0-9]{4,6})',
                r'verification[:\s]+([0-9]{4,6})',
                r'\b([0-9]{4,6})\b.*(?:passcode|code|otp|verify)',
                r'<[^>]*>([0-9]{4,6})<[^>]*>',  # OTP in HTML tags
                r'([0-9]{6})',  # Any 6-digit number as fallback
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    otp = match.group(1)
                    if otp and len(otp) >= 4:  # OTP should be at least 4 digits
                        logger.info(f"[OK] OTP extracted: {otp}")
                        return otp
            
            logger.warning("Could not extract OTP from email body")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting OTP: {str(e)}")
            return None
