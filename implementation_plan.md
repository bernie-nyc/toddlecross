# Implementation Plan - Batch 2: Admin Dashboard and User Management

This plan outlines the changes to establish admin access, superuser validation, and frontend user management.

## User Review Required

- None. The user has pre-approved execution of this plan.

---

## Proposed Changes

### Configuration

#### [MODIFY] [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py)
- [ ] Add configurations for default superuser credentials from environment variables.
- [ ] Add settings for social account admin shortcuts.

---

### Management Commands

#### [NEW] [ensure_superuser.py](file:///h:/My%20Drive/Toddlecross/toddlecross/management/commands/ensure_superuser.py)
- [ ] Implement a Django management command to check if a superuser exists and create one if not, using credentials loaded from the settings.

---

### Views and Gating

#### [MODIFY] [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py)
- [ ] Update `home_view` to fetch all users and pass them to the template for staff/admin users.
- [ ] Create `invite_user_view` to handle the POST request from the user invitation form, creating a new user in the database.

#### [MODIFY] [urls.py](file:///h:/My%20Drive/Toddlecross/toddlecross/urls.py)
- [ ] Add URL routing path `/invite-user/` mapping to `invite_user_view`.

---

### Templates

#### [MODIFY] [dashboard.html](file:///h:/My%20Drive/Toddlecross/toddlecross/templates/toddlecross/dashboard.html)
- [ ] Replace the mock admin card with a fully interactive user management console.
- [ ] Add a list of active users showing username, email, and staff status.
- [ ] Add an inline user creation/invitation form with email and staff toggle.

---

## Verification Plan

### Automated Tests
- [ ] Add unit tests in [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py) to check:
  - Only staff users can view the user list and access the invite URL.
  - Submitting the invite form creates a new user in the database.
  - Duplicate email invites are handled gracefully with an error.

### Manual Verification
- [ ] Run the ensure_superuser command and check that the superuser is created.
- [ ] Navigate to the dashboard as a staff user and verify that user lists and invitations work.
