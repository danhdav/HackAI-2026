"""Deterministic 1040 draft calculation logic."""

from app.models.response_models import Draft1040Values
from app.utils.constants import SINGLE_FILER_TAX_BRACKETS, STANDARD_DEDUCTION_SINGLE


class CalculationService:
    """Computes required 1040 draft fields from parsed session data."""

    @staticmethod
    def calculate_single_filer_tax(taxable_income: float) -> float:
        """Compute progressive federal tax for single filer brackets."""
        if taxable_income <= 0:
            return 0.0

        tax = 0.0
        lower_bound = 0.0
        remaining = taxable_income

        for upper_bound, rate in SINGLE_FILER_TAX_BRACKETS:
            bracket_width = upper_bound - lower_bound
            taxable_in_bracket = min(remaining, bracket_width)
            if taxable_in_bracket <= 0:
                break

            tax += taxable_in_bracket * rate
            remaining -= taxable_in_bracket
            lower_bound = upper_bound

            if remaining <= 0:
                break

        return round(tax, 2)

    def compute_draft_1040(self, parsed_data: dict) -> Draft1040Values:
        """
        Apply MVP deterministic formulas for selected 1040 fields.

        TODO: Add education credit logic using 1098-T values.
        TODO: Add owed amount handling (e.g., line 37) if withholding < tax.
        """
        w2_data = parsed_data.get("w2") or {}
        wages = float(w2_data.get("box1", 0.0))
        withholding = float(w2_data.get("box2", 0.0))

        line_1a = wages
        line_1z = line_1a
        line_9 = line_1z
        line_11a = line_9
        line_11b = line_11a

        taxable_income = max(line_11b - STANDARD_DEDUCTION_SINGLE, 0.0)
        line_15 = taxable_income
        line_16 = self.calculate_single_filer_tax(taxable_income)

        line_25a = withholding
        line_25d = line_25a

        refund = max(line_25d - line_16, 0.0)
        line_34 = refund

        return Draft1040Values(
            line_1a=round(line_1a, 2),
            line_1z=round(line_1z, 2),
            line_9=round(line_9, 2),
            line_11a=round(line_11a, 2),
            line_11b=round(line_11b, 2),
            line_15=round(line_15, 2),
            line_16=round(line_16, 2),
            line_25a=round(line_25a, 2),
            line_25d=round(line_25d, 2),
            line_34=round(line_34, 2),
        )
