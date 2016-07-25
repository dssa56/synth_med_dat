from cancer_story import Birth, ev_dict
from ev_cl import State
from collections import defaultdict
import json
import names
from generate_risk import generate_risk
import models.humanname as hn
import models.patient as pt
import models.condition as cnd
import models.identifier as idn
import models.codeableconcept as cc
from make_date import set_dates
from models.fhirreference import FHIRReference

n_years = 100
n_records = 5
icd_10 = json.load(open('icd.json'))

patpath = '/Users/lawrence.phillips/synth_dat/generated_data/patients/'
conpath = '/Users/lawrence.phillips/synth_dat/generated_data/conditions/'
qpath = '/Users/lawrence.phillips/synth_dat/generated_data/questionnaires/'

rd = {'M': defaultdict(list), 'F': defaultdict(list)}

for sex in rd.keys():
    state = State(contents=[sex])
    b = Birth(state, n_years)

    for i in range(n_records):
        pat_identifier = idn.Identifier({'value': sex+str(i)})
        cond_identifier = idn.Identifier({'value': sex+'c'+str(i)})
        name = hn.HumanName()
        patient = pt.Patient()
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
        set_dates(record[0][1], condition, patient)
        reference = {'reference': patpath+pat_identifier.value+'.json'}
        condition.patient = FHIRReference(reference)

        condition.code = cc.CodeableConcept(
                {'coding': [{'system': 'icd-10', 'code': record[0][0]}],
                 'text': icd_10[record[0][0]]}
        )

        condition.verificationStatus = 'confirmed'

        risk = generate_risk(record[0][0], condition.patient, pat_identifier)

        json.dump(risk.as_json(),
                  open(qpath+risk.identifier.value+'.json', 'w'))
        json.dump(patient.as_json(),
                  open(patpath+pat_identifier.value+'.json', 'w'))
        json.dump(condition.as_json(),
                  open(conpath+cond_identifier.value+'.json', 'w'))


json.dump(rd, open('rd.json', 'w'))
