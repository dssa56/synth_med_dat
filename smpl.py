from cancer_story import Birth, ev_dict
from ev_cl import State
from collections import defaultdict
from make_observations import make_observations
import json
import names
from make_fam_hist import make_fam_hist
from make_fam_quest import make_fam_quest
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
from survive import build_family_genotype, build_family_phenotype

n_years = 75  # maximum age at diagnosis
n_records = 50  # number of records per sex

icd_10 = json.load(open('icd.json'))  # cancer type - icd code mapping
stdict = json.load(open('st_dict.json'))  # cancer stage - snomed code mapping

gdpth = '/Users/lawrence.phillips/synth_dat/generated_data/'

paths = {
    'patpath': gdpth + 'patients/',
    'conpath': gdpth + 'conditions/',
    'qpath': gdpth + 'risk_questionnaires/',
    'fhpath': gdpth + 'family_histories/',
    'fqpath': gdpth + 'family_questionnaires/',
    'imppath': gdpth + 'impressions/',
    'obspath': gdpth + 'observations/',
    'dreppath': gdpth + 'diagnostic_reports/'
    }

for path in paths.keys():
    for f in glob(paths[path] + '*'):
        os.remove(f)

rd = {'M': defaultdict(list), 'F': defaultdict(list)}

for sex in rd.keys():
    state = State(contents=[sex])
    b = Birth(state, n_years)

    for i in range(n_records):
        state = State(contents=[sex])
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
            cns = []
            for event in events:
                cn = event.get_consequences()
                if cn:
                    cns = cns + cn
            cns = [cn for cn in cns if cn is not None]
            if not cns:
                break
            for cn in cns:
                record.append(cn)
            events = [ev_dict[c[0]](state, dict(record)) for c in cns]

        condition = cnd.Condition()
        condition.identifier = [cond_identifier]
        base_date = set_dates(record[0][1], patient)
        reference = {'reference':
                     paths['patpath']+pat_identifier.value+'.json'}

        if record[0][0] == 'C50':
            genotype = build_family_genotype(record[0][1])
            famhist = build_family_phenotype(genotype, record[0][1])
            make_fam_hist(famhist,
                          reference,
                          pat_identifier)
            make_fam_quest(famhist,
                           reference,
                           pat_identifier)

        condition.patient = FHIRReference(reference)

        condition.code = cc.CodeableConcept(
                {'coding': [{'system': 'icd-10', 'code': record[0][0]}],
                 'text': icd_10[record[0][0]]}
        )

        condition.verificationStatus = 'confirmed'

        make_observations(record, state, reference, base_date, patient)

        risk = generate_risk(record[0][0], condition.patient, patient)

        json.dump(risk.as_json(),
                  open(paths['qpath']+risk.identifier.value+'.json', 'w'))
        json.dump(patient.as_json(),
                  open(paths['patpath']+pat_identifier.value+'.json', 'w'))
        json.dump(condition.as_json(),
                  open(paths['conpath']+cond_identifier.value+'.json', 'w'))

json.dump(rd, open('rd.json', 'w'))
