# Task List - Batch 13: Dynamic Cron Scheduling in Django Admin

- [x] Add `croniter` to `requirements.txt` and install it in virtualenv
- [x] Add `SyncSchedule` model and validation checks inside `toddlecross/models.py`
- [x] Run Django database migrations to apply the schema change
- [x] Register and format `SyncSchedule` inside the new `toddlecross/admin.py`
- [x] Implement scheduling evaluation in `run_sync` command inside `toddlecross/management/commands/run_sync.py`
- [x] Implement and verify unit tests for scheduling triggers and validations
- [x] Verify test suite and local/remote CI pipelines pass successfully
