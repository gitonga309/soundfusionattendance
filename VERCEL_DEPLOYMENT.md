# DEPLOY TO VERCEL (FREE) - Django Attendance System

## ⭐ Is Vercel Right For Your Django App?

**Vercel** is traditionally for frontend, but you can use **Vercel Functions** (serverless) to run Django.

### Pros:
✅ Completely FREE (no credit card needed)
✅ Auto-scaling
✅ No servers to manage
✅ Custom domain included
✅ Automatic deployments from GitHub
✅ Built-in CI/CD

### Cons:
❌ Cold start (first request takes 3-5 seconds)
❌ Request timeout: 60 seconds
❌ Limited to serverless architecture
❌ Not ideal for background jobs
❌ Database must be external

### Best For:
- Small teams
- Low traffic applications
- Development/testing
- Proof of concepts

---

## OPTION 1: VERCEL + NEON (PostgreSQL - FREE)

### Step 1: Create Neon Database (Free PostgreSQL)

1. Go to https://neon.tech
2. Sign up (free)
3. Create a project
4. Copy the connection string (looks like: `postgresql://user:password@host/database`)

### Step 2: Prepare Your Django App for Vercel

Create `vercel.json` in your project root:

```json
{
  "builds": [
    {
      "src": "soundfusion_attendance/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    },
    {
      "src": "public/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/public/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "soundfusion_attendance/wsgi.py"
    }
  ]
}
```

### Step 3: Create `api/` Directory for Serverless Functions

```bash
mkdir api
```

Create `api/index.py`:

```python
import os
import sys
import django

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soundfusion_attendance.settings")
django.setup()

# Import your WSGI app
from soundfusion_attendance.wsgi import application

def handler(request):
    return application(request)
```

### Step 4: Update `soundfusion_attendance/settings.py`

```python
# At the top, add:
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Allowed hosts
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Database - Use Neon PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=0  # Important for serverless
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public/static')

# For Vercel
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://yourdomain.com"
]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
```

### Step 5: Create `.vercelignore`

```
db.sqlite3
*.pyc
__pycache__
venv
.env
.env.local
.git
node_modules
```

### Step 6: Create `.env.local` (Local Testing)

```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host/database
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.vercel.app
```

### Step 7: Update `requirements.txt`

```bash
pip install gunicorn python-decouple whitenoise
pip freeze > requirements.txt
```

Make sure it includes:
```
Django==5.1.4
gunicorn
whitenoise
dj-database-url
psycopg2-binary
python-decouple
```

### Step 8: Create `manage.py` for Vercel

Create a small script to run migrations on Vercel:

```bash
echo "from django.core.management import execute_from_command_line
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundfusion_attendance.settings')
execute_from_command_line(['manage.py', 'migrate'])" > vercel_migrate.py
```

### Step 9: Deploy to Vercel

1. **Push to GitHub:**
```bash
git add .
git commit -m "Vercel deployment setup"
git push origin main
```

2. **Go to https://vercel.com**
3. **Sign up with GitHub**
4. **Import your repository**
5. **Fill in environment variables:**
   - `DEBUG`: `False`
   - `SECRET_KEY`: (generate new one)
   - `DATABASE_URL`: (from Neon)
   - `ALLOWED_HOSTS`: `yourdomain.vercel.app,www.yourdomain.com`

6. **Click "Deploy"**
7. **After deployment, run migrations:**

```bash
# Via Vercel CLI
vercel env pull
python manage.py migrate --settings=soundfusion_attendance.settings
```

---

## OPTION 2: VERCEL + MONGODB ATLAS (FREE)

### Advantages:
- Completely free NoSQL database
- No schema migrations needed
- Easier for serverless

### Disadvantages:
- Would need to refactor Django models to work with MongoDB
- Not recommended for this project

---

## OPTION 3: VERCEL + RAILWAY (RECOMMENDED)

### Better Alternative - Use Railway Instead of Vercel

If you want serverless with Django, **Railway.app** is much better:

1. Go to https://railway.app
2. Sign up (free)
3. Deploy from GitHub
4. Railway auto-detects Django
5. Add PostgreSQL (free)
6. Done!

**Cost:** Free credits + cheap pay-as-you-go after  
**Difficulty:** ⭐ Easiest  
**Time:** 2 minutes

---

## ⚠️ VERCEL LIMITATIONS FOR DJANGO

### Function Timeout
- Maximum 60 seconds per request
- Cold start: 3-5 seconds
- Not suitable for long-running tasks

### Database Connections
- Can't persist connections
- Must use connection pooling
- Neon allows free connection pooling

### Storage
- No persistent local storage
- Use S3 or external storage for uploads
- Database must be external

### Best Practices for Vercel + Django

```python
# settings.py optimizations for Vercel
DATABASES['default']['CONN_MAX_AGE'] = 0  # Don't persist connections
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Use caching for frequently accessed data
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Reduce query count
# Use select_related() and prefetch_related()
# Already done in your code ✅
```

---

## QUICK COMPARISON: FREE OPTIONS

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| **Vercel** | Free | 15 min | Frontend + lite backend |
| **Railway** | Free | 2 min | Django apps |
| **Render** | Free | 5 min | Full Django apps |
| **Heroku** | Paid | 5 min | Reliable Django |
| **Neon** | Free | 1 min | Database only |
| **Supabase** | Free | 1 min | Database only |

---

## MY RECOMMENDATION

### For Your Django App (FREE):

**Use Railway.app** - It's 10x easier than Vercel for Django:

```bash
1. Go to https://railway.app
2. Sign up with GitHub
3. Create project from GitHub
4. Railway detects Django automatically
5. Add PostgreSQL plugin
6. Set environment variables
7. Deploy (automatic)
8. Free forever with credits
```

### If You Really Want Vercel:

Use the setup above with Neon database, but be aware of:
- Cold starts
- Timeout limits
- Connection issues

---

## FULL VERCEL + NEON SETUP (Step-by-Step)

### Step 1: Create Neon Database

```bash
# 1. Go to https://neon.tech
# 2. Sign up (GitHub)
# 3. Create project
# 4. Copy connection string: postgresql://user:password@region.neon.tech/database
```

### Step 2: Install Vercel CLI

```bash
npm install -g vercel
# or
choco install vercel
```

### Step 3: Configure Project

```bash
cd C:\Users\alexk\Desktop\SoundFusionLimited

# Create vercel.json
cat > vercel.json << 'EOF'
{
  "builds": [
    {
      "src": "soundfusion_attendance/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "soundfusion_attendance/wsgi.py"
    }
  ],
  "env": {
    "DEBUG": "False",
    "PYTHONUNBUFFERED": "1"
  }
}
EOF

# Create .vercelignore
cat > .vercelignore << 'EOF'
db.sqlite3
*.pyc
__pycache__
venv
.git
EOF
```

### Step 4: Deploy

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No (first time)
# - Project name? soundfusion-attendance
# - Framework? Django
# - Output directory? ./
```

### Step 5: Set Environment Variables

```bash
# Via Vercel CLI
vercel env add DATABASE_URL
# Paste your Neon connection string

vercel env add SECRET_KEY
# Generate and paste new secret key

vercel env add ALLOWED_HOSTS
# Enter: soundfusion-attendance.vercel.app

# Redeploy
vercel --prod
```

### Step 6: Run Migrations

```bash
# Create a temporary script
cat > migrate.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundfusion_attendance.settings')
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate'])
EOF

python migrate.py
```

### Step 7: Create Superuser

```bash
# You'll need to do this after deployment via environment
# Or create via admin interface manually

# For now, create locally:
python manage.py createsuperuser
```

---

## TROUBLESHOOTING VERCEL + DJANGO

### Error: "No module named 'django'"
```bash
# Make sure requirements.txt includes Django
pip freeze > requirements.txt
git push
```

### Error: "Static files not found"
```python
# In settings.py
STATIC_URL = '/public/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public/static')

# Collect static files
python manage.py collectstatic --noinput
git add public/
git push
```

### Error: "Database connection timeout"
```python
# In settings.py
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=15000'
}

# Add connection pooling:
# Neon dashboard → Connection pooling → PgBouncer
```

### Error: "Cold start too slow"
- This is normal for Vercel (3-5 seconds)
- Use Railway for faster cold starts
- Add caching to reduce queries

---

## FINAL RECOMMENDATION

### Best Free Django Hosting:

1. **Railway.app** ⭐⭐⭐⭐⭐
   - Easiest setup
   - Good for Django
   - Free credits
   - Recommended!

2. **Render.com** ⭐⭐⭐⭐
   - Also very easy
   - Free tier available
   - Good reliability

3. **Vercel** ⭐⭐⭐
   - Better for frontend
   - Can work with Django
   - Requires more setup
   - Cold start delays

---

**My strong recommendation: Use Railway.app instead of Vercel for your Django app. It's simpler and better designed for Python/Django.**

If you still want to use Vercel, follow the steps above with Neon database. 🚀
