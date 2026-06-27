# Walkthrough - Batch 10: Teacher Sync Pipeline Expansion

This walkthrough details the addition of teacher synchronization logic, integrating it into the automatic run execution sequence alongside students.

## Changes Made

### 1. Teacher Sync Engine (Issue #28)
- Created the `map_teacher(self, veracross_teacher)` schema-matching helper in [sync_pipeline.py](file:///h:/My%20Drive/Toddlecross/toddlecross/engine/sync_pipeline.py).
- Implemented `sync_teachers(self)` running:
  - Retrieval of teacher profiles from Veracross client.
  - Verification and mapping of teacher attributes (name, email, unique sis_id).
  - Graphql query lookup (`GetExistingTeachers`) of current records on Toddle.
  - Difference calculations (create, update, delete lists).
  - Toddle mutations execution (`CreateTeacher`, `UpdateTeacher`, `DeleteTeacher`).
- Updated the pipeline metric updates to accumulate sums (using addition operators) rather than overwriting fields.

### 2. views.py Background Sync (Issue #28)
- Updated `run_sync_job_background` in [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py) to invoke `pipeline.sync_teachers()` directly after student updates complete.

### 3. Expanded Test Suite & Mock Adjustments (Issue #28)
- Appended two unit test methods inside `SyncPipelineTests` in [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py):
  - `test_map_teacher`: Checks key translation and formatting alignment.
  - `test_sync_teachers_workflow`: Mock-verifies query and mutation sequence.
- Updated view and shell command checks (`test_run_sync_job_background_success`, `test_run_sync_job_background_failure`, `test_run_sync_command_success`) to patch both `sync_students` and `sync_teachers`.

---

## Verification Results

### Local Unit Tests & Coverage Check
We ran the complete unit tests locally:
- **Test Executions**: All **33 tests** passed successfully:
  ```cmd
  Ran 33 tests in 9.439s
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
  toddlecross\management\commands\run_sync.py      11      0   100%
  toddlecross\models.py                            15      1    93%
  toddlecross\urls.py                               5      0   100%
  toddlecross\views.py                            103      9    91%
  ---------------------------------------------------------------------------
  TOTAL                                           403     69    83%
  ```

### GitHub Actions CI/CD Verification
The pipeline ran and passed on GitHub:
- **Action Run URL**: [Run 28292364740](https://github.com/bernie-nyc/toddlecross/actions/runs/28292364740)
- **Job Outcome**: The `test` job passed successfully in `40s`.
