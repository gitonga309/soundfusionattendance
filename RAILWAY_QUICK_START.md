# RAILWAY DEPLOYMENT - QUICK START

## ⏱️ Time to Deploy: 5-10 Minutes

---

## STEP 1: Prepare Your Code

Your app is already configured! Just run this once:

```bash
pip freeze > requirements.txt
python manage.py collectstatic --noinput
```

Push to GitHub:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

---

## STEP 2: Create Railway Project

1. **Go to:** https://railway.app
2. **Sign up with GitHub** (free)
3. **Click "Create New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your `soundfusionattendance` repository**
6. **Railway will auto-detect Django!** ✅

---

## STEP 3: Add PostgreSQL Database

In your Railway dashboard:

1. **Click the "+" button** (Add plugin)
2. **Select "PostgreSQL"**
3. **Click "Create"**
4. Railway automatically links it via `DATABASE_URL` ✅

---

## STEP 4: Set Environment Variables

In Railway dashboard → **Variables tab**:

```
DEBUG=False
SECRET_KEY=generate-new-secret-key-using-command-below
RAILWAY_DOMAIN=your-app.railway.app
```

**Generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## STEP 5: Deploy!

1. **Click "Deploy"** button
2. **Wait for deployment** (2-5 minutes)
3. **Your app is live!** 🎉

Default URL: `https://yourappdomain.railway.app`

---

## STEP 6: Run First Migrations

After deployment succeeds:

```bash
# Railway automatically runs migrations via Procfile:release hook
# But if needed, you can run manually via CLI:

# Install Railway CLI
npm install -g @railway/cli
# or
choco install @railway/cli

# Login
railway login

# Connect to your project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser
```

---

## STEP 7: Create Admin User

Option A: Via CLI
```bash
railway run python manage.py createsuperuser
```

Option B: Via Web (if migrations ran)
1. Go to `https://yourappdomain.railway.app/admin/`
2. You may see a login error - this means you need to create superuser first
3. Use Option A

---

## ⚡ Your App Load Time

### Cold Start (First Request): **2-3 seconds**
- Normal for serverless
- Only happens after inactive period

### Subsequent Requests: **200-500ms**
- Same as development
- Fast and responsive

### Why It's Fast:
✅ Railway uses real servers (not serverless like Vercel)  
✅ No major cold start delays  
✅ PostgreSQL keeps data between deployments  
✅ Static files cached with WhiteNoise  

---

## 🌐 Access Your App

- **Homepage:** https://yourappdomain.railway.app
- **Dashboard:** https://yourappdomain.railway.app/dashboard/
- **Admin:** https://yourappdomain.railway.app/admin/
- **Register:** https://yourappdomain.railway.app/register/

---

## 📊 Monitoring & Logs

In Railway Dashboard:

1. **Deployments tab** - See all past deployments
2. **Logs tab** - Real-time server logs
3. **Metrics tab** - CPU, Memory, Requests
4. **Environment tab** - Manage variables

---

## 💰 Cost

**Completely FREE** with credits:
- Free credits ($5/month)
- Railway gives new users extra credits
- Perfect for small projects
- When credits run out: ~$0.60/day per app

---

## 🔄 Auto-Deploy on Git Push

Once connected to GitHub, **automatic deploys happen when you push to main**:

```bash
git add .
git commit -m "New feature"
git push origin main
# Deployment starts automatically in Railway dashboard!
```

---

## 🐛 Troubleshooting

### Error: "Railway deployment failed"

Check logs in Railway dashboard:
1. Go to **Logs tab**
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Database not created
   - Invalid SECRET_KEY

**Fix:**
```bash
# Reconnect variables
# Rebuild and redeploy in Railway dashboard
```

### Error: "502 Bad Gateway"

App is still starting. Wait 2-3 minutes and refresh.

### Error: "Static files not found"

Already handled! WhiteNoise is configured. Just redeploy:
```bash
git push origin main
```

### Error: "Can't connect to database"

1. Verify PostgreSQL plugin is added (Railway dashboard)
2. Check `DATABASE_URL` is set in environment
3. Rebuild deployment

---

## 📝 Deployment Checklist

Before deploying:

- [ ] Push latest code to GitHub
- [ ] `DEBUG=False` in environment variables
- [ ] New `SECRET_KEY` generated
- [ ] PostgreSQL plugin added
- [ ] `ALLOWED_HOSTS` includes your Railway domain
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] All migrations applied locally (`python manage.py migrate`)

---

## 🚀 Quick Deploy Command

After initial setup, pushing updates is one command:

```bash
git push origin main
# Done! Railway auto-deploys in 2-5 minutes
```

---

## 🎯 Next Steps

1. ✅ Deploy to Railway (today)
2. ✅ Create admin user
3. ✅ Test the app
4. ✅ Invite team members
5. Share the live URL with your team!

---

**Ready? Let's go!** 🚀

Go to https://railway.app and start deploying!
