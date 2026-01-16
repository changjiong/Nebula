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

### [2026-01-16] Chat Endpoint 404, CORS Errors & Frontend Build Failures
- **Description**: 
  1. `npm run build` failed due to incorrect `Link` path params in `ToolsList.tsx`.
  2. Sending messages returned 404 "Conversation not found".
  3. Streaming chat returned CORS errors.
- **Cause**: 
  1. Frontend: Route path schema mismatch (used `/admin/tools/$id` instead of `/tools/$id`).
  2. Backend: `send_message` required existing conversation ID versus `stream_chat`'s lazy creation.
  3. Config: Strict CORS settings blocked local development requests.
- **Fix**: 
  1. Corrected `Link` path in frontend.
  2. Implemented lazy conversation creation in `chat.py`.
  3. Temporarily relaxed CORS to `["*"]` in `config.py`.
- **Files Modified**:
  - `frontend/src/components/Admin/Tools/ToolsList.tsx`
  - `backend/app/api/routes/chat.py`
  - `backend/app/core/config.py`
