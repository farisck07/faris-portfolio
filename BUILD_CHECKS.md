# Build verification

- Python 3.12.14 / Django 5.2.19. Exact tested package versions: requirements-tested.txt.
- All 17 Django tests passed. Coverage includes owner access, edits to each content type, draft visibility, CSRF, template escaping, image validation and setup.
- Django system check passed. Migration consistency check passed. Static asset collection passed.
- Clean source setup created a fresh database and a single owner. Repeating setup preserved the owner and content.
- Desktop design inspected in Chrome. Narrow layouts inspected in 390 px and 320 px frames, with no horizontal overflow after the mobile adjustment.
- Mobile menu, Escape-to-close, project filters, empty filter state and motion pause control verified in Chrome.
- Browser review used HTML rendered from the Django templates; server behavior was tested with Django's test client.
- Production deployment check reported only the two documented opt-in HSTS subdomain and preload warnings.

This package has not been deployed to live Python hosting. The Windows launcher was reviewed but not executed on Windows; this build was validated on Linux. Fill in your real email, projects, qualifications and certifications after setup.
