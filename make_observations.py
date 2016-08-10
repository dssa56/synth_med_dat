import models.observation as ob
import models.codeableconcept as cc
import models.diagnosticreport as dr
from models.fhirreference import FHIRReference
import re
import json
import datetime
import random
import pandas

stdict = json.load(open('st_dict.json'))
codes = pandas.read_csv('stomach_snomed.csv')

path = '/Users/lawrence.phillips/synth_dat/generated_data/'


def add_days(d, plusdays):
    l = [int(i) for i in d.split('-')]
    inc = datetime.timedelta(days=plusdays)
    cd = datetime.date(*l) + inc
    return str(cd)


def get_instant():
    hr = str(random.choice(range(24)))
    mi = str(random.choice(range(60)))
    sec = str(random.choice(range(60)))
    t = [hr, mi, sec]
    t = [i if len(i) == 2 else '0' + i for i in t]
    return 'T' + ':'.join(t) + 'Z'


def make_observations(record, state, reference, base_date, pat):
    r = dict(record)
    condition = [i for i in r.keys() if re.match(re.compile('C[0-9]'), i)][0]
    if condition == 'C16':
        stage = [i for i in state.contents
                 if type(i) == tuple and
                 re.match(re.compile('C[0-9]'), i[0])][0][1]
        TNM = random.choice(stdict['C16'][str(stage)])
        endob_list = []
        endob_inst = get_instant()
        for i, finding in enumerate(TNM):
            l = ['T', 'N'][i]
            if finding == '0':
                continue
            end_ob = ob.Observation()
            end_ob.status = 'final'
            end_ob.subject = FHIRReference(reference)
            end_ob.code = cc.CodeableConcept({'coding':
                                             [{'code': '18751-8',
                                               'system': 'LOINC'}],
                                              'text': 'Endoscopy study'})
            end_ob.valueCodeableConcept = cc.CodeableConcept(
                {'coding': [{'code':
                             str(codes.code[
                                 codes['tnm'] == l+finding].iloc[0]),
                             'system': 'SNOMED-CT'}],
                 'text':
                     codes.description[codes['tnm'] == l+finding].iloc[0]})
            end_ob.instant = (add_days(base_date, r['Test: Endoscopy'])
                              + endob_inst)
            endob_list.append({'reference':
                              path + 'observations/' +
                              pat.identifier[0].value +
                              str(i) + '.json'})
            json.dump(end_ob.as_json(), open(path + 'observations/' +
                                             pat.identifier[0].value + 'end' +
                                             str(i) + '.json', 'w'))

        drep = dr.DiagnosticReport({'code':
                                    {'coding':
                                     [{'code': '18751-8',
                                       'system': 'LOINC'}],
                                     'text': 'Endoscopy study'},
                                    'status': 'final',
                                    'issued': (add_days(base_date,
                                                        r['Test: Endoscopy'])
                                               + endob_inst),
                                    'effectiveDateTime':
                                    add_days(base_date, r['Test: Endoscopy']),
                                    'performer': {'reference':
                                                  'Endoscopy dept.'},
                                    'subject': reference,
                                    'result': endob_list})
        json.dump(drep.as_json(), open(path + 'diagnostic_reports/' +
                                       pat.identifier[0].value, 'w'))

        ct_ob = ob.Observation()
        ct_ob.status = 'final'
        ct_ob.subject = FHIRReference(reference)
        ct_ob.code = cc.CodeableConcept({'coding':
                                         [{'code': '24627-2',
                                           'system': 'LOINC'}],
                                         'text': 'Chest CT'})
        ct_ob.valueCodeableConcept = cc.CodeableConcept(
            {'coding': [{'code': '14926007'
                                 if stage == 4 else '19408000',
                         'system': 'SNOMED-CT'}],
             'text': 'No distant metastasis' if stage != 4
                     else 'Distant metastasis present'})
        ct_ob.instant = (add_days(base_date, r['Test: CT scan'])
                         + get_instant())

        json.dump(ct_ob.as_json(), open(path + 'observations/' +
                                        pat.identifier[0].value + 'ct'
                                        + '.json', 'w'))
