# Muhammed Faris C K — Django Portfolio

A fresh, database-backed portfolio with a charcoal and violet design, a programming-themed CSS 3D laptop, and a private editing studio for one owner.

## Start on Windows

Install Python 3.12 or newer and select **Add Python to PATH**. Extract the ZIP fully, open the `faris_portfolio` folder, and double-click **START_WINDOWS.bat**.

The launcher creates a virtual environment, installs dependencies, creates the local database, and asks you to choose your owner username and password. Password typing is hidden. Keep the terminal open while using the site.

- Portfolio: http://127.0.0.1:8000/
- Your editor: http://127.0.0.1:8000/admin/

Only the account you create through `create_owner` can use the editor. There is no default password and no public signup. Stop the server with Ctrl+C.

## Start on macOS / Linux

From a terminal in this folder, run:

    bash start.sh

Python 3.12+ and an internet connection are needed for the first dependency installation.

## Manual setup

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\activate

Or on macOS/Linux:

    source .venv/bin/activate

Then:

    python -m pip install -r requirements.txt
    python setup_local.py
    python manage.py runserver

`setup_local.py` creates a random local secret in `.env`, applies the included migrations, and creates starter content and your owner account. Running it again preserves your account and existing content. It is a local development helper, not a production deployment command.

## Make it yours

Sign in to `/admin/`, then use the editor:

| Section | What you can change |
| --- | --- |
| Profile & contact details | Name, developer role, headline, intro, about text, email, location, availability, GitHub, LinkedIn and CV link |
| Projects | Title, summary, description, screenshot, accessible image description, technologies, category, live URL, source URL, featured status and display order |
| Passions | Title, description, symbol and order |
| Skills | Skill name, category, description, optional level and order |
| Certifications | Title, issuer, issue date, description, credential ID, verification URL and order |
| Qualifications | Qualification, institution, period, description and order |

New content starts as a draft. Check **Published** to show it on the website. Uncheck it to hide it, including project detail pages. **Position** controls order; smaller numbers appear first. Featured projects appear before other projects. Bulk publish and draft actions are available.

The profile uses your supplied name and Django/Python role. The about text, passions and initial skills are editable starter copy: review them before publishing your site. Projects, qualifications and certifications start empty so no unverified achievements appear. Set your real email and links to activate the contact and social buttons; blank links stay hidden. Add a public CV URL to show the résumé button.

Project images accept JPG, PNG and WebP up to 5 MB. Images are public portfolio assets; draft status hides the project page but is not an access restriction for a previously shared media URL. Do not upload confidential documents. Certifications use a verification URL rather than requiring a certificate file upload.

## Owner access

- Admin authorization checks the bound owner on every admin request. Other staff accounts and even unbound superusers cannot use this studio.
- The owner binding is not editable through the browser. Users and groups are not exposed in this admin site.
- Account creation is available only through the server-side `create_owner` command. `createsuperuser` alone does not grant portfolio editing access.
- Use a strong, unique password and keep your hosting account and database private. Someone with server or database control can change the application outside the browser.
- To reset your own password from your terminal:

      python manage.py changepassword YOUR_USERNAME

Do not delete the database to reset a password; that also deletes your content.

## Included functionality

- Responsive desktop and mobile layouts, including an accessible mobile menu.
- Real CSS 3D laptop, pointer tilt, floating programming labels and a motion pause control.
- Automatic respect for reduced-motion preferences.
- Project category filtering and separate, linkable project pages.
- Django models, migrations, image uploads, owner-only administration and draft/publish controls.
- CSRF protection, template escaping, password validation and production security settings.
- Self-hosted Manrope font. No frontend CDN, API key or paid 3D service is required.

## Verify the build

After setup, run:

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test portfolio
    python manage.py collectstatic --noinput

The test suite covers all five content editors, profile changes, non-owner access, owner login, draft visibility, CSRF, HTML escaping, upload validation, setup, ordering and single-owner binding.

`requirements.txt` permits compatible updates. `requirements-tested.txt` records the exact versions used for this build on Python 3.12. For a reproducible install, use that file instead. Continue applying supported security updates over time.

## Deploy on Python hosting

This is a Django application and needs a Python host with persistent storage. A static-only web host cannot run its editor or database. Local `runserver` is for development only.

1. Upload the source, including `portfolio/migrations`. Exclude `.env`, `.venv`, test data and caches.
2. Install the Python dependencies. Set environment variables on your host:

       DJANGO_DEBUG=false
       DJANGO_SECRET_KEY=<a-new-random-secret-at-least-40-characters>
       DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
       DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
       DJANGO_DATA_DIR=/your/persistent/data
       DJANGO_MEDIA_ROOT=/your/persistent/media

   Generate a new key with `python -c "import secrets; print(secrets.token_urlsafe(64))"`. Never commit it.

3. If your trusted proxy terminates HTTPS and strips user-supplied forwarded headers, set `DJANGO_TRUST_PROXY=true`. Otherwise leave it false and configure HTTPS at the application server. Incorrect proxy configuration can create redirect loops.
4. Run `python manage.py migrate`, `python manage.py seed_portfolio`, and `python manage.py create_owner`. If you are transferring your existing database, keep its owner binding and skip creating a new owner.
5. Run `python manage.py collectstatic --noinput` and `python manage.py check --deploy` with production settings.
6. Start a production WSGI server, for example on Linux:

       gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -

7. Put it behind HTTPS. Configure your web server or host to serve `/media/` from `DJANGO_MEDIA_ROOT` with directory listing disabled. WhiteNoise serves collected static CSS, JS, fonts and admin assets, **not** user-uploaded media. The included `deploy/nginx.conf.example` shows the relevant proxy and media settings.
8. Add rate limiting at the host or proxy for `/admin/login/`. Back up the database and media directory. Keep both on a persistent volume; ephemeral filesystems will lose your content when redeployed. SQLite suits a single-host personal portfolio; use PostgreSQL if you later need multiple application hosts.

HTTPS cookies and a one-year HSTS policy are enabled when debug is off. HSTS subdomains and preload are separate opt-in environment flags (`DJANGO_HSTS_SUBDOMAINS`, `DJANGO_HSTS_PRELOAD`): enable them only after verifying HTTPS for all relevant domains. The deployment check can warn about these intentional opt-outs.

## Project structure

    config/                 Django configuration and routes
    portfolio/              Models, private admin, views and tests
    portfolio/migrations/   Database schema
    portfolio/management/   Owner creation and starter content commands
    templates/              Public portfolio, project page and private studio
    static/portfolio/       CSS, JavaScript, favicon and local font
    deploy/                 Example production proxy configuration
    setup_local.py          Safe first-run development setup

The downloadable source contains no login credentials, private secret, populated database or uploaded personal files. Add your own content after setup.

## References and font license

- Django admin: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
- Django deployment checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- Manrope is distributed under the SIL Open Font License. Its license is included at `static/portfolio/fonts/OFL.txt`; source: https://github.com/google/fonts/tree/main/ofl/manrope.
