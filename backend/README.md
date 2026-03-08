# Running Backend

Prerequisites:
Install [uv](https://docs.astral.sh/uv/) 

In the backend folder:
`uv init`

Install from the dependencies file pyproject.toml:
`uv sync`

Activate your venv:
`source .venv/bin/activate`

OR if using powershell:
`.venv\bin\activate`

Run:
`uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`