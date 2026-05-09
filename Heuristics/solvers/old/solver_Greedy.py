'''
AMMM Project Heuristics

Karger-inspired algorithm: contracts heaviest pipes (keeps them), leaving lightest pipes as the cut.
Specialist assignment uses greedy 0-1 knapsack.
'''

import random
import time
from Heuristics.solver import _Solver
from Heuristics.solvers.localSearch import LocalSearch
from Heuristics.util import UnionFind


class Solver_Greedy(_Solver):

    def construction(self):
        solution = self.instance.createSolution()
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()

        # Using a UnionFind data structure for efficiency
        uf = UnionFind(nBases)

        # Sort pipes by demand descending (contract heaviest first = keep them)
        sortedPipes = sorted(pipes, key=lambda p: p.getDemand(), reverse=True)

        mergesNeeded = nBases - 2
        mergesDone = 0

        for pipe in sortedPipes:
            if mergesDone >= mergesNeeded:
                break
            baseI, baseJ = pipe.getBaseI(), pipe.getBaseJ()
            if not uf.connected(baseI, baseJ):
                uf.union(baseI, baseJ)
                mergesDone += 1

        # Keep merging until there are only two components (a.k.a gropus) left in the graph
        if uf.numComponents > 2:
            components = uf.getComponents(nBases)
            roots = list(components.keys())
            while uf.numComponents > 2:
                uf.union(roots[0], roots[-1])
                roots.pop()

        if uf.numComponents < 2:
            solution.makeInfeasible()
            return solution

        # Build partition from the 2 final components
        components = uf.getComponents(nBases)
        groupId = 0
        for root, members in components.items():
            for base in members:
                solution.setGroup(base, groupId)
            groupId += 1

        # Compute cut and assign specialists via greedy knapsack
        solution.computePipesToDestroy()
        feasible = solution.assignSpecialistsToDestroyPipes()
        if not feasible:
            solution.makeInfeasible()

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
            ls = LocalSearch(self.config, None)
            endTime = self.startTime + self.config.maxExecTime
            solution = ls.solve(solution=solution, startTime=self.startTime, endTime=endTime)

        self.elapsedEvalTime = time.time() - self.startTime
        self.writeLogLine(solution.getFitness(), 1)
        self.numSolutionsConstructed = 1
        self.printPerformance()

        return solution
