from ev_cl import Event
from cancer_env import cancer_t_dist, cancer_c_dist
import json

no_sex = json.load(open('no_sex.json'))


class Birth(Event):
    def __init__(self,  state, lt):
        consequences = ['C34', 'C18', 'C61', 'C81', 'C50']

        self.consequences = ([c for c in consequences
                              if c not in no_sex['no_f']]
                             if 'F' in state.contents else
                             [c for c in consequences
                              if c not in no_sex['no_m']])

        self.t_distributions = [cancer_t_dist(lt, c, state.contents)
                                for c in self.consequences]

        self.c_distribution = cancer_c_dist(
                               self.consequences, state.contents)


ev_dict = {'B': Birth,
           'C18': Event,
           'C34': Event,
           'C50': Event,
           'C61': Event,
           'C81': Event}
