import os, sys, random
import shutil
from Heuristics.datParser import DATParser
from AMMMGlobals import AMMMException
from InstanceGenerator import InstanceGenerator
from Heuristics.solvers.solver_GRASP import Solver_GRASP
from Heuristics.problem.instance import Instance


class AlphaTuning:

    ALPHA_VALUES = [round(x * 0.1, 1) for x in range(11)]  # [0.0, 0.1, ..., 1.0]
    NUM_INSTANCES = 5       # number of generated instances
    NUM_ITERATIONS = 50     # iterations GRASP per run
    INSTANCE_SIZES = [100, 200, 500]  # values for numBases and num Specialists

    def __init__(self, configGenerator, configSolver):
        self.configGenerator = configGenerator  # config file for instances
        self.configSolver = configSolver  # config file for GRASP

    def _buildConfig(self, size, instanceIndex):
        config = type('Config', (), {})()
        config.instancesDirectory = 'tuning_instances'
        config.fileNamePrefix = f'tuning_{size}_{instanceIndex}'
        config.fileNameExtension = 'dat'
        config.numInstances = 1
        config.numBases = size
        config.numSpecialists = size
        config.minHours = self.configGenerator.minHours
        config.maxHours = self.configGenerator.maxHours
        config.minCapacity = self.configGenerator.minCapacity
        config.maxCapacity = self.configGenerator.maxCapacity
        config.minFee = self.configGenerator.minFee
        config.maxFee = self.configGenerator.maxFee
        return config

    def _generateInstance(self, size, instanceIndex):
        config = self._buildConfig(size, instanceIndex)
        gen = InstanceGenerator(config)
        gen.generate()
        instancePath = os.path.join(
            config.instancesDirectory,
            f'tuning_{size}_{instanceIndex}_0.dat'
        )
        return instancePath

    def _runGRASP(self, instancePath, alpha):
        data = DATParser.parse(instancePath)
        data.w = list(data.w)
        data.c = list(data.c)
        data.t = [list(row) for row in data.t]

        self.configSolver.alpha = alpha
        instance = Instance(self.configSolver, data)
        solver = Solver_GRASP(self.configSolver, instance)
        solution = solver.solve()
        return solution.getFitness()

    def run(self):

        if os.path.isdir('tuning_instances'):
            shutil.rmtree('tuning_instances')
        # results[alpha] = list of the costs for instances created
        results = {alpha: [] for alpha in self.ALPHA_VALUES}

        for size in self.INSTANCE_SIZES:
            print(f'\n Taille m={size}')
            for i in range(self.NUM_INSTANCES):
                print(f'  Instance {i+1}/{self.NUM_INSTANCES}...', end=' ')
                instancePath = self._generateInstance(size, i)

                for alpha in self.ALPHA_VALUES:
                    cost = self._runGRASP(instancePath, alpha)
                    results[alpha].append(cost)
                    print(f'α={alpha:.1f}→{cost}', end='  ')