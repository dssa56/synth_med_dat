import json
import numpy as np

sur_d = json.load(open('survival.json'))


genes = [('BRCA1', 'BRCA2', 'N'), ('Y', 'N')]
genotypes = [(a, b) for a in genes for b in genes]

genotype_key = {0: 'BRCA1Y',
                1: 'BRCA1N',
                2: 'BRCA2Y',
                3: 'BRCA2N',
                4: 'NY',
                5: 'NN'}

th = 13.0377

event_probs = {}
for k in sur_d.keys():
    event_probs[k+'N'] = [1 - sur_d[k][0]] + [sur_d[k][i] - sur_d[k][i+1]
                                              for i in range(4)]
    event_probs[k+'Y'] = (
        [1 - sur_d[k][0]**th] +
        [sur_d[k][i]**th - sur_d[k][i+1]**th for i in range(4)]
        )


def get_patient_genotype(age):
    if age < 30:
        age = 30

    age = age // 10 - 3
    probs = [(0.1139)*1/500*event_probs['BRCA1Y'][age],
             (1 - 0.1139)*1/500*event_probs['BRCA1N'][age],
             (0.1139)*1/500*event_probs['BRCA2Y'][age],
             (1 - 0.1139)*1/500*event_probs['BRCA2N'][age],
             (0.1139)*498/500*event_probs['NY'][age],
             (1 - 0.1139)*498/500*event_probs['NN'][age]]

    norm = sum(probs)
    probs = [p/norm for p in probs]

    pop_probs = [1/500, 1/500, 1/500, 1/500, 498/500, 498/500]
    norm = sum(pop_probs)
    pop_probs = [p/norm for p in pop_probs]

    copy_1 = np.random.choice(range(6), p=probs)
    copy_2 = np.random.choice(range(6), p=pop_probs)

    return (genotype_key[copy_1], genotype_key[copy_2])
