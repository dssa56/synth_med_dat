from risk_modules import sub_alpha, gnt_proba, modifier, genotypes, genopairs
from survive import genotype_pops
import json
import re

path = '/Users/lawrence.phillips/synth_dat/generated_data/'

austrs = [s + '_sib_' + str(i) + mfp
          for s in ['mum', 'dad']
          for i in range(3)
          for mfp in ['m', 'f', 'ptnr']]

adstrs = [s + '_sib_' + str(i) + '_daught_' + str(j)
          for s in ['mum', 'dad'] for i in range(3) for j in range(3)]

rlns = austrs + ['mum', 'dad', 'gmm', 'gfm', 'gmp',
                 'gfp', 'sis_0', 'sis_1', 'sis_2'] + adstrs


g_genotype_pops = dict(((a, b), genotype_pops[a]*genotype_pops[b])
                       for a in genotype_pops.keys()
                       for b in genotype_pops.keys())


def get_tuples(st, fh, d):
        for qu in fh['group']['group']:
            ind = 0
            bc_ans, age_ans = '', ''
            for squ in qu['question']:
                if list(squ['answer'][0].values())[0] == st:
                    for k in range(3):
                        ans = list(
                         qu['question'][k]['answer'][0].values())[0]
                        if type(ans) == bool:
                            bc_ans = 'BC' if ans else 'N'
                        elif type(ans) == int:
                            age_ans = ans
                    d[st] = (bc_ans, age_ans)
                    ind = 1
                    break
            if ind == 1:
                break


def bc_prob(idnt):
    ages = [35, 45, 55, 65, 75]
    pat_pnts = [('BC', age) for age in ages]
    famhist = json.load(open(path + 'family_questionnaires/'
                             + idnt + '.json'))
    hd = {}
    for rln in rlns:
        get_tuples(rln, famhist, hd)

    m_sib = [k for k in hd.keys()
             if 'mum_sib_' in k and 'daught' not in k]

    m_sib_mods = []
    for sib in m_sib:
        dstr = re.search(re.compile('(mum_sib_[0-2]).+'), sib).group(1)
        ds = [hd[k] for k in hd.keys() if dstr in k and '_daught_' in k]
        identmod = [dict((gnt, 1) for gnt in genotypes)
                    for _ in range(len(ds))]
        if 'ptnr' in sib:
            d = (
                [(m*g_genotype_pops(g[0])*sub_alpha(g[0], hd[sib]), g)
                 for m, g in modifier(ds, identmod)])
            dp = dict((genotype, sum([d[[gt2, genotype]]
                                     for gt2 in genotypes]))
                      for genotype in genotypes)
            m_sib_mods.append(dp)
        else:
            d = (
                [(m*g_genotype_pops(g[1])*sub_alpha(g[1], hd[sib]), g)
                 for m, g in modifier(ds, identmod)])
            dp = dict((genotype, sum([d[[genotype, gt2]]
                                     for gt2 in genotypes]))
                      for genotype in genotypes)
            m_sib_mods.append(dp)

    if not m_sib_mods:
        m_sib_mods = [dict((gnp, 1) for gnp in genopairs)
                      for _ in range(len(m_sib))]

    p_gpm = modifier([hd[k] for k in m_sib], m_sib_mods)

    p_m = dict((gnt, sum([p_gpm[genopair]*gnt_proba(gnt, genopair)
                          * sub_alpha(genopair[0], hd['gmp'])
                          * g_genotype_pops[genopair[0]]
                          * g_genotype_pops[genopair[1]]
                          for genopair in genopairs])
                * sub_alpha(gnt, hd['mum'])) for gnt in genotypes)

    p_sib = [k for k in hd.keys()
             if 'dad_sib_' in k and 'daught' not in k]

    p_sib_mods = []
    for sib in p_sib:
        dstr = re.search(re.compile('(dad_sib_[0-2]).+'), sib).group(1)
        ds = [hd[k] for k in hd.keys() if dstr in k and '_daught_' in k]
        identmod = [dict((gnt, 1) for gnt in genotypes)
                    for _ in range(len(ds))]
        if 'ptnr' in sib:
            d = (
                [(m*genotype_pops(g[0])*sub_alpha(g[0], hd[sib]), g)
                 for m, g in modifier(ds, identmod)])
            dp = dict((genotype, sum([d[[gt2, genotype]]
                                     for gt2 in genotypes]))
                      for genotype in genotypes)
            p_sib_mods.append(dp)
        else:
            d = (
                [(m*genotype_pops(g[1])*sub_alpha(g[1], hd[sib]), g)
                 for m, g in modifier(ds, identmod)])
            dp = dict((genotype, sum([d[[genotype, gt2]]
                                     for gt2 in genotypes]))
                      for genotype in genotypes)
            p_sib_mods.append(dp)

    if not p_sib_mods:
        p_sib_mods = [dict((gnp, 1) for gnp in genopairs)
                      for _ in range(len(p_sib))]

    p_gpp = modifier([hd[k] for k in p_sib], p_sib_mods)

    p_p = dict((gnt, sum([p_gpp[genopair]*gnt_proba(gnt, genopair)
                          * sub_alpha(genopair[0], hd['gmp'])
                          * g_genotype_pops[genopair[0]]
                          * g_genotype_pops[genopair[1]]
                          for genopair in genopairs])) for gnt in genotypes)

    sisters = [hd[k] for k in hd.keys() if 'sis' in k]
    smod = modifier(sisters, [dict((gnt, 1) for gnt in genotypes)
                              for _ in range(len(sisters))])
    if not smod:
        smod = dict((gnp, 1) for gnp in genopairs)
    p_m_d = dict((gnp, p_m[gnp[0]] * p_p[gnp[1]] * smod[gnp])
                 for gnp in genopairs)
    p_pat = dict((gnt, sum([gnt_proba(gnt, gnp)*p_m_d[gnp]
                            for gnp in genopairs]))
                 for gnt in genotypes)

    p_can_t = dict((pt[1], sum([sub_alpha(gnt, pt)*p_pat[gnt]
                               for gnt in genotypes]))
                   for pt in pat_pnts)
    p_can_t = dict((k, p_can_t[k]/sum(p_can_t.values()))
                   for k in p_can_t.keys())
    return p_can_t
