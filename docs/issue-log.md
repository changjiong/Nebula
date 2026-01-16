# Issue and Fix Log

This directory contains records of issues encountered and their corresponding fixes.

## Format

### [Date] Issue Title
- **Description**: Brief description of the issue.
- **Cause**: Root cause analysis.
- **Fix**: Steps taken to resolve the issue.
- **Files Modified**: List of files changed.

---

### [2026-01-15] Backend Startup Failure (IndentationError)
- **Description**: Login failed with `net::ERR_CONNECTION_REFUSED` on port 8000. Backend container was exiting immediately after start.
- **Cause**: `IndentationError: unexpected indent` in `backend/app/api/routes/chat.py` at line 242.
- **Fix**: Corrected indentation in `nfc_stream_generator` function and rebuilt the backend container.
- **Files Modified**: 
  - `backend/app/api/routes/chat.py`
