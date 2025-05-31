import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# 1. SECURITY / SECRET_KEY / DEBUG
# ----------------------------
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("DJANGO SECRET_KEY environment variable not set. Aborting.")

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS must come from an env var; default to localhost for local dev
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1').split(' ')

# ----------------------------
# 2. APPLICATION DEFINITION
# ----------------------------
INSTALLED_APPS = [
    # 'daphne',   # Remove or comment out if you do NOT need Channels in production
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'channels', # Remove if you’re not using WebSockets in production
    'rest_framework',
    'users',
    'sessions',
    'recommendations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'peerlearn.urls'

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

# If you removed Channels, comment out these two lines:
# ASGI_APPLICATION = 'peerlearn.asgi.application'
WSGI_APPLICATION = 'peerlearn.wsgi.application'

# ----------------------------
# 3. DATABASE (Postgres via dj_database_url)
# ----------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR}/db.sqlite3",
        conn_max_age=600,
        ssl_require=False
    )
}

# If you truly need Channels in prod, configure channel layers here (e.g. Redis).
# Otherwise, comment it out:
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',
#     }
# }

# ----------------------------
# 4. AUTHENTICATION
# ----------------------------
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ----------------------------
# 5. PASSWORD VALIDATION
# ----------------------------
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

# ----------------------------
# 6. INTERNATIONALIZATION
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------
# 7. STATIC FILES (WhiteNoise)
# ----------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Let WhiteNoise compress and cache‐bust static files:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ----------------------------
# 8. MEDIA FILES
# ----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Note: On Render’s free tier, MEDIA_ROOT is ephemeral. Uploaded files will not persist across deploys.

# ----------------------------
# 9. DEFAULT PRIMARY KEY FIELD TYPE
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------
# 10. CSRF TRUSTED ORIGINS (Adjust locally / remove if not on Replit)
# ----------------------------
# You can leave these for local dev or Replit if needed, but Render will ignore them:
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'https://*.replit.dev',
    'https://*.replit.app',
    'https://*.replit.co',
]
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# ----------------------------
# 11. LOGIN / LOGOUT REDIRECTS
# ----------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
