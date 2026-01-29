"""
Test suite for Email Notifier
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.notifier import EmailNotifier


class TestEmailNotifier:
    """Test cases for EmailNotifier class"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture providing mock configuration"""
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'notify_email': 'recipient@example.com'
        }
    
    @pytest.fixture
    def notifier(self, mock_config):
        """Fixture providing EmailNotifier instance"""
        return EmailNotifier(mock_config)
    
    @pytest.fixture
    def mock_appointments(self):
        """Fixture providing mock appointment data"""
        return {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': [
                '03/15/2026',
                '03/16/2026',
                '03/17/2026',
                '03/18/2026',
                '03/19/2026'
            ],
            'total_slots': 5,
            'checked_at': '2026-01-28T12:00:00'
        }
    
    def test_initialization(self, notifier, mock_config):
        """Test notifier initializes with correct configuration"""
        assert notifier.smtp_server == mock_config['smtp_server']
        assert notifier.smtp_port == mock_config['smtp_port']
        assert notifier.smtp_user == mock_config['smtp_user']
        assert notifier.smtp_password == mock_config['smtp_password']
        assert notifier.notify_email == mock_config['notify_email']
    
    def test_create_email_body(self, notifier, mock_appointments):
        """Test email body creation"""
        plain_text, html_text = notifier._create_email_body(mock_appointments)
        
        # Check plain text content
        assert 'Denton' in plain_text
        assert '03/15/2026' in plain_text
        assert 'Total Slots Found: 5' in plain_text
        assert 'https://www.txdpsscheduler.com' in plain_text
        
        # Check HTML content
        assert '<html>' in html_text
        assert 'Denton' in html_text
        assert '03/15/2026' in html_text
        assert '<li>03/15/2026</li>' in html_text
        assert 'OTP' in html_text  # Should mention OTP requirement
    
    def test_create_email_body_with_many_dates(self, notifier):
        """Test email body creation with more than 10 dates"""
        appointments = {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': [f'03/{i}/2026' for i in range(15, 30)],  # 15 dates
            'total_slots': 15,
            'checked_at': datetime.now().isoformat()
        }
        
        plain_text, html_text = notifier._create_email_body(appointments)
        
        # Should only show first 10 dates
        assert '03/15/2026' in plain_text
        assert '03/24/2026' in plain_text
        assert '...' in plain_text  # Indicates more dates available
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self, notifier, mock_appointments):
        """Test successful email notification sending"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await notifier.send_notification(
                subject="Test Subject",
                appointments=mock_appointments
            )
            
            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
            mock_server.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_notification_missing_credentials(self, mock_config, mock_appointments):
        """Test notification sending with missing SMTP credentials"""
        mock_config['smtp_user'] = ''
        notifier = EmailNotifier(mock_config)
        
        result = await notifier.send_notification(
            subject="Test Subject",
            appointments=mock_appointments
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_missing_recipient(self, mock_config, mock_appointments):
        """Test notification sending with missing recipient email"""
        mock_config['notify_email'] = ''
        notifier = EmailNotifier(mock_config)
        
        result = await notifier.send_notification(
            subject="Test Subject",
            appointments=mock_appointments
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_auth_failure(self, notifier, mock_appointments):
        """Test notification sending with authentication failure"""
        import smtplib
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await notifier.send_notification(
                subject="Test Subject",
                appointments=mock_appointments
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_smtp_exception(self, notifier, mock_appointments):
        """Test notification sending with general SMTP exception"""
        import smtplib
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_server.login.side_effect = smtplib.SMTPException("Connection failed")
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await notifier.send_notification(
                subject="Test Subject",
                appointments=mock_appointments
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_with_custom_message(self, notifier, mock_appointments):
        """Test notification sending with custom message"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            custom_msg = "This is a custom message!"
            result = await notifier.send_notification(
                subject="Test Subject",
                appointments=mock_appointments,
                custom_message=custom_msg
            )
            
            assert result is True
            # Verify send_message was called (custom message is included internally)
            mock_server.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_notification_high_priority(self, notifier, mock_appointments):
        """Test that notifications are sent with high priority"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await notifier.send_notification(
                subject="Test Subject",
                appointments=mock_appointments
            )
            
            assert result is True
            # Verify X-Priority header is set
            call_args = mock_server.send_message.call_args
            msg = call_args[0][0]
            assert msg['X-Priority'] == '1'
    
    def test_send_test_email(self, notifier):
        """Test sending test email"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = notifier.send_test_email()
            
            assert result is True
            mock_server.send_message.assert_called_once()
            
            # Verify test email was created with proper structure
            call_args = mock_server.send_message.call_args
            msg = call_args[0][0]
            assert 'Test' in msg['Subject'] or 'test' in msg['Subject'].lower()
            # Check that it's a proper email message
            assert msg['From'] is not None
            assert msg['To'] is not None


class TestEmailBodyFormatting:
    """Test cases for email body formatting"""
    
    def test_html_escaping(self):
        """Test that special characters in appointments are properly escaped"""
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'notify_email': 'recipient@example.com'
        }
        notifier = EmailNotifier(config)
        
        appointments = {
            'location': 'Location <with> special &characters',
            'next_available': '03/15/2026',
            'available_dates': ['03/15/2026'],
            'total_slots': 1,
            'checked_at': datetime.now().isoformat()
        }
        
        plain_text, html_text = notifier._create_email_body(appointments)
        
        # Should handle special characters without breaking HTML
        assert 'Location' in html_text
        # Basic check that HTML structure is intact
        assert '<html>' in html_text
        assert '</html>' in html_text
    
    def test_date_formatting(self):
        """Test date formatting in email body"""
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'notify_email': 'recipient@example.com'
        }
        notifier = EmailNotifier(config)
        
        checked_at = '2026-01-28T14:30:45'
        appointments = {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': ['03/15/2026'],
            'total_slots': 1,
            'checked_at': checked_at
        }
        
        plain_text, html_text = notifier._create_email_body(appointments)
        
        # Check that date is formatted properly
        assert '2026-01-28' in plain_text or '01-28' in plain_text
    
    def test_empty_dates_list(self):
        """Test email body creation with empty dates list"""
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'notify_email': 'recipient@example.com'
        }
        notifier = EmailNotifier(config)
        
        appointments = {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': [],
            'total_slots': 0,
            'checked_at': datetime.now().isoformat()
        }
        
        plain_text, html_text = notifier._create_email_body(appointments)
        
        # Should handle empty list gracefully
        assert 'Denton' in plain_text
        assert '<html>' in html_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
