# 🚀 DPS Monitor - START HERE!

## What is This?

An automated tool that monitors Texas DPS appointment availability using **Playwright** and sends you instant email notifications when slots open up.

## 📚 Documentation Index

**Read these in order:**

1. **[README.md](README.md)** - Start here! Overview and features
2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed step-by-step setup
3. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Technical documentation
4. **[QUICK_SETUP.md](QUICK_SETUP.md)** - 5-minute setup checklist (from Selenium version)

## 🎯 Quick Decision Tree

**Choose your path:**

### Path A: GitHub Actions (Recommended) ✅
**Best for**: Automated 24/7 monitoring, no laptop needed

**Steps**:
1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) → "GitHub Actions Setup"
2. Get Gmail App Password (5 minutes)
3. Fork repository
4. Add 12 GitHub Secrets
5. Enable Actions
6. Done! Runs every 5 minutes automatically

**Time**: 15 minutes setup, then automated

### Path B: Local Development 💻
**Best for**: Testing, customization, understanding the code

**Steps**:
1. Run `./quickstart.sh` (auto-setup script)
2. OR follow [SETUP_GUIDE.md](SETUP_GUIDE.md) → "Local Setup"
3. Edit `.env` file with your info
4. Run `cd src && python appointment_checker.py`

**Time**: 10 minutes setup, manual execution

## 📦 What's Included

```
✅ Playwright-based automation (modern & reliable)
✅ Comprehensive test suite (87% coverage)
✅ Email notifications with beautiful HTML
✅ GitHub Actions workflow (cloud-based)
✅ Error handling & screenshots
✅ Detailed logging
✅ Setup scripts for easy installation
```

## ⚡ Super Quick Start (3 Steps)

If you just want to get running ASAP:

```bash
# 1. Run setup script
./quickstart.sh

# 2. Edit your info
nano .env

# 3. Run checker
cd src && python appointment_checker.py
```

## 📖 File Guide

| File | What is it? | When to read |
|------|-------------|--------------|
| **README.md** | Complete overview | First |
| **SETUP_GUIDE.md** | Detailed setup steps | During setup |
| **PROJECT_STRUCTURE.md** | Technical details | For developers |
| **QUICK_SETUP.md** | 5-min checklist | Quick reference |

## 🔧 Key Files

### Essential Configuration
- `.env.example` → Copy to `.env` and fill in your details
- `requirements.txt` → Python dependencies

### Source Code
- `src/appointment_checker.py` → Main checker (320 lines)
- `src/utils/notifier.py` → Email notifications (180 lines)
- `src/utils/logger.py` → Logging (60 lines)

### Tests
- `tests/test_appointment_checker.py` → Checker tests (400+ lines)
- `tests/test_notifier.py` → Notifier tests (300+ lines)

### Scripts
- `quickstart.sh` → Automated setup script
- `run_tests.sh` → Test runner with options

### GitHub Actions
- `.github/workflows/monitor_appointments.yml` → Workflow definition

## 🎓 Understanding the Project

### Architecture
```
GitHub Actions (every 5 min)
    ↓
appointment_checker.py
    ↓
Playwright Browser → DPS Website
    ↓
Extract Appointments
    ↓
notifier.py → Email Alert → You!
```

### Technology Stack
- **Python 3.11+** - Modern async/await support
- **Playwright** - Reliable browser automation
- **Pytest** - Comprehensive testing
- **GitHub Actions** - Free cloud automation
- **SMTP** - Email notifications

## ⚠️ Important Notes

1. **OTP Limitation**: The tool can detect appointments but cannot book them automatically due to OTP verification. You'll need to complete booking manually after receiving the alert.

2. **Free Tier**: GitHub Actions provides 2,000 free minutes/month (private repos) or unlimited (public repos).

3. **Privacy**: Use a private repository to protect your personal information.

4. **App Password**: You MUST use a Gmail App Password, not your regular password.

## 🆘 Quick Help

### Problem: Tests failing
```bash
pip install -r requirements.txt
playwright install chromium
pytest tests/ -v -m "not integration"
```

### Problem: No emails received
1. Check spam folder
2. Verify Gmail App Password (16 chars)
3. Check GitHub Actions logs for errors

### Problem: GitHub Actions not running
1. Settings → Actions → Enable
2. Verify workflow file exists
3. Try manual run first

## 📞 Getting Help

1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) → Troubleshooting section
2. Review [GitHub Actions logs](https://github.com/yourusername/dps-monitor/actions)
3. Read [README.md](README.md) → Troubleshooting
4. Create an issue with error details

## ✅ Success Checklist

Before you're done:

- [ ] Read README.md
- [ ] Followed SETUP_GUIDE.md
- [ ] Gmail App Password created
- [ ] .env file configured (local) OR GitHub Secrets added (Actions)
- [ ] Tests pass: `./run_tests.sh -u`
- [ ] Checker runs successfully
- [ ] Test email received
- [ ] GitHub Actions enabled (if using)
- [ ] Repository set to Private (recommended)

## 🎯 Expected Results

**When working correctly**:
- Checks run every 5 minutes (GitHub Actions) or manually (local)
- You receive HTML emails when appointments found
- Logs show successful execution
- No errors in GitHub Actions

**When appointments found**:
- Instant email notification with:
  - Location name (Denton)
  - Next available date
  - List of available dates
  - Direct booking link
- JSON file saved in `results/` directory
- Success logged

## 🚀 Next Steps

1. **Start with README.md** - Understand what this is
2. **Follow SETUP_GUIDE.md** - Get it running
3. **Test it** - Run tests and manual check
4. **Deploy to GitHub Actions** - Let it run automatically
5. **Enable mobile notifications** - Gmail app on phone
6. **Be ready** - Have documents ready to book quickly

---

## 💡 Pro Tips

- Enable Gmail push notifications on your phone for instant alerts
- Keep your documents ready so you can book immediately
- Check GitHub Actions logs daily to ensure it's running
- Test the system with a manual workflow run first
- Consider setting up multiple notification methods

---

**Ready to start? Begin with [README.md](README.md)!** 📖

**Need quick setup? Jump to [SETUP_GUIDE.md](SETUP_GUIDE.md)!** ⚡

**Good luck getting your appointment!** 🍀
