"""
AMMM Project Heuristics

Neighborhoods:
  - Reassignment: move one base to the other group.
"""

import copy
import time
from Heuristics.solver import _Solver
from AMMMGlobals import AMMMException


class Move(object):
    def __init__(self, baseId, fromGroup, toGroup):
        self.baseId = baseId
        self.fromGroup = fromGroup
        self.toGroup = toGroup

    def __str__(self):
        return "baseId: %d Move: %d -> %d" % (self.baseId, self.fromGroup, self.toGroup)


class LocalSearch(_Solver):
    def __init__(self, config, instance):
        self.enabled = config.localSearch
        self.policy = config.policy
        self.maxExecTime = config.maxExecTime
        super().__init__(config, instance)


    def createNeighborSolution(self, solution, moves):
        neighbor = solution.clone()
        for move in moves:
            neighbor.setGroup(move.baseId, move.toGroup)
        feasible = neighbor.evaluate()
        if not feasible:
            return None
        return neighbor


    def exploreReassignment(self, solution):
        """Move one base to the other group."""
        curCost = solution.getFitness()
        bestNeighbor = solution

        for baseId in range(solution.nBases):
            # Groups should always be 0/1
            curGroup = solution.getGroup(baseId)
            newGroup = 1 - curGroup

            # A valid partition must have both groups non-empty
            newPartition = solution.getPartition()
            newPartition[baseId] = newGroup
            if not (any(g == 0 for g in newPartition) and any(g == 1 for g in newPartition)):
                continue

            moves = [Move(baseId, curGroup, newGroup)]
            neighbor = self.createNeighborSolution(solution, moves)
            if neighbor is None:
                continue

            neighborCost = neighbor.getFitness()
            if neighborCost < curCost:
                if self.policy == 'FirstImprovement':
                    return neighbor
                else:
                    bestNeighbor = neighbor
                    curCost = neighborCost

        return bestNeighbor


    def exploreNeighborhood(self, solution):
        return self.exploreReassignment(solution)


    def solve(self, **kwargs):
        initialSolution = kwargs.get('solution', None)
        if initialSolution is None:
            raise AMMMException('[local search] No solution could be retrieved')

        if not initialSolution.isFeasible():
            return initialSolution

        self.startTime = kwargs.get('startTime', None)
        endTime = kwargs.get('endTime', None)

        incumbent = initialSolution
        incumbentFitness = incumbent.getFitness()
        iterations = 0

        while time.time() < endTime:
            iterations += 1
            neighbor = self.exploreNeighborhood(incumbent)
            if neighbor is None:
                break
            neighborFitness = neighbor.getFitness()
            if incumbentFitness <= neighborFitness:
                break
            incumbent = neighbor
            incumbentFitness = neighborFitness

        return incumbent
