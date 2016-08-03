import json
import models.questionnaireresponse as qr
import models.identifier as idn
from models.fhirreference import FHIRReference

path = '/Users/lawrence.phillips/synth_dat/generated_data/'


def make_fam_quest(famhist, patient, idnt):
    q = [{'question':
         [{'text': 'relation',
           'answer': [{'valueString': k}]},
          {'text': 'bc_diagnosis?',
           'answer': [{'valueBoolean':
                      True if 'BC' in famhist[k][0]
                      else False}]},
          {'text': 'age_at_diagnosis' if famhist[k][0] == 'BC' else
                   'current_age',
           'answer': [{'valueInteger': famhist[k][1]}]}]}
         for k in famhist.keys()]

    response = qr.QuestionnaireResponse(strict=False)
    response.status = 'completed'
    response.group = qr.QuestionnaireResponseGroup({'group': q})
    response.source = FHIRReference(patient)
    response.identifier = idn.Identifier({'value':
                                          idnt.value})
    json.dump(response.as_json(), open(path + 'family_questionnaires/'
                                       + idnt.value + '.json', 'w'))
