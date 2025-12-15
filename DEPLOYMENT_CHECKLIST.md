# PRE-DEPLOYMENT CHECKLIST

## ✅ Code Preparation

- [ ] Run `python system_test.py` - All tests pass ✅
- [ ] All migrations applied: `python manage.py showmigrations`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Update `requirements.txt`: `pip freeze > requirements.txt`
- [ ] Push code to GitHub

## ✅ Django Settings (settings.py)

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` stored in environment variable (generated)
- [ ] `ALLOWED_HOSTS` set to your domain
- [ ] `DATABASES` configured for PostgreSQL
- [ ] `STATIC_ROOT` pointing to correct directory
- [ ] `STATIC_URL = '/static/'`
- [ ] `WSGI_APPLICATION` is correct

## ✅ Security Settings

- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`
- [ ] Email backend configured (optional)

## ✅ Database

- [ ] PostgreSQL installed on server/platform
- [ ] Database created
- [ ] Database user created with correct permissions
- [ ] `DATABASE_URL` environment variable set
- [ ] Migrations applied: `python manage.py migrate`

## ✅ Static Files & Media

- [ ] `collectstatic` command successful
- [ ] Static files served by web server (not Django)
- [ ] Static files location accessible at `STATIC_URL`

## ✅ Admin User

- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Can login to `/admin/` dashboard
- [ ] Admin email verified (optional)

## ✅ Environment Variables Set

```
DEBUG=False
SECRET_KEY=<your-generated-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## ✅ Web Server / Gunicorn

- [ ] Gunicorn installed: `pip install gunicorn`
- [ ] Test locally: `gunicorn soundfusion_attendance.wsgi:application --bind 0.0.0.0:8000`
- [ ] Systemd service created (if self-hosting)
- [ ] Nginx configured as reverse proxy (if self-hosting)

## ✅ SSL Certificate

- [ ] HTTPS enabled (free via Let's Encrypt)
- [ ] Certificate valid and auto-renewing
- [ ] All HTTP traffic redirects to HTTPS

## ✅ Backups

- [ ] Database backup strategy defined
- [ ] Regular backup scheduled
- [ ] Test restore procedure works

## ✅ Monitoring

- [ ] Error logging configured
- [ ] Server monitoring in place (CPU, memory, disk)
- [ ] Uptime monitoring enabled
- [ ] Alert notifications configured

## ✅ Testing (Post-Deployment)

- [ ] Visit homepage: https://yourdomain.com/
- [ ] Register new user account
- [ ] Mark attendance
- [ ] View dashboard
- [ ] Admin panel working: https://yourdomain.com/admin/
- [ ] Static files loading (CSS, images)
- [ ] No console errors (check browser dev tools)

## ✅ Performance

- [ ] Database queries optimized (select_related, prefetch_related)
- [ ] Caching enabled
- [ ] Static file compression enabled (gzip)
- [ ] Database connection pooling configured

## ✅ Documentation

- [ ] README.md updated with deployment info
- [ ] Admin users documented
- [ ] Emergency procedures documented
- [ ] Contact information provided

---

## PLATFORM-SPECIFIC CHECKLISTS

### For Render.com:
- [ ] GitHub account connected
- [ ] Repository pushed to GitHub
- [ ] Procfile exists
- [ ] runtime.txt exists (python-3.13.1)
- [ ] Environment variables set in Render dashboard
- [ ] PostgreSQL addon provisioned
- [ ] Auto-deploy on push enabled

### For Digital Ocean:
- [ ] Droplet created (Ubuntu 22.04)
- [ ] SSH key configured
- [ ] Security groups configured
- [ ] Domain DNS pointing to droplet IP
- [ ] PostgreSQL installed
- [ ] Gunicorn and Nginx installed
- [ ] SSL certificate provisioned
- [ ] Firewall rules set (80, 443 open)

### For Heroku:
- [ ] Heroku CLI installed
- [ ] Logged in to Heroku
- [ ] App created
- [ ] Procfile exists
- [ ] PostgreSQL add-on enabled
- [ ] Buildpacks configured
- [ ] Config vars set
- [ ] Dyno type chosen

### For Railway.app:
- [ ] GitHub connected
- [ ] Project created
- [ ] PostgreSQL plugin added
- [ ] Environment variables set
- [ ] Domain configured
- [ ] Deploy button triggered

---

## DEPLOYMENT COMMAND SEQUENCE

```bash
# 1. Prepare local environment
python system_test.py

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations (will run on server automatically too)
python manage.py migrate

# 4. Create superuser (or will do on server)
python manage.py createsuperuser

# 5. Freeze requirements
pip freeze > requirements.txt

# 6. Commit and push
git add .
git commit -m "Pre-deployment update"
git push origin main

# 7. Deploy on chosen platform (follow platform-specific instructions)
```

---

## QUICK START (RENDER.COM)

1. Create account at https://render.com
2. Connect GitHub
3. Click "New Web Service"
4. Select your repository
5. Fill in details:
   - Name: `soundfusion-attendance`
   - Start Command: `gunicorn soundfusion_attendance.wsgi:application`
6. Add environment variables
7. Provision PostgreSQL
8. Click "Create Web Service"
9. Wait 3-5 minutes for deployment
10. Visit your app URL

---

## COSTS AT A GLANCE

| Platform | Free? | Starting Cost | Best For |
|----------|-------|---------------|----------|
| Render | Yes | Free/$7/mo | Beginners |
| Railway | Yes | Free/$5+/mo | Quick setup |
| Heroku | No | $7/month | Reliability |
| Digital Ocean | No | $4-6/month | Control |
| PythonAnywhere | Yes | Free/£5/mo | Python |

---

Ready to deploy? Pick a platform and start! 🚀
