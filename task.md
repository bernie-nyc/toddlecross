# Task List - Batch 2: Admin Dashboard and User Management

- [x] Update Django settings: Configure superuser settings from environment variables in `config/settings.py`
- [x] Create superuser script: Implement `ensure_superuser` command in `toddlecross/management/commands/ensure_superuser.py`
- [x] Add URL routing: Add path `/invite-user/` in `toddlecross/urls.py`
- [x] Implement invite views: Write `invite_user_view` and update `home_view` in `toddlecross/views.py`
- [x] Update dashboard UI: Add the user list and invite form to `toddlecross/templates/toddlecross/dashboard.html`
- [ ] Verify: Write unit tests in `toddlecross/tests.py` and run them to ensure everything is correct
