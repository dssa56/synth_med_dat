import json
import numpy as np

sur_d = json.load(open('survival.json'))


genes = [('BRCA1', 'BRCA2', 'N'), ('Y', 'N')]
genotypes = [(a, b) for a in genes[0] for b in genes[1]]


genotype_pops = {('BRCA1', 'Y'): 0.1139*1/500,
                 ('BRCA1', 'N'): (1 - 0.1139)*1/500,
                 ('BRCA2', 'Y'): 0.1139*1/500,
                 ('BRCA2', 'N'): (1 - 0.1139)*1/500,
                 ('N', 'Y'): 0.1139*498/500,
                 ('N', 'N'): (1 - 0.1139)*498/500}

th = 13.0377

event_probs = {}
for k in sur_d.keys():
    event_probs[(k, 'N')] = [1 - sur_d[k][0]] + [sur_d[k][i] - sur_d[k][i+1]
                                                 for i in range(4)]
    event_probs[(k, 'Y')] = (
        [1 - sur_d[k][0]**th] +
        [sur_d[k][i]**th - sur_d[k][i+1]**th for i in range(4)]
        )


def get_patient_genotype(age):
    if age < 30:
        age = 30

    age = age // 10 - 3
    probs = [genotype_pops[gn]*event_probs[gn][age]
             for gn in genotypes]

    norm = sum(probs)
    probs = [p/norm for p in probs]

    copy_1 = np.random.choice(range(6), p=probs)
    copy_2 = np.random.choice(range(6), p=list(genotype_pops.values()))

    return (genotypes[copy_1], genotypes[copy_2])


def parent_genotype_prob(child_genotype, parent_genotypes):
    prob = 1
    for sex in [0, 1]:
        for locus, cg in enumerate(child_genotype[sex]):
            prob *= len([1 for pg in parent_genotypes[sex]
                         if pg[locus] == cg])/2
    return prob


def get_parent_genotypes(child_genotype):
    possibilities = [[(pgmm, pgmf), (pgfm, pgff)]
                     for pgmm in genotypes for pgmf in genotypes
                     for pgfm in genotypes for pgff in genotypes]
    probs = [parent_genotype_prob(child_genotype, poss) *
             genotype_pops[poss[0][0]]*genotype_pops[poss[0][1]] *
             genotype_pops[poss[1][0]]*genotype_pops[poss[1][1]]
             for poss in possibilities]
    norm = sum(probs)
    probs = [p/norm for p in probs]
    return possibilities[np.random.choice(len(possibilities),
                                          p=probs)]
