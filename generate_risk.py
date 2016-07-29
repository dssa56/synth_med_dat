import pandas
import numpy as np
import models.questionnaireresponse as qr
import models.identifier as idn

rdat = pandas.read_csv('risk.csv')


def generate_risk(diagnosis, pref, pat):
    factors = rdat[diagnosis][rdat.sex == pat.gender].tolist()
    risks = [np.random.choice([1, 0], p=[factors[i]/100, 1 - factors[i]/100])
             for i, _ in enumerate(factors)]
    q = [{'text': rdat.exposure.tolist()[i],
          'answer': [{'valueBoolean': True if risks[i] else False}]}
         for i in range(len(factors))]

    response = qr.QuestionnaireResponse(strict=False)
    response.status = 'completed'
    response.group = qr.QuestionnaireResponseGroup({'question': q})
    response.source = pref
    response.identifier = idn.Identifier({'value':
                                          'q'+pat.identifier[0].value})
    return response
