# HEROKU DEPLOYMENT - Step-by-Step Guide

## ⏱️ Total Time: 15 Minutes

Your Django app is ready to deploy to Heroku! Follow these exact steps.

---

## STEP 1: Install Heroku CLI (One-time setup)

### On Windows (PowerShell):
```powershell
choco install heroku-cli
# or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### On Mac:
```bash
brew tap heroku/brew && brew install heroku
```

### On Linux:
```bash
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
```

**Verify installation:**
```bash
heroku --version
```

---

## STEP 2: Generate SECRET_KEY for Production

Run this command to generate a new SECRET_KEY:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** - you'll need it in Step 4.

---

## STEP 3: Push Code to GitHub

Make sure all your code is on GitHub:

```bash
git status
git add .
git commit -m "Prepare for Heroku deployment"
git push origin main
```

**Verify:** Go to https://github.com/gitonga309/soundfusionattendance and confirm code is there.

---

## STEP 4: Create Heroku Account

1. Go to **https://heroku.com**
2. Click **"Sign up"**
3. Create account (email, password)
4. Verify email
5. Login to Heroku dashboard

---

## STEP 5: Login to Heroku CLI

In your terminal:

```bash
heroku login
```

This opens browser → sign in → returns to terminal

---

## STEP 6: Create Heroku App

```bash
heroku create soundfusion-attendance
```

**Output will show:**
```
Creating app... done, ⬢ soundfusion-attendance
https://soundfusion-attendance.herokuapp.com/ | https://git.heroku.com/soundfusion-attendance.git
```

**Your live URL will be:** `https://soundfusion-attendance.herokuapp.com`

---

## STEP 7: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:mini --app soundfusion-attendance
```

This automatically sets `DATABASE_URL` environment variable.

**Verify:**
```bash
heroku config --app soundfusion-attendance
```

You should see `DATABASE_URL=postgresql://...`

---

## STEP 8: Set Environment Variables

Set all required environment variables:

```bash
heroku config:set DEBUG=False --app soundfusion-attendance
heroku config:set SECRET_KEY="your-secret-key-here" --app soundfusion-attendance
heroku config:set ALLOWED_HOSTS="soundfusion-attendance.herokuapp.com" --app soundfusion-attendance
```

**Verify they're set:**
```bash
heroku config --app soundfusion-attendance
```

---

## STEP 9: Deploy!

### Option A: Deploy from Heroku CLI (Quick)

```bash
heroku git:remote -a soundfusion-attendance
git push heroku main
```

Wait 2-3 minutes for deployment...

### Option B: Deploy from GitHub (Recommended)

1. Go to **https://dashboard.heroku.com**
2. Click your app **soundfusion-attendance**
3. Go to **Deploy** tab
4. Under **Deployment method**, select **GitHub**
5. Click **Connect to GitHub**
6. Search **soundfusionattendance** repo
7. Click **Connect**
8. Click **Enable Automatic Deploys** (optional - auto-deploy when you push)
9. Click **Deploy Branch** → **main**

Wait 2-5 minutes for deployment...

---

## STEP 10: Run Migrations

After deployment succeeds, run migrations:

```bash
heroku run python manage.py migrate --app soundfusion-attendance
```

This creates database tables.

---

## STEP 11: Create Admin User (Superuser)

```bash
heroku run python manage.py createsuperuser --app soundfusion-attendance
```

**Answer prompts:**
```
Username: admin
Email: your@email.com
Password: (create secure password)
```

---

## STEP 12: Test Your App!

1. **Homepage:** https://soundfusion-attendance.herokuapp.com
2. **Dashboard:** https://soundfusion-attendance.herokuapp.com/dashboard/
3. **Admin:** https://soundfusion-attendance.herokuapp.com/admin/
4. **Register:** https://soundfusion-attendance.herokuapp.com/register/

---

## ✅ Verification Checklist

- [ ] Heroku CLI installed
- [ ] Created Heroku account
- [ ] App created: `soundfusion-attendance`
- [ ] PostgreSQL database added
- [ ] Environment variables set (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- [ ] Code deployed (migrations ran)
- [ ] Superuser created
- [ ] Homepage loads
- [ ] Admin panel accessible

---

## 📊 Common Commands

### View app status:
```bash
heroku logs -t --app soundfusion-attendance
```

### Restart app:
```bash
heroku restart --app soundfusion-attendance
```

### View environment variables:
```bash
heroku config --app soundfusion-attendance
```

### Scale workers:
```bash
heroku ps:scale web=1 --app soundfusion-attendance
```

### Clear database and restart:
```bash
heroku pg:reset DATABASE --app soundfusion-attendance
heroku run python manage.py migrate --app soundfusion-attendance
```

---

## 🚀 Auto-Deploy Setup (Optional)

After initial deployment, enable automatic deploys:

1. Go to **https://dashboard.heroku.com**
2. Select **soundfusion-attendance**
3. Go to **Deploy** tab
4. Under **Automatic deploys**, select **main** branch
5. Click **Enable Automatic Deploys**

Now, every time you `git push origin main`, Heroku automatically deploys! 🎉

---

## ⚠️ Troubleshooting

### Error: "Application error"
```bash
# Check logs
heroku logs -t --app soundfusion-attendance
```

### Error: "No such table"
```bash
# Migrations didn't run - run them manually
heroku run python manage.py migrate --app soundfusion-attendance
```

### Error: "SECRET_KEY not set"
```bash
# Set environment variables
heroku config:set SECRET_KEY="your-key" --app soundfusion-attendance
heroku restart --app soundfusion-attendance
```

### Database connection error
```bash
# Reset database
heroku pg:reset DATABASE --app soundfusion-attendance
heroku run python manage.py migrate --app soundfusion-attendance
heroku run python manage.py createsuperuser --app soundfusion-attendance
```

### App keeps crashing
```bash
# View detailed logs
heroku logs --tail --app soundfusion-attendance
# Common issues: missing dependencies (add to requirements.txt), env vars not set
```

---

## 💰 Cost

**Heroku Pricing:**
- Web dyno: **Free** (with limitations) or **$7/month** (production)
- PostgreSQL: **Free** (with 10GB limit) or **$20+/month** (production)

For small projects: **FREE tier is sufficient!**

---

## 🎯 You're Done!

Your Django app is now **LIVE** on Heroku! 🎉

**Share your URL:** https://soundfusion-attendance.herokuapp.com

Users can now:
- ✅ Register accounts
- ✅ Mark attendance
- ✅ View balance
- ✅ Admins manage users

---

## 📚 Next Steps

1. **Test all features** on live site
2. **Share with team** - give them the URL
3. **Set up backups** (optional):
   ```bash
   heroku pg:backups:schedule --at "02:00 UTC" --app soundfusion-attendance
   ```
4. **Monitor app** - check logs daily
5. **Add custom domain** (optional, paid feature)

---

## 🆘 Need Help?

### View real-time logs:
```bash
heroku logs -t --app soundfusion-attendance
```

### Run Django shell:
```bash
heroku run python manage.py shell --app soundfusion-attendance
```

### Execute custom command:
```bash
heroku run python manage.py [command] --app soundfusion-attendance
```

---

**Questions? Check Heroku docs:** https://devcenter.heroku.com/articles/django-app-configuration

**Your app is ready! Deploy now! 🚀**
