import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-kajala-final-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',  # IMPORTANT - Sessions app
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'products',
    'cart',
    'orders',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # IMPORTANT - Session middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kajala.urls'

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
                'cart.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'kajala.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==================== SESSION SETTINGS (FIX) ====================
# Use cached_db for better session persistence
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Session age - 7 days (604800 seconds)
SESSION_COOKIE_AGE = 604800

# Don't expire session when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Save session on every request to keep it alive
SESSION_SAVE_EVERY_REQUEST = True

# Secure session cookie
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==================== AUTH SETTINGS ====================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'accounts.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== CONTACT INFO ====================
ADMIN_PHONE = '0748755636'
ADMIN_EMAIL = 'jeremiahkajala20@gmail.com'
SELLER_PAYMENT_NUMBER = '0748755636'
SELLER_ACCOUNT_NAME = 'Ramadhan Kajala'
SELLER_BANK = 'CRDB Bank'
SELLER_ACCOUNT_NUMBER = '0152703154600'

# ==================== EMAIL SETTINGS ====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jeremiahkajala20@gmail.com'
EMAIL_HOST_PASSWORD = 'oekv jbba jdpz enti'

# ==================== WHATSAPP ====================
WHATSAPP_NUMBER = '255748755636'

# ==================== AFRICA'S TALKING SMS ====================
AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY', '')