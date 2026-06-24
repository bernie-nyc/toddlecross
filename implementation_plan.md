# Implementation Plan - Batch 4: Asynchronous Execution and Monitoring

This plan outlines the changes to implement the Run History database schema, background worker threads, and a live log streaming interface for the sync pipeline.

## User Review Required

- None. The user has pre-approved execution of this plan.

---

## Proposed Changes

### Models and Database

#### [MODIFY] [models.py](file:///h:/My%20Drive/Toddlecross/toddlecross/models.py)
- [ ] Create `SyncJob` model to store status (Pending, Running, Success, Failed), run timestamps, log text, and success counters.

---

### Views and Gating

#### [MODIFY] [views.py](file:///h:/My%20Drive/Toddlecross/toddlecross/views.py)
- [ ] Implement `trigger_sync_view` to start a sync job in a background thread and return its job ID.
- [ ] Implement `sync_status_view` to return the status, metrics, and logs of a specific sync job as JSON.
- [ ] Update `home_view` to retrieve and context-pass the latest sync jobs to the dashboard.

#### [MODIFY] [urls.py](file:///h:/My%20Drive/Toddlecross/toddlecross/urls.py)
- [ ] Register path `/sync/trigger/` mapping to `trigger_sync_view`.
- [ ] Register path `/sync/status/<int:job_id>/` mapping to `sync_status_view`.

---

### Templates and Dashboard

#### [MODIFY] [dashboard.html](file:///h:/My%20Drive/Toddlecross/toddlecross/templates/toddlecross/dashboard.html)
- [ ] Connect the "Run Data Job" button to make an AJAX POST request triggering the sync.
- [ ] Add a live log viewer pane that polls `/sync/status/<job_id>/` to stream logs.
- [ ] Add a run history table showing the last 10 sync jobs.

---

## Verification Plan

### Automated Tests
- [ ] Add unit tests in [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py) to check:
  - Starting a sync job triggers a background thread and returns the job ID.
  - The status view returns the correct JSON payload containing log text and run state.
  - Running a successful or failed sync job correctly saves the outcome in the database.
