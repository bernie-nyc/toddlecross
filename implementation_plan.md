# Implementation Plan - Batch 5: Production Readiness and Deployment

This plan outlines the changes to prepare the Toddlecross web application for production deployment.

## User Review Required

- None. The user has pre-approved execution of this plan.

---

## Proposed Changes

### Configuration and Dependencies

#### [MODIFY] [requirements.txt](file:///h:/My%20Drive/Toddlecross/requirements.txt)
- [ ] Add `psycopg2-binary` for PostgreSQL support in production.
- [ ] Add `whitenoise` to serve static files efficiently.
- [ ] Add `gunicorn` as the production WSGI application server.

#### [MODIFY] [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py)
- [ ] Add `STATIC_ROOT` setting for static files collection.
- [ ] Add WhiteNoise middleware to `MIDDLEWARE`.
- [ ] Configure proxy SSL and security headers (SSL redirect, secure session cookies, secure CSRF cookies).

---

### Deployment Files

#### [NEW] [Dockerfile](file:///h:/My%20Drive/Toddlecross/Dockerfile)
- [ ] Create a production Dockerfile to build and package the application inside a container.

#### [NEW] [entrypoint.sh](file:///h:/My%20Drive/Toddlecross/entrypoint.sh)
- [ ] Create a startup script to run database migrations, collect static assets, ensure the default superuser exists, and run gunicorn.

---

## Verification Plan

### Automated Tests
- [ ] Run `.venv\Scripts\python.exe manage.py test` to ensure settings alterations did not break any views or authentication.

### Manual Verification
- [ ] Test the static asset collector command locally using `.venv\Scripts\python.exe manage.py collectstatic --noinput` to verify that assets are written to the static root folder.
