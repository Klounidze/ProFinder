#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import traceback

# Путь к проекту на сервере
project_dir = '/home/x92933ku/pfinder.site'
sys.path.insert(0, project_dir)

# Указываем настройки Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

# Включаем вывод ошибок
sys.stderr = sys.stdout

try:
    from django.core.management import execute_from_command_line

    print("Content-Type: text/plain; charset=utf-8\n")
    print("🔄 Начинаем миграции...")

    # Выполняем миграции
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])

    print("\n✅ Миграции выполнены успешно!")

except Exception as e:
    print("Content-Type: text/plain; charset=utf-8\n")
    print(f"❌ ОШИБКА: {e}")
    print("\n📋 Подробный трейсбек:")
    print(traceback.format_exc())