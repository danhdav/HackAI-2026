"""Sample data fixtures for mock/testing flows."""

from copy import deepcopy

SAMPLE_SESSION_ID = "session_mock_001"

SAMPLE_W2_PARSED = {"box1": 52000.0, "box2": 4100.0}
SAMPLE_1098T_PARSED = {"box1": 9000.0, "box5": 2500.0}

SAMPLE_PARSED_DATA = {
    "w2": deepcopy(SAMPLE_W2_PARSED),
    "1098t": deepcopy(SAMPLE_1098T_PARSED),
}

SAMPLE_DRAFT_1040 = {
    "line_1a": 52000.0,
    "line_1z": 52000.0,
    "line_9": 52000.0,
    "line_11a": 52000.0,
    "line_11b": 52000.0,
    "line_15": 37400.0,
    "line_16": 4276.0,
    "line_25a": 4100.0,
    "line_25d": 4100.0,
    "line_34": 0.0,
}

SAMPLE_FULL_SESSION = {
    "session_id": SAMPLE_SESSION_ID,
    "parsed_data": deepcopy(SAMPLE_PARSED_DATA),
    "calculation_inputs": {"filing_status": "single", "deduction_type": "standard"},
    "draft_1040": deepcopy(SAMPLE_DRAFT_1040),
    "chatbot_history": [],
    "status": {
        "parser_status": "completed",
        "calculation_status": "completed",
        "chatbot_status": "disabled",
    },
    "metadata": {
        "user_id": "demo_user_001",
        "tax_year": 2024,
        "notes": "Mock seed session for local testing",
        "extras": {},
    },
}


def get_sample_parsed_data() -> dict:
    """Return deep-copied sample parsed intake data."""
    return deepcopy(SAMPLE_PARSED_DATA)


def get_sample_draft_1040() -> dict:
    """Return deep-copied sample draft 1040 values."""
    return deepcopy(SAMPLE_DRAFT_1040)


def get_sample_session() -> dict:
    """Return deep-copied sample session document."""
    return deepcopy(SAMPLE_FULL_SESSION)
