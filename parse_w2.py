def parse_w2_fields(document_fields):

    parsed_data = {"parsed_data": {"w2": {}}}
    w2 = parsed_data["parsed_data"]["w2"]

    # -------------------------
    # Box 1
    # -------------------------
    if document_fields.get('WagesTipsAndOtherCompensation'):
        if 'content' in document_fields['WagesTipsAndOtherCompensation']:
            w2["box1"] = document_fields['WagesTipsAndOtherCompensation']['content']
        print("Box 1 parse successful!")

    # -------------------------
    # Box 2
    # -------------------------
    if document_fields.get('FederalIncomeTaxWithheld'):
        if 'content' in document_fields['FederalIncomeTaxWithheld']:
            w2["box2"] = document_fields['FederalIncomeTaxWithheld']['content']
        print("Box 2 parse successful!")

    # -------------------------
    # Box 3
    # -------------------------
    if document_fields.get('SocialSecurityWages'):
        if 'content' in document_fields['SocialSecurityWages']:
            w2["box3"] = document_fields['SocialSecurityWages']['content']
        print("Box 3 parse successful!")

    # -------------------------
    # Box 4
    # -------------------------
    if document_fields.get('SocialSecurityTaxWithheld'):
        if 'content' in document_fields['SocialSecurityTaxWithheld']:
            w2["box4"] = document_fields['SocialSecurityTaxWithheld']['content']
        print("Box 4 parse successful!")

    # -------------------------
    # Box 5
    # -------------------------
    if document_fields.get('MedicareWagesAndTips'):
        if 'content' in document_fields['MedicareWagesAndTips']:
            w2["box5"] = document_fields['MedicareWagesAndTips']['content']
        print("Box 5 parse successful!")

    # -------------------------
    # Box 6
    # -------------------------
    if document_fields.get('MedicareTaxWithheld'):
        if 'content' in document_fields['MedicareTaxWithheld']:
            w2["box6"] = document_fields['MedicareTaxWithheld']['content']
            print("Box 6 parse successful!")

    # -------------------------
    # Box 7
    # -------------------------
    if document_fields.get('SocialSecurityTips'):
        if 'content' in document_fields['SocialSecurityTips']:
            w2["box7"] = document_fields['SocialSecurityTips']['content']
        print("Box 7 parse successful!")

    # -------------------------
    # Box 8
    # -------------------------
    if document_fields.get('AllocatedTips'):
        if 'content' in document_fields['AllocatedTips']:
            w2["box8"] = document_fields['AllocatedTips']['content']
        print("Box 8 parse successful!")

    # -------------------------
    # Box 9
    # -------------------------
    if document_fields.get('VerificationCode'):
        if 'content' in document_fields['VerificationCode']:
            w2["box9"] = document_fields['VerificationCode']['content']
        print("Box 9 parse successful!")

    # -------------------------
    # Box 10
    # -------------------------
    if document_fields.get('DependentCareBenefits'):
        if 'content' in document_fields['DependentCareBenefits']:
            w2["box10"] = document_fields['DependentCareBenefits']['content']
        print("Box 10 parse successful!")

    # -------------------------
    # Box 11
    # -------------------------
    if document_fields.get('NonQualifiedPlans'):
        if 'content' in document_fields['NonQualifiedPlans']:
            w2["box11"] = document_fields['NonQualifiedPlans']['content']
        print("Box 11 parse successful!")

    # -------------------------
    # Box 12 (multiple)
    # I'm having issues with box 12 parsing for now
    # -------------------------
    # if document_fields.get('AdditionalInfo'):
    #     w2["box12"] = []

    #     for item in document_fields['AdditionalInfo']['valueArray']:
    #         if 'content' in item['valueObject']['LetterCode'] and 'content' in item['valueObject']['Amount']:
    #             code = item['valueObject']['LetterCode']['content']
    #             amount = item['valueObject']['Amount']['content']

    #             w2["box12"].append({
    #                 "code": code,
    #                 "amount": amount
    #             })

    # -------------------------
    # Box 13 Flags
    # -------------------------
    box13 = {}

    if document_fields.get('IsStatutoryEmployee'):
        if 'content' in document_fields['IsStatutoryEmployee']:
            box13["statutory_employee"] = document_fields['IsStatutoryEmployee']['content']

    if document_fields.get('IsRetirementPlan'):
        if 'content' in document_fields['IsRetirementPlan']:
            box13["retirement_plan"] = document_fields['IsRetirementPlan']['content']

    if document_fields.get('IsThirdPartySickPay'):
        if 'content' in document_fields['IsThirdPartySickPay']:
            box13["third_party_sick_pay"] = document_fields['IsThirdPartySickPay']['content']

    if box13:
        w2["box13"] = box13

    # -------------------------
    # Box 14
    # -------------------------
    if document_fields.get('Other'):
        if 'content' in document_fields['Other']:
            w2["box14"] = document_fields['Other']['content']

    # -------------------------
    # State Tax Info (15–17)
    # -------------------------
    # if document_fields.get('StateTaxInfos'):
    #     w2["state_tax_info"] = []

    #     for state in document_fields['StateTaxInfos']['valueArray']:
    #         state_obj = state['valueObject']
    #         entry = {}

    #         if state_obj.get('State'):
    #             entry["state"] = state_obj['State']['content']

    #         if state_obj.get('EmployerStateIdNumber'):
    #             entry["employer_state_id"] = state_obj['EmployerStateIdNumber']['content']

    #         if state_obj.get('StateWagesTipsEtc'):
    #             entry["state_wages"] = state_obj['StateWagesTipsEtc']['content']

    #         if state_obj.get('StateIncomeTax'):
    #             entry["state_income_tax"] = state_obj['StateIncomeTax']['content']

    #         if entry:
    #             w2["state_tax_info"].append(entry)

    # -------------------------
    # Local Tax Info (18–20)
    # -------------------------
    # if document_fields.get('LocalTaxInfos'):
    #     w2["local_tax_info"] = []

    #     for local in document_fields['LocalTaxInfos']['valueArray']:
    #         local_obj = local['valueObject']
    #         entry = {}

    #         if local_obj.get('LocalWagesTipsEtc'):
    #             entry["local_wages"] = local_obj['LocalWagesTipsEtc']['content']

    #         if local_obj.get('LocalIncomeTax'):
    #             entry["local_income_tax"] = local_obj['LocalIncomeTax']['content']

    #         if local_obj.get('LocalityName'):
    #             entry["locality_name"] = local_obj['LocalityName']['content']

    #         if entry:
    #             w2["local_tax_info"].append(entry)

    print("W2 parsing complete!")
    return parsed_data