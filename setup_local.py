"""First-run local setup. Does not overwrite an existing environment or owner."""
import os
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parent
environment = ROOT / ".env"
if not environment.exists():
    with environment.open("x", encoding="utf-8") as handle:
        handle.write(
            f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n"
            "DJANGO_DEBUG=true\n"
            "DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,[::1]\n"
        )
    try:
        environment.chmod(0o600)
    except OSError:
        pass
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.conf import settings
from django.core.management import call_command
from portfolio.models import Owner

if not settings.DEBUG:
    raise SystemExit("setup_local.py is for local development. Use migrate and create_owner directly on your configured production host.")
call_command("migrate")
call_command("seed_portfolio")
if not Owner.objects.exists():
    call_command("create_owner")
else:
    print("Owner already configured. Existing account kept.")
print("\nReady. Run: python manage.py runserver\nPortfolio: http://127.0.0.1:8000/\nYour editor: http://127.0.0.1:8000/admin/")
