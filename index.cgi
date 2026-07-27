#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Добавляем путь к проекту
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Устанавливаем настройки Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

# Импортируем WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Запускаем через CGI
from flup.server.cgi import WSGIServer
WSGIServer(application).run()