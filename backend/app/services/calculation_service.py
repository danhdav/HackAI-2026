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

    def _extract_inputs(self, parsed_data: dict) -> tuple[float, float, float, float]:
        """Extract normalized numeric inputs from parsed data payload."""
        w2_data = parsed_data.get("w2") or {}
        t1098_data = parsed_data.get("1098t") or {}

        wages = max(float(w2_data.get("box1", 0.0)), 0.0)
        withholding = max(float(w2_data.get("box2", 0.0)), 0.0)
        tuition_paid = max(float(t1098_data.get("box1", 0.0)), 0.0)
        scholarships = max(float(t1098_data.get("box5", 0.0)), 0.0)

        return wages, withholding, tuition_paid, scholarships

    def compute_draft_1040(self, parsed_data: dict) -> Draft1040Values:
        """
        Apply MVP deterministic formulas for selected 1040 fields.

        TODO: Add education credit logic using 1098-T values.
        TODO: Add owed amount handling (e.g., line 37) if withholding < tax.
        """
        wages, withholding, _, _ = self._extract_inputs(parsed_data)

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

    def build_calculation_inputs(self, parsed_data: dict) -> dict:
        """
        Return normalized inputs/intermediate values used for drafting.

        This keeps storage explicit so frontend and chatbot can explain
        how the deterministic draft was produced.
        """
        wages, withholding, tuition_paid, scholarships = self._extract_inputs(parsed_data)
        taxable_income = max(wages - STANDARD_DEDUCTION_SINGLE, 0.0)

        return {
            "filing_status": "single",
            "deduction_type": "standard",
            "standard_deduction_single": round(STANDARD_DEDUCTION_SINGLE, 2),
            "w2_box1_wages": round(wages, 2),
            "w2_box2_withholding": round(withholding, 2),
            "form_1098t_box1_tuition_paid": round(tuition_paid, 2),
            "form_1098t_box5_scholarships": round(scholarships, 2),
            "taxable_income": round(taxable_income, 2),
        }
