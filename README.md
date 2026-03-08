# TaxMaxx

TaxMaxx is a hackathon project that helps users upload tax documents (W-2 and 1098-T), extract the key values, run deterministic 1040 draft calculations, and present a clear summary through a modern frontend experience.

## Problem We Are Solving

Filing taxes is confusing for many students and first-time filers.  
TaxMaxx is designed to reduce friction by:
- parsing key values from tax forms,
- explaining what those values mean,
- showing a draft 1040-oriented summary users can review before filing.

## Current Implementation

### Frontend
- React-based upload and results flow
- Supports document upload for:
  - `W2.pdf`
  - `1098-T.pdf`
- Displays tax summary values returned by backend calculations
- Basic chatbot UI scaffold is present

### Backend
- FastAPI backend scaffold with modular structure (`routes`, `services`, `models`, `db`)
- MongoDB integration for session-oriented data persistence
- Parser endpoints:
  - canonical parse endpoint (`/api/parser/parse`)
  - frontend-compatible parser flow (`/api/parser/box-data`)
  - box-data storage/edit endpoints (`/api/parser/box-data/store`, update/delete)
- Deterministic tax calculation pipeline for draft 1040 fields
- Health, session, and calculations endpoints for frontend integration

### Data Flow (Current)
1. User uploads W-2 and 1098-T from frontend.
2. Backend parser extracts / normalizes required values.
3. Parsed values are stored in MongoDB.
4. Deterministic calculation service computes draft 1040 values.
5. Frontend renders summary cards and allows iterative UX improvements.

## In Progress / Planned

### Parser Improvements
- Improve extraction accuracy and validation for real-world PDFs
- Better confidence/error reporting from parser pipeline
- Stronger file-type checking beyond filename assumptions

### Calculation Expansion
- Extend 1040 coverage beyond current MVP lines
- Add tax-owed path (not only refund estimate)
- Add richer education-credit logic using 1098-T fields

### Chatbot Integration
- Connect chatbot to live session/draft data
- Add explanation-first responses ("why this number?")
- Add guarded edit flow for user-approved value corrections

### Product & Demo Readiness
- Harden environment setup and teammate onboarding docs
- Add test coverage (API smoke + service-level tests)
- Improve reliability and observability (errors/logging/diagnostics)

## Tech Stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: MongoDB Atlas
- Document Parsing: Azure Document Intelligence (plus mock mode support)

## Team Development Notes
- We maintain modular backend services to allow parallel development.
- Mock/test modes are used to unblock frontend and calculations when parser APIs are limited.
- We are actively integrating parser, storage, calculations, and UX flows into a cohesive demo-ready product.
