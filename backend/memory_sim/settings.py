
# Django settings for the MemorySim project
# This file contains all the configuration settings for the Django application

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # /backend

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # image be stored in backend/media/
ABSOLUTE_BASE_URL = "http://127.0.0.1:9000" # backend runs at port 9000

# SECURITY WARNING: keep the secret key used in production secret!
# TODO: Move this to environment variables in production
SECRET_KEY = 'django-insecure-please_change_this_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# List of allowed hosts that can serve this Django application
ALLOWED_HOSTS = ['*']

# CORS settings for development - allows all origins for frontend integration
CORS_ALLOW_ALL_ORIGINS = True

# Application definition - Django apps installed in this project
INSTALLED_APPS = [
    # Default Django admin interface
    'django.contrib.admin',
    # Django authentication system
    'django.contrib.auth',
    # Django content types framework
    'django.contrib.contenttypes',
    # Django sessions framework
    'django.contrib.sessions',
    # Django messaging framework
    'django.contrib.messages',
    # Static files handling
    'django.contrib.staticfiles',
    # CORS headers for cross-origin requests
    'corsheaders',
    # Custom API app for handling API endpoints
    'api',
    # Core app for basic functionality
    'core',
    # Shared models and utilities
    'shared',
    'images',
    'django_dramatiq',
]

# dramatiq
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": "redis://localhost:6379/0",
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
    ]
}

DRAMATIQ_TASKS_DATABASE = "default"


# Middleware stack - processes requests and responses in order
MIDDLEWARE = [
    # CORS middleware must be at the top to handle cross-origin requests
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Security middleware for security headers
    'django.middleware.security.SecurityMiddleware',
    # Session middleware for user sessions
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF protection middleware
    'django.middleware.csrf.CsrfViewMiddleware',
    # Authentication middleware for user authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Messages middleware for displaying messages to users
    'django.contrib.messages.middleware.MessageMiddleware',
    # Clickjacking protection middleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration module
ROOT_URLCONF = 'memory_sim.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Template directories - looks for templates in the templates folder
        'DIRS': [BASE_DIR / 'templates'],
        # Allow apps to have their own template directories
        'APP_DIRS': True,
        'OPTIONS': {
            # Context processors that add variables to template context
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application configuration for deployment
WSGI_APPLICATION = 'memory_sim.wsgi.application'

# Database configuration (using SQLite for development)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'memorysim_db',
        'USER': 'memorysim_user',
        'PASSWORD': 'password123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation settings for user authentication
AUTH_PASSWORD_VALIDATORS = [
    {
        # Prevents passwords that are too similar to user information
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Enforces minimum password length
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Prevents commonly used passwords
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Prevents purely numeric passwords
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
# Set timezone to Brisbane for Australian deployment
TIME_ZONE = 'Australia/Brisbane'
# Enable internationalization
USE_I18N = True
# Use timezone-aware datetimes
USE_TZ = True

# Static files configuration (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
