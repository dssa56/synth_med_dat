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
    if age > 70:
        age = 70

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


def get_child_genotype(parent_genotypes):
    from_mum = [parent_genotypes[0][np.random.choice(2)][0],
                parent_genotypes[0][np.random.choice(2)][1]]
    from_dad = [parent_genotypes[0][np.random.choice(2)][0],
                parent_genotypes[0][np.random.choice(2)][1]]
    return (from_mum, from_dad)


def build_family_genotype(age):
    g = {}
    possibilities = [(pgmm, pgmf) for pgmm in genotypes for pgmf in genotypes]
    pop_prs = [genotype_pops[poss[0]]*genotype_pops[poss[1]]
               for poss in possibilities]
    g['pat'] = get_patient_genotype(age)
    g['mum'], g['dad'] = get_parent_genotypes(g['pat'])
    g['gmm'], g['gfm'] = get_parent_genotypes(g['mum'])
    g['gmp'], g['gfp'] = get_parent_genotypes(g['dad'])

    nmsib = np.random.choice(3)
    for i in range(nmsib):
        sex = ['m', 'f'][np.random.choice(2)]
        g['mum_sib_' + str(i) + '_' + sex] = (
                        get_child_genotype((g['gmm'], g['gfm'])))
        g['mum_sib_' + str(i) + '_ptnr'] = (
                        possibilities[np.random.choice(len(possibilities),
                                                       p=pop_prs)])
        for j in range(np.random.choice(3)):
            g['mum_sib_' + str(i) + '_daught_' + str(j)] = (
                get_child_genotype((g['mum_sib_' + str(i) + '_' + sex],
                                    g['mum_sib_' + str(i) + '_ptnr']
                                    )))

    ndsib = np.random.choice(3)
    for i in range(ndsib):
        sex = ['m', 'f'][np.random.choice(2)]
        g['dad_sib_' + str(i) + '_' + sex] = (
                        get_child_genotype((g['gmm'], g['gfm'])))
        g['dad_sib_' + str(i) + '_ptnr'] = (
                        possibilities[np.random.choice(len(possibilities),
                                                       p=pop_prs)])
        for j in range(np.random.choice(3)):
            g['dad_sib_' + str(i) + '_daught_' + str(j)] = (
                get_child_genotype((g['dad_sib_' + str(i) + '_' + sex],
                                    g['dad_sib_' + str(i) + '_ptnr']
                                    )))

    for i in range(np.random.choice(3)):
        g['sis_' + str(i)] = get_child_genotype((g['mum'], g['dad']))

    return g


def build_family_phenotype(fmly_gnt, age):
    n_m_sis = np.random.choice(
        len([k for k in fmly_gnt.keys()
             if 'mum_sib' in k
             and 'daught' not in k
             and 'ptnr' not in k]) + 1
    )

    n_f_sis = np.random.choice(
        len([k for k in fmly_gnt.keys()
             if 'dad_sib' in k
             and 'daught' not in k
             and 'ptnr' not in k]) + 1
    )

    ages = {'mum': age + 30 - np.random.choice(11),
            'gmm': age + 60 - np.random.choice(22),
            'gmp': age + 60 - np.random.choice(22)}

    for i in range(n_m_sis):
        try:
            fmly_gnt['mum_sib_' + str(i) + '_f']
            ages['mum_sib_' + str(i) + '_f'] = age + 30 - np.random.choice(11)
        except KeyError:
            ages['mum_sib_' + str(i) + '_ptnr'] = (
                age + 30 - np.random.choice(11))

    for i in range(n_f_sis):
        try:
            fmly_gnt['dad_sib_' + str(i) + '_f']
            ages['dad_sib_' + str(i) + '_f'] = age + 30 - np.random.choice(11)
        except KeyError:
            ages['dad_sib_' + str(i) + '_ptnr'] = (
                age + 30 - np.random.choice(11))

    for i in range(len([k for k in fmly_gnt.keys() if 'mum_sib' in k])):
        for j in range(len([k for k in fmly_gnt.keys()
                            if 'mum_sib_' + str(i) in k
                            and 'daught' in k])):
            ages['mum_sib_' + str(i) + '_daught_' + str(j)] = (
                age + 5 - np.random.choice(11)
            )

    for i in range(len([k for k in fmly_gnt.keys() if 'dad_sib' in k])):
        for j in range(len([k for k in fmly_gnt.keys()
                            if 'dad_sib_' + str(i) in k
                            and 'daught' in k])):
            ages['dad_sib_' + str(i) + '_daught_' + str(j)] = (
                age + 5 - np.random.choice(11)
            )

    for i in range(len([k for k in fmly_gnt.keys() if 'sis' in k])):
        ages['sis_' + str(i)] = age + 5 - np.random.choice(11)

    p = {}
    for k in ages.keys():
        k_age = ages[k] // 10 - 3
        k_age = k_age + 1 if k_age < 5 else 5
        if 'BRCA1' in fmly_gnt[k][0] or 'BRCA1' in fmly_gnt[k][1]:
            expr1 = 'BRCA1'
        elif 'BRCA2' in fmly_gnt[k][0] or 'BRCA2' in fmly_gnt[k][1]:
            expr1 = 'BRCA2'
        else:
            expr1 = 'N'
        if 'Y' in fmly_gnt[k][0] or 'Y' in fmly_gnt[k][1]:
            expr2 = 'Y'
        else:
            expr2 = 'N'
        can_prob = sum(event_probs[(expr1, expr2)][:k_age])
        if np.random.choice(2, p=[1 - can_prob, can_prob]):
            probs = [p/can_prob
                     for p in event_probs[(expr1, expr2)][:k_age]]
            can_age = np.random.choice(k_age, p=probs)
            can_age = (can_age + 3)*10 + np.random.choice(10)
            p[k] = ('BC', can_age)
        else:
            p[k] = ('NC', ages[k])

    return p
