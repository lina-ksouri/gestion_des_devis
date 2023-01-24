"""Django's command-line utility for administrative tasks."""
import os
import sys

cwd = os.getcwd()
INTERP = cwd+'/hayaenv/bin/python'
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(cwd)
sys.path.append(cwd + '/hayaenv')

sys.path.insert(0,cwd+'/hayaenv/bin')
sys.path.insert(0,cwd+'/hayaenv/lib/python3.5/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "backend.settings_prod"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
