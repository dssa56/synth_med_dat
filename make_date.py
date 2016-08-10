import random
from models.fhirdate import FHIRDate


def set_dates(age, pat):
    year = random.choice([2016 - i for i in range(10)])
    month = random.choice([1+i for i in range(12)])
    day = random.choice([1+i for i in range(28)])

    basedate = str(year)+'-'+str(month)+'-'+str(day)

    year = year - age
    month = random.choice([1+i for i in range(12)])
    day = random.choice([1+i for i in range(28)])

    pat.birthDate = FHIRDate(jsonval=str(year)+'-'+str(month)+'-'+str(day))

    return basedate
