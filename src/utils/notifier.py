"""
Email notification module for sending appointment alerts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailNotifier:
    """Handles email notifications for appointment availability"""
    
    def __init__(self, config: Dict):
        """
        Initialize email notifier
        
        Args:
            config: Configuration dictionary with SMTP settings
        """
        self.config = config
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user', '')
        self.smtp_password = config.get('smtp_password', '')
        self.notify_email = config.get('notify_email', '')
    
    def _create_email_body(self, appointments: Dict) -> tuple[str, str]:
        """
        Create email body in both plain text and HTML
        
        Args:
            appointments: Dictionary with appointment information
            
        Returns:
            Tuple of (plain_text, html_text)
        """
        location = appointments.get('location', 'Unknown')
        next_available = appointments.get('next_available', 'Unknown')
        available_dates = appointments.get('available_dates', [])
        total_slots = appointments.get('total_slots', 0)
        checked_at = appointments.get('checked_at', datetime.now().isoformat())
        
        # Plain text version
        plain_text = f"""
🎉 Texas DPS Appointment Available!

Location: {location}
Next Available Date: {next_available}
Total Slots Found: {total_slots}

Available Dates:
{chr(10).join(f"  • {date}" for date in available_dates[:10])}

{"..." if len(available_dates) > 10 else ""}

⚡ ACT FAST! Book your appointment now at:
https://www.txdpsscheduler.com

Note: You will need to complete OTP verification during booking.

---
Checked at: {datetime.fromisoformat(checked_at).strftime('%Y-%m-%d %I:%M:%S %p')}
Automated by DPS Appointment Monitor
"""
        
        # HTML version
        dates_html = "".join([f"<li>{date}</li>" for date in available_dates[:10]])
        
        html_text = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .info-box {{
            background: white;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .info-box strong {{
            color: #667eea;
        }}
        .dates-list {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .dates-list ul {{
            list-style: none;
            padding: 0;
        }}
        .dates-list li {{
            padding: 8px;
            margin: 5px 0;
            background: #e9ecef;
            border-radius: 3px;
        }}
        .cta-button {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .cta-button:hover {{
            background: #218838;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 DPS Appointment Available!</h1>
    </div>
    
    <div class="content">
        <div class="info-box">
            <strong>📍 Location:</strong> {location}
        </div>
        
        <div class="info-box">
            <strong>📅 Next Available Date:</strong> {next_available}
        </div>
        
        <div class="info-box">
            <strong>🎫 Total Slots Found:</strong> {total_slots}
        </div>
        
        <div class="dates-list">
            <h3>Available Dates:</h3>
            <ul>
                {dates_html}
                {"<li><em>...and more</em></li>" if len(available_dates) > 10 else ""}
            </ul>
        </div>
        
        <div class="warning">
            <strong>⚠️ Important:</strong> You will need to complete OTP (One-Time Passcode) verification via SMS or email during the booking process. Have your phone ready!
        </div>
        
        <center>
            <a href="https://www.txdpsscheduler.com" class="cta-button">
                ⚡ BOOK NOW - ACT FAST!
            </a>
        </center>
        
        <div class="footer">
            <p>Checked at: {datetime.fromisoformat(checked_at).strftime('%Y-%m-%d %I:%M:%S %p')}</p>
            <p>Automated by DPS Appointment Monitor</p>
        </div>
    </div>
</body>
</html>
"""
        
        return plain_text, html_text
    
    async def send_notification(
        self, 
        subject: str, 
        appointments: Dict,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Send email notification about available appointments
        
        Args:
            subject: Email subject line
            appointments: Dictionary with appointment information
            custom_message: Optional custom message to prepend
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                return False
            
            if not self.notify_email:
                logger.error("Notification email not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.notify_email
            msg['X-Priority'] = '1'  # High priority
            
            # Create email body
            plain_text, html_text = self._create_email_body(appointments)
            
            if custom_message:
                plain_text = f"{custom_message}\n\n{plain_text}"
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(html_text, 'html'))
            
            # Send email
            logger.info(f"Sending notification to {self.notify_email}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"[OK] Notification sent successfully to {self.notify_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("[FAILED] SMTP authentication failed - check your email/password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"[FAILED] SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[FAILED] Failed to send notification: {str(e)}")
            return False
    
    def send_test_email(self) -> bool:
        """
        Send a test email to verify configuration
        
        Returns:
            True if test email sent successfully, False otherwise
        """
        try:
            test_appointments = {
                'location': 'Denton (Test)',
                'next_available': '01/30/2026',
                'available_dates': ['01/30/2026', '01/31/2026', '02/01/2026'],
                'total_slots': 3,
                'checked_at': datetime.now().isoformat()
            }
            
            return asyncio.run(self.send_notification(
                subject="🧪 Test - DPS Monitor Email Configuration",
                appointments=test_appointments,
                custom_message="This is a test email to verify your DPS Monitor email configuration is working correctly."
            ))
            
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False


# For compatibility with sync code
import asyncio

def send_notification_sync(config: Dict, subject: str, appointments: Dict) -> bool:
    """Synchronous wrapper for sending notifications"""
    notifier = EmailNotifier(config)
    return asyncio.run(notifier.send_notification(subject, appointments))
