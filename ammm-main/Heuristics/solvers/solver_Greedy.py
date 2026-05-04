'''
AMMM Project Heuristics
Greedy solver for the pipe-destruction problem.
Karger-inspired: contracts heaviest pipes (keeps them), leaving lightest pipes as the cut.
Specialist assignment uses greedy knapsack.
'''

import random
import time
from Heuristics.solver import _Solver
from Heuristics.solvers.localSearch import LocalSearch


class UnionFind(object):
    """Disjoint-set / Union-Find with path compression and union by rank."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.numComponents = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x
        return root

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.numComponents -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def getComponents(self, n):
        components = {}
        for i in range(n):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return components


class Solver_Greedy(_Solver):

    def construction(self):
        solution = self.instance.createSolution()
        pipes = self.instance.getPipes()
        nBases = self.instance.getNumBases()

        specialists = self.instance.getSpecialists()

        if self.config.verbose:
            print(f"Computing destruction costs for {len(pipes)} pipes...")

        pipesWithCosts = []
        for pipe in pipes:
            cost, specialists_lists = pipe.getDestructionCost(specialists)
            pipesWithCosts.append((pipe, cost))

            if self.config.verbose and cost == float('inf'):
               print(f" Pipe {pipe.getId()} ({pipe.getBaseI()},{pipe.getBaseJ()}) "
                      f"cannot be destroyed with the specialists available ")

        sortedPipes = sorted(pipesWithCosts, key=lambda x: x[1], reverse=True)

        sortedPipes = [pipe for pipe, cost in sortedPipes]

        if self.config.verbose:
            print(f"Pipes sorted by destruction cost (descending):")


        uf = UnionFind(nBases)

        mergesNeeded = nBases - 2
        mergesDone = 0

        for pipe in sortedPipes:
            if mergesDone >= mergesNeeded:
                break
            baseI, baseJ = pipe.getBaseI(), pipe.getBaseJ()
            if not uf.connected(baseI, baseJ):
                uf.union(baseI, baseJ)
                mergesDone += 1

        # If graph is sparse and we still have > 2 components, merge remaining
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
        solution.computeCutPipes()
        feasible = solution.assignSpecialistsGreedy()
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


