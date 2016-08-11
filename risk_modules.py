from survive import event_probs

genes = [('BRCA1', 'BRCA2', 'N'), ('Y', 'N')]
gnt = [(a, b) for a in genes[0] for b in genes[1]]
genotypes = [(a, b) for a in gnt for b in gnt]
genopairs = [(a, b) for a in genotypes for b in genotypes]


def gntype_iter(allowed_gn, n):
    l = len(allowed_gn)
    i = 0
    while i < l ** n:
        inds = [(i // l ** j) % l for j in range(n)]
        yield [allowed_gn[k] for k in inds]
        i += 1


def sub_alpha(gntyp, phenotype):
    k_age = phenotype[1] // 10 - 3
    k_age = k_age if k_age < 5 else 4
    if 'BRCA1' in gntyp[0] or 'BRCA1' in gntyp[1]:
        expr1 = 'BRCA1'
    elif 'BRCA2' in gntyp[0] or 'BRCA2' in gntyp[1]:
        expr1 = 'BRCA2'
    else:
        expr1 = 'N'
    if 'Y' in gntyp[0] or 'Y' in gntyp[1]:
        expr2 = 'Y'
    else:
        expr2 = 'N'
    if phenotype[0] == 'BC':
        return event_probs[(expr1, expr2)][k_age]/10
    else:
        return (1 - sum(event_probs[(expr1, expr2)][:k_age]) -
                event_probs[(expr1, expr2)][k_age]*(phenotype[1] % 10)/10)


def gnt_proba(gntyp, parent_genotypes):
    mz = [[parent_genotypes[0][i][j] for i in range(2)] for j in range(2)]
    fz = [[parent_genotypes[1][i][j] for i in range(2)] for j in range(2)]
    pm = [mz[i].count(gntyp[0][i])/2 for i in range(2)]
    pf = [fz[i].count(gntyp[1][i])/2 for i in range(2)]
    return pm[0]*pm[1]*pf[0]*pf[1]


def get_allowed_genotypes(gnp):
    allowed = list(set([((gnp[0][i][0], gnp[0][j][1]),
                   (gnp[1][k][0], gnp[1][l][1]))
                  for i in range(2)
                  for j in range(2)
                  for k in range(2)
                  for l in range(2)]))
    return allowed


def modifier(pt, mdf):
    mod = {}
    for gnpr in genopairs:
        s = 0
        allowed_gn = get_allowed_genotypes(gnpr)
        for pgt in gntype_iter(allowed_gn, len(pt)):
            p = 1
            for i, gt in enumerate(pgt):
                p *= gnt_proba(gt, gnpr)*sub_alpha(gt, pt[i])*mdf[i][gt]
            s += p
        mod[gnpr] = s
    return mod
