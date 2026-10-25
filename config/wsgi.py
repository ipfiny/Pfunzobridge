import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Production database initialization fail-safe (e.g. Render, Railway ephemeral containers)
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM auth_user LIMIT 1;")
except Exception:
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        # Avoid crashing startup if migration fails here; gunicorn start command will report
        pass
