"""
AMMM Project Heuristics
Representation of a Specialist
"""


class Specialist(object):
    def __init__(self, specId, capacity, cost):
        self._specId = specId
        self._capacity = capacity  # w[s]: work hours this specialist can provide
        self._cost = cost          # c[s]: cost of hiring this specialist

    def getId(self):
        return self._specId

    def getCapacity(self):
        return self._capacity

    def getCost(self):
        return self._cost

    def getCostEffectiveness(self):
        """Cost per unit of work capacity (lower is better)."""
        if self._capacity == 0:
            return float('inf')
        return self._cost / self._capacity

    def __str__(self):
        return "specId: %d (capacity: %d, cost: %d)" % (self._specId, self._capacity, self._cost)
