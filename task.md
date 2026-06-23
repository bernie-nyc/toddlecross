# Task List - Batch 1: SSO & Access Gating

- [x] Update Django settings: Add `LoginRequiredMiddleware` and set `LOGIN_URL = '/'` in `config/settings.py`
- [x] Exempt public LTI views: Decorate views in `toddlecross/lti_views.py` with `@login_not_required`
- [x] Exempt root view: Decorate `home_view` in `toddlecross/views.py` with `@login_not_required`
- [x] Implement custom logout template: Create `toddlecross/templates/account/logout.html`
- [x] Verify: Add test cases to verify gating redirection, and run all unit tests
