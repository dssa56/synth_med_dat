import models.familymemberhistory as fmh
import json

smf = json.load(open('snomed_fam.json'))
path = 'generated_data/family_history/'


def make_fam_hist(famhist, patient, ident):
    i = 0
    for k in famhist.keys():
        if 'BC' in famhist[k]:
            if k == 'gmm':
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Maternal Grandma']}],
                         'text': 'Maternal Grandmother'}
                )
            elif k == 'gmp':
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Paternal Grandma']}],
                         'text': 'Paternal Grandmother'}
                )
            elif k == 'mum':
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Mother']}],
                         'text': 'Mother'}
                )
            elif 'sib' in k and 'daught' in k:
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Female Cousin']}],
                         'text': 'Female Cousin'}
                )
            elif 'sib' in k:
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Aunt']}],
                         'text': 'Aunt'}
                )
            else:
                rln = (
                        {'coding': [{'system': 'SNOMED-CT',
                                     'code': smf['Sister']}],
                         'text': 'Sister'}
                )

            hist = fmh.FamilyMemberHistory({'status': 'completed',
                                            'patient': patient,
                                            'relationship': rln})

            hist.condition = [fmh.FamilyMemberHistoryCondition(
                {'code': (
                    {'coding': [{'system': 'icd-10', 'code': 'C50'}],
                     'text': 'Malignant neoplasm of breast'}),
                 'onsetQuantity': {'value': famhist[k][1], 'unit': 'years'}}
            )]

            json.dump(hist.as_json(),
                      open(path + ident.value + str(i) + '.json', 'w'))
            i += 1
