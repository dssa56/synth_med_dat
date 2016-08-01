from cancer_story import Birth, ev_dict
from ev_cl import State
from collections import defaultdict
import json
import names
from make_fam_hist import make_fam_hist
from generate_risk import generate_risk
import models.humanname as hn
import models.patient as pt
import models.condition as cnd
import models.identifier as idn
import models.codeableconcept as cc
from make_date import set_dates
from models.fhirreference import FHIRReference
import os
from glob import glob

n_years = 100
n_records = 100
icd_10 = json.load(open('icd.json'))

gdpth = '/Users/lawrence.phillips/synth_dat/generated_data/'

paths = {
    'patpath': gdpth + 'patients/',
    'conpath': gdpth + 'conditions/',
    'qpath': gdpth + 'questionnaires/',
    'fhpath': gdpth + 'family_history/',
    'fspath': gdpth + 'family_structure/'
    }

for path in paths.keys():
    for f in glob(paths[path] + '*.json'):
        os.remove(f)

rd = {'M': defaultdict(list), 'F': defaultdict(list)}

for sex in rd.keys():
    state = State(contents=[sex])
    b = Birth(state, n_years)

    for i in range(n_records):
        pat_identifier = idn.Identifier({'value': sex+str(i)})
        cond_identifier = idn.Identifier({'value': sex+str(i)})
        name = hn.HumanName()
        patient = pt.Patient()
        patient.identifier = [pat_identifier]
        name.given = [names.get_first_name(gender='male'
                                           if sex == 'M' else 'female')]
        name.family = [names.get_last_name()]
        patient.name = [name]
        patient.gender = sex
        record = []
        events = [b]
        while True:
            cns = [event.get_consequences() for event in events]
            cns = [cn for cn in cns if cn is not None]
            if not cns:
                break
            for cn in cns:
                record.append(cn)
            events = [ev_dict[c[0]](state, n_years) for c in cns]

        condition = cnd.Condition()
        condition.identifier = [cond_identifier]
        set_dates(record[0][1], condition, patient)
        reference = {'reference':
                     paths['patpath']+pat_identifier.value+'.json'}

        if record[0][0] == 'C50':
            make_fam_hist(record[0][1], reference, pat_identifier)

        condition.patient = FHIRReference(reference)

        condition.code = cc.CodeableConcept(
                {'coding': [{'system': 'icd-10', 'code': record[0][0]}],
                 'text': icd_10[record[0][0]]}
        )

        condition.verificationStatus = 'confirmed'

        risk = generate_risk(record[0][0], condition.patient, patient)

        json.dump(risk.as_json(),
                  open(paths['qpath']+risk.identifier.value+'.json', 'w'))
        json.dump(patient.as_json(),
                  open(paths['patpath']+pat_identifier.value+'.json', 'w'))
        json.dump(condition.as_json(),
                  open(paths['conpath']+cond_identifier.value+'.json', 'w'))


json.dump(rd, open('rd.json', 'w'))
