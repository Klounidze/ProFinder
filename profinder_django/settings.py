"""
Django settings for profinder_django project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локальной разработки)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============= БЕЗОПАСНОСТЬ =============
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Если ключ не найден - выбрасываем ошибку (для продакшена)
if not SECRET_KEY:
    if os.environ.get('DEBUG', 'False') == 'True':
        # Только для разработки!
        SECRET_KEY = 'django-insecure-fallback-key-for-dev-only'
        print("⚠️  WARNING: Using fallback SECRET_KEY. DO NOT USE IN PRODUCTION!")
    else:
        raise ValueError("❌ DJANGO_SECRET_KEY environment variable is not set!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ============= НАСТРОЙКИ ДЛЯ SNAPDEPLOY =============
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.snapdeploy.app',  # Разрешает все поддомены snapdeploy.app
    '.containers.snapdeploy.app',  # Альтернативный вариант
    '.snapdeploy.com',  # Если используется
]

# Добавляем хост из SITE_URL если он задан
site_url = os.environ.get('SITE_URL')
if site_url:
    host = site_url.replace('https://', '').replace('http://', '').split('/')[0]
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://*.snapdeploy.app',
    'http://*.snapdeploy.app',
    'https://*.containers.snapdeploy.app',
    'http://*.containers.snapdeploy.app',
    'https://*.snapdeploy.com',
    'http://*.snapdeploy.com',
]

# Добавляем текущий SITE_URL
if site_url:
    CSRF_TRUSTED_ORIGINS.append(site_url)
    CSRF_TRUSTED_ORIGINS.append(site_url.replace('https://', 'http://'))

# Настройки для работы за прокси (Cloudflare, nginx и т.д.)
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============= БЕЗОПАСНОСТЬ В ПРОДАКШЕНЕ =============
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ============= ОСНОВНЫЕ НАСТРОЙКИ DJANGO =============
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
    'providers',
    'reviews',
    'chat',
    'telegram_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статических файлов
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'profinder_django.urls'

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
                'users.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'profinder_django.wsgi.application'

# ============= БАЗА ДАННЫХ =============
# Используем SQLite (просто и надежно)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============= ВАЛИДАЦИЯ ПАРОЛЕЙ =============
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============= ИНТЕРНАЦИОНАЛИЗАЦИЯ =============
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = False
USE_TZ = True

# ============= СТАТИЧЕСКИЕ ФАЙЛЫ =============
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============= МЕДИА ФАЙЛЫ =============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============= ДРУГИЕ НАСТРОЙКИ =============
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ============= EMAIL НАСТРОЙКИ =============
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# ============= ЛОГИРОВАНИЕ =============
LOG_DIR = BASE_DIR / 'logs'
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============= КАТЕГОРИИ ДЛЯ ПРОВАЙДЕРОВ =============
CATEGORIES = [
    'Электрика',
    'Сантехника',
    'Медицина',
    'Строительство',
    'Хэндимен',
    'Образование',
    'Хендмейд',
    'Дом',
    'IT и программирование',
    'Дизайн',
    'Фотография',
    'Переводы',
    'Юриспруденция',
    'Бухгалтерия',
    'Уборка',
    'Ремонт',
    'Доставка',
    'Красота и здоровье',
    'Фитнес и спорт',
]

# ============= ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ =============
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
