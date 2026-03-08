def parse_tax_fields(document_fields, document_type):
    parsed_data = {"parsed_data": {document_type: {}}}
    form = parsed_data["parsed_data"][document_type]

    # Money-related 1098-T fields
    money_fields = [
        # 1098
        "PaymentReceived",
        "AdjustmentsForPriorYear",
        "Scholarships",
        "ScholarshipsAdjustments",
        "InsuranceContractReimbursements"

        # W2
        "WagesTipsAndOtherCompensation",
        "FederalIncomeTaxWithheld",
        "SocialSecurityWages",
        "SocialSecurityTaxWithheld",
        "MedicareWagesAndTips",
        "MedicareTaxWithheld",
        "SocialSecurityTips"
    ]

    for field in money_fields:

        field_obj = document_fields.get(field)

        if not field_obj:
            continue

        # Drill down into valueObject if present
        if "valueObject" in field_obj:
            field_obj = field_obj["valueObject"]

        # Extract content if available
        if "content" in field_obj and field_obj["content"] is not None:
            form[field] = field_obj["content"]
            print(f"{field} parse successful!")

    print("Money field parsing complete!")

    return parsed_data