"""
AMMM Project Heuristics
Representation of a Pipe (edge between two bases)
"""


class Pipe(object):
    def __init__(self, pipeId, baseI, baseJ, demand):
        self._pipeId = pipeId
        self._baseI = baseI    # 0-indexed base
        self._baseJ = baseJ    # 0-indexed base
        self._demand = demand  # t[i][j]: work hours needed to destroy this pipe

    def getId(self):
        return self._pipeId

    def getBaseI(self):
        return self._baseI

    def getBaseJ(self):
        return self._baseJ

    def getDemand(self):
        return self._demand

    def __str__(self):
        return "pipeId: %d ({%d,%d}, demand: %d)" % (self._pipeId, self._baseI, self._baseJ, self._demand)
