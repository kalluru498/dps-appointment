# Texas DPS Appointment Monitor - Playwright Edition 🚗

[![Tests](https://github.com/yourusername/dps-monitor/actions/workflows/monitor_appointments.yml/badge.svg)](https://github.com/yourusername/dps-monitor/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40-green.svg)](https://playwright.dev/)

Automated monitoring tool for Texas DPS driver license appointment availability using **Playwright** for robust browser automation. Monitors Denton, TX locations and sends instant email notifications when appointments become available.

## 🎯 Features

- ✅ **Playwright-based**: More reliable and modern than Selenium
- ✅ **Async/Await**: Efficient asynchronous operations
- ✅ **Comprehensive Testing**: Full test suite with pytest
- ✅ **Cloud-Based**: Runs automatically in GitHub Actions (free tier)
- ✅ **Email Notifications**: Beautiful HTML emails with appointment details
- ✅ **Error Handling**: Screenshots and logs for debugging
- ✅ **Type Safety**: Well-structured, maintainable code

## 📁 Project Structure

```
dps-monitor/
├── .github/
│   └── workflows/
│       └── monitor_appointments.yml    # GitHub Actions workflow
├── src/
│   ├── appointment_checker.py          # Main checker logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                   # Logging utilities
│       └── notifier.py                 # Email notification handler
├── tests/
│   ├── test_appointment_checker.py     # Checker tests
│   └── test_notifier.py                # Notifier tests
├── logs/                               # Log files (auto-generated)
├── screenshots/                        # Error screenshots (auto-generated)
├── results/                            # Appointment results (auto-generated)
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── pytest.ini                          # Pytest configuration
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended - No Laptop Required)

1. **Fork this repository**
   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Set up GitHub Secrets**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
   
   | Secret Name | Your Value |
   |------------|------------|
   | `FIRST_NAME` | Your first name |
   | `LAST_NAME` | Your last name |
   | `DOB` | Date of birth (MM/DD/YYYY) |
   | `SSN_LAST4` | Last 4 digits of SSN |
   | `PHONE` | Phone number |
   | `EMAIL` | Your email |
   | `ZIP_CODE` | `76201` (Denton) |
   | `NOTIFY_EMAIL` | Email for notifications |
   | `SMTP_USER` | Gmail address |
   | `SMTP_PASSWORD` | Gmail App Password* |
   | `SMTP_SERVER` | `smtp.gmail.com` |
   | `SMTP_PORT` | `587` |

   **\*How to get Gmail App Password:**
   1. Go to https://myaccount.google.com/security
   2. Enable 2-Step Verification
   3. Search "App passwords"
   4. Create one for "Mail"
   5. Copy the 16-character password

3. **Enable GitHub Actions**
   - Go to Actions tab
   - Click "I understand my workflows, go ahead and enable them"

4. **Test it manually**
   - Go to Actions → Texas DPS Appointment Monitor
   - Click "Run workflow"
   - Watch it run!

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dps-monitor.git
   cd dps-monitor
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your information
   nano .env  # or use your preferred editor
   ```

5. **Run the checker**
   ```bash
   cd src
   python appointment_checker.py
   ```

## 🧪 Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run unit tests only (fast)
```bash
pytest tests/ -v -m "not integration"
```

### Run integration tests (requires internet)
```bash
pytest tests/ -v -m integration
```

### Run with coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_appointment_checker.py -v
```

## 📅 Monitoring Schedule

The GitHub Actions workflow runs:
- **Every 5 minutes** during business hours (9 AM - 6 PM CT) on weekdays
- **Every 10 minutes** on weekends
- Approximately **200+ checks per day**

Customize the schedule by editing `.github/workflows/monitor_appointments.yml`:
```yaml
schedule:
  - cron: '*/5 15-23 * * 1-5'  # Every 5 minutes, Mon-Fri
```

## 📧 Email Notifications

When appointments are found, you'll receive an HTML email with:
- ✅ Location name
- ✅ Next available date
- ✅ List of all available dates (up to 10)
- ✅ Total number of slots
- ✅ Direct booking link
- ✅ OTP verification reminder

## ⚠️ Important Limitations

### OTP Verification Challenge

The Texas DPS website requires **One-Time Passcode (OTP)** verification via SMS/email after login. This means:

**What the Tool CAN Do:**
- ✅ Check appointment availability automatically
- ✅ Send instant notifications when slots open
- ✅ Run 24/7 without manual intervention

**What the Tool CANNOT Do:**
- ❌ Complete OTP verification automatically
- ❌ Book appointments without human interaction

**Recommended Workflow:**
1. Tool checks every 5 minutes
2. When appointments found → You get instant email
3. **Immediately** go to https://www.txdpsscheduler.com
4. Complete OTP verification manually
5. Book your appointment quickly!

## 🔧 Configuration Options

All configuration can be done via environment variables:

```bash
# Personal Information
FIRST_NAME=Your first name
LAST_NAME=Your last name
DOB=MM/DD/YYYY
SSN_LAST4=1234
PHONE=(555) 123-4567
EMAIL=you@example.com

# Location Settings
ZIP_CODE=76201
LOCATION_PREFERENCE=Denton
MAX_DISTANCE_MILES=20

# Notification Settings  
NOTIFY_EMAIL=notify@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password

# Browser Settings
HEADLESS=true                    # Run browser in headless mode
SCREENSHOT_ON_ERROR=true         # Save screenshots on errors
```

## 🐛 Troubleshooting

### No emails received?

1. **Check spam folder**
2. **Verify Gmail App Password** (16 characters, no spaces)
3. **Check GitHub Actions logs**:
   - Go to Actions tab
   - Click on latest run
   - Look for error messages

### GitHub Actions not running?

1. **Verify Actions are enabled**: Settings → Actions → Enable
2. **Check workflow syntax**: Validate YAML in `.github/workflows/`
3. **Review Action logs** for specific errors

### Tests failing?

1. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

2. **Check Python version** (requires 3.11+):
   ```bash
   python --version
   ```

3. **Verify all dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

### Playwright errors?

1. **Install system dependencies**:
   ```bash
   playwright install-deps chromium
   ```

2. **Update Playwright**:
   ```bash
   pip install --upgrade playwright
   playwright install chromium
   ```

## 📊 Viewing Results

### Check monitoring history

1. Go to **Actions** tab in GitHub
2. Click on workflow runs
3. Download artifacts:
   - `logs` - Detailed execution logs
   - `screenshots` - Error screenshots (if any)
   - `results` - JSON files with appointment data

### Example result JSON

```json
{
  "location": "Denton",
  "next_available": "03/15/2026",
  "available_dates": [
    "03/15/2026",
    "03/16/2026",
    "03/17/2026"
  ],
  "total_slots": 3,
  "checked_at": "2026-01-28T12:00:00"
}
```

## 🔒 Security Best Practices

- ✅ Use **private repository** for personal data protection
- ✅ Never commit `.env` file (it's in `.gitignore`)
- ✅ Use GitHub Secrets for sensitive data
- ✅ Use Gmail App Passwords (not your main password)
- ✅ Regularly rotate your app passwords
- ✅ Review GitHub Actions logs periodically

## 💰 Cost

**Completely FREE!**

- GitHub Actions: 2,000 free minutes/month (private repos)
- Public repos: Unlimited free minutes
- Each check takes ~2-3 minutes
- Can run 500-1,000 checks/month on free tier

## 🛠️ Development

### Code formatting
```bash
black src/ tests/
```

### Linting
```bash
flake8 src/ tests/
```

### Type checking
```bash
mypy src/
```

### Pre-commit checks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 Testing Philosophy

This project follows test-driven development principles:

- **Unit Tests**: Fast, no external dependencies
- **Integration Tests**: Test actual website interaction
- **Mocking**: Used extensively for external services
- **Coverage**: Aim for >80% code coverage

Run specific test types:
```bash
# Fast unit tests only
pytest tests/ -m "not integration" -v

# All tests including integration
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

## ⚖️ Legal Disclaimer

**For Personal Use Only**

This tool is designed for legitimate personal use to check appointment availability. By using this tool, you agree to:

- Use it only for checking appointment availability
- Not modify it to spam or overload the DPS website
- Follow the configured rate limits (5-minute intervals)
- Comply with Texas DPS terms of service
- Use it only for legitimate scheduling needs

This tool:
- ✅ Only reads public availability information
- ✅ Does NOT bypass any security measures
- ✅ Does NOT automate booking (OTP prevents this)
- ✅ Respects rate limits and server resources

**You are responsible** for ensuring your use complies with all applicable terms of service and local laws.

## 📱 Mobile Notifications

For instant alerts on your phone:

1. **Enable Gmail notifications**:
   - Install Gmail app
   - Enable push notifications
   - Set as high priority

2. **Use IFTTT** (optional):
   - Connect Gmail to IFTTT
   - Create applet: Gmail → Phone notification
   - Trigger on emails from GitHub Actions

3. **Custom solutions**:
   - Add Twilio for SMS (requires code modification)
   - Use Pushover API
   - Set up Telegram bot

## 🙏 Acknowledgments

- Created to help international students navigate the Texas DPS appointment system
- Built with Playwright for reliable automation
- Inspired by the need for a more robust solution than Selenium-based alternatives

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [GitHub Actions logs](https://github.com/yourusername/dps-monitor/actions)
3. Search [existing issues](https://github.com/yourusername/dps-monitor/issues)
4. Create a [new issue](https://github.com/yourusername/dps-monitor/issues/new) with:
   - Error logs
   - Screenshots (remove sensitive data!)
   - Steps to reproduce

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

## 🌟 Star History

If this tool helps you get your appointment, please consider giving it a star ⭐️

---

**Remember**: When you receive a notification, act quickly! Appointment slots fill up fast. Have your documents ready and be prepared to complete the OTP verification immediately.

**Good luck with your license renewal! 🍀**
