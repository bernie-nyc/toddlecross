# Umbrella Issue: Toddlecross Core Engine & Platform Gating

This document serves as our offline Umbrella Issue tracking system, organizing the next milestones into structured batches of work. These can be migrated to GitHub Issues once the GitHub API rate limit resets.

---

## 📦 Batch 1: SSO & Access Gating (Milestone 2 Completion)
*Focus: Fully protect the web application, enforce authenticated sessions, and polish the user flow.*

### 🔹 Issue #10: Implement View-Gating Middleware/Decorator
- **Description**: Secure all views within the `toddlecross` application, ensuring unauthenticated requests are redirected to the Google SSO / Sign-in page.
- **Tasks**:
  - [ ] Implement custom middleware or view decorators to check `request.user.is_authenticated`.
  - [ ] Configure public route exemptions (such as LTI login, launch, and keyset endpoints, which must remain accessible to the public/Toddle).
- **Files**:
  - `toddlecross/middleware.py` [NEW]
  - `config/settings.py` [MODIFY]
  - `toddlecross/views.py` [MODIFY]

### 🔹 Issue #11: Refine Login / Logout Glassmorphic UI
- **Description**: Polish the user sign-in and sign-out interfaces to ensure a premium, modern feel.
- **Tasks**:
  - [ ] Review CSS transitions, loading feedback on the Google SSO button.
  - [ ] Build a sleek Logout confirmation page.
- **Files**:
  - `toddlecross/templates/toddlecross/login.html` [MODIFY]
  - `toddlecross/templates/toddlecross/logout.html` [NEW]

---

## 📦 Batch 2: Admin Dashboard & User Management (Milestone 3)
*Focus: Enable site administrators to manage and invite accounts without touching the backend shell.*

### 🔹 Issue #12: Superuser Verification & Settings
- **Description**: Establish and document admin access, wiring user listings in the Django admin console.
- **Tasks**:
  - [ ] Setup superuser validation scripts or instructions.
  - [ ] Configure `allauth` admin shortcuts.
- **Files**:
  - `config/settings.py` [MODIFY]

### 🔹 Issue #13: Frontend User Invite & Administration Dashboard
- **Description**: Add user management cards/views on the frontend dashboard visible only to staff/admin users.
- **Tasks**:
  - [ ] Create `/admin/users/` view (or embed in dashboard) displaying active users.
  - [ ] Add an "Invite/Add User" form to register new users (emails) into the database so they can subsequently login via Google SSO or LTI.
- **Files**:
  - `toddlecross/views.py` [MODIFY]
  - `toddlecross/templates/toddlecross/dashboard.html` [MODIFY]

---

## 📦 Batch 3: Core Integration & Data Clients (Milestone 4 - Part A)
*Focus: Build secure Python clients for Toddle and Veracross using environment credentials.*

### 🔹 Issue #14: Toddle GraphQL & REST API Client
- **Description**: Develop a robust client class for the Toddleapp API using credentials from `.env`.
- **Tasks**:
  - [ ] Create Python wrapper to interact with `/graphql` endpoint.
  - [ ] Support querying endpoints and schemas securely.
- **Files**:
  - `toddlecross/engine/toddle_client.py` [NEW]

### 🔹 Issue #15: Veracross OAuth2 & API Client
- **Description**: Develop a client class for the Veracross API, handling OAuth token refresh and REST queries.
- **Tasks**:
  - [ ] Implement OAuth2 token flow.
  - [ ] Support requesting student/teacher datasets from `https://api.veracross.com/`.
- **Files**:
  - `toddlecross/engine/veracross_client.py` [NEW]

### 🔹 Issue #16: Sync & Mapping Workflow Runner
- **Description**: Implement the pipeline mapping student/staff data from Veracross to Toddle format.
- **Tasks**:
  - [ ] Map field schemas between platforms.
  - [ ] Implement logic to identify diffs and push updates.
- **Files**:
  - `toddlecross/engine/sync_pipeline.py` [NEW]

---

## 📦 Batch 4: Asynchronous Execution & Monitoring (Milestone 4 - Part B)
*Focus: Connect the Python sync engine to the Django UI to execute and track jobs in real time.*

### 🔹 Issue #17: Run History & Job Logging Schema
- **Description**: Store historical records of data sync runs, status, and diagnostic logs in the database.
- **Tasks**:
  - [ ] Create a `SyncJob` model tracking status (Pending, Running, Success, Failed) and log records.
- **Files**:
  - `toddlecross/models.py` [MODIFY]

### 🔹 Issue #18: Async Trigger & Log Streaming Interface
- **Description**: Allow admins to run sync tasks asynchronously from the dashboard page and view live log feeds.
- **Tasks**:
  - [ ] Implement background worker or thread execution for the sync pipeline.
  - [ ] Expose an endpoint returning real-time status and logs of the active/latest run.
- **Files**:
  - `toddlecross/views.py` [MODIFY]
  - `toddlecross/templates/toddlecross/dashboard.html` [MODIFY]
