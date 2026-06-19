# Implementation Plan — LTI 1.3 Integration

This plan outlines the steps to implement LTI 1.3 Tool capabilities in our Django application (`toddlecross`) to allow authentication launches from Toddle.

## User Review Required

> [!IMPORTANT]
> Since Toddle acts as the LTI Platform (deploying our tool), we must establish an RSA Key Pair for our application. We generate this RSA key pair programmatically and save the files under `config/lti_keys/` inside the project folder. This directory will be added to `.gitignore` to prevent committing the private key.

> [!IMPORTANT]
> **User Authentication & Provisioning Constraints**:
> - We will **not** create a Django user if they do not exist in the database.
> - The LTI Launch view will extract the user's email from the launch token and lookup the user in the Django database.
> - If no user matches the email, the LTI Launch view will return an HTTP 403 Forbidden error with a message indicating they do not have an account.
> - If a matching user is found, they are authenticated via `django.contrib.auth.login` and redirected to the dashboard (`/`).

---

## Proposed Changes

### Configuration & Dependencies

#### [MODIFY] [requirements.txt](file:///h:/My%20Drive/Toddlecross/requirements.txt)
- Add `PyLTI1p3>=1.18.0` for LTI 1.3 protocol validation.
- Add `cryptography` for RSA keys generation and signing.

#### [MODIFY] [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py)
- Load LTI credentials from environment variables.
- Configure path to the LTI keys directory (`config/lti_keys/`).

#### [MODIFY] [.gitignore](file:///h:/My%20Drive/Toddlecross/.gitignore)
- Add `config/lti_keys/` to ignore local private/public RSA key files.

---

### Key Generation Helper

#### [NEW] [generate_lti_keys.py](file:///h:/My%20Drive/Toddlecross/toddlecross/generate_lti_keys.py)
- A helper script to programmatically generate 2048-bit RSA private and public keys if they do not exist, saving them to `config/lti_keys/`.

---

### LTI Views & Endpoints

#### [NEW] [lti_views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/lti_views.py)
- Implement `LtiLoginView`: Initiates the OIDC authentication request.
- Implement `LtiLaunchView`: Receives LTI POST launch, validates JWT signature against Toddle's Keyset URL, handles login lookup by email (no auto-provisioning), and redirects to `/`.
- Implement `LtiKeysetView`: Exposes our JWKS (JSON Web Key Set) serving our public key to Toddle.

#### [MODIFY] [urls.py](file:///h:/My%20Drive/Toddlecross/toddlecross/urls.py)
- Add paths:
  - `/lti/login/` -> `LtiLoginView`
  - `/lti/launch/` -> `LtiLaunchView`
  - `/lti/keyset/` -> `LtiKeysetView`

---

## Verification Plan

### Automated Tests
- Run `.venv\Scripts\python.exe manage.py test` to ensure Django builds and runs without errors.
- Mock LTI 1.3 launch payload requests and test login/launch redirection in `tests.py`.

### Manual Verification
- Deploy to DigitalOcean App Platform.
- Fill the registration URLs in Toddle:
  - Initiate login URL: `https://<do-app-url>/lti/login/`
  - Launch/Redirect URL(s): `https://<do-app-url>/lti/launch/`
  - Keyset URL: `https://<do-app-url>/lti/keyset/`
  - Target link URI: `https://<do-app-url>/lti/launch/`
- Perform a launch test from Toddle.
