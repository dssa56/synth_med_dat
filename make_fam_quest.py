import json
import models.questionnaireresponse as qr
import models.identifier as idn
from models.fhirreference import FHIRReference

path = '/Users/lawrence.phillips/synth_dat/generated_data/'


def make_fam_quest(famhist, patient, idnt):
    q = [{'text': k,
          'answer': [{'valueString': str(famhist[k])}]}
         for k in famhist.keys()]

    response = qr.QuestionnaireResponse(strict=False)
    response.status = 'completed'
    response.group = qr.QuestionnaireResponseGroup({'question': q})
    response.source = FHIRReference(patient)
    response.identifier = idn.Identifier({'value':
                                          'q'+idnt.value})
    json.dump(response.as_json(), open(path + 'family_questionnaires/'
                                       + idnt.value, 'w'))
