# Complete Setup Guide

This guide walks you through setting up the DPS Monitor from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Python 3.11 or higher
- Git
- Gmail account (for notifications)
- GitHub account (for automated monitoring)

### Check Your Python Version
```bash
python3 --version
# Should show 3.11.0 or higher
```

If you need to install Python 3.11:
- **macOS**: `brew install python@3.11`
- **Ubuntu**: `sudo apt install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

---

## Local Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/dps-monitor.git
cd dps-monitor
```

### Step 2: Run Quick Start Script (Recommended)

```bash
./quickstart.sh
```

This script will:
- Check Python version
- Create virtual environment
- Install all dependencies
- Install Playwright browsers
- Create .env file
- Set up directories
- Run tests (optional)

### Step 3: Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium

# Create environment file
cp .env.example .env

# Edit with your information
nano .env  # or use your preferred editor
```

### Step 4: Configure Environment Variables

Edit `.env` file with your actual information:

```bash
# Personal Information
FIRST_NAME=Naveen              # Your first name
LAST_NAME=Kumar                # Your last name
DOB=07/21/2000                 # MM/DD/YYYY
SSN_LAST4=1234                 # Last 4 digits of SSN
PHONE=(940) 977-2486           # Your phone number
EMAIL=your@email.com           # Your email

# Location
ZIP_CODE=76201                 # Denton zip code
LOCATION_PREFERENCE=Denton     # Preferred location name

# Notifications
NOTIFY_EMAIL=your@email.com    # Where to send notifications

# Gmail Settings (see below for setup)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App password
```

### Step 5: Set Up Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Search for "App passwords" in the search bar
4. Click "App passwords"
5. Select:
   - App: "Mail"
   - Device: "Other (Custom name)"
   - Name it: "DPS Monitor"
6. Click "Generate"
7. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
8. Paste it into your `.env` file as `SMTP_PASSWORD`

⚠️ **Important**: Use the app password, NOT your regular Gmail password!

### Step 6: Test Your Setup

```bash
# Run unit tests
./run_tests.sh -u

# Or manually
pytest tests/ -v -m "not integration"
```

### Step 7: Run the Monitor

```bash
cd src
python appointment_checker.py
```

You should see output like:
```
INFO - Starting DPS Appointment Check
INFO - Time: 2026-01-28 02:45:00 PM
INFO - Navigating to https://www.txdpsscheduler.com
INFO - Selected English language
INFO - Filling login form
...
```

---

## GitHub Actions Setup

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `dps-monitor`
3. **Set to Private** (recommended for security)
4. Click "Create repository"

### Step 2: Push Your Code

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - DPS Monitor"

# Add remote
git remote add origin https://github.com/yourusername/dps-monitor.git

# Push
git push -u origin main
```

### Step 3: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

#### Required Secrets

| Secret Name | Value | Example |
|------------|-------|---------|
| `FIRST_NAME` | Your first name | `Naveen` |
| `LAST_NAME` | Your last name | `Kumar` |
| `DOB` | Date of birth | `07/21/2000` |
| `SSN_LAST4` | Last 4 of SSN | `1234` |
| `PHONE` | Phone number | `(940) 977-2486` |
| `EMAIL` | Your email | `naveen@example.com` |
| `ZIP_CODE` | Denton zip | `76201` |
| `NOTIFY_EMAIL` | Notification email | `naveen@example.com` |
| `SMTP_USER` | Gmail address | `naveen@gmail.com` |
| `SMTP_PASSWORD` | Gmail app password | `xxxx xxxx xxxx xxxx` |
| `SMTP_SERVER` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |

#### Adding Each Secret

For each secret above:
1. Click "New repository secret"
2. Name: Enter the secret name exactly as shown above
3. Value: Enter your actual value
4. Click "Add secret"

### Step 4: Enable GitHub Actions

1. Go to **Actions** tab
2. If prompted, click "I understand my workflows, go ahead and enable them"
3. You should see "Texas DPS Appointment Monitor (Playwright)" workflow

### Step 5: Test the Workflow

1. Click on "Texas DPS Appointment Monitor (Playwright)"
2. Click "Run workflow" dropdown
3. Click green "Run workflow" button
4. Watch it run (takes 2-3 minutes)

### Step 6: Check Results

After the workflow completes:
1. Click on the workflow run
2. Check the logs for any errors
3. If successful, you'll see: "Check completed"
4. Download artifacts if available (logs, screenshots, results)

---

## Testing

### Quick Test Commands

```bash
# Run all unit tests (fast)
./run_tests.sh -u

# Run all tests with coverage
./run_tests.sh -u -c

# Run integration tests (slow, requires internet)
./run_tests.sh -i

# Run with verbose output
./run_tests.sh -u -v
```

### Manual Testing

```bash
# Activate virtual environment first
source venv/bin/activate

# Run specific test file
pytest tests/test_appointment_checker.py -v

# Run specific test
pytest tests/test_appointment_checker.py::TestDPSAppointmentChecker::test_initialization -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
# Then open htmlcov/index.html in browser
```

### Test Structure

```
tests/
├── test_appointment_checker.py   # Tests for main checker
└── test_notifier.py               # Tests for email notifier
```

### Test Markers

- `unit`: Fast tests, no external dependencies
- `integration`: Slow tests, requires internet/browser

---

## Troubleshooting

### Common Issues

#### 1. Python Version Error

**Error**: `Python 3.11+ required`

**Solution**:
```bash
# Check version
python3 --version

# Install Python 3.11 if needed
# macOS
brew install python@3.11

# Ubuntu
sudo apt install python3.11

# Then recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Playwright Installation Error

**Error**: `playwright: command not found`

**Solution**:
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall Playwright
pip install playwright
playwright install chromium
playwright install-deps chromium
```

#### 3. Gmail Authentication Failed

**Error**: `SMTP authentication failed`

**Solution**:
- ✅ Verify you're using an **App Password**, not your regular password
- ✅ Make sure 2-Step Verification is enabled
- ✅ Check no extra spaces in password
- ✅ Regenerate app password if needed

#### 4. GitHub Actions Not Running

**Error**: Workflow doesn't run on schedule

**Solution**:
- ✅ Check Actions are enabled: Settings → Actions → Allow
- ✅ Verify workflow file is in `.github/workflows/`
- ✅ Check cron syntax is correct
- ✅ Remember: Scheduled workflows may have up to 10-minute delay
- ✅ Manual runs work even if scheduled runs don't

#### 5. Tests Failing

**Error**: Import errors or test failures

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Make sure you're in project root
cd /path/to/dps-monitor

# Run tests from project root
pytest tests/ -v
```

#### 6. No Emails Received

**Possible causes**:

1. **Check spam folder** - GitHub emails might be filtered
2. **Verify SMTP settings** - Make sure all SMTP secrets are set correctly
3. **Check Gmail account** - Make sure app password is active
4. **Review logs** - Check GitHub Actions logs for email errors

**Debug steps**:
```bash
# Test email locally
cd src
python -c "from utils.notifier import EmailNotifier; import os; from dotenv import load_dotenv; load_dotenv(); notifier = EmailNotifier({}); print(notifier.send_test_email())"
```

---

## Next Steps

Once everything is set up:

1. **Monitor GitHub Actions**
   - Check Actions tab daily
   - Review logs for any errors
   - Ensure workflow runs successfully

2. **Set Up Phone Notifications**
   - Enable Gmail notifications on phone
   - Set as high priority
   - Enable sound/vibration

3. **Be Ready to Book**
   - Keep documents ready
   - Have DPS website bookmarked
   - Be prepared to respond within minutes

4. **Test the System**
   - Run manual workflow runs occasionally
   - Verify emails are received
   - Check logs are being generated

---

## Getting Help

If you're still stuck:

1. Check the main [README.md](README.md)
2. Review [GitHub Actions logs](https://github.com/yourusername/dps-monitor/actions)
3. Search [Issues](https://github.com/yourusername/dps-monitor/issues)
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Your Python version
   - Operating system

---

## Security Checklist

Before going live:

- [ ] Repository is set to Private
- [ ] `.env` file is NOT committed (in `.gitignore`)
- [ ] All secrets are added to GitHub
- [ ] Using Gmail App Password (not main password)
- [ ] Tested workflow runs successfully
- [ ] Email notifications working
- [ ] No sensitive data in commit history

---

**You're all set! Good luck with your appointment!** 🍀
