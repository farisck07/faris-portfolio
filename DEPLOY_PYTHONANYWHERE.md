# Free PythonAnywhere deployment (Django portfolio)

This project is configured for a **single-owner Django portfolio** with SQLite and public project screenshots. PythonAnywhere's free filesystem persists across web app reloads; it is not a substitute for backups. The free tier has usage/storage limits and requires web app renewal.

## 1. Account and repository

Create a free Beginner account at https://www.pythonanywhere.com/ and open **Consoles > Bash**. On the US system your hostname is `USERNAME.pythonanywhere.com`; on the EU system it may be `USERNAME.eu.pythonanywhere.com`. **Use the exact hostname shown in the Web tab**, not a guessed one.

```bash
git clone https://github.com/farisck07/faris-portfolio.git
cd faris-portfolio
mkvirtualenv --python=python3.12 farisportfolio
pip install --no-cache-dir -r requirements.txt
```

Use the same available Python version for the virtualenv and web app. If Python 3.12 is not available, select a supported Python >= 3.12 and use that version consistently.

## 2. Production environment, SQLite, and uploads

From the project folder in a Bash console, **replace** the placeholder below with the actual hostname shown in PythonAnywhere:

```bash
export PA_HOST="YOUR_USERNAME.pythonanywhere.com"
python - <<'PY'
from pathlib import Path
from secrets import token_urlsafe
import os

host = os.environ["PA_HOST"].strip()
if "://" in host or "/" in host or " " in host or "." not in host:
    raise SystemExit("PA_HOST must be a hostname, not a URL.")
base = Path.home()
db_dir = base / "faris-portfolio-data"
media_dir = base / "faris-portfolio-media"
db_dir.mkdir(mode=0o700, exist_ok=True)
media_dir.mkdir(mode=0o700, exist_ok=True)
env = Path(".env")
if env.exists():
    raise SystemExit("Existing .env found; not overwriting secrets.")
env.write_text(
    f"DJANGO_SECRET_KEY={token_urlsafe(64)}\n"
    "DJANGO_DEBUG=false\n"
    f"DJANGO_ALLOWED_HOSTS={host}\n"
    f"DJANGO_CSRF_TRUSTED_ORIGINS=https://{host}\n"
    "DJANGO_SSL_REDIRECT=false\n"
    "DJANGO_TRUST_PROXY=false\n"
    f"DJANGO_DATA_DIR={db_dir}\n"
    f"DJANGO_MEDIA_ROOT={media_dir}\n"
)
env.chmod(0o600)
print("Created private production configuration and persistent directories for", host)
PY
```

**Why `DJANGO_SSL_REDIRECT=false`?** Enable **Force HTTPS** in the PythonAnywhere Web tab instead. That makes the front-end proxy enforce HTTPS, including for static files; it avoids a potential Django redirect loop when Django cannot reliably see the original HTTPS scheme. The secure session/CSRF cookies remain enabled because `DJANGO_DEBUG=false`. Do not enable `DJANGO_TRUST_PROXY` unless you have verified that your hosting proxy reliably removes incoming `X-Forwarded-Proto` and sets its own trusted value.

Keep `.env`, the database, and user media **out of GitHub**. These directories are separate from the repository so a `git pull` will not overwrite them.

## 3. Set up the owner and assets

Run from `~/faris-portfolio` with the virtualenv active (use `workon farisportfolio` if needed):

```bash
python manage.py migrate
python manage.py seed_portfolio
python manage.py create_owner
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The `create_owner` command prompts for a strong, unique username and password. Only this bound owner may log in to the private Django admin at `/admin/`. Do **not** run `setup_local.py` in production: it is development-only.

The deployment check can warn about intentionally disabled HSTS subdomain/preload flags. Review any other warnings; do not switch DEBUG on to work around errors.

## 4. Configure the Web tab

Choose **Add a new web app > Manual configuration** and the *same Python version* as your virtualenv. Do not choose Django quickstart; this repo is an existing application.

Set:
- **Source code and working directory:** `/home/YOUR_USERNAME/faris-portfolio`
- **Virtualenv:** `/home/YOUR_USERNAME/.virtualenvs/farisportfolio`

Open the **WSGI configuration file linked on the Web tab** (not `config/wsgi.py`) and replace its template with:

```python
import os
import sys
from pathlib import Path

path = str(Path.home() / "faris-portfolio")
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Set up **Static files** mappings on the Web tab:

| URL prefix | Directory |
| --- | --- |
| `/static/` | `/home/YOUR_USERNAME/faris-portfolio/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/faris-portfolio-media` |

Replace `YOUR_USERNAME` with your real PythonAnywhere username (case-sensitive). The `/media/` mapping serves **public** portfolio images; never upload private documents or secret files to project images.

Enable **Force HTTPS** on the Web tab and click **Reload**.

## 5. Test and maintain

Open your live HTTPS homepage and `https://YOUR_HOSTNAME/admin/`. Test private login, changes to the profile, publishing a new project, and uploading an image. Refresh and reload the web app to verify edits and the image persist. Review the Web tab's error log if there is an error.

When your GitHub code changes:

```bash
cd ~/faris-portfolio
workon farisportfolio
git pull --ff-only
pip install --no-cache-dir -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Click **Reload** on the Web tab after updating. Do not run `seed_portfolio` to replace your existing content; it is safe/idempotent but normally unnecessary once initial content exists.

**Backups:** Regularly download copies of `~/faris-portfolio-data/db.sqlite3` and `~/faris-portfolio-media/` to secure storage. Use SQLite's backup API or a consistent snapshot (not a copy during active writes). Keep backups private. Check disk usage: the free plan is limited to **512 MiB** total, including environments and assets. Renew the free web app in PythonAnywhere before its one-month expiry.

**Security:** Choose a strong admin password; prevent public access to the database and secrets; install dependency security updates; consider adding login throttling and MFA if you plan on using the service long-term.
