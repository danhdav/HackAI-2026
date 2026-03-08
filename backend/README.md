# TaxMaxx Backend (FastAPI Skeleton)

This backend is a hackathon-friendly scaffold for the TaxMaxx tax-assistant app.  
It focuses on clear API contracts first, with modular sections so two backend developers can work in parallel.

## Purpose

The backend supports this flow:
1. Intake W-2 / 1098-T documents (or mock values)
2. Normalize and store parsed values in a tax session
3. Run deterministic calculations to produce draft 1040 fields
4. Return draft values in a frontend-friendly JSON shape

Gemini chatbot support is scaffolded separately and optional.

## Backend Sections

### Section 1 (Mandatory): Parser / Intake Pipeline
- Endpoint: `POST /api/parser/parse`
- Accepts uploaded files (`w2_file`, `form_1098t_file`) or `mock_mode=true`
- Returns normalized parsed values with a `source` value of `mock` or `parsed`
- Parser internals are TODO placeholders so this can be implemented independently

### Section 2 (Mandatory): MongoDB + Calculations + 1040 Output
- Endpoints:
  - `POST /api/tax-session/upsert`
  - `GET /api/tax-session/{session_id}`
  - `POST /api/calculations/run/{session_id}`
  - `GET /api/calculations/draft/{session_id}`
- Stores sessions in MongoDB (with in-memory fallback for local testing)
- Computes required draft 1040 lines deterministically
- Lets frontend proceed even if parser implementation is incomplete

### Section 3 (Optional/Future): Gemini Chatbot Integration
- Endpoint: `POST /api/chatbot/ask/{session_id}`
- Uses Gemini when enabled and falls back to deterministic mock responses
- Grounded in stored `parsed_data` + `draft_1040`
- Privacy-safe by design (identity fields are not parsed)
- TODOs included for possible future DB-edit actions via chatbot
- Backend remains fully functional without this section

## Project Structure

```text
backend/
  sample_pdfs/
    .gitkeep
    README.md
  app/
    main.py
    config.py
    models/
      parser_models.py
      tax_session.py
      response_models.py
    routes/
      health.py
      parser.py
      tax_session.py
      calculations.py
      chatbot.py
    services/
      parser_service.py
      mongodb_service.py
      calculation_service.py
      chatbot_service.py
    utils/
      constants.py
      sample_data.py
    db/
      mongo.py
  requirements.txt
  .env.example
  README.md
```

## Sample PDF Storage (for parser testing)

Store local testing PDFs in:
- `backend/sample_pdfs/`

Recommended naming:
- `w2_sample_01.pdf`
- `1098t_sample_01.pdf`

Notes:
- This folder is meant for test files used during parser development.
- Keep real user documents and sensitive data out of the repository.

## API Contracts (Frontend Integration Reference)

This section describes what each endpoint is for and the response format expected by frontend.

### 1) `GET /api/health`
Purpose:
- Basic backend liveness check.

Response:
```json
{
  "status": "ok",
  "service": "backend"
}
```

### 2) `POST /api/parser/parse`
Purpose:
- Intake step for uploaded documents.
- Can run in mock mode so frontend can integrate before parser internals are complete.

Request (`multipart/form-data`):
- `mock_mode` (bool, optional; default from env)
- `w2_file` (file, optional)
- `form_1098t_file` (file, optional)

Response:
```json
{
  "session_id": "session_mock_001",
  "parsed_data": {
    "w2": { "box1": 52000, "box2": 4100 },
    "1098t": { "box1": 9000, "box5": 2500 }
  },
  "source": "mock"
}
```

Parser implementation status (important):
- Parser supports Azure Document Intelligence extraction for W-2/1098-T when
  `AZURE_KEY` and `AZURE_ENDPOINT` are configured.
- It still supports mock mode for safe local testing and quota protection.
- Main parser modules:
  - `app/services/parser_service.py`
  - `app/routes/parser.py`
  - `parser/extract.py`
  - `parser/parse_fields.py`
  - `parser/utility.py`

### 2b) `POST /api/parser/box-data` (Daniel frontend-compatible)
Purpose:
- Accepts a list of files (`files`) from frontend upload flow.
- Runs Daniel-style parsing and returns `calculations + box_data`.
- Also creates/updates canonical TaxMaxx session and draft 1040 in Mongo.

Request (`multipart/form-data`):
- `files` (repeatable file field, expected names include `W2` and `1098-T`)
- `mock_mode` (bool, optional)

Response:
```json
{
  "session_id": "session_ab12cd34ef56",
  "source": "parsed",
  "calculations": {
    "income": {},
    "deductions_credits": {},
    "tax_and_refund": {}
  },
  "box_data": {},
  "draft_1040": {
    "line_1a": 52000,
    "line_1z": 52000
  }
}
```

### 2c) Parser raw-data persistence endpoints (frontend editing flow)
- `POST /api/parser/box-data/store`
- `PUT /api/parser/box-data/{doc_id}`
- `DELETE /api/parser/box-data/{doc_id}`

### 3) `POST /api/tax-session/upsert`
Purpose:
- Create or update a tax session in MongoDB (or in-memory fallback).
- Stores parsed values and metadata for later calculations/chat.

Request (`application/json`):
```json
{
  "session_id": "session_mock_001",
  "parsed_data": {
    "w2": { "box1": 52000, "box2": 4100 },
    "1098t": { "box1": 9000, "box5": 2500 }
  },
  "metadata": {
    "user_id": "demo_user_001",
    "tax_year": 2024,
    "notes": "optional note",
    "extras": {}
  }
}
```

Response:
```json
{
  "session_id": "session_mock_001",
  "message": "Session upserted successfully.",
  "session": {
    "session_id": "session_mock_001",
    "created_at": "2026-03-07T00:00:00Z",
    "updated_at": "2026-03-07T00:00:00Z",
    "parsed_data": {
      "w2": { "box1": 52000, "box2": 4100 },
      "1098t": { "box1": 9000, "box5": 2500 }
    },
    "calculation_inputs": { "filing_status": "single", "deduction_type": "standard" },
    "draft_1040": null,
    "chatbot_history": [],
    "status": {
      "parser_status": "completed",
      "calculation_status": "pending",
      "chatbot_status": "disabled"
    },
    "metadata": {
      "user_id": "demo_user_001",
      "tax_year": 2024,
      "notes": "optional note",
      "extras": {}
    }
  }
}
```

### 4) `GET /api/tax-session/{session_id}`
Purpose:
- Fetch full stored session state (parsed intake + any drafted 1040 values).

Response:
- Same `session` object shape shown in upsert response.

### 5) `POST /api/calculations/run/{session_id}`
Purpose:
- Run deterministic MVP tax calculations from stored parsed values.
- Persist computed draft 1040 values in session.

Response:
```json
{
  "session_id": "session_mock_001",
  "draft_1040": {
    "line_1a": 52000,
    "line_1z": 52000,
    "line_9": 52000,
    "line_11a": 52000,
    "line_11b": 52000,
    "line_15": 37400,
    "line_16": 4276,
    "line_25a": 4100,
    "line_25d": 4100,
    "line_34": 0
  }
}
```

### 6) `GET /api/calculations/draft/{session_id}`
Purpose:
- Return only draft 1040 values in the frontend-ready shape.

Response:
- Same shape as `POST /api/calculations/run/{session_id}` response.

### 7) `POST /api/chatbot/ask/{session_id}` (Optional/Future)
Purpose:
- Ask questions about the current session and draft values.
- Works with Gemini when configured and deterministic fallback when unavailable.

Request (`application/json`):
```json
{
  "message": "Why is line_34 zero?"
}
```

Response (mock mode example):
```json
{
  "session_id": "session_mock_001",
  "answer": "Line 34 estimates refund as max(line 25d - line 16, 0)...",
  "source": "gemini"
}
```

Chatbot guardrails:
- Explains only supported lines and stored values.
- Explains math in plain English with session values.
- States unsupported sections require more inputs/rules.
- States personal identity fields (name/SSN/address) are intentionally not parsed for privacy and must be manually filled on the 1040 PDF.
- Reminds users to use the 1040 PDF tab as the form companion.

## Required Input Fields (Current MVP)

From W-2:
- `box1`
- `box2`

From 1098-T:
- `box1`
- `box5`

No additional intake fields are supported yet.

## Required Draft 1040 Output Fields

The backend currently returns:
- `line_1a`
- `line_1z`
- `line_9`
- `line_11a`
- `line_11b`
- `line_15`
- `line_16`
- `line_25a`
- `line_25d`
- `line_34`

## Calculation Notes

Implemented assumptions (MVP):
- Single filer
- Standard deduction
- No dependents
- No additional income sources
- Federal only

Current formulas:
- `line_1a = W-2 box1`
- `line_1z = line_1a`
- `line_9 = line_1z`
- `line_11a = line_9`
- `line_11b = line_11a`
- `line_15 = max(line_11b - standard_deduction_single, 0)`
- `line_16 = single-filer bracket tax(line_15)`
- `line_25a = W-2 box2`
- `line_25d = line_25a`
- `line_34 = max(line_25d - line_16, 0)`

Future TODOs:
- Expose amount owed path (line 37 style output) if tax exceeds withholding
- Integrate education-credit logic using 1098-T values

## Mock Mode and Parallel Development

Mock fixtures are provided in `app/utils/sample_data.py`:
- sample W-2 parse
- sample 1098-T parse
- sample full session
- sample draft 1040

This allows:
- frontend integration to start immediately
- calculations to be tested before parser internals are complete
- API contract stability while teams work in parallel

## Run Locally

Recommended (venv-first):

1. Create and activate virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Create environment file:
   - `cp .env.example .env`
3. Install dependencies:
   - `python -m pip install -r requirements.txt`
4. Start API:
   - `python -m uvicorn app.main:app --reload`
5. Open docs:
   - `http://127.0.0.1:8000/docs`

Dependency management note:
- The backend source of truth is `requirements.txt` (pip).
- If teammates use other tooling (e.g., `uv`), keep generated lock/tool files optional and do not replace this baseline unless the team agrees.

Parser env note:
- For live Azure parsing in `/api/parser/box-data` or `/api/parser/parse`:
  - set `AZURE_KEY`
  - set `AZURE_ENDPOINT`

## External non-coding tasks

- Obtain/generate sample W-2 and 1098-T PDFs for parser testing
- Decide local MongoDB vs MongoDB Atlas for team setup
- Decide Gemini API key ownership and environment strategy (if enabled later)
- Confirm standard deduction value and tax year used in calculations
- Confirm frontend expected payload shapes and field naming
- Confirm parser approach for PDFs before implementation
