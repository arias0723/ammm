"""
AMMM Project Heuristics
Solution for the resource-allocation sub-problem (Phase 2).

After Stoer-Wagner determines the min-cut (partition), this solution represents
the assignment of specialists to the cut pipes (resource allocation).
"""

import copy
from Heuristics.solution import _Solution


class Solution(_Solution):
    """
    Represents a specialist-to-pipe assignment for a fixed set of cut pipes.

    Decision: for each specialist, either unassigned or assigned to exactly one pipe.
    Feasibility: every pipe's demand must be covered by total capacity of assigned specialists.
    Objective: minimize total cost of assigned specialists.
    """

    def __init__(self, nBases, partition, cutPipes, specialists):
        """
        Args:
            nBases: number of bases
            partition: list[int] of length nBases (0/1 group assignment)
            cutPipes: list of Pipe objects that cross the partition (to be destroyed)
            specialists: list of all Specialist objects
        """
        self.nBases = nBases
        self.partition = partition[:]
        self.cutPipes = cutPipes          # fixed set of pipes to destroy
        self.specialists = specialists

        # Assignment state
        self.specialistToPipe = {}         # specId -> pipeId (or absent if unassigned)
        self.pipeToSpecialists = {p.getId(): [] for p in cutPipes}  # pipeId -> [specId, ...]
        self.pipeRemainingDemand = {p.getId(): p.getDemand() for p in cutPipes}

        super().__init__()

    def clone(self):
        return copy.deepcopy(self)

    # ---- Assignment operations ----

    def assign(self, specId, pipeId):
        """Assign specialist specId to pipe pipeId."""
        self.specialistToPipe[specId] = pipeId
        self.pipeToSpecialists[pipeId].append(specId)
        self.pipeRemainingDemand[pipeId] -= self.specialists[specId].getCapacity()

    def unassign(self, specId):
        """Remove specialist specId from its current assignment."""
        if specId not in self.specialistToPipe:
            return
        pipeId = self.specialistToPipe[specId]
        self.pipeToSpecialists[pipeId].remove(specId)
        self.pipeRemainingDemand[pipeId] += self.specialists[specId].getCapacity()
        del self.specialistToPipe[specId]

    def isSpecialistAssigned(self, specId):
        return specId in self.specialistToPipe

    def getAssignedPipe(self, specId):
        return self.specialistToPipe.get(specId, None)

    def getSpecialistsOnPipe(self, pipeId):
        return self.pipeToSpecialists[pipeId][:]

    def getUnassignedSpecialists(self):
        return [s for s in self.specialists if s.getId() not in self.specialistToPipe]

    def getAssignedSpecialists(self):
        return [s for s in self.specialists if s.getId() in self.specialistToPipe]

    def isPipeCovered(self, pipeId):
        return self.pipeRemainingDemand[pipeId] <= 0

    def allPipesCovered(self):
        return all(self.pipeRemainingDemand[p.getId()] <= 0 for p in self.cutPipes)

    def computeCost(self):
        return sum(self.specialists[sId].getCost() for sId in self.specialistToPipe)

    def evaluate(self):
        """Recompute feasibility and fitness."""
        if not self.cutPipes:
            self.makeInfeasible()
            return False
        if self.allPipesCovered():
            self.feasible = True
            self.fitness = self.computeCost()
            return True
        else:
            self.makeInfeasible()
            return False

    def getExcessCapacity(self, pipeId):
        """How much extra capacity beyond demand is assigned to this pipe."""
        return -self.pipeRemainingDemand[pipeId]  # positive = excess

    def canRemoveSpecialist(self, specId):
        """Check if removing this specialist still leaves its pipe feasible."""
        if specId not in self.specialistToPipe:
            return False
        pipeId = self.specialistToPipe[specId]
        excess = self.getExcessCapacity(pipeId)
        return excess >= self.specialists[specId].getCapacity()

    def getPartition(self):
        return self.partition[:]

    def __str__(self):
        strSol = 'z = %10.8f;\n' % self.fitness
        if self.fitness == float('inf'):
            return strSol

        strSol += '\nMin-cut partition:\n'
        group0 = [i for i in range(self.nBases) if self.partition[i] == 0]
        group1 = [i for i in range(self.nBases) if self.partition[i] == 1]
        strSol += '  Group 0: {%s}\n' % ', '.join(str(b) for b in group0)
        strSol += '  Group 1: {%s}\n' % ', '.join(str(b) for b in group1)

        strSol += '\nDestroyed pipes (resource allocation):\n'
        for pipe in self.cutPipes:
            pipeId = pipe.getId()
            specs = self.pipeToSpecialists.get(pipeId, [])
            totalCap = sum(self.specialists[sId].getCapacity() for sId in specs)
            strSol += '  Pipe {%d,%d} (demand=%d, assigned_cap=%d) <- specialists: %s\n' % (
                pipe.getBaseI(), pipe.getBaseJ(), pipe.getDemand(), totalCap,
                ', '.join(str(s) for s in specs)
            )

        strSol += '\nTotal cost: %d\n' % int(self.fitness)
        return strSol

    def saveToFile(self, filePath):
        with open(filePath, 'w') as f:
            f.write(self.__str__())
