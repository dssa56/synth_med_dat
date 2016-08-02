from survive import event_probs

genes = [('BRCA1', 'BRCA2', 'N'), ('Y', 'N')]
genotypes = [(a, b) for a in genes[0] for b in genes[1]]
genopairs = [(a, b) for a in genotypes for b in genotypes]


def gnpr_iter(l, n):
    i = 0
    while i < l ** n:
        inds = [(i // l ** j) % l for j in range(n)]
        yield [genopairs[k] for k in inds]
        i += 1


def sub_alpha(index, genotype, phenotype):
    if 'BRCA1' in genotype[0] or 'BRCA1' in genotype[1]:
        expr1 = 'BRCA1'
    elif 'BRCA2' in genotype[0] or 'BRCA2' in genotype[1]:
        expr1 = 'BRCA2'
    else:
        expr1 = 'N'
    if 'Y' in genotype[0] or 'Y' in genotype[1]:
        expr2 = 'Y'
    else:
        expr2 = 'N'
    if phenotype[0] == 'BC':
        return event_probs[(expr1, expr2)][phenotype[1]]
    else:
        return 1 - sum(event_probs[(expr1, expr2)][:phenotype[1]])


def gnt_proba(genotype, parent_genotypes):
    mz = [[parent_genotypes[0][i][j] for i in range(2)] for j in range(2)]
    fz = [[parent_genotypes[1][i][j] for i in range(2)] for j in range(2)]
    pm = [mz[i].count(genotype[0][i])/2 for i in range(2)]
    pf = [fz[i].count(genotype[1][i])/2 for i in range(2)]
    return pm[0]*pm[1]*pf[0]*pf[1]


def modifier(n_sub_people, pt):
    mod = []
    for gnp in genopairs:
        s = 0
        for pgt in gnpr_iter(n_sub_people, len(genopairs)):
            p = 1
            for i, gt in enumerate(pgt):
                p *= gnt_proba(gt, gnp)*sub_alpha(i, gt, pt)
            s += p
        mod.append[s]
    return mod
