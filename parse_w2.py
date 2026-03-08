def print_w2_fields(document_fields):

    # -------------------------
    # Box 1
    # -------------------------
    if document_fields.get('WagesTipsAndOtherCompensation'):
        print('Box1:', document_fields['WagesTipsAndOtherCompensation']['content'])

    # -------------------------
    # Box 2
    # -------------------------
    if document_fields.get('FederalIncomeTaxWithheld'):
        print('Box2:', document_fields['FederalIncomeTaxWithheld']['content'])

    # -------------------------
    # Box 3
    # -------------------------
    if document_fields.get('SocialSecurityWages'):
        print('Box3:', document_fields['SocialSecurityWages']['content'])

    # -------------------------
    # Box 4
    # -------------------------
    if document_fields.get('SocialSecurityTaxWithheld'):
        print('Box4:', document_fields['SocialSecurityTaxWithheld']['content'])

    # -------------------------
    # Box 5
    # -------------------------
    if document_fields.get('MedicareWagesAndTips'):
        print('Box5:', document_fields['MedicareWagesAndTips']['content'])

    # -------------------------
    # Box 6
    # -------------------------
    if document_fields.get('MedicareTaxWithheld'):
        print('Box6:', document_fields['MedicareTaxWithheld']['content'])

    # -------------------------
    # Box 7
    # -------------------------
    if document_fields.get('SocialSecurityTips'):
        if document_fields['SocialSecurityTips']['content']:
            print('Box7:', document_fields['SocialSecurityTips']['content'])

    # -------------------------
    # Box 8
    # -------------------------
    if document_fields.get('AllocatedTips'):
        print('Box8:', document_fields['AllocatedTips']['content'])

    # -------------------------
    # Box 9 (Verification Code)
    # -------------------------
    if document_fields.get('VerificationCode'):
        print('Box9:', document_fields['VerificationCode']['content'])

    # -------------------------
    # Box 10
    # -------------------------
    if document_fields.get('DependentCareBenefits'):
        print('Box10:', document_fields['DependentCareBenefits']['content'])

    # -------------------------
    # Box 11
    # -------------------------
    if document_fields.get('NonQualifiedPlans'):
        print('Box11:', document_fields['NonQualifiedPlans']['content'])

    # -------------------------
    # Box 12 (Multiple entries)
    # -------------------------
    if document_fields.get('AdditionalInfo'):
        for item in document_fields['AdditionalInfo']['valueArray']:
            code = item['valueObject']['LetterCode']['content']
            amount = item['valueObject']['Amount']['content']
            print(f'Box12 ({code}):', amount)

    # -------------------------
    # Box 13 Flags
    # -------------------------
    if document_fields.get('IsStatutoryEmployee'):
        print('Box13 StatutoryEmployee:', document_fields['IsStatutoryEmployee']['content'])

    if document_fields.get('IsRetirementPlan'):
        print('Box13 RetirementPlan:', document_fields['IsRetirementPlan']['content'])

    if document_fields.get('IsThirdPartySickPay'):
        print('Box13 ThirdPartySickPay:', document_fields['IsThirdPartySickPay']['content'])

    # -------------------------
    # Box 14
    # -------------------------
    if document_fields.get('Other'):
        print('Box14:', document_fields['Other']['content'])

    # -------------------------
    # Boxes 15–17 (State)
    # -------------------------
    if document_fields.get('StateTaxInfos'):
        for state in document_fields['StateTaxInfos']['valueArray']:
            state_obj = state['valueObject']

            if state_obj.get('State'):
                print('Box15 State:', state_obj['State']['content'])

            if state_obj.get('EmployerStateIdNumber'):
                print('Box15 EmployerStateID:', state_obj['EmployerStateIdNumber']['content'])

            if state_obj.get('StateWagesTipsEtc'):
                print('Box16 StateWages:', state_obj['StateWagesTipsEtc']['content'])

            if state_obj.get('StateIncomeTax'):
                print('Box17 StateIncomeTax:', state_obj['StateIncomeTax']['content'])

    # -------------------------
    # Boxes 18–20 (Local)
    # -------------------------
    if document_fields.get('LocalTaxInfos'):
        for local in document_fields['LocalTaxInfos']['valueArray']:
            local_obj = local['valueObject']

            if local_obj.get('LocalWagesTipsEtc'):
                print('Box18 LocalWages:', local_obj['LocalWagesTipsEtc']['content'])

            if local_obj.get('LocalIncomeTax'):
                print('Box19 LocalIncomeTax:', local_obj['LocalIncomeTax']['content'])

            if local_obj.get('LocalityName'):
                print('Box20 LocalityName:', local_obj['LocalityName']['content'])
