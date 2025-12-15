"""
Django settings for soundfusion_attendance project.
"""


import os
import dj_database_url  # MAKE SURE THIS IMPORT IS AT TOP
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-3&!7*&s4o=$9j6_d4tq)geg#%%6wh*xmc5%l&yi2*nrci89mm3')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS for Railway & Heroku & local development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Railway.app deployment
RAILWAY_DOMAIN = os.environ.get('RAILWAY_DOMAIN')
if RAILWAY_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)
    ALLOWED_HOSTS.append(f"*.{RAILWAY_DOMAIN}")

# Heroku deployment
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')
if HEROKU_APP_NAME:
    ALLOWED_HOSTS.append(f"{HEROKU_APP_NAME}.herokuapp.com")

# Custom domain support
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soundfusion_attendance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'soundfusion_attendance.wsgi.application'


# Database Configuration
# Use MySQL for local development, PostgreSQL for production on Render
# Database Configuration - Force PostgreSQL on Render
# Database Configuration
import dj_database_url

# Default database (will be overridden by DATABASE_URL on Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with PostgreSQL on Render
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Caching Configuration for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sound-fusion-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Cache timeout (1 hour)
CACHE_TIMEOUT = 3600

# Database optimization
DATABASES['default']['CONN_MAX_AGE'] = 600  # Connection pooling
DATABASES['default']['OPTIONS'] = {
    'timeout': 20,
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True