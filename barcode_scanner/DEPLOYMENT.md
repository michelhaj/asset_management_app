# Free Deployment Guide for Asset Management App

This guide covers deploying your Django asset management application to various free hosting platforms.

---

## Option 1: PythonAnywhere (Recommended)

**Why PythonAnywhere?**
- Truly free forever (no credit card required)
- Native Python/Django support
- SQLite works perfectly
- Simple setup process

### Step-by-Step Instructions

#### 1. Create Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Start running Python online" and sign up for a **Beginner (Free)** account
3. Confirm your email

#### 2. Open a Bash Console
1. Go to **Consoles** tab
2. Click **Bash** under "Start a new console"

#### 3. Clone Your Repository
```bash
git clone https://github.com/YOUR_USERNAME/asset_management_app.git
cd asset_management_app/barcode_scanner
```

#### 4. Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 assetenv
pip install -r requirements.txt
```

#### 5. Set Up the Database
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Create admin user
```

#### 6. Configure Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Click **Next** (accept the free domain)
4. Select **Manual configuration**
5. Select **Python 3.10**
6. Click **Next**

#### 7. Configure Paths (in Web tab)
Set these values (replace `yourusername` with your PythonAnywhere username):

| Setting | Value |
|---------|-------|
| Source code | `/home/yourusername/asset_management_app/barcode_scanner` |
| Working directory | `/home/yourusername/asset_management_app/barcode_scanner` |
| Virtualenv | `/home/yourusername/.virtualenvs/assetenv` |

#### 8. Edit WSGI Configuration
Click on the **WSGI configuration file** link and replace ALL contents with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/asset_management_app/barcode_scanner'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'barcode_scanner.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['PYTHONANYWHERE_USERNAME'] = 'yourusername'

# Activate your virtual env
activate_this = '/home/yourusername/.virtualenvs/assetenv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important:** Replace `yourusername` with your actual PythonAnywhere username!

#### 9. Configure Static Files
In the **Web** tab, scroll to **Static files** section and add:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/asset_management_app/barcode_scanner/staticfiles` |

#### 10. Reload and Test
1. Click the green **Reload** button at the top of the Web tab
2. Visit `https://yourusername.pythonanywhere.com`
3. Admin panel: `https://yourusername.pythonanywhere.com/admin/`

### Troubleshooting PythonAnywhere

**Error: "Something went wrong"**
- Check the **Error log** in Web tab
- Common issue: Wrong paths - verify all paths match your username

**Static files not loading**
- Run `python manage.py collectstatic` in Bash console
- Verify the static files mapping in Web tab

**Database errors**
- Run `python manage.py migrate` in Bash console

---

## Option 2: Render.com

**Pros:** Auto-deploys from GitHub, free PostgreSQL (90 days)
**Cons:** App sleeps after 15 min inactivity, cold starts

### Steps

1. Push code to GitHub
2. Sign up at [render.com](https://render.com)
3. Click **New +** → **Web Service**
4. Connect your GitHub repository
5. Configure:
   - **Name:** `asset-management`
   - **Root Directory:** `barcode_scanner`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn barcode_scanner.wsgi:application`

6. Add Environment Variables:
   - `DJANGO_DEBUG` = `False`
   - `DJANGO_SECRET_KEY` = (generate a secure key)
   - `PYTHON_VERSION` = `3.10.0`

7. Click **Create Web Service**

### Generate a Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Option 3: Railway.app

**Pros:** $5 free credits/month, easy GitHub integration
**Cons:** Limited free tier

### Steps

1. Sign up at [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway auto-detects Django and configures it
5. Add environment variables in **Variables** tab:
   - `DJANGO_DEBUG` = `False`
   - `DJANGO_SECRET_KEY` = (your secret key)

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_DEBUG` | Set to `False` in production | `False` |
| `DJANGO_SECRET_KEY` | Your secret key (keep private!) | `your-secret-key-here` |
| `PYTHONANYWHERE_USERNAME` | Your PythonAnywhere username | `johndoe` |

---

## Security Checklist for Production

- [ ] Set `DJANGO_DEBUG=False`
- [ ] Use a secure, unique `DJANGO_SECRET_KEY`
- [ ] Verify `ALLOWED_HOSTS` includes your domain
- [ ] Run `python manage.py check --deploy` to verify security
- [ ] Create a strong admin password
- [ ] Regularly backup your database

---

## Updating Your Deployed App

### PythonAnywhere
```bash
cd ~/asset_management_app
git pull origin main
cd barcode_scanner
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then click **Reload** in the Web tab.

### Render/Railway
Just push to GitHub - they auto-deploy!

---

## Free Tier Limitations

| Platform | Limitations |
|----------|-------------|
| PythonAnywhere | 512MB storage, limited CPU, 1 web app |
| Render | Sleeps after 15 min, spins down after inactivity |
| Railway | $5/month credits, then charges |

**Recommendation:** PythonAnywhere is best for a Django app with SQLite because:
- No sleep/spindown issues
- Native Django support
- SQLite works perfectly
- Truly free with no credit card
