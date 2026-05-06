"""
AMMM Project Heuristics

Phase 1: Stoer-Wagner min-cut to determine the partition and cut pipes.
Phase 2: Greedy resource allocation of specialists to cut pipes.
"""

import time
from Heuristics.solver import _Solver
from Heuristics.solvers.stoer_wagner import StoerWagner
from Heuristics.solvers.localSearch2 import LocalSearch2
from Heuristics.problem.solution2 import Solution2


class Solver_Greedy2(_Solver):

    def _computeMinCut(self):
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()
        cut_weight, partition = StoerWagner(nBases, pipes)
        return partition

    def _getCutPipes(self, partition):
        pipes = self.instance.getPipes()
        return [p for p in pipes if partition[p.getBaseI()] != partition[p.getBaseJ()]]


    def construction(self):
        """
        Greedy construction for resource allocation:
        - Sort pipes by demand (descending) - hardest pipes first
        - For each pipe, greedily assign cheapest-per-unit specialists until demand is met
        """
        partition = self._computeMinCut()
        cutPipes = self._getCutPipes(partition)

        nBases = self.instance.getNumBases()
        specialists = self.instance.getSpecialists()

        solution = Solution2(nBases, partition, cutPipes, specialists)

        if not cutPipes:
            solution.makeInfeasible()
            return solution

        # Sort cut pipes by demand descending (hardest first)
        sortedPipes = sorted(cutPipes, key=lambda p: p.getDemand(), reverse=True)

        # Sort specialists by cost-effectiveness (cost/capacity, lower = better)
        sortedSpecs = sorted(specialists, key=lambda s: s.getCostEffectiveness())

        for pipe in sortedPipes:
            pipeId = pipe.getId()
            for spec in sortedSpecs:
                if solution.isSpecialistAssigned(spec.getId()):
                    continue
                if solution.isPipeCovered(pipeId):
                    break
                solution.assign(spec.getId(), pipeId)

            if not solution.isPipeCovered(pipeId):
                solution.makeInfeasible()
                return solution

        solution.evaluate()
        return solution

    def solve(self, **kwargs):
        self.startTimeMeasure()

        solver = kwargs.get('solver', None)
        if solver is not None:
            self.config.solver = solver
        localSearch = kwargs.get('localSearch', None)
        if localSearch is not None:
            self.config.localSearch = localSearch

        self.writeLogLine(float('inf'), 0)

        solution = self.construction()
        if self.config.localSearch and solution.isFeasible():
            ls = LocalSearch2(self.config, None)
            endTime = self.startTime + self.config.maxExecTime
            solution = ls.solve(solution=solution, startTime=self.startTime, endTime=endTime)

        self.elapsedEvalTime = time.time() - self.startTime
        self.writeLogLine(solution.getFitness(), 1)
        self.numSolutionsConstructed = 1
        self.printPerformance()

        return solution
