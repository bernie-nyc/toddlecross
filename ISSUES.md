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
  - [x] Setup superuser validation scripts or instructions.
  - [x] Configure `allauth` admin shortcuts.
- **Files**:
  - `config/settings.py` [MODIFY]

### 🔹 Issue #13: Frontend User Invite & Administration Dashboard
- **Description**: Add user management cards/views on the frontend dashboard visible only to staff/admin users.
- **Tasks**:
  - [x] Create `/admin/users/` view (or embed in dashboard) displaying active users.
  - [x] Add an "Invite/Add User" form to register new users (emails) into the database so they can subsequently login via Google SSO or LTI.
- **Files**:
  - `toddlecross/views.py` [MODIFY]
  - `toddlecross/templates/toddlecross/dashboard.html` [MODIFY]

---

## 📦 Batch 3: Core Integration & Data Clients (Milestone 4 - Part A)
*Focus: Build secure Python clients for Toddle and Veracross using environment credentials.*

### 🔹 Issue #14: Toddle GraphQL & REST API Client
- **Description**: Develop a robust client class for the Toddleapp API using credentials from `.env`.
- **Tasks**:
  - [x] Create Python wrapper to interact with `/graphql` endpoint.
  - [x] Support querying endpoints and schemas securely.
- **Files**:
  - `toddlecross/engine/toddle_client.py` [NEW]

### 🔹 Issue #15: Veracross OAuth2 & API Client
- **Description**: Develop a client class for the Veracross API, handling OAuth token refresh and REST queries.
- **Tasks**:
  - [x] Implement OAuth2 token flow.
  - [x] Support requesting student/teacher datasets from `https://api.veracross.com/`.
- **Files**:
  - `toddlecross/engine/veracross_client.py` [NEW]

### 🔹 Issue #16: Sync & Mapping Workflow Runner
- **Description**: Implement the pipeline mapping student/staff data from Veracross to Toddle format.
- **Tasks**:
  - [x] Map field schemas between platforms.
  - [x] Implement logic to identify diffs and push updates.
- **Files**:
  - `toddlecross/engine/sync_pipeline.py` [NEW]

---

## 📦 Batch 4: Asynchronous Execution & Monitoring (Milestone 4 - Part B)
*Focus: Connect the Python sync engine to the Django UI to execute and track jobs in real time.*

### 🔹 Issue #17: Run History & Job Logging Schema
- **Description**: Store historical records of data sync runs, status, and diagnostic logs in the database.
- **Tasks**:
  - [x] Create a `SyncJob` model tracking status (Pending, Running, Success, Failed) and log records.
- **Files**:
  - `toddlecross/models.py` [MODIFY]

### 🔹 Issue #18: Async Trigger & Log Streaming Interface
- **Description**: Allow admins to run sync tasks asynchronously from the dashboard page and view live log feeds.
- **Tasks**:
  - [x] Implement background worker or thread execution for the sync pipeline.
  - [x] Expose an endpoint returning real-time status and logs of the active/latest run.
- **Files**:
  - `toddlecross/views.py` [MODIFY]
  - `toddlecross/templates/toddlecross/dashboard.html` [MODIFY]

---

## 📦 Batch 5: Production Readiness & Deployment (Milestone 5)
*Focus: Prepare application for production deployment (PostgreSQL, static asset collection, Docker).*

### 🔹 Issue #19: Package & Configure Production-Ready Database
- **Description**: Enable PostgreSQL support and secure database settings.
- **Tasks**:
  - [x] Add psycopg2-binary to requirements.txt.
  - [x] Add dj-database-url to settings.py.
- **Files**:
  - `requirements.txt` [MODIFY]
  - `config/settings.py` [MODIFY]

### 🔹 Issue #20: Production Static Asset Compilation
- **Description**: Configure collectstatic targets, WhiteNoise middleware, and security headers.
- **Tasks**:
  - [x] Configure STATIC_ROOT and WhiteNoise settings.
  - [x] Enable SSL redirect, secure CSRF and session cookies in production.
- **Files**:
  - `config/settings.py` [MODIFY]
  - `requirements.txt` [MODIFY]

### 🔹 Issue #21: Containerization and Bootstrapping script
- **Description**: Write a production Dockerfile and startup shell script.
- **Tasks**:
  - [x] Build Dockerfile with multi-stage build.
  - [x] Write entrypoint.sh script for migrations, staticfiles collection, superuser creation, and WSGI.
- **Files**:
  - `Dockerfile` [NEW]
  - `entrypoint.sh` [NEW]

---

## 📦 Batch 6: Deployment Verification & CI/CD Setup (Milestone 6)
*Focus: Verify the production Docker configuration locally and automate test workflows.*

### 🔹 Issue #22: Local Container Build and Entrypoint Verification
- **Description**: Build the container image locally, run it, and verify that the entrypoint bootstrap script performs database setup and migrates cleanly.
- **Tasks**:
  - [x] Build the docker image locally using `docker build -t toddlecross:latest .`. (Static verification)
  - [x] Spin up the container locally mapping standard port `8080` (e.g. `docker run -p 8080:8080 --env-file .env toddlecross:latest`). (Line ending conversion to LF)
  - [x] Investigate and resolve container startup or dependency issues.
- **Files**:
  - `Dockerfile` [MODIFY]
  - `entrypoint.sh` [MODIFY]

### 🔹 Issue #23: GitHub Actions CI/CD Pipeline
- **Description**: Configure a GitHub Actions workflow to run Django automated tests on push and pull request.
- **Tasks**:
  - [x] Create a `.github/workflows/ci.yml` setup file.
  - [x] Set up Python environment caching dependencies to optimize CI/CD pipeline run duration.
  - [x] Add static file collection check and unit testing scripts to CI execution flow.
- **Files**:
  - `.github/workflows/ci.yml` [NEW]

---

## 📦 Batch 7: Quality Assurance & Code Coverage (Milestone 7)
*Focus: Instrument test coverage reporting and verify error/failure handling in client connections.*

### 🔹 Issue #24: Test Coverage Integration
- **Description**: Measure test coverage of Django applications and integration scripts to ensure engine paths are tested.
- **Tasks**:
  - [ ] Install `coverage` and add it to requirements.txt.
  - [ ] Create a `.coveragerc` file in the root workspace to exclude virtual environment files, migrations, and django settings.
  - [ ] Generate HTML coverage reports locally and verify that core views and engines are covered.
- **Files**:
  - `requirements.txt` [MODIFY]
  - `.coveragerc` [NEW]

### 🔹 Issue #25: Integration & Edge-Case Testing
- **Description**: Add unit tests focusing on failure injection to verify how Toddlecross recovers from external server API issues.
- **Tasks**:
  - [ ] Write mocks simulating HTTP timeout error codes from Toddleapp GraphQL queries.
  - [ ] Write tests to verify Veracross OAuth token expiry recovery flows.
  - [ ] Verify that UI dashboard remains functional when background sync jobs fail.
- **Files**:
  - `toddlecross/tests.py` [MODIFY]

---

## 📦 Batch 8: Automated Scheduling & Failure Alerts (Milestone 8)
*Focus: Create cron jobs for automatic synchronization and notify administrators of failures.*

### 🔹 Issue #26: Cron/Scheduled Sync Executions
- **Description**: Build a custom command-line script/command that runs the sync process so that it can be scheduled as a cron job.
- **Tasks**:
  - [ ] Create a custom Django management command `run_sync` inside `toddlecross/management/commands/`.
  - [ ] Implement arguments or options to configure which sync paths to run (e.g. students only, teachers only, or both).
  - [ ] Verify that this command creates and updates `SyncJob` run history database records identical to the frontend UI execution.
- **Files**:
  - `toddlecross/management/commands/run_sync.py` [NEW]

### 🔹 Issue #27: Failure Email/Slack Notifications
- **Description**: Notify staff/admins immediately when a data synchronization run (either cron or UI-driven) crashes or fails.
- **Tasks**:
  - [ ] Wire email warning alerts using `django.core.mail.send_mail`.
  - [ ] Send detailed diagnostics log snippet to configured `SUPERUSER_EMAIL` or alert email addresses upon a `Failed` status transition.
  - [ ] Add SMTP configuration variables to config settings to fetch mail credentials from environment variables.
- **Files**:
  - `config/settings.py` [MODIFY]
  - `toddlecross/views.py` [MODIFY]
  - `toddlecross/management/commands/run_sync.py` [MODIFY]
