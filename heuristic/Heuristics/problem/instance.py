"""
AMMM Project Heuristics
Representation of a problem instance for the pipe-destruction (graph cut) problem.
"""

from Heuristics.problem.Pipe import Pipe
from Heuristics.problem.Specialist import Specialist
from Heuristics.problem.solution import Solution


class Instance(object):
    def __init__(self, config, inputData):
        self.config = config
        self.inputData = inputData

        n = inputData.n   # number of bases
        m = inputData.m   # number of specialists
        w = inputData.w   # work capacity per specialist
        c = inputData.c   # cost per specialist
        t = inputData.t   # adjacency matrix of pipe demands

        self.nBases = n

        self.specialists = []
        for sId in range(m):
            self.specialists.append(Specialist(sId, w[sId], c[sId]))

        self.pipes = []
        pipeId = 0
        for i in range(n):
            for j in range(i + 1, n):
                if t[i][j] > 0:
                    self.pipes.append(Pipe(pipeId, i, j, t[i][j]))
                    pipeId += 1

    def getNumBases(self):
        return self.nBases

    def getNumSpecialists(self):
        return len(self.specialists)

    def getNumPipes(self):
        return len(self.pipes)

    def getPipes(self):
        return self.pipes

    def getSpecialists(self):
        return self.specialists

    def createSolution(self):
        solution = Solution(self.nBases, self.pipes, self.specialists)
        solution.setVerbose(self.config.verbose)
        return solution

    def checkInstance(self):
        if self.nBases < 2:
            return False
        if len(self.pipes) == 0:
            return False
        totalCapacity = sum(s.getCapacity() for s in self.specialists)
        minDemand = min(p.getDemand() for p in self.pipes)
        return totalCapacity >= minDemand
