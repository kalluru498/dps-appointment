# Quick Setup Guide

## 5-Minute Setup Checklist

### ☑️ Step 1: Gmail App Password (2 minutes)
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already on)
3. Search "App passwords"
4. Create one for "Mail" - name it "DPS Monitor"
5. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)

### ☑️ Step 2: Create GitHub Repository (1 minute)
1. Go to: https://github.com/new
2. Name: `dps-appointment-monitor`
3. **Make it Private** (for security)
4. Create repository

### ☑️ Step 3: Upload Files (1 minute)
Upload these 5 files to your repository:
- `check_appointments.py`
- `.github/workflows/monitor_appointments.yml` (create `.github/workflows/` folder first)
- `requirements.txt`
- `README.md`
- `check_appointments_simple.py`

### ☑️ Step 4: Add Secrets (3 minutes)

Go to: Settings → Secrets and variables → Actions → New repository secret

Add these **12 secrets** (copy your information from screenshots):

| Secret Name | Your Value |
|------------|------------|
| FIRST_NAME | `Naveen` |
| LAST_NAME | `Kumar` |
| DOB | `07/21/2000` |
| SSN_LAST4 | `[8587]` |
| PHONE | `(940) 758-4860` |
| EMAIL | `naveenreddyusa498@gmail.com` |
| ZIP_CODE | `76201` |
| NOTIFY_EMAIL | `naveenreddyusa498@gmail.com` |
| SMTP_USER | `naveenreddyusa498@gmail.com` |
| SMTP_PASSWORD | `[Naveen11625071kK@498]` |
| SMTP_SERVER | `smtp.gmail.com` |
| SMTP_PORT | `587` |

### ☑️ Step 5: Enable Actions (30 seconds)
1. Go to "Actions" tab
2. Click "I understand, enable them"

### ☑️ Step 6: Test It! (1 minute)
1. Actions → "Texas DPS Appointment Monitor"
2. Click "Run workflow"
3. Watch it run!

## ✅ You're Done!

The monitor will now run automatically every 5 minutes and email you when appointments are found!

---

## 🔔 What Happens Next?

1. **Every 5 minutes**: Script checks for appointments
2. **When found**: You get an email instantly
3. **Your action**: Go to https://www.txdpsscheduler.com immediately
4. **Login**: Enter your info and complete OTP verification
5. **Book**: Select your appointment quickly!

---

## ⚠️ Important Note About OTP

The Texas DPS website requires OTP (one-time password) verification via SMS/email after login. This means:

- ✅ Script CAN detect if appointments are available
- ❌ Script CANNOT complete booking automatically
- ✅ You'll get instant notification when slots open
- ✅ You can then book manually (much better than constant refreshing!)

---

## 📱 Get Mobile Notifications

For instant phone alerts:

1. **Turn on Gmail notifications** on your phone
2. **Allow notifications** from Gmail app
3. **Set as priority**: Star emails from GitHub
4. Now you'll get instant push notifications!

---

## 🐛 Troubleshooting

### Not receiving emails?
1. Check spam folder
2. Verify SMTP_PASSWORD is the 16-character app password
3. Check Actions logs for errors

### Actions not running?
1. Check Settings → Actions → Enable
2. Verify workflow file is in `.github/workflows/`
3. Wait 5 minutes for first scheduled run

### Script errors?
1. Go to Actions tab
2. Click failed run
3. Read error logs
4. Check all secrets are set correctly

---

## 📊 Monitoring Your Monitor

Check if it's working:
1. Go to "Actions" tab
2. See green checkmarks ✅ = Working
3. Red X ❌ = Error (click to see details)
4. Check runs every few hours to ensure it's working

---

## 💡 Pro Tips

1. **Check inbox regularly** when you know slots typically open (mornings, afternoons)
2. **Have your documents ready** so you can book immediately when notified
3. **Keep browser logged in** to TxDPS scheduler to save time
4. **Set up Gmail filters** to make DPS notifications stand out
5. **Tell friends!** Help other international students by sharing this tool

---

## 🆘 Need Help?

Common issues and solutions are in the main README.md file.

---

**Good luck with your appointment! 🍀**
