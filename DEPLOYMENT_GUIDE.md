# 🚀 DEPLOYMENT GUIDE - Sound Fusion Limited Attendance System

## Quick Summary
Your Django application is production-ready and can be deployed to several hosting platforms.

---

## Option 1: RENDER.COM (Recommended - Free Tier Available)

### Step 1: Prepare Your Code
```bash
# 1. Create a Procfile (already exists)
# 2. Create runtime.txt (already exists)
# 3. Ensure requirements.txt is up to date
pip freeze > requirements.txt
```

### Step 2: Push to GitHub
```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/soundfusionattendance.git
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to https://render.com
2. Sign up with GitHub account
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Fill in the form:
   - **Name:** soundfusion-attendance
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn soundfusion_attendance.wsgi:application`
6. Add Environment Variables:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here (generate one!)
   ALLOWED_HOSTS=soundfusion-attendance.onrender.com
   DATABASE_URL=postgresql://... (if using PostgreSQL)
   ```
7. Choose PostgreSQL database (optional but recommended)
8. Click "Create Web Service"

### Estimated Cost
- **Free tier:** Up to 750 hours/month (enough for low usage)
- **Paid:** Starts at $7/month

---

## Option 2: HEROKU (Paid Option)

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or install via chocolatey:
choco install heroku-cli
```

### Step 2: Login and Create App
```bash
heroku login
heroku create soundfusion-attendance
```

### Step 3: Deploy
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Step 4: Set Environment Variables
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=soundfusion-attendance.herokuapp.com
```

### Estimated Cost
- **Paid:** Starts at $7/month minimum

---

## Option 3: PYTHONANYWHERE (Easiest for Beginners)

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Sign up (free account available)
3. Create a web app → Django

### Step 2: Upload Code
1. Use their file editor or upload via bash console
2. Configure WSGI file
3. Set static files location

### Step 3: Configure Settings
- Set `ALLOWED_HOSTS` to your pythonanywhere domain
- Set `DEBUG=False`
- Create superuser via bash console

### Estimated Cost
- **Free:** Limited
- **Paid:** Starts at £5/month

---

## Option 4: RAILWAY.APP (Modern & Simple)

### Step 1: Sign Up
1. Go to https://railway.app
2. Connect GitHub

### Step 2: Deploy
1. Click "New Project"
2. Select "GitHub Repo"
3. Choose your repo
4. Railway auto-detects Django
5. Add PostgreSQL plugin
6. Set environment variables

### Estimated Cost
- **Free credit:** $5/month
- **Paid:** Pay-as-you-go, usually $5-15/month for small apps

---

## Option 5: DIGITAL OCEAN (Full Control)

### Step 1: Create Droplet
1. Go to https://www.digitalocean.com
2. Create Ubuntu 22.04 droplet (smallest: $4/month)

### Step 2: SSH and Install
```bash
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Python and PostgreSQL
apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx gunicorn -y
```

### Step 3: Clone and Setup
```bash
cd /home
git clone https://github.com/YOUR_USERNAME/soundfusionattendance.git
cd soundfusionattendance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Database
```bash
sudo -u postgres psql
CREATE DATABASE soundfusion;
CREATE USER soundfusion WITH PASSWORD 'password';
ALTER ROLE soundfusion SET client_encoding TO 'utf8';
ALTER ROLE soundfusion SET default_transaction_isolation TO 'read committed';
ALTER ROLE soundfusion SET default_transaction_deferrable TO on;
ALTER ROLE soundfusion SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE soundfusion TO soundfusion;
\q
```

### Step 5: Configure Django
```bash
# Edit settings.py
nano soundfusion_attendance/settings.py

# Add to ALLOWED_HOSTS:
ALLOWED_HOSTS = ['your_domain.com', 'www.your_domain.com', 'your_ip']

# Change DEBUG to False
DEBUG = False

# Set DATABASE_URL or configure DATABASES
```

### Step 6: Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Step 7: Configure Gunicorn
```bash
# Test gunicorn
gunicorn --bind 0.0.0.0:8000 soundfusion_attendance.wsgi

# Create systemd service file
sudo nano /etc/systemd/system/soundfusion.service
```

Add:
```
[Unit]
Description=Sound Fusion Attendance System
After=network.target

[Service]
User=root
WorkingDirectory=/home/soundfusionattendance
ExecStart=/home/soundfusionattendance/venv/bin/gunicorn --bind 0.0.0.0:8000 soundfusion_attendance.wsgi
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start soundfusion
sudo systemctl enable soundfusion
```

### Step 8: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/soundfusion
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/soundfusionattendance/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/soundfusion /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 9: Add SSL (Free via Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

### Estimated Cost
- **Droplet:** $4-6/month
- **Total:** $4-6/month

---

## QUICK COMPARISON TABLE

| Platform | Cost | Difficulty | Best For |
|----------|------|-----------|----------|
| **Render** | Free/$7+ | ⭐ Easy | Beginners, small teams |
| **Railway** | Free/$5+ | ⭐ Easy | Quick deployment |
| **PythonAnywhere** | Free/£5+ | ⭐ Easy | Python projects |
| **Heroku** | $7+ | ⭐⭐ Medium | Proven reliability |
| **Digital Ocean** | $4-6 | ⭐⭐⭐ Hard | Full control, learning |
| **AWS** | Variable | ⭐⭐⭐ Hard | Enterprise |

---

## IMPORTANT: Pre-Deployment Checklist

Before deploying, ensure:

✅ **1. Generate Secret Key**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
Store this safely in environment variables (NOT in code)

✅ **2. Update settings.py**
```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.getenv('SECRET_KEY')  # From environment variable

# Use PostgreSQL in production
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://user:password@localhost/dbname',
        conn_max_age=600
    )
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {...}
```

✅ **3. Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

✅ **4. Create Superuser**
```bash
python manage.py createsuperuser
```

✅ **5. Test in Production Mode Locally**
```bash
DEBUG = False
python manage.py runserver
```

✅ **6. Use PostgreSQL (NOT SQLite)**
SQLite is NOT recommended for production. Use PostgreSQL.

✅ **7. Set Up HTTPS**
Always use SSL certificates (free via Let's Encrypt)

✅ **8. Environment Variables**
Never hardcode secrets. Use .env file locally and platform settings in production:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## RECOMMENDED DEPLOYMENT PATH

### For Small Teams / Local Use:
1. **Start:** Render.com (free tier)
2. **Scale:** Railway.app (pay-as-you-go)
3. **Mature:** Digital Ocean (full control)

### For Enterprise:
1. AWS Lambda
2. Google Cloud
3. Azure App Service

---

## POST-DEPLOYMENT

After deployment:

1. **Create admin account:**
   ```bash
   # On the hosting platform's console/terminal
   python manage.py createsuperuser
   ```

2. **Access admin panel:**
   ```
   https://yourdomain.com/admin/
   ```

3. **Monitor logs:**
   - Render: Dashboard → Logs
   - Digital Ocean: SSH and check journal
   - Heroku: `heroku logs --tail`

4. **Set up email (optional):**
   - Configure SMTP in settings.py
   - Use SendGrid, Mailgun, or AWS SES

5. **Back up database regularly:**
   - Use platform's backup features
   - Or pg_dump for PostgreSQL

---

## TROUBLESHOOTING

### Static Files Not Loading
```python
# In settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
```

### Database Connection Error
- Check `DATABASE_URL` environment variable
- Verify database credentials
- Ensure database exists

### Gunicorn Failed to Start
```bash
# Test gunicorn locally
gunicorn soundfusion_attendance.wsgi:application --bind 0.0.0.0:8000
```

### 500 Server Error
- Check server logs
- Ensure all migrations applied
- Verify DEBUG=False doesn't hide errors (temporarily)

---

## NEED HELP?

For specific platform questions:
- **Render:** render.com/docs
- **Railway:** docs.railway.app
- **Heroku:** devcenter.heroku.com
- **Digital Ocean:** docs.digitalocean.com

Your project is ready to deploy! Choose a platform and follow the steps above.
