"""
AMMM Project Heuristics
Alpha Tuning Main Function.
"""

import sys
import os
from Heuristics.datParser import DATParser
from AMMMGlobals import AMMMException
from ValidateAlphaConfig import ValidateAlphaConfig
from InstanceGenerator import InstanceGenerator
from AlphaTuning import AlphaTuning


# Import your heuristic solver here
# Example: from YourSolver import YourSolver


def run_your_heuristic_with_alpha(alpha, instance_file):

    try:
        # Chargez votre instance
        # inputData = DATParser.parse(instance_file)

        # Lancez votre heuristique avec alpha
        # solver = YourSolver(alpha)
        # solution = solver.solve(inputData)

        # Retournez la valeur objective
        # if solution.isFeasible():
        #     return solution.objective
        # return None

        # PLACEHOLDER - ENLEVER CETTE LIGNE
        raise NotImplementedError("Vous devez implémenter run_your_heuristic_with_alpha()")

    except Exception as e:
        print("Error running heuristic: %s" % str(e))
        return None


def run():
    try:
        configFile = "configAlpha.dat"
        print("=" * 80)
        print("AMMM Alpha Parameter Tuning")
        print("=" * 80)

        # Step 1: Read and validate configuration
        print("Reading Config file %s..." % configFile)
        config = DATParser.parse(configFile)
        ValidateAlphaConfig.validate(config)

        # Step 2: Generate instances for tuning
        print("\nGenerating Tuning Instances...")
        instGen = InstanceGenerator(config)
        instGen.generate()
        print("Instances generated in: %s" % config.instancesDirectory)

        # Step 3: Run alpha tuning
        print("\nStarting Alpha Tuning Process...")
        print("=" * 80)
        tuner = AlphaTuning(config)

        # Pass your heuristic function to the tuner
        best_alpha = tuner.run_tuning(run_your_heuristic_with_alpha)

        # Step 4: Display recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if best_alpha is not None:
            print("\nBased on the tuning results, the recommended alpha value is: %.1f" % best_alpha)
            print("\nTo use this value in your solver:")
            print("  1. Update your config.dat file: alpha = %.1f" % best_alpha)
            print("  2. Or set it programmatically: alpha = %.1f" % best_alpha)
        else:
            print("\nCould not determine best alpha value.")

        print("\nDetailed results have been saved to: %s" % config.outputFile)
        print("\nNote: The 'best' alpha may vary depending on:")
        print("  - Instance characteristics")
        print("  - Computational time constraints")
        print("  - Solution quality requirements")
        print("\nConsider testing the top 2-3 alpha values on your specific problem instances.")

        print("\n" + "=" * 80)
        print("Alpha Tuning Completed Successfully")
        print("=" * 80)

        return 0

    except AMMMException as e:
        print("\nAMMMException: %s" % e)
        return 1
    except Exception as e:
        print("\nException: %s" % e)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run())