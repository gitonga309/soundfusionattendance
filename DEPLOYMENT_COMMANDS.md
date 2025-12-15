# DEPLOYMENT QUICK COMMANDS

## PREPARE FOR DEPLOYMENT

```bash
# 1. Test system
python system_test.py

# 2. Update requirements
pip freeze > requirements.txt

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Test in production mode (locally)
export DEBUG=False
python manage.py runserver
# Then set back to True

# 7. Push to GitHub
git add .
git commit -m "Pre-deployment"
git push origin main
```

---

## DEPLOY TO RENDER.COM (EASIEST)

```bash
# 1. Go to https://render.com
# 2. Sign up with GitHub
# 3. Click "New Web Service"
# 4. Select your GitHub repo
# 5. Fill form:
#    Name: soundfusion-attendance
#    Start Command: gunicorn soundfusion_attendance.wsgi:application
# 6. Click "Create Web Service"
# Done! Renders builds and deploys automatically
```

---

## DEPLOY TO HEROKU

```bash
# 1. Install Heroku CLI
choco install heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create soundfusion-attendance

# 4. Deploy
git push heroku main

# 5. Run migrations
heroku run python manage.py migrate

# 6. Create superuser
heroku run python manage.py createsuperuser

# 7. Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=soundfusion-attendance.herokuapp.com

# View logs
heroku logs --tail
```

---

## DEPLOY TO RAILWAY.APP

```bash
# 1. Go to https://railway.app
# 2. Click "New Project"
# 3. Select "Deploy from GitHub"
# 4. Authorize and select repo
# 5. Railway auto-detects Django
# 6. Add PostgreSQL plugin
# 7. Set environment variables
# 8. Deploy!
```

---

## DEPLOY TO DIGITAL OCEAN

```bash
# On your local machine:
# 1. Get droplet IP address
# 2. SSH into droplet
ssh root@YOUR_DROPLET_IP

# On the droplet:
# 1. Update system
apt update && apt upgrade -y

# 2. Install dependencies
apt install python3 python3-pip python3-venv postgresql nginx gunicorn -y

# 3. Clone repository
cd /home
git clone https://github.com/YOUR_USERNAME/soundfusionattendance.git
cd soundfusionattendance

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE soundfusion;
CREATE USER soundfusion WITH PASSWORD 'your_password';
ALTER ROLE soundfusion SET client_encoding TO 'utf8';
ALTER ROLE soundfusion SET default_transaction_isolation TO 'read committed';
ALTER ROLE soundfusion SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE soundfusion TO soundfusion;
\q

# 7. Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=your_domain.com
DATABASE_URL=postgresql://soundfusion:your_password@localhost:5432/soundfusion
EOF

# 8. Run migrations
python manage.py migrate

# 9. Collect static files
python manage.py collectstatic --noinput

# 10. Create superuser
python manage.py createsuperuser

# 11. Test gunicorn
gunicorn --bind 0.0.0.0:8000 soundfusion_attendance.wsgi

# 12. Create systemd service
sudo nano /etc/systemd/system/soundfusion.service
# [Paste service file from DEPLOYMENT_GUIDE.md]
# Press Ctrl+O, Enter, Ctrl+X

# 13. Start service
sudo systemctl daemon-reload
sudo systemctl start soundfusion
sudo systemctl enable soundfusion

# 14. Configure Nginx
sudo nano /etc/nginx/sites-available/soundfusion
# [Paste nginx config from DEPLOYMENT_GUIDE.md]
# Press Ctrl+O, Enter, Ctrl+X

# 15. Enable site
sudo ln -s /etc/nginx/sites-available/soundfusion /etc/nginx/sites-enabled/

# 16. Test nginx
sudo nginx -t

# 17. Restart nginx
sudo systemctl restart nginx

# 18. Install SSL (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com

# Done! Your site is live at https://your_domain.com
```

---

## GENERATE SECRET KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## TEST DEPLOYED SITE

```bash
# Test homepage
curl https://yourdomain.com

# Test admin panel
curl https://yourdomain.com/admin/

# Test API response times
time curl https://yourdomain.com/dashboard/
```

---

## COMMON ISSUES & FIXES

### Static files not loading
```bash
# SSH to server and run:
python manage.py collectstatic --noinput
systemctl restart soundfusion
```

### Database connection error
```bash
# Check DATABASE_URL is set correctly
heroku config  # For Heroku
# or
echo $DATABASE_URL  # For other servers
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Permission denied errors
```bash
# Fix permissions
sudo chown -R www-data:www-data /home/soundfusionattendance
sudo chmod -R 755 /home/soundfusionattendance
```

---

## MONITORING AFTER DEPLOYMENT

```bash
# Check Heroku logs
heroku logs --tail

# Check Render logs
# Go to Render Dashboard → Your App → Logs

# Check Digital Ocean logs
sudo journalctl -u soundfusion -f

# Check Nginx errors
sudo tail -f /var/log/nginx/error.log

# Check app database
heroku pg  # Heroku
# or
psql -U soundfusion -d soundfusion  # Digital Ocean
```

---

## BACKUP DATABASE

```bash
# Heroku
heroku pg:backups:capture
heroku pg:backups:download

# Digital Ocean
pg_dump -U soundfusion -d soundfusion > backup.sql

# Render
# Automatic backups included
```

---

## ROLLBACK IN CASE OF ISSUES

```bash
# Heroku
git revert HEAD
git push heroku main

# Render
# Go to Dashboard → Deployments → Select previous version

# Digital Ocean
git revert HEAD
git push origin main
systemctl restart soundfusion
```

---

## SCALE YOUR APP

### More Traffic?
- **Render:** Upgrade to Paid tier
- **Heroku:** Increase dyno size
- **Railway:** Auto-scales
- **Digital Ocean:** Upgrade droplet

### More Storage?
- **Render:** Upgrade disk
- **Heroku:** Upgrade database plan
- **Railway:** Upgrade database
- **Digital Ocean:** Upgrade droplet

---

## SECURITY CHECKLIST

```bash
# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Run security check
python manage.py check --deploy

# Update dependencies
pip install --upgrade pip
pip list --outdated
```

---

## SUPPORT RESOURCES

- **Render:** https://render.com/docs
- **Heroku:** https://devcenter.heroku.com
- **Railway:** https://docs.railway.app
- **Digital Ocean:** https://docs.digitalocean.com
- **Django:** https://docs.djangoproject.com

---

Choose a platform above and run the commands! 🚀
