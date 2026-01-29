"""
Test suite for DPS Appointment Checker
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from appointment_checker import DPSAppointmentChecker


class TestDPSAppointmentChecker:
    """Test cases for DPSAppointmentChecker class"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture providing mock configuration"""
        return {
            'first_name': 'Test',
            'last_name': 'User',
            'dob': '01/01/2000',
            'ssn_last4': '1234',
            'phone': '(555) 123-4567',
            'email': 'test@example.com',
            'zip_code': '76201',
            'notify_email': 'test@example.com',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'location_preference': 'Denton',
            'max_distance_miles': 20,
            'headless': True,
            'screenshot_on_error': False,
        }
    
    @pytest.fixture
    def checker(self, mock_config):
        """Fixture providing DPSAppointmentChecker instance"""
        return DPSAppointmentChecker(config=mock_config)
    
    def test_initialization(self, checker, mock_config):
        """Test checker initializes with correct configuration"""
        assert checker.config == mock_config
        assert checker.base_url == "https://www.txdpsscheduler.com"
        assert checker.browser is None
        assert checker.page is None
    
    def test_load_config_from_env(self):
        """Test configuration loading from environment variables"""
        with patch.dict(os.environ, {
            'FIRST_NAME': 'John',
            'LAST_NAME': 'Doe',
            'DOB': '05/15/1995',
            'SSN_LAST4': '5678',
            'ZIP_CODE': '75001'
        }):
            checker = DPSAppointmentChecker()
            assert checker.config['first_name'] == 'John'
            assert checker.config['last_name'] == 'Doe'
            assert checker.config['dob'] == '05/15/1995'
            assert checker.config['ssn_last4'] == '5678'
            assert checker.config['zip_code'] == '75001'
    
    @pytest.mark.asyncio
    async def test_setup_browser(self, checker):
        """Test browser setup creates browser and page instances"""
        with patch('appointment_checker.async_playwright') as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            mock_context = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            
            mock_page = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)
            
            await checker.setup_browser()
            
            assert checker.browser is not None
            assert checker.page is not None
            mock_playwright.return_value.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_navigate_to_scheduler_success(self, checker):
        """Test successful navigation to scheduler"""
        checker.page = AsyncMock()
        checker.page.goto = AsyncMock()
        checker.page.wait_for_selector = AsyncMock()
        checker.page.click = AsyncMock()
        checker.page.wait_for_load_state = AsyncMock()
        
        result = await checker.navigate_to_scheduler()
        
        assert result is True
        checker.page.goto.assert_called_once()
        checker.page.click.assert_called_once_with("button:has-text('ENGLISH')")
    
    @pytest.mark.asyncio
    async def test_navigate_to_scheduler_timeout(self, checker):
        """Test navigation timeout handling"""
        from playwright.async_api import TimeoutError as PlaywrightTimeout
        
        checker.page = AsyncMock()
        checker.page.goto = AsyncMock(side_effect=PlaywrightTimeout("Timeout"))
        checker.config['screenshot_on_error'] = False
        
        result = await checker.navigate_to_scheduler()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_fill_login_form_success(self, checker):
        """Test successful login form filling"""
        checker.page = AsyncMock()
        checker.page.wait_for_selector = AsyncMock()
        checker.page.fill = AsyncMock()
        checker.page.click = AsyncMock()
        checker.page.wait_for_load_state = AsyncMock()
        
        result = await checker.fill_login_form()
        
        assert result is True
        # Check that all fields were filled
        assert checker.page.fill.call_count >= 5  # first name, last name, dob, ssn, phone
    
    @pytest.mark.asyncio
    async def test_fill_login_form_missing_elements(self, checker):
        """Test login form handling when elements are missing"""
        from playwright.async_api import TimeoutError as PlaywrightTimeout
        
        checker.page = AsyncMock()
        checker.page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("Element not found"))
        checker.config['screenshot_on_error'] = False
        
        result = await checker.fill_login_form()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_handle_otp_verification_required(self, checker):
        """Test OTP verification detection when required"""
        checker.page = AsyncMock()
        mock_otp_field = AsyncMock()
        checker.page.query_selector = AsyncMock(return_value=mock_otp_field)
        
        result = await checker.handle_otp_verification()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_handle_otp_verification_not_required(self, checker):
        """Test OTP verification detection when not required"""
        checker.page = AsyncMock()
        checker.page.query_selector = AsyncMock(return_value=None)
        
        result = await checker.handle_otp_verification()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_select_appointment_type_success(self, checker):
        """Test successful appointment type selection"""
        checker.page = AsyncMock()
        checker.page.wait_for_selector = AsyncMock()
        checker.page.click = AsyncMock()
        
        result = await checker.select_appointment_type()
        
        assert result is True
        assert checker.page.click.call_count == 2  # New appointment + service type
    
    @pytest.mark.asyncio
    async def test_search_location_success(self, checker):
        """Test successful location search"""
        checker.page = AsyncMock()
        checker.page.wait_for_selector = AsyncMock()
        checker.page.fill = AsyncMock()
        checker.page.click = AsyncMock()
        checker.page.wait_for_load_state = AsyncMock()
        
        result = await checker.search_location()
        
        assert result is True
        checker.page.fill.assert_called_once_with(
            "input[placeholder='#####'], input[id*='zip']",
            '76201'
        )
    
    @pytest.mark.asyncio
    async def test_get_available_appointments_found(self, checker):
        """Test getting available appointments when found"""
        checker.page = AsyncMock()
        
        # Mock location element
        mock_location = AsyncMock()
        checker.page.query_selector = AsyncMock(side_effect=[mock_location, AsyncMock()])
        
        # Mock location section
        checker.page.locator = Mock()
        mock_locator = AsyncMock()
        mock_locator.first.text_content = AsyncMock(return_value="03/15/2026")
        checker.page.locator.return_value.locator.return_value = mock_locator
        
        # Mock date elements
        mock_date1 = AsyncMock()
        mock_date1.text_content = AsyncMock(return_value="03/15/2026")
        mock_date2 = AsyncMock()
        mock_date2.text_content = AsyncMock(return_value="03/16/2026")
        
        checker.page.locator.return_value.all = AsyncMock(return_value=[mock_date1, mock_date2])
        
        result = await checker.get_available_appointments()
        
        assert result is not None
        assert result['location'] == 'Denton'
        assert 'next_available' in result
        assert 'available_dates' in result
        assert 'checked_at' in result
    
    @pytest.mark.asyncio
    async def test_get_available_appointments_not_found(self, checker):
        """Test getting appointments when location not found"""
        checker.page = AsyncMock()
        checker.page.query_selector = AsyncMock(return_value=None)
        
        result = await checker.get_available_appointments()
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_screenshot(self, checker, tmp_path):
        """Test screenshot saving functionality"""
        checker.page = AsyncMock()
        checker.page.screenshot = AsyncMock()
        
        with patch('os.makedirs'):
            await checker._save_screenshot('test')
        
        checker.page.screenshot.assert_called_once()
    
    def test_save_results(self, checker, tmp_path):
        """Test results saving to JSON file"""
        test_appointments = {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': ['03/15/2026', '03/16/2026'],
            'total_slots': 2,
            'checked_at': datetime.now().isoformat()
        }
        
        with patch('os.makedirs'), \
             patch('builtins.open', create=True) as mock_open:
            checker._save_results(test_appointments)
            mock_open.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, checker):
        """Test browser cleanup"""
        checker.page = AsyncMock()
        checker.browser = AsyncMock()
        checker.page.close = AsyncMock()
        checker.browser.close = AsyncMock()
        
        await checker.cleanup()
        
        checker.page.close.assert_called_once()
        checker.browser.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_appointments_full_flow_success(self, checker):
        """Test full appointment checking flow with successful result"""
        # Mock all the sub-methods
        checker.setup_browser = AsyncMock()
        checker.navigate_to_scheduler = AsyncMock(return_value=True)
        checker.fill_login_form = AsyncMock(return_value=True)
        checker.handle_otp_verification = AsyncMock(return_value=False)
        checker.select_appointment_type = AsyncMock(return_value=True)
        checker.search_location = AsyncMock(return_value=True)
        
        mock_appointments = {
            'location': 'Denton',
            'next_available': '03/15/2026',
            'available_dates': ['03/15/2026'],
            'total_slots': 1,
            'checked_at': datetime.now().isoformat()
        }
        checker.get_available_appointments = AsyncMock(return_value=mock_appointments)
        checker.notifier.send_notification = AsyncMock(return_value=True)
        checker._save_results = Mock()
        checker.cleanup = AsyncMock()
        
        result = await checker.check_appointments()
        
        assert result is not None
        assert result['location'] == 'Denton'
        checker.notifier.send_notification.assert_called_once()
        checker._save_results.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_appointments_full_flow_no_appointments(self, checker):
        """Test full appointment checking flow with no appointments found"""
        checker.setup_browser = AsyncMock()
        checker.navigate_to_scheduler = AsyncMock(return_value=True)
        checker.fill_login_form = AsyncMock(return_value=True)
        checker.handle_otp_verification = AsyncMock(return_value=False)
        checker.select_appointment_type = AsyncMock(return_value=True)
        checker.search_location = AsyncMock(return_value=True)
        checker.get_available_appointments = AsyncMock(return_value=None)
        checker.cleanup = AsyncMock()
        
        result = await checker.check_appointments()
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_check_appointments_navigation_failure(self, checker):
        """Test appointment checking when navigation fails"""
        checker.setup_browser = AsyncMock()
        checker.navigate_to_scheduler = AsyncMock(return_value=False)
        checker.cleanup = AsyncMock()
        
        result = await checker.check_appointments()
        
        assert result is None


class TestConfigurationValidation:
    """Test cases for configuration validation"""
    
    def test_missing_required_env_vars(self):
        """Test behavior with missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            checker = DPSAppointmentChecker()
            # Should initialize with empty strings, not fail
            assert checker.config['first_name'] == ''
            assert checker.config['last_name'] == ''
    
    def test_default_values(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            checker = DPSAppointmentChecker()
            assert checker.config['zip_code'] == '76201'
            assert checker.config['headless'] is True
            assert checker.config['screenshot_on_error'] is True
            assert checker.config['smtp_server'] == 'smtp.gmail.com'
            assert checker.config['smtp_port'] == 587


class TestIntegration:
    """Integration tests (require actual browser)"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_browser_setup(self):
        """Test actual browser setup (requires Playwright installed)"""
        config = {
            'first_name': 'Test',
            'last_name': 'User',
            'dob': '01/01/2000',
            'ssn_last4': '1234',
            'phone': '(555) 123-4567',
            'email': 'test@example.com',
            'zip_code': '76201',
            'notify_email': 'test@example.com',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'location_preference': 'Denton',
            'max_distance_miles': 20,
            'headless': True,
            'screenshot_on_error': False,
        }
        
        checker = DPSAppointmentChecker(config=config)
        
        try:
            await checker.setup_browser()
            assert checker.browser is not None
            assert checker.page is not None
        finally:
            await checker.cleanup()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_website_navigation(self):
        """Test navigation to actual DPS website (requires internet)"""
        config = {
            'first_name': 'Test',
            'last_name': 'User',
            'dob': '01/01/2000',
            'ssn_last4': '1234',
            'phone': '(555) 123-4567',
            'email': 'test@example.com',
            'zip_code': '76201',
            'notify_email': 'test@example.com',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': 'test@gmail.com',
            'smtp_password': 'test_password',
            'location_preference': 'Denton',
            'max_distance_miles': 20,
            'headless': True,
            'screenshot_on_error': False,
        }
        
        checker = DPSAppointmentChecker(config=config)
        
        try:
            await checker.setup_browser()
            result = await checker.navigate_to_scheduler()
            # Should successfully navigate to the page
            assert result is True
        finally:
            await checker.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
