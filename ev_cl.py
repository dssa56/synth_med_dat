class Event:
    def __init__(
     self, state, lt, consequences=[], c_distribution=[], t_distributions=[]):
        self.consequences = consequences
        self.c_distribution = c_distribution
        self.t_distributions = t_distributions

    def get_consequences(self):
        if self.consequences:
            cns = []
            for i in range(len(self.c_distribution)):
                cind = self.c_distribution[i].rvs()
                con = self.consequences[i][cind]
                t = self.t_distributions[i][cind].rvs()
                cns.append((con, int(t)))
            return cns


class State:
    def __init__(self, contents=[]):
        self.contents = contents

    def add(self, x):
        self.contents.append(x)

    def remove(self, x):
        self.contents = [y for y in self.contents if y != x]
