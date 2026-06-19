# Walkthrough - LTI 1.3 Tool Integration

We have successfully completed the implementation of the LTI 1.3 Tool integration on the `dev` branch.

## Changes Made

### 1. Requirements & Settings
- Added `PyLTI1p3>=1.18.0` and `cryptography>=42.0.0` to [requirements.txt](file:///h:/My%20Drive/Toddlecross/requirements.txt) and installed them.
- Configured `.gitignore` to exclude the project RSA keys folder `config/lti_keys/` from version control.
- Added LTI settings in [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py) to load OIDC endpoints and credentials from environment variables.

### 2. RSA Key Generation
- Created a helper script [generate_lti_keys.py](file:///h:/My%20Drive/Toddlecross/toddlecross/generate_lti_keys.py) that programmatically generates a secure 2048-bit RSA key pair under `config/lti_keys/` if not present.
- Ran the script to generate keys.

### 3. LTI views & Endpoints
- Implemented OIDC and LTI views in [lti_views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/lti_views.py):
  - `lti_login`: Third-party OIDC login initializer.
  - `lti_launch`: Receives the LTI POST request, validates signature and claims, checks that the user already exists in the Django database (no auto-provisioning), logs in the user, and redirects to the dashboard `/`.
  - `lti_keyset`: Serves the public key as JWKS (JSON Web Key Set).
- Wired views under [urls.py](file:///h:/My%20Drive/Toddlecross/toddlecross/urls.py):
  - `/lti/login/`
  - `/lti/launch/`
  - `/lti/keyset/`
- Created [lti_error.html](file:///h:/My%20Drive/Toddlecross/toddlecross/templates/toddlecross/lti_error.html) to render a clean, premium access denied page when an unauthorized or unregistered user attempts an LTI launch.

---

## Verification Results

### Automated Tests
We added unit tests under [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py) covering keyset validation, login redirect, successful launch (existing user), and failing launch scenarios (unregistered user / missing email claims).

All tests passed successfully:
```cmd
Creating test database for alias 'default'...
.....
----------------------------------------------------------------------
Ran 5 tests in 1.363s

OK
Destroying test database for alias 'default'...
Found 5 test(s).
System check identified no issues (0 silenced).
```
