#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Добавляем пути для поиска модулей
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Если Django установлен в папке проекта
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'django'))

# Включаем вывод ошибок
sys.stderr = sys.stdout

try:
    # Указываем настройки Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

    from django.core.management import execute_from_command_line

    print("Content-Type: text/plain\n")
    print("🔄 Начинаем миграции...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("✅ Миграции выполнены успешно!")

except Exception as e:
    print("Content-Type: text/plain\n")
    print(f"❌ ОШИБКА: {e}")
    import traceback

    print("\n📋 Подробный трейсбек:")
    print(traceback.format_exc())