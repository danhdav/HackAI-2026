# TaxMaxx

TaxMaxx is a tax-assistant web app that helps users upload a W-2 and 1098-T, extract key values, and generate a draft 1040 summary.

## Current State

### Frontend
- React + Vite UI with Figma-inspired upload/results flow
- Upload validation for `W2.pdf` and `1098-T.pdf`
- Results page now displays live backend-calculated draft 1040 values (not hardcoded)
- Chatbot panel is scaffolded in the UI

### Backend
- FastAPI backend with modular architecture (`routes`, `services`, `models`, `db`)
- MongoDB persistence for:
  - tax sessions (`tax_sessions`)
  - parser box-data docs (`box_data`)
- Parser integration supports:
  - canonical endpoint: `POST /api/parser/parse`
  - frontend-compatible endpoint: `POST /api/parser/box-data`
- Deterministic 1040 calculation pipeline and draft retrieval:
  - `POST /api/calculations/run/{session_id}`
  - `GET /api/calculations/draft/{session_id}`

### Document Parsing
- Azure Document Intelligence integration for W-2 / 1098-T
- Filename-based model selection (`W2` vs `1098-T`)
- Mock mode remains available for low-cost testing

## Planned / In Progress

- Improve parser robustness for real-world PDFs (confidence/error handling)
- Expand tax logic beyond MVP lines and assumptions
- Finish chatbot backend integration (currently scaffold only)
- Add stronger automated testing and better production error reporting

## Tech Stack

- Frontend: React, Vite
- Backend: Python, FastAPI
- Database: MongoDB Atlas
- Parsing: Azure Document Intelligence

## Local Dev Quick Start

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
