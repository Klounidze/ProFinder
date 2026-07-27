#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

print("Content-Type: text/plain\n")

try:
    import django
    print(f"✅ Django версия: {django.get_version()}")
    print(f"✅ Путь к Django: {django.__file__}")
except ImportError as e:
    print(f"❌ Django не найден: {e}")
    print("\n📋 Пути поиска Python:")
    for path in sys.path:
        print(f"  - {path}")