# Walkthrough - Batch 11: Granular Dashboard Sync Controls

This walkthrough details the addition of granular controls allowing administrators to run Student-only, Teacher-only, or Complete synchronization runs.

## Changes Made

### 1. Database Schema Migration (Issue #29)
- Added `sync_type` CharField to `SyncJob` inside [models.py](file:///h:/My%20Drive/Toddlecross/toddlecross/models.py) with options `'students'`, `'teachers'`, and `'both'`.
- Successfully generated and applied Django migration `0002_syncjob_sync_type.py`.

### 2. Views and Trigger Integration (Issue #29)
- Updated `run_sync_job_background` in [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py) to read `job.sync_type` and run corresponding mappings:
  - `students` -> `pipeline.sync_students()` only
  - `teachers` -> `pipeline.sync_teachers()` only
  - `both` -> runs both pipelines sequentially
- Updated `trigger_sync_view` to read `sync_type` parameters from JSON body POST requests and register it on the created database record.

### 3. Command Line Interface (Issue #29)
- Added a `--type` argument to `run_sync.py` command inside [run_sync.py](file:///h:/My%20Drive/Toddlecross/toddlecross/management/commands/run_sync.py) specifying `students`, `teachers`, or `both`.

### 4. Admin Dashboard UI Enhancements (Issue #29)
- Updated the Django template [dashboard.html](file:///h:/My%20Drive/Toddlecross/toddlecross/templates/toddlecross/dashboard.html):
  - Replaced the single run button with a button group enabling "Sync All Data", "Sync Students", and "Sync Teachers".
  - Configured JavaScript triggers to pass the selected action value in the JSON payload body.
  - Implemented a "Scope" column in the Execution Run History table displaying the job type.

### 5. Test Suite Expansion (Issue #29)
- Appended unit test methods inside [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py):
  - `test_trigger_sync_view_custom_type`: Verifies POST payloads create `SyncJob` with correct scope fields.
  - `test_run_sync_job_background_students_only` and `test_run_sync_job_background_teachers_only`: Verify background thread invokes only the expected sync steps.
  - `test_run_sync_command_custom_type`: Verifies CLI `--type` execution.

---

## Verification Results

### Local Unit Tests & Coverage Check
We ran the complete unit tests locally:
- **Test Executions**: All **37 tests** passed successfully:
  ```cmd
  Ran 37 tests in 12.122s
  OK
  ```
- **Coverage Metrics**: Total application coverage measured at **83%**:
  ```cmd
  Name                                          Stmts   Miss  Cover
  ---------------------------------------------------------------------------
  toddlecross\__init__.py                           0      0   100%
  toddlecross\engine\sync_pipeline.py             144     43    70%
  toddlecross\engine\toddle_client.py              27     10    63%
  toddlecross\engine\veracross_client.py           33      1    97%
  toddlecross\lti_views.py                         65      5    92%
  toddlecross\management\commands\run_sync.py      17      2    88%
  toddlecross\models.py                            16      1    94%
  toddlecross\urls.py                               5      0   100%
  toddlecross\views.py                            116     10    91%
  ---------------------------------------------------------------------------
  TOTAL                                           423     72    83%
  ```
