# Toddlecross: Project Roadmap & Tracking (Umbrella Issue)

This document tracks the milestones, requirements, and progress for the **Toddlecross** platform. 

---

## 📋 Project Overview
A secure, Python-driven application with a web frontend gated by Google SSO, featuring an administrative control panel for account provisioning and instance management. The primary engine of the platform focuses on data generation, integration, and processing written in Python.

---

## 🗺️ Milestones & Status

### 🟩 Milestone 1: Project Initialization & Git Setup
*Goal: Establish a clean, stable project workspace and link it to GitHub.*
- [x] Initialize Git repository
- [x] Set up branch protections and strategy (Active work on `/dev`, merge to `/main` on milestones)
- [x] Configure `.gitignore` for secrets and environment variables
- [x] Set up stable Python 3.11 virtual environment
- [x] Initialize Django project (`config`) and core application (`toddlecross`)
- [x] Create public GitHub repository `bernie-nyc/toddlecross` and push code

---

### 🟩 Milestone 2: Google SSO Authentication & Access Gating
*Goal: Ensure the web interface is fully protected by Google SSO.*
- [x] Integrate `django-allauth` into Django settings and URLs
- [x] Configure settings-based Google credentials via `SOCIALACCOUNT_PROVIDERS`
- [x] Setup `LOGGING` for authentication troubleshooting
- [x] Configure local `.env` with active Google OAuth Client credentials
- [x] Implement middleware or decorator to gate all frontend views, redirecting unauthenticated users to the SSO sign-in page
- [x] Design and refine custom frontend SSO login and logout pages using glassmorphic UI styles

---

### 🟩 Milestone 3: Instance Administration & User Provisioning
*Goal: Enable the instance admin to add and manage additional user accounts.*
- [x] Update Site settings to match local hosting domain and port (`127.0.0.1:8080`)
- [x] Verify creation of primary instance admin (superuser)
- [x] Expose user management actions in the Django Admin console (`/admin/auth/user/`)
- [x] Create a frontend admin interface/card that allows the logged-in admin to quickly view and invite/add user accounts

---

### 🟩 Milestone 4: Python Integration & Data Engine
*Goal: Build the core data generation, integration, and processing pipelines in Python.*
- [x] Create dedicated processing module structure (e.g., `toddlecross/engine/`)
- [x] Implement API client for Toddleapp using environment credentials (base URL & API Key)
- [x] Implement API client for Veracross using environment credentials (base URL, client ID, client secret)
- [x] Write integration workflows (fetching data from Veracross, mapping, and syncing to Toddleapp)
- [x] Build a database schema to store run history, logs, and job status
- [x] Expose trigger buttons and real-time status indicators on the frontend dashboard to run Python scripts asynchronously

---

### 🟩 Milestone 5: Production Readiness & Deployment
*Goal: Prepare the application for staging/production deployment.*
- [x] Configure production-ready database support (e.g., PostgreSQL via `DATABASE_URL`)
- [x] Set up static file collection (`collectstatic`) and security headers
- [x] Write deployment configuration (e.g., Dockerfile or deployment scripts)

---

### 🟩 Milestone 6: Deployment Verification & CI/CD Setup
*Goal: Verify local container execution and automate unit testing on push.*
- [x] Build and test the Docker container locally (Static verification)
- [x] Troubleshoot entrypoint startup issues in docker environment (Line endings conversion to LF)
- [x] Configure GitHub Actions workflow `.github/workflows/ci.yml` to run tests automatically

---

### ⬜ Milestone 7: Quality Assurance & Code Coverage
*Goal: Instrument test coverage and expand edge case coverage.*
- [ ] Integrate `coverage` packages and configure `.coveragerc`
- [ ] Achieve >90% test coverage on engine sync components
- [ ] Implement robust mock assertions for API failure states (rate limits, timeouts)

---

### ⬜ Milestone 8: Automated Scheduling & Failure Alerts
*Goal: Enable automatic background execution and alerting for sync failures.*
- [ ] Build a custom Django management command to run sync jobs from shell
- [ ] Implement SMTP-based administrative email notifications on sync job failure
- [ ] Design and test scheduling strategy (host system cron or background worker scheduler)
