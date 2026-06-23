# Implementation Plan - Batch 3: Core Integration and Data Clients

This plan outlines the changes to build the API clients and data processing pipeline for Toddle and Veracross.

## User Review Required

- None. The user has pre-approved execution of this plan.

---

## Proposed Changes

### Core Python Engine

#### [NEW] [toddle_client.py](file:///h:/My%20Drive/Toddlecross/toddlecross/engine/toddle_client.py)
- [ ] Develop the Toddle API client class to interact with Toddle's GraphQL and REST endpoints.
- [ ] Load credentials from settings and handle request authorization headers.

#### [NEW] [veracross_client.py](file:///h:/My%20Drive/Toddlecross/toddlecross/engine/veracross_client.py)
- [ ] Develop the Veracross API client class supporting OAuth2 authentication flow and token refresh.
- [ ] Support requesting student and teacher datasets.

#### [NEW] [sync_pipeline.py](file:///h:/My%20Drive/Toddlecross/toddlecross/engine/sync_pipeline.py)
- [ ] Create a pipeline class that maps student and teacher data structures between Veracross and Toddle formats.
- [ ] Implement diff generation logic to identify additions, changes, and deletions, pushing them to Toddle.

---

## Verification Plan

### Automated Tests
- [ ] Add unit tests in [tests.py](file:///h:/My%20Drive/Toddlecross/toddlecross/tests.py) to check:
  - Mocked Toddle client GraphQL query requests and authorization headers.
  - Mocked Veracross client OAuth2 authentication token request and REST queries.
  - Sync pipeline mapping logic and diff calculations.
