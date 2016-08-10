from ev_cl import Event
from cancer_env import cancer_t_dist, cancer_c_dist
import json
import scipy.stats as st
import numpy as np

no_sex = json.load(open('no_sex.json'))


class Birth(Event):
    def __init__(self,  state, lt):
        consequences = ['C34', 'C16', 'C64', 'C25', 'C50']

        consequences = ([c for c in consequences
                         if c not in no_sex['no_f']]
                        if 'F' in state.contents else
                        [c for c in consequences
                         if c not in no_sex['no_m']])

        self.consequences = [consequences]

        self.t_distributions = [[cancer_t_dist(lt, c, state.contents)
                                for c in self.consequences[0]]]

        self.c_distribution = [cancer_c_dist(
                               self.consequences[0], state.contents)]


class C16(Event):
    def __init__(self, state, record):
        stage = np.random.choice([1, 2, 3, 4],
                                 p=[1/100, 6/100, 14/100, 79/100])
        self.consequences = [['Test: Endoscopy']]
        self.t_distributions = [[st.norm(loc=14, scale=3)]]
        self.c_distribution = [st.rv_discrete(values=([0], [1]))]
        state.add(('C16', stage))


class End(Event):
    def __init__(self, state, record):
        self.consequences = [['Test: CT scan'],
                             ['Plan: Chemo', 'Plan: Surgery']]
        self.t_distributions = [[st.norm(loc=7, scale=2)],
                                [st.rv_discrete(values=([0], [1])),
                                 st.rv_discrete(values=([0], [1]))]]
        self.c_distribution = [st.rv_discrete(values=([0], [1])),
                               st.rv_discrete(values=([0, 1], [0.5, 0.5]))]

ev_dict = {'B': Birth,
           'C16': C16,
           'C34': Event,
           'C64': Event,
           'C25': Event,
           'C50': Event,
           'Test: Endoscopy': End,
           'Test: CT scan': Event,
           'Plan: Chemo': Event,
           'Plan: Surgery': Event}
