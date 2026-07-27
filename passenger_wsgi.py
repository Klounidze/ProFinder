import sys
import os

# Путь к вашему проекту на сервере
project_dir = '/home/ваш-логин/ваш-сайт.рф'
sys.path.insert(0, project_dir)

# Активируем виртуальное окружение
activate_this = project_dir + '/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()