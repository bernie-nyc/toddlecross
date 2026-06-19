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

### 🟨 Milestone 2: Google SSO Authentication & Access Gating
*Goal: Ensure the web interface is fully protected by Google SSO.*
- [x] Integrate `django-allauth` into Django settings and URLs
- [x] Configure settings-based Google credentials via `SOCIALACCOUNT_PROVIDERS`
- [x] Setup `LOGGING` for authentication troubleshooting
- [ ] Configure local `.env` with active Google OAuth Client credentials
- [ ] Implement middleware or decorator to gate all frontend views, redirecting unauthenticated users to the SSO sign-in page
- [ ] Design and refine custom frontend SSO login and logout pages using glassmorphic UI styles

---

### ⬜ Milestone 3: Instance Administration & User Provisioning
*Goal: Enable the instance admin to add and manage additional user accounts.*
- [x] Update Site settings to match local hosting domain and port (`127.0.0.1:8080`)
- [ ] Verify creation of primary instance admin (superuser)
- [ ] Expose user management actions in the Django Admin console (`/admin/auth/user/`)
- [ ] Create a frontend admin interface/card that allows the logged-in admin to quickly view and invite/add user accounts

---

### ⬜ Milestone 4: Python Integration & Data Engine
*Goal: Build the core data generation, integration, and processing pipelines in Python.*
- [ ] Create dedicated processing module structure (e.g., `toddlecross/engine/`)
- [ ] Implement API client for Toddleapp using environment credentials (base URL & API Key)
- [ ] Implement API client for Veracross using environment credentials (base URL, client ID, client secret)
- [ ] Write integration workflows (fetching data from Veracross, mapping, and syncing to Toddleapp)
- [ ] Build a database schema to store run history, logs, and job status
- [ ] Expose trigger buttons and real-time status indicators on the frontend dashboard to run Python scripts asynchronously

---

### ⬜ Milestone 5: Production Readiness & Deployment
*Goal: Prepare the application for staging/production deployment.*
- [ ] Configure production-ready database support (e.g., PostgreSQL via `DATABASE_URL`)
- [ ] Set up static file collection (`collectstatic`) and security headers
- [ ] Write deployment configuration (e.g., Dockerfile or deployment scripts)
