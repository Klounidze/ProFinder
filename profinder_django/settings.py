import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'ваш-секретный-ключ')

DEBUG = False  # ВАЖНО: False для продакшена

ALLOWED_HOSTS = [
    'pfinder.site'
  # Если есть subdomain
]

# База данных (используйте PostgreSQL или MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Или 'django.db.backends.mysql'
        'NAME': 'u3590216_pfinder_db',
        'USER': 'u3590216_profinder_user',
        'PASSWORD': 'LimebridgeGiY58ax!',
        'HOST': 'localhost',
        'PORT': '5432',  # Для MySQL: '3306'
    }
}

# Статика
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'  # или ваш SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ваш-email@yandex.ru'
EMAIL_HOST_PASSWORD = 'ваш-пароль'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Безопасность (настройте после установки SSL)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True