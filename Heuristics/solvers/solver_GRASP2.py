"""
AMMM Project Heuristics
GRASP solver for the Stoer-Wagner + Resource Allocation approach.

Phase 1: Stoer-Wagner min-cut (deterministic).
Phase 2: GRASP construction + local search for resource allocation.

The randomization is in the specialist selection during assignment:
instead of always picking the best cost-effective specialist, we use an RCL.
"""

import random
import time
from Heuristics.solver import _Solver
from Heuristics.solvers.stoer_wagner import StoerWagner
from Heuristics.solvers.localSearch2 import LocalSearch2
from Heuristics.problem.solution2 import Solution2


class Solver_GRASP2(_Solver):

    def _computeMinCut(self):
        """Use Stoer-Wagner to find the min-cut partition."""
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()
        cut_weight, partition = StoerWagner(nBases, pipes)
        return partition

    def _getCutPipes(self, partition):
        """Identify pipes crossing the partition."""
        pipes = self.instance.getPipes()
        return [p for p in pipes if partition[p.getBaseI()] != partition[p.getBaseJ()]]

    def _greedyRandomizedConstruction(self, alpha, partition, cutPipes):
        """
        GRASP construction for resource allocation:
        - For each pipe (random order with bias toward high demand),
          build an RCL of available specialists by cost-effectiveness,
          then pick randomly from the RCL until demand is met.
        """
        nBases = self.instance.getNumBases()
        specialists = self.instance.getSpecialists()

        solution = Solution2(nBases, partition, cutPipes, specialists)

        if not cutPipes:
            solution.makeInfeasible()
            return solution

        # Randomize pipe processing order (bias toward high demand)
        sortedPipes = sorted(cutPipes, key=lambda p: p.getDemand(), reverse=True)

        for pipe in sortedPipes:
            pipeId = pipe.getId()

            while not solution.isPipeCovered(pipeId):
                # Available specialists (not yet assigned)
                available = [s for s in specialists if not solution.isSpecialistAssigned(s.getId())]
                if not available:
                    solution.makeInfeasible()
                    return solution

                # Sort by cost-effectiveness
                available.sort(key=lambda s: s.getCostEffectiveness())

                # Build RCL
                bestCE = available[0].getCostEffectiveness()
                worstCE = available[-1].getCostEffectiveness()
                threshold = bestCE + alpha * (worstCE - bestCE)

                rcl = [s for s in available if s.getCostEffectiveness() <= threshold]
                if not rcl:
                    rcl = [available[0]]

                # Pick randomly from RCL
                selected = random.choice(rcl)
                solution.assign(selected.getId(), pipeId)

        solution.evaluate()
        return solution

    def stopCriteria(self):
        self.elapsedEvalTime = time.time() - self.startTime
        return time.time() - self.startTime > self.config.maxExecTime

    def solve(self, **kwargs):
        self.startTimeMeasure()

        # Compute min-cut once (deterministic)
        partition = self._computeMinCut()
        cutPipes = self._getCutPipes(partition)

        incumbent = Solution2(
            self.instance.getNumBases(), partition, cutPipes, self.instance.getSpecialists()
        )
        incumbent.makeInfeasible()
        bestCost = incumbent.getFitness()
        self.writeLogLine(bestCost, 0)

        iteration = 0
        while not self.stopCriteria():
            iteration += 1

            # First iteration pure greedy (alpha=0), then randomized
            alpha = 0.0 if iteration == 1 else self.config.alpha

            solution = self._greedyRandomizedConstruction(alpha, partition, cutPipes)

            if self.config.localSearch and solution.isFeasible():
                ls = LocalSearch2(self.config, None)
                endTime = self.startTime + self.config.maxExecTime
                solution = ls.solve(solution=solution, startTime=self.startTime, endTime=endTime)

            if solution.isFeasible():
                solutionCost = solution.getFitness()
                if solutionCost < bestCost:
                    incumbent = solution
                    bestCost = solutionCost
                    self.writeLogLine(bestCost, iteration)

        self.writeLogLine(bestCost, iteration)
        self.numSolutionsConstructed = iteration
        self.printPerformance()
        return incumbent
