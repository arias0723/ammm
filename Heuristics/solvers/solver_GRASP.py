'''
AMMM Project Heuristics
GRASP solver for the pipe-destruction problem.
Randomized Karger construction + local search.
'''

import random
import time
from Heuristics.solver import _Solver
from Heuristics.solvers.localSearch import LocalSearch
from Heuristics.solvers.solver_Greedy import UnionFind


class Solver_GRASP(_Solver):

    def _greedyRandomizedConstruction(self, alpha):
        solution = self.instance.createSolution()
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()

        uf = UnionFind(nBases)

        mergesNeeded = nBases - 2
        mergesDone = 0

        while mergesDone < mergesNeeded:
            # Build candidate list: pipes connecting different components
            candidates = [p for p in pipes
                          if not uf.connected(p.getBaseI(), p.getBaseJ())]

            if not candidates:
                break

            # Sort by demand descending (heavy pipes = good to contract/keep)
            candidates.sort(key=lambda p: p.getDemand(), reverse=True)

            # RCL based on alpha
            maxDemand = candidates[0].getDemand()
            minDemand = candidates[-1].getDemand()
            threshold = maxDemand - alpha * (maxDemand - minDemand)

            rcl = [p for p in candidates if p.getDemand() >= threshold]
            if not rcl:
                rcl = [candidates[0]]

            selected = random.choice(rcl)
            uf.union(selected.getBaseI(), selected.getBaseJ())
            mergesDone += 1

        # Merge remaining components if > 2
        if uf.numComponents > 2:
            components = uf.getComponents(nBases)
            roots = list(components.keys())
            while uf.numComponents > 2:
                uf.union(roots[0], roots[-1])
                roots.pop()

        if uf.numComponents < 2:
            solution.makeInfeasible()
            return solution

        # Build partition
        components = uf.getComponents(nBases)
        groupId = 0
        for root, members in components.items():
            for base in members:
                solution.setGroup(base, groupId)
            groupId += 1

        # Compute cut and assign specialists
        solution.computeCutPipes()
        feasible = solution.assignSpecialistsGreedy()
        if not feasible:
            solution.makeInfeasible()

        return solution

    def stopCriteria(self):
        self.elapsedEvalTime = time.time() - self.startTime
        return time.time() - self.startTime > self.config.maxExecTime

    def solve(self, **kwargs):
        self.startTimeMeasure()
        incumbent = self.instance.createSolution()
        incumbent.makeInfeasible()
        bestCost = incumbent.getFitness()
        self.writeLogLine(bestCost, 0)

        iteration = 0
        while not self.stopCriteria():
            iteration += 1

            # Force first iteration as pure Greedy (alpha == 0)
            alpha = 0 if iteration == 1 else self.config.alpha

            solution = self._greedyRandomizedConstruction(alpha)
            if self.config.localSearch and solution.isFeasible():
                localSearch = LocalSearch(self.config, None)
                endTime = self.startTime + self.config.maxExecTime
                solution = localSearch.solve(solution=solution, startTime=self.startTime, endTime=endTime)

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

