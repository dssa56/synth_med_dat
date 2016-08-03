from risk_modules import sub_alpha, gnt_proba, modifier
import json

path = '/Users/lawrence.phillips/synth_dat/generated_data/'


def query(st, hist):
    for record in hist['group']['question']:
        if record['text'] == st:
            return record
    return None


def bc_prob(idnt):
    famhist = json.load(open(path + 'family_questionnaires/'
                             + idnt.value))
    dad_sib_ds = []
    for i in range(3):
        s = 'dad_sib_' + str(i)
        for j in range(3):
