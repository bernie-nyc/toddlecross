# Toddlecross Local Installation & Testing Guide

This guide details the step-by-step instructions to configure, run, and test the **Toddlecross** synchronization engine and admin dashboard.

---

## 📋 Prerequisites

Ensure the following tools are installed on your host system:
1. **Python 3.11** (with `pip` and `venv` support)
2. **Docker** and **Docker Compose**
3. **OpenSSL** (optional, for manual LTI key generation)

---

## ⚙️ 1. Environment Configurations (`.env`)

Copy `.env.example` to `.env` in the project root:
```cmd
copy .env.example .env
```

Open `.env` and fill in the required credentials:

```ini
# Django Settings
SECRET_KEY=generate_a_secure_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings (Only override if using PostgreSQL container/server)
# DATABASE_URL=postgres://toddlecross:toddlecross_secure_pwd@db:5432/toddlecross

# Google SSO OAuth2 Configuration (For Administrator login)
SOCIAL_AUTH_GOOGLE_CLIENT_ID=your_google_oauth_client_id
SOCIAL_AUTH_GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret

# Toddle LTI Launch Credentials
TODDLE_LTI_ISSUER_URL=your_toddle_lti_issuer_url
TODDLE_LTI_CLIENT_ID=your_toddle_lti_client_id
TODDLE_LTI_LOGIN_URL=your_toddle_lti_login_url
TODDLE_LTI_KEYSET_URL=your_toddle_lti_keyset_url
TODDLE_LTI_TOKEN_URL=your_toddle_lti_token_url
TODDLE_LTI_DEPLOYMENT_ID=your_toddle_lti_deployment_id

# Veracross Client Credentials
VERACROSS_API_URL=https://api.veracross.com/your_school
VERACROSS_CLIENT_ID=your_veracross_client_id
VERACROSS_CLIENT_SECRET=your_veracross_client_secret

# Toddle GraphQL Client Credentials
TODDLE_API_URL=https://ap-southeast-1-production-apis.toddleapp.com/graphql
TODDLE_API_TOKEN=your_toddle_graphql_api_token

# Email Server Settings (For Failure Alerts)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_alert_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password
ALERT_EMAIL=admin_notifications@yourdomain.com

# Webhook Alert URLs (For Slack & Discord Notification Templates)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/X00
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/000/000

# Default Superuser Credentials
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=adminpassword
```

---

## 🛠️ 2. Local Installation (Standard Virtualenv)

Follow these steps to run the application directly in your local environment:

### Step A: Initialize Virtual Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step B: Generate LTI Encryption Keys
Generate the LTI private and public RSA signing keys:
```bash
python toddlecross/generate_lti_keys.py
```
This script creates a `config/lti_keys/` folder containing `private.key` and `public.key`.

### Step C: Database Setup & Migrations
Create the local SQLite database and run migrations:
```bash
python manage.py migrate
```

### Step D: Initialize Default Superuser
Automatically generate the default administrator account (using variables defined in `.env`):
```bash
python manage.py ensure_superuser
```

### Step E: Run Development Server
```bash
python manage.py runserver 8080
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) to access the application.

---

## 🐳 3. Docker Compose Orchestration

To run the complete web server and PostgreSQL database together in containers:

### Step A: Boot services
Run Docker Compose in the project root:
```bash
docker compose up --build
```

Docker Compose spins up two containers:
1. `toddlecross_db`: A PostgreSQL database container storing jobs, logs, and user schedules.
2. `toddlecross_web`: The Django web application running under Gunicorn.

> [!NOTE]
> During container boot, the `entrypoint.sh` bootstrap script executes:
> - Auto-generation of missing LTI keys.
> - Database migration checks.
> - Static asset collection.
> - Superuser validation.
> - Starts Gunicorn serving on port `8080`.

Open [http://localhost:8080](http://localhost:8080) to inspect.

---

## 🧪 4. Running the Test Suite

Verify that all unit tests run and pass cleanly:

### Run local tests
```bash
coverage run manage.py test
```

### View coverage report
```bash
coverage report
```

### Run code lint check
Ensure Ruff checks pass:
```bash
ruff check .
```

---

## ⚙️ 5. Setting up Scheduled Syncs

Administrators can configure automated runs using the database scheduling engine:

1. Log into the Django Admin dashboard at [http://127.0.0.1:8080/admin](http://127.0.0.1:8080/admin) using your superuser credentials.
2. Click **Sync schedules** -> **Add Sync Schedule**.
3. Create a schedule (e.g., Name: `Hourly Teacher Sync`, Active: `Checked`, Cron: `0 * * * *`, Sync Type: `teachers`).
4. To check and run scheduled triggers, set up a host crontab task or scheduler executing the management command every minute:
   ```bash
   python manage.py run_sync --scheduled
   ```
