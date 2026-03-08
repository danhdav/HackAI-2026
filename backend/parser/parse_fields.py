"""Extract relevant monetary fields from Azure parser output."""


def parse_tax_fields(document_fields: dict, document_type: str) -> dict:
    """Construct parser payload keyed by tax form type."""
    parsed_data = {"parsed_data": {document_type: {}}}
    form = parsed_data["parsed_data"][document_type]

    money_fields = [
        # 1098-T
        "PaymentReceived",
        "AdjustmentsForPriorYear",
        "Scholarships",
        "ScholarshipsAdjustments",
        "InsuranceContractReimbursements",
        # W-2
        "WagesTipsAndOtherCompensation",
        "FederalIncomeTaxWithheld",
        "SocialSecurityWages",
        "SocialSecurityTaxWithheld",
        "MedicareWagesAndTips",
        "MedicareTaxWithheld",
        "SocialSecurityTips",
    ]

    for field in money_fields:
        field_obj = document_fields.get(field)
        if not field_obj:
            continue

        if "valueObject" in field_obj:
            field_obj = field_obj["valueObject"]

        if "content" in field_obj and field_obj["content"] is not None:
            form[field] = field_obj["content"]

    return parsed_data
