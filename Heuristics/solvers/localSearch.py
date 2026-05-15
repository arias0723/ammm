"""
AMMM Project Heuristics
Local Search for the resource-allocation sub-problem (Phase 2).

Neighborhoods:
  1. Replace: replace an assigned specialist with a cheaper unassigned one (if feasible).
  2. Remove: remove an over-provisioned specialist (reduce excess capacity -> save cost).
"""

import time
from Heuristics.solver import _Solver
from AMMMGlobals import AMMMException


class LocalSearch(_Solver):
    def __init__(self, config, instance):
        self.enabled = config.localSearch
        self.policy = config.policy
        self.maxExecTime = config.maxExecTime
        super().__init__(config, instance)


    def _exploreRemove(self, solution):
        """
        Try removing an assigned specialist whose capacity is fully excess
        (pipe remains covered without them)
        """
        curCost = solution.getFitness()
        bestNeighbor = solution

        assignedSpecs = solution.getAssignedSpecialists()
        # Let's try removing expensive ones first
        assignedSpecs.sort(key=lambda s: s.getCost(), reverse=True)

        for spec in assignedSpecs:
            # Check if can remove assigned spec and pipe is still covered
            if solution.canRemoveSpecialist(spec.getId()):
                neighbor = solution.clone()
                neighbor.unassign(spec.getId())

                # It should decrease the total cost. Recompute the fitness (cost) and select the one
                if neighbor.evaluate():
                    neighborCost = neighbor.getFitness()
                    if neighborCost < curCost:
                        if self.policy == 'FirstImprovement':
                            return neighbor
                        elif neighborCost < bestNeighbor.getFitness():
                            bestNeighbor = neighbor
                            curCost = neighborCost

        return bestNeighbor


    def _exploreReplace(self, solution):
        """
        Try replacing an assigned specialist with a cheaper unassigned one,
        keeping the pipe feasible.
        """
        curCost = solution.getFitness()
        bestNeighbor = solution

        assignedSpecs = solution.getAssignedSpecialists()
        unassignedSpecs = solution.getUnassignedSpecialists()

        if not unassignedSpecs:
            return bestNeighbor

        # Sort assigned by cost descending (try to replace expensive ones)
        assignedSpecs.sort(key=lambda s: s.getCost(), reverse=True)
        # Sort unassigned by cost ascending (prefer cheap replacements)
        unassignedSpecs.sort(key=lambda s: s.getCost())

        for oldSpec in assignedSpecs:
            pipeId = solution.getAssignedPipe(oldSpec.getId())
            excess = solution.getExcessCapacity(pipeId)

            for newSpec in unassignedSpecs:
                # Only worth if new specialist is cheaper
                if newSpec.getCost() >= oldSpec.getCost():
                    break

                # Check if replacing maintains feasibility:
                # after removing old and adding new, remaining demand must be <= 0
                # current excess = old_excess
                # new excess = excess - old.cap + new.cap
                newExcess = excess - oldSpec.getCapacity() + newSpec.getCapacity()
                if newExcess >= 0:
                    # Feasible replacement
                    neighbor = solution.clone()
                    neighbor.unassign(oldSpec.getId())
                    neighbor.assign(newSpec.getId(), pipeId)

                    if neighbor.evaluate():
                        neighborCost = neighbor.getFitness()
                        if neighborCost < curCost:
                            if self.policy == 'FirstImprovement':
                                return neighbor
                            elif neighborCost < bestNeighbor.getFitness():
                                bestNeighbor = neighbor
                                curCost = neighborCost

        return bestNeighbor


    # def _exploreSwap(self, solution):
    #     """
    #     Try swapping a specialist from one pipe with a specialist from another pipe,
    #     if it results in lower cost (both pipes remain feasible).
    #     """
    #     curCost = solution.getFitness()
    #     bestNeighbor = solution
    #
    #     cutPipes = solution.cutPipes
    #     if len(cutPipes) < 2:
    #         return bestNeighbor
    #
    #     for i, pipeA in enumerate(cutPipes):
    #         pipeAId = pipeA.getId()
    #         specsA = solution.getSpecialistsOnPipe(pipeAId)
    #
    #         for j in range(i + 1, len(cutPipes)):
    #             pipeB = cutPipes[j]
    #             pipeBId = pipeB.getId()
    #             specsB = solution.getSpecialistsOnPipe(pipeBId)
    #
    #             for sIdA in specsA:
    #                 for sIdB in specsB:
    #                     specA = solution.specialists[sIdA]
    #                     specB = solution.specialists[sIdB]
    #
    #                     # Check feasibility after swap:
    #                     # PipeA loses specA, gains specB
    #                     excessA = solution.getExcessCapacity(pipeAId)
    #                     newExcessA = excessA - specA.getCapacity() + specB.getCapacity()
    #                     if newExcessA < 0:
    #                         continue
    #
    #                     # PipeB loses specB, gains specA
    #                     excessB = solution.getExcessCapacity(pipeBId)
    #                     newExcessB = excessB - specB.getCapacity() + specA.getCapacity()
    #                     if newExcessB < 0:
    #                         continue
    #
    #                     # Cost doesn't change in a swap (same specialists used)
    #                     # But it can enable future Remove/Replace moves
    #                     # Skip if no cost improvement possible
    #                     # Actually, swap is useful if combined with remove,
    #                     # but alone doesn't reduce cost. Skip pure swaps.
    #                     # Instead: swap assigned with unassigned handled by Replace.
    #                     pass
    #
    #     return bestNeighbor


    def exploreNeighborhood(self, solution):
        neighbor = solution

        if self.config.neighborhoodStrategy == 'Both':
            improved = self._exploreRemove(neighbor)
            if improved.getFitness() < neighbor.getFitness():
                neighbor = improved
                
            improved = self._exploreReplace(neighbor)
            if improved.getFitness() < neighbor.getFitness():
                neighbor = improved
        elif self.config.neighborhoodStrategy == 'Remove':
            improved = self._exploreRemove(solution)
            if improved.getFitness() < solution.getFitness():
                neighbor = improved
        else:
            improved = self._exploreReplace(solution)
            if improved.getFitness() < solution.getFitness():
                neighbor = improved

        return neighbor


    def stopCriteria(self, iteration, endTime, endIterations):
        if endIterations is not None and endIterations > 0:
            if iteration >= endIterations:
                return True
            return False
        return time.time() >= endTime


    def solve(self, **kwargs):
        initialSolution = kwargs.get('solution', None)
        if initialSolution is None:
            raise AMMMException('[local search] No solution provided')

        if not initialSolution.isFeasible():
            return initialSolution

        self.startTime = kwargs.get('startTime', None)
        endTime = kwargs.get('endTime', None)
        endIterations = kwargs.get('endIterations', None)

        incumbent = initialSolution
        incumbentFitness = incumbent.getFitness()
        iterations = 0

        while not self.stopCriteria(iterations, endTime, endIterations):
            iterations += 1

            neighbor = self.exploreNeighborhood(incumbent)
            if neighbor is None:
                break
            neighborFitness = neighbor.getFitness()

            if incumbentFitness <= neighborFitness:
                # if self.config.verbose:
                #     print(f" Local optimum reached after {iterations} iterations")
                break

            incumbent = neighbor
            incumbentFitness = neighborFitness

        # if self.config.verbose:
        #     print(f" Final cost: {incumbentFitness:.2f} "
        #           f"(improvement: {initialSolution.getFitness() - incumbentFitness:.2f})")

        return incumbent