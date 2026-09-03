from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'brothers-cafe-tirupattur-secret-key-2024-change-in-production'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# ── APPS ──────────────────────────────────────────────────────────────────────
# cloudinary + cloudinary_storage are only added when env vars are present,
# so the app starts normally locally without those packages installed.
_cloudinary_configured = all([
    os.environ.get('CLOUDINARY_CLOUD_NAME'),
    os.environ.get('CLOUDINARY_API_KEY'),
    os.environ.get('CLOUDINARY_API_SECRET'),
])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'restaurant',
] + (['cloudinary', 'cloudinary_storage'] if _cloudinary_configured else [])

# ── MIDDLEWARE ────────────────────────────────────────────────────────────────
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

ROOT_URLCONF = 'brothers_cafe.urls'

# ── TEMPLATES ─────────────────────────────────────────────────────────────────
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

WSGI_APPLICATION = 'brothers_cafe.wsgi.application'

# ── DATABASE (Supabase PostgreSQL) ────────────────────────────────────────────
# Locally uses SQLite. In production set DATABASE_URL env var to your
# Supabase connection string (Transaction Pooler — port 6543).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

_db_url = os.environ.get('DATABASE_URL', '')
if _db_url and _db_url.startswith(('postgres', 'postgresql')):
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(
            default=_db_url,
            conn_max_age=600,
            ssl_require=True,
        )}
    except ImportError:
        pass

# ── AUTH ──────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = []

# ── INTERNATIONALISATION ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── STATIC FILES (WhiteNoise) ─────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'restaurant' / 'static'] if (BASE_DIR / 'restaurant' / 'static').exists() else []
STATIC_ROOT = os.path.join(str(BASE_DIR), 'staticfiles')

# ── CLOUDINARY (image storage) ────────────────────────────────────────────────
# Set these three env vars in your Render / Railway dashboard:
#   CLOUDINARY_CLOUD_NAME   your-cloud-name
#   CLOUDINARY_API_KEY      123456789012345
#   CLOUDINARY_API_SECRET   your-api-secret
# _cloudinary_configured is defined above alongside INSTALLED_APPS

if _cloudinary_configured:
    import cloudinary
    cloudinary.config(
        cloud_name = os.environ['CLOUDINARY_CLOUD_NAME'],
        api_key    = os.environ['CLOUDINARY_API_KEY'],
        api_secret = os.environ['CLOUDINARY_API_SECRET'],
        secure     = True,
    )
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ['CLOUDINARY_CLOUD_NAME'],
        'API_KEY':    os.environ['CLOUDINARY_API_KEY'],
        'API_SECRET': os.environ['CLOUDINARY_API_SECRET'],
        'SECURE':     True,   # Always serve images over HTTPS
    }
else:
    # Local / no Cloudinary → serve media from disk
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage.CompressedManifestStaticFilesStorage"
                if os.environ.get("USE_COMPRESSED_STATIC") == "True"
                else "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    }

# ── MEDIA FILES (local fallback) ─────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(str(BASE_DIR), 'media')

# ── CSRF ──────────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://*.render.com',
    'https://*.onrender.com',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.0.0/16',
    'http://10.0.0.0/8',
]

# ── MISC ──────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── FILE UPLOAD SIZE LIMIT ─────────────────────────────────────────────────────
# Django default is 2.5 MB — images larger than that cause a "Network error"
# in the staff portal. Raising to 10 MB fixes the upload failure.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB

SHOP_NAME     = "Brothers Cafe"
SHOP_LOCATION = "Tirupattur"
SHOP_GSTIN    = "23278537256752"
