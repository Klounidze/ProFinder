#!/usr/bin/env python
import os
import sys

project_dir = '/home/x29233ku/pfinder.site"
sys.path.insert(0, project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
print("✅ Статические файлы собраны!")