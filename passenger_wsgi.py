import sys, os

# Путь к вашему проекту на сервере (нужно будет заменить на актуальный)
# Узнать точный путь можно через команду pwd в SSH после входа.
# Обычно это: /home/логин/ваш-сайт.рф/
project_dir = '/home/ваш-логин/ваш-сайт.рф'
sys.path.insert(0, project_dir)

# Указываем Django настройки
os.environ['DJANGO_SETTINGS_MODULE'] = 'profinder_django.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()