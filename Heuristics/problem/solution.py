"""
AMMM Project Heuristics
Solution for the pipe-destruction (graph cut) problem.
"""

import copy
from Heuristics.solution import _Solution


class Assignment(object):
    """Represents a candidate move: reassigning a base to a new group."""
    def __init__(self, baseId, newGroup, cost):
        self.baseId = baseId
        self.newGroup = newGroup
        self.cost = cost

    def __str__(self):
        return "<base_%d -> group_%d>: cost: %.2f" % (self.baseId, self.newGroup, self.cost)


class Solution(_Solution):
    def __init__(self, nBases, pipes, specialists):
        self.nBases = nBases
        self.pipes = pipes
        self.specialists = specialists

        self.group = [0] * nBases           # partition: 0 or 1 for each base
        self.cutPipeIds = set()             # ids of pipes crossing the partition
        self.specialistToPipe = {}          # specId -> pipeId
        self.pipeToSpecialists = {}         # pipeId -> [specId, ...]

        super().__init__()

    def clone(self):
        return copy.deepcopy(self)

    def setGroup(self, baseId, groupId):
        self.group[baseId] = groupId

    def getGroup(self, baseId):
        return self.group[baseId]

    def getPartition(self):
        return self.group[:]

    def setPartition(self, partition):
        self.group = partition[:]

    def isValidPartition(self):
        hasZero = any(g == 0 for g in self.group)
        hasOne = any(g == 1 for g in self.group)
        return hasZero and hasOne

    def computeCutPipes(self):
        self.cutPipeIds = set()
        for pipe in self.pipes:
            if self.group[pipe.getBaseI()] != self.group[pipe.getBaseJ()]:
                self.cutPipeIds.add(pipe.getId())

    def getCutPipeIds(self):
        return self.cutPipeIds


    def assignSpecialistsGreedy(self):
        """Assign specialists to cut pipes using a greedy knapsack approach.
        Pipes are processed by demand descending; specialists by cost-effectiveness ascending."""
        self.specialistToPipe = {}
        self.pipeToSpecialists = {}
        self.fitness = 0.0

        cutPipes = sorted(
            [p for p in self.pipes if p.getId() in self.cutPipeIds],
            key=lambda p: p.getDemand(), reverse=True
        )
        if not cutPipes:
            self.makeInfeasible()
            return False

        sortedSpecs = sorted(self.specialists, key=lambda s: s.getCostEffectiveness())
        usedSpecialists = set()

        for pipe in cutPipes:
            demand = pipe.getDemand()
            pipeId = pipe.getId()
            assigned = []
            coveredCapacity = 0

            for spec in sortedSpecs:
                if spec.getId() in usedSpecialists:
                    continue
                assigned.append(spec.getId())
                coveredCapacity += spec.getCapacity()
                usedSpecialists.add(spec.getId())
                if coveredCapacity >= demand:
                    break

            if coveredCapacity < demand:
                self.makeInfeasible()
                return False

            self.pipeToSpecialists[pipeId] = assigned
            for sId in assigned:
                self.specialistToPipe[sId] = pipeId

        self.fitness = sum(self.specialists[sId].getCost() for sId in self.specialistToPipe)
        return True


    def evaluate(self):
        """Recompute cut pipes and reassign specialists. Returns True if feasible."""
        self.feasible = True
        if not self.isValidPartition():
            self.makeInfeasible()
            return False
        self.computeCutPipes()
        return self.assignSpecialistsGreedy()


    def __str__(self):
        strSolution = 'z = %10.8f;\n' % self.fitness
        if self.fitness == float('inf'):
            return strSolution

        strSolution += '\nDestroyed pipes:\n'
        for pipe in self.pipes:
            if pipe.getId() in self.cutPipeIds:
                specs = self.pipeToSpecialists.get(pipe.getId(), [])
                strSolution += '  Pipe {%d,%d} (demand=%d) <- specialists: %s\n' % (
                    pipe.getBaseI(), pipe.getBaseJ(), pipe.getDemand(),
                    ', '.join(str(s) for s in specs)
                )

        group0 = [i for i in range(self.nBases) if self.group[i] == 0]
        group1 = [i for i in range(self.nBases) if self.group[i] == 1]
        strSolution += '\nPartition:\n'
        strSolution += '  Group 0: {%s}\n' % ', '.join(str(b) for b in group0)
        strSolution += '  Group 1: {%s}\n' % ', '.join(str(b) for b in group1)

        return strSolution

    def saveToFile(self, filePath):
        f = open(filePath, 'w')
        f.write(self.__str__())
        f.close()
