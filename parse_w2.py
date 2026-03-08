def parse_w2_fields(document_fields):

    parsed_data = {"parsed_data": {"w2": {}}}
    w2 = parsed_data["parsed_data"]["w2"]

    # -------------------------
    # Box 1
    # -------------------------
    if document_fields.get('WagesTipsAndOtherCompensation'):
        w2["box1"] = document_fields['WagesTipsAndOtherCompensation']['content']

    # -------------------------
    # Box 2
    # -------------------------
    if document_fields.get('FederalIncomeTaxWithheld'):
        w2["box2"] = document_fields['FederalIncomeTaxWithheld']['content']

    # -------------------------
    # Box 3
    # -------------------------
    if document_fields.get('SocialSecurityWages'):
        w2["box3"] = document_fields['SocialSecurityWages']['content']

    # -------------------------
    # Box 4
    # -------------------------
    if document_fields.get('SocialSecurityTaxWithheld'):
        w2["box4"] = document_fields['SocialSecurityTaxWithheld']['content']

    # -------------------------
    # Box 5
    # -------------------------
    if document_fields.get('MedicareWagesAndTips'):
        w2["box5"] = document_fields['MedicareWagesAndTips']['content']

    # -------------------------
    # Box 6
    # -------------------------
    if document_fields.get('MedicareTaxWithheld'):
        w2["box6"] = document_fields['MedicareTaxWithheld']['content']

    # -------------------------
    # Box 7
    # -------------------------
    if document_fields.get('SocialSecurityTips'):
        if document_fields['SocialSecurityTips']['content']:
            w2["box7"] = document_fields['SocialSecurityTips']['content']

    # -------------------------
    # Box 8
    # -------------------------
    if document_fields.get('AllocatedTips'):
        w2["box8"] = document_fields['AllocatedTips']['content']

    # -------------------------
    # Box 9
    # -------------------------
    if document_fields.get('VerificationCode'):
        w2["box9"] = document_fields['VerificationCode']['content']

    # -------------------------
    # Box 10
    # -------------------------
    if document_fields.get('DependentCareBenefits'):
        w2["box10"] = document_fields['DependentCareBenefits']['content']

    # -------------------------
    # Box 11
    # -------------------------
    if document_fields.get('NonQualifiedPlans'):
        w2["box11"] = document_fields['NonQualifiedPlans']['content']

    # -------------------------
    # Box 12 (multiple)
    # -------------------------
    if document_fields.get('AdditionalInfo'):
        w2["box12"] = []

        for item in document_fields['AdditionalInfo']['valueArray']:
            code = item['valueObject']['LetterCode']['content']
            amount = item['valueObject']['Amount']['content']

            w2["box12"].append({
                "code": code,
                "amount": amount
            })

    # -------------------------
    # Box 13 Flags
    # -------------------------
    box13 = {}

    if document_fields.get('IsStatutoryEmployee'):
        box13["statutory_employee"] = document_fields['IsStatutoryEmployee']['content']

    if document_fields.get('IsRetirementPlan'):
        box13["retirement_plan"] = document_fields['IsRetirementPlan']['content']

    if document_fields.get('IsThirdPartySickPay'):
        box13["third_party_sick_pay"] = document_fields['IsThirdPartySickPay']['content']

    if box13:
        w2["box13"] = box13

    # -------------------------
    # Box 14
    # -------------------------
    if document_fields.get('Other'):
        w2["box14"] = document_fields['Other']['content']

    # -------------------------
    # State Tax Info (15–17)
    # -------------------------
    if document_fields.get('StateTaxInfos'):
        w2["state_tax_info"] = []

        for state in document_fields['StateTaxInfos']['valueArray']:
            state_obj = state['valueObject']
            entry = {}

            if state_obj.get('State'):
                entry["state"] = state_obj['State']['content']

            if state_obj.get('EmployerStateIdNumber'):
                entry["employer_state_id"] = state_obj['EmployerStateIdNumber']['content']

            if state_obj.get('StateWagesTipsEtc'):
                entry["state_wages"] = state_obj['StateWagesTipsEtc']['content']

            if state_obj.get('StateIncomeTax'):
                entry["state_income_tax"] = state_obj['StateIncomeTax']['content']

            if entry:
                w2["state_tax_info"].append(entry)

    # -------------------------
    # Local Tax Info (18–20)
    # -------------------------
    if document_fields.get('LocalTaxInfos'):
        w2["local_tax_info"] = []

        for local in document_fields['LocalTaxInfos']['valueArray']:
            local_obj = local['valueObject']
            entry = {}

            if local_obj.get('LocalWagesTipsEtc'):
                entry["local_wages"] = local_obj['LocalWagesTipsEtc']['content']

            if local_obj.get('LocalIncomeTax'):
                entry["local_income_tax"] = local_obj['LocalIncomeTax']['content']

            if local_obj.get('LocalityName'):
                entry["locality_name"] = local_obj['LocalityName']['content']

            if entry:
                w2["local_tax_info"].append(entry)

    return parsed_data