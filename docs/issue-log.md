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

### [2026-01-17] Avatar Persistence & Chat Layout Fixes
- **Description**: 
  1. User avatars were lost after backend container restart.
  2. Chat message bubble width (`max-w-3xl`) was inconsistent with input box width (`max-w-5xl`).
- **Cause**: 
  1. `static/avatars` directory was not mounted as a volume in `docker-compose.yml` (incorrectly mounted to `db` service).
  2. `MessageList.tsx` used a hardcoded narrow width class.
- **Fix**: 
  1. Corrected `docker-compose.yml` to mount `./backend/static:/app/static` to the `backend` service.
  2. Updated `MessageList.tsx` to use `max-w-5xl`.
- **Files Modified**:
  - `docker-compose.yml`
  - `frontend/src/components/Chat/MessageList.tsx`

### [2026-01-17] Chat Send Endpoint CORS/500 Error
- **Description**: Sending a message resulted in a CORS error on the frontend and a 500 Internal Server Error on the backend (`TypeError: got multiple values for keyword argument 'conversation_id'`).
- **Cause**: The running backend container was using an outdated version of `backend/app/api/routes/chat.py`. The code on disk had the fix (`exclude={"conversation_id"}`), but the container had not been rebuilt to include it.
- **Fix**: Rebuilt the backend container (`docker compose up -d --build backend`).
- **Files Modified**:
  - `backend/app/api/routes/chat.py` (Fix was already present on disk, applied via rebuild)

### [2026-01-17] Thinking Process & Layout Fixes
- **Description**: 
  1. Thinking Process displayed duplicates, infinite spinners, and truncated text.
  2. Chat messages and input box were misaligned.
- **Cause**: 
  1. Backend: New `think_id` generated for streaming (orphaning initial step).
  2. Frontend: CSS `truncate` class used in `ThinkingMessage.tsx`.
  3. Frontend: `MessageList.tsx` had mismatched padding (`px-3` vs `p-4`).
- **Fix**: 
  1. Backend: Reused `initial_think_id` for streaming.
  2. Frontend: Removed `truncate`, added `whitespace-pre-wrap`.
  3. Frontend: Adjusted `MessageList.tsx` padding to `px-4`.
- **Files Modified**:
  - `backend/app/api/routes/chat.py`
  - `frontend/src/components/Chat/ThinkingMessage.tsx`
  - `frontend/src/components/Chat/MessageList.tsx`
