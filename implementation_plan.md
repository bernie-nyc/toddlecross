# Implementation Plan — Batch 1: SSO & Access Gating

This plan outlines the changes to implement strict view-gating and refine the login/logout user flow.

## User Review Required

> [!IMPORTANT]
> **Secure-by-Default Architecture**:
> - We will enable Django's built-in `LoginRequiredMiddleware` so that all views are protected by default.
> - We will set `LOGIN_URL = '/'` in settings. This ensures that any unauthenticated access to a protected page redirects to the home/login page.
> - We will exempt public LTI endpoints and the root `home_view` using the `@login_not_required` decorator.
> - We will create a custom logout confirmation page using the glassmorphic style to replace the default django-allauth logout page.

---

## Proposed Changes

### Configuration

#### [MODIFY] [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py)
- Add `'django.contrib.auth.middleware.LoginRequiredMiddleware'` to `MIDDLEWARE`.
- Set `LOGIN_URL = '/'`.

---

### Views & Gating

#### [MODIFY] [lti_views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/lti_views.py)
- Import `login_not_required` from `django.contrib.auth.decorators`.
- Decorate `lti_login`, `lti_launch`, and `lti_keyset` with `@login_not_required`.

#### [MODIFY] [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py)
- Import `login_not_required` from `django.contrib.auth.decorators`.
- Decorate `home_view` with `@login_not_required` so that unauthenticated users can access it and see the custom login interface.

---

### Templates

#### [NEW] [logout.html](file:///h:/My%20Drive/Toddlecross/toddlecross/templates/account/logout.html)
- Create a beautiful custom logout confirmation page under `templates/account/` to override allauth's default logout template.

---

## Verification Plan

### Automated Tests
- Extend [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py) to check that unauthenticated requests to protected views (e.g., dashboard, admin paths) are redirected to `/`.
- Verify all tests continue to pass.

### Manual Verification
- Access the web interface as an anonymous user and confirm that accessing protected views redirects to the home login page.
- Test logging in and logging out to verify the new logout template works correctly.
