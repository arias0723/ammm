# runAlphaTunnig.py
import sys
from pathlib import Path
from argparse import ArgumentParser
from Heuristics.datParser import DATParser
from AMMMGlobals import AMMMException
from Heuristics.ValidateConfig import ValidateConfig
from AlphaTuning import AlphaTuning


def run():
    try:
        configGeneratorFile = "config/config.dat"           # InstanceGenerator/config/config.dat
        configSolverFile = "../Heuristics/config/config.dat"  # Heuristics/config/config.dat

        print("Tuning for Alpha")

        configGenerator = DATParser.parse(configGeneratorFile)
        configSolver = DATParser.parse(configSolverFile)

        tuner = AlphaTuning(configGenerator, configSolver)
        results = tuner.run()

        best_alpha = min(results, key=lambda a: sum(results[a]) / len(results[a]))
        print(f'\n✓ Best alpha : {best_alpha}')
        return 0

    except AMMMException as e:
        print('Exception:', e)
        return 1


if __name__ == '__main__':
    sys.exit(run())