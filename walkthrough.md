# Walkthrough - Batch 9: Multi-Channel Alerts

This walkthrough details the integration of Slack and Discord webhooks to alert administrators upon synchronization job failures.

## Changes Made

### 1. Webhook Configuration (Issue #27)
- Added `SLACK_WEBHOOK_URL` and `DISCORD_WEBHOOK_URL` inside [settings.py](file:///h:/My%20Drive/Toddlecross/config/settings.py) to read credentials safely from environment variables.

### 2. Multi-Channel Webhook Triggers (Issue #27)
- Updated `run_sync_job_background` within [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py) to send HTTP POST requests:
  - **Slack**: Dispatches rich markdown text alerting that a job failed, referencing the sync job ID, error name, and diagnostic log details.
  - **Discord**: Dispatches a colored embed object targeting Discord webhook formatting rules, complete with error trace and log snippets.
- Wrapped each dispatcher call in its own try-except handler to ensure that network errors or timeout outages do not prevent job finalization or mask database sync logs.

### 3. Unit Tests (Issue #27)
- Appended unit test methods to class `EdgeCaseIntegrationTests` in [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py):
  - `test_run_sync_command_failure_dispatches_webhooks`: Verifies mock POST payloads are sent to Slack and Discord with the correct content structures.
  - `test_run_sync_command_webhooks_graceful_on_timeout`: Verifies that request connection timeouts are caught safely, logging a warning record inside the `SyncJob` instead of raising uncaught runtime errors.
- Adjusted mock target URLs to generic `example.com` values to prevent triggering GitHub push protection scanning rules.

---

## Verification Results

### Local Unit Tests & Coverage Check
We ran the unit tests under coverage locally:
- **Test Executions**: All **31 tests** passed successfully:
  ```cmd
  Ran 31 tests in 9.206s
  OK
  ```
- **Coverage Metrics**: Total application coverage measured at **86%**:
  ```cmd
  Name                                          Stmts   Miss  Cover
  ---------------------------------------------------------------------------
  toddlecross\__init__.py                           0      0   100%
  toddlecross\engine\sync_pipeline.py              90     23    74%
  toddlecross\engine\toddle_client.py              27     10    63%
  toddlecross\engine\veracross_client.py           33      1    97%
  toddlecross\lti_views.py                         65      5    92%
  toddlecross\management\commands\run_sync.py      11      0   100%
  toddlecross\models.py                            15      1    93%
  toddlecross\urls.py                               5      0   100%
  toddlecross\views.py                            102      9    91%
  ---------------------------------------------------------------------------
  TOTAL                                           348     49    86%
  ```

### GitHub Actions CI/CD Verification
The updated test suite ran and passed successfully on GitHub:
- **Action Run URL**: [Run 28273746676](https://github.com/bernie-nyc/toddlecross/actions/runs/28273746676)
- **Job Outcome**: The `test` job passed successfully in `23s`.
