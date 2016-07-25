import pandas
import numpy as np
import models.questionnaireresponse as qr
import models.identifier as idn

rdat = pandas.read_csv('risk.csv')


def generate_risk(diagnosis, pref, pid):
    factors = rdat[diagnosis].tolist()
    risks = [np.random.choice([1, 0], [factors[i]/100, 1 - factors[i]/100])
             for i, _ in enumerate(factors)]
    q = [{'text': rdat.exposure.tolist()[i],
          'answer': {'valueBoolean': risks[i]}}
         for i in range(len(factors))]

    response = qr.QuestionnaireResponse()
    response.status = 'completed'
    response.question = q
    response.source = pref
    response.identifier = idn.Identifier({'value': 'q'+pid.value})
    return response
