"""
AMMM Project Heuristics

Phase 1: Min-cut to determine the partition and cut pipes.
Phase 2: GRASP construction + local search for resource allocation.

The randomization is in the specialist selection during assignment:
instead of always picking the best cost-effective specialist, we use an RCL.
"""

import random
import time
from Heuristics.solver import _Solver
from Heuristics.solvers.karger import Karger
from Heuristics.solvers.stoer_wagner import StoerWagner
from Heuristics.solvers.localSearch import LocalSearch
from Heuristics.problem.solution import Solution


class Solver_GRASP(_Solver):

    def _computeMinCut(self):
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()
        # cut_weight, partition = StoerWagner(nBases, pipes)
        cut_weight, partition = Karger(nBases, pipes, 1)

        return partition

    def _getCutPipes(self, partition):
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

        solution = Solution(nBases, partition, cutPipes, specialists)

        if not cutPipes:
            solution.makeInfeasible()
            return solution

        # Sort cut pipes by demand descending (hardest first)
        sortedPipes = sorted(cutPipes, key=lambda p: p.getDemand(), reverse=True)

        # Sort specialists by cost-effectiveness (cost/capacity, lower = better)
        sortedSpecs = sorted(specialists, key=lambda s: s.getCostEffectiveness())

        for pipe in sortedPipes:
            pipeId = pipe.getId()

            while not solution.isPipeCovered(pipeId):
                # Available specialists
                available = [s for s in sortedSpecs if not solution.isSpecialistAssigned(s.getId())]
                if not available:
                    solution.makeInfeasible()
                    return solution

                # Build RCL
                bestCE = available[0].getCostEffectiveness()
                worstCE = available[-1].getCostEffectiveness()
                threshold = bestCE + alpha * (worstCE - bestCE)

                rcl = [s for s in available if s.getCostEffectiveness() <= threshold]
                if not rcl:
                    rcl = [available[0]]

                # Pick randomly from RCL
                selectedSpec = random.choice(rcl)
                solution.assign(selectedSpec.getId(), pipeId)

        solution.evaluate()
        return solution

    def stopCriteria(self):
        self.elapsedEvalTime = time.time() - self.startTime
        return time.time() - self.startTime > self.config.maxExecTime

    def solve(self, **kwargs):
        self.startTimeMeasure()

        # Compute min-cut once
        partition = self._computeMinCut()
        cutPipes = self._getCutPipes(partition)

        incumbent = Solution(
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
                ls = LocalSearch(self.config, None)
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
