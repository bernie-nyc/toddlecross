# Task List - LTI 1.3 Integration

- [x] Update dependencies: Add `PyLTI1p3>=1.18.0` and `cryptography` to `requirements.txt` and install them
- [x] Configure `.gitignore`: Add `config/lti_keys/`
- [x] Implement key generation script: `toddlecross/generate_lti_keys.py` and run it to create keys
- [x] Update Django settings: Configure LTI variables and key paths in `config/settings.py`
- [x] Implement views: Write login, launch, and keyset views in `toddlecross/lti_views.py`
- [x] Add routing: Connect views in `toddlecross/urls.py`
- [x] Verify: Write unit tests in `toddlecross/tests.py` and run them to ensure everything is correct
