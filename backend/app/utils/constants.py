"""Shared constants for deterministic tax calculations."""

from app.config import settings

# TODO: Validate the filing year with product requirements.
STANDARD_DEDUCTION_SINGLE = settings.standard_deduction_single

# Single filer federal brackets for an MVP approximation.
# These should be validated and versioned by tax year in production.
SINGLE_FILER_TAX_BRACKETS = [
    (11600.0, 0.10),
    (47150.0, 0.12),
    (100525.0, 0.22),
    (191950.0, 0.24),
    (243725.0, 0.32),
    (609350.0, 0.35),
    (float("inf"), 0.37),
]
