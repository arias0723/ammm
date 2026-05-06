"""
AMMM Project Heuristics

"""

from argparse import ArgumentParser
from pathlib import Path
import sys

from Heuristics.datParser import DATParser
from AMMMGlobals import AMMMException
from Heuristics.validateInputDataP2 import ValidateInputData
from Heuristics.ValidateConfig import ValidateConfig
from Heuristics.problem.instance import Instance
from Heuristics.solvers.solver_Greedy2 import Solver_Greedy2
from Heuristics.solvers.solver_GRASP2 import Solver_GRASP2


class Main2:
    def __init__(self, config):
        self.config = config

    def run(self, data):
        try:
            if self.config.verbose:
                print('Creating Problem Instance...')
            instance = Instance(self.config, data)

            if self.config.verbose:
                print('Solving with Stoer-Wagner + Resource Allocation...')

            if not instance.checkInstance():
                print('Instance is infeasible.')
                return 1

            if self.config.solver == 'Greedy':
                solver = Solver_Greedy2(self.config, instance)
            elif self.config.solver == 'GRASP':
                solver = Solver_GRASP2(self.config, instance)
            else:
                raise AMMMException('Solver %s not supported.' % str(self.config.solver))

            solution = solver.solve()
            print(solution)
            solution.saveToFile(self.config.solutionFile)
            return 0

        except AMMMException as e:
            print('Exception:', e)
            return 1


if __name__ == '__main__':
    parser = ArgumentParser(description='AMMM Project Heuristics - Stoer-Wagner Approach')
    parser.add_argument('-c', '--configFile', nargs='?', type=Path,
                        default=Path(__file__).parent / 'config/config.dat',
                        help='specifies the config file')
    args = parser.parse_args()

    config = DATParser.parse(args.configFile)
    ValidateConfig.validate(config)
    inputData = DATParser.parse(config.inputDataFile)
    ValidateInputData.validate(inputData)

    if config.verbose:
        print('AMMM Project Heuristics - Stoer-Wagner + Resource Allocation')
        print('-------------------------------------------------------------')
        print('Config file: %s' % args.configFile)
        print('Input Data file: %s' % config.inputDataFile)

    main = Main2(config)
    sys.exit(main.run(inputData))
