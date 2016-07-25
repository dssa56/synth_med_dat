import pandas
import numpy as np
import scipy.stats as st

can_stats = pandas.read_csv(open('cancer.csv'))


def cancer_t_prob(time, code, stt):
    last_digit = time if time < 10 else time % ((time//10)*10)
    last_digit = 4 if last_digit <= 4 else 9
    time = last_digit if time < 10 else 10*(time//10) + last_digit
    time = time if time < 90 else 90
    can_prob = (
        can_stats[str(time)][can_stats['icd'] == code]
        [can_stats['sex'] == 'M'].iloc[0]
        if 'M' in stt else
        can_stats[str(time)][can_stats['icd'] == code]
        [can_stats['sex'] == 'F'].iloc[0]
    )
    return can_prob


def mname(self, arg):
    pass


def cancer_c_prob(code, stt):
    can_prob = (
        can_stats['all'][can_stats.icd == code][can_stats.sex == 'M'].iloc[0]
        if 'M' in stt else
        can_stats['all'][can_stats.icd == code][can_stats.sex == 'F'].iloc[0]
    )
    return can_prob


def cancer_t_dist(lt, code, stt):
        norm = sum([cancer_t_prob(t, code, stt) for t in range(lt)])
        probs = np.array([cancer_t_prob(t, code, stt)/norm
                          for t in range(lt)])
        return st.rv_discrete(values=(range(lt), probs))


def cancer_c_dist(lc, stt):
    probs = np.array([cancer_c_prob(c, stt) for c in lc])
    norm = sum(probs)
    probs = [prob/norm for prob in probs]
    return st.rv_discrete(values=(range(len(lc)), probs))
