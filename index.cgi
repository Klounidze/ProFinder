#!/usr/bin/env python3.11
import sys
import os

sys.path.insert(0, '/home/www/pfinder.site')

os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

from django.core.wsgi import get_wsgi_application
from flup.server.cgi import WSGIServer

application = get_wsgi_application()
WSGIServer(application).run()