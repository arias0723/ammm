"""
AMMM Project Heuristics
Alpha Tuning Main Function.
"""

import subprocess
import tempfile
import re
import sys
import os
from typing import Any

from Heuristics.datParser import DATParser
from AMMMGlobals import AMMMException
from ValidateAlphaConfig import ValidateAlphaConfig
from InstanceGenerator import InstanceGenerator
from AlphaTuning import AlphaTuning


# Import your heuristic solver here
# Example: from YourSolver import YourSolver

def run_your_heuristic_with_alpha(alpha, instance_file):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_script = os.path.join(project_root, "Heuristics", "Main.py")

        temp_config_path = get_config(alpha, instance_file, project_root)

        result = subprocess.run(
            [sys.executable, main_script, "-c", temp_config_path],
            capture_output=True,
            text=True
        )
        # Print the output to the same CLI as the caller
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        os.remove(temp_config_path)

        # 4. Parse the output to find the objective/cost. 
        # You will need to adjust the regex based on exactly what `print(solution)` outputs.
        # Assuming it prints something like: "Total Cost: 450" or similar.
        match = re.search(r'(?:Cost|Objective)[\s:=]+([\d.]+)', result.stdout, re.IGNORECASE)
        
        if match:
            return float(match.group(1))
        
        return None

    except Exception as e:
        print(f"Error running heuristic: {e}")
        return None


def get_config(alpha, instance_file, project_root: str | bytes | LiteralString | Any) -> str:
    # Read parameters from config.dat
    config_path = os.path.join(project_root, "Heuristics", "config", "config.dat")
    base_config_lines = []
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not any(x in line for x in ['alpha', 'inputDataFile', 'solutionFile']):
                        base_config_lines.append(line)

    # 1. Create a temporary config file for this specific run
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as temp_config:
        temp_config_path = temp_config.name
        # temp_config.write(f"solver = GRASP;\n")
        temp_config.write(f"alpha = {alpha};\n")
        temp_config.write(f"inputDataFile = {instance_file};\n")
        temp_config.write(f"solutionFile = temp_solution.sol;\n")
        # temp_config.write(f"verbose = True;\n")
        # temp_config.write(f"maxExecTime = 60;\n")
        # Add any other required config params here
        for line in base_config_lines:
            temp_config.write(f"{line}\n")

    # Print the content of the temporary config file
    # print(f"--- Content of {temp_config_path} ---")
    # with open(temp_config_path, 'r') as f:
    #     print(f.read())
    # print("---------------------------------------")
    return temp_config_path


# def run_your_heuristic_with_alpha(alpha, instance_file):
#     try:
#         project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         if project_root not in sys.path:
#             sys.path.insert(0, project_root)

#         from Heuristics.datParser import DATParser
#         from Heuristics.problem.instance import Instance
#         from Heuristics.solvers.solver_GRASP import Solver_GRASP

#         config_path = os.path.join(project_root, "Heuristics", "config", "config.dat")
#         if os.path.exists(config_path):
#             config = DATParser.parse(config_path)
#         else:
#             class DummyConfig: pass
#             config = DummyConfig()
            
#         config.solver = 'GRASP'
#         config.alpha = alpha
#         config.verbose = False
        
#         inputData = DATParser.parse(instance_file)
        
#         instance = Instance(config, inputData)
#         if not instance.checkInstance():
#             return None
            
#         solver = Solver_GRASP(config, instance)
#         solution = solver.solve()
        
#         if solution is not None:
#             if hasattr(solution, 'totalCost'):
#                 return solution.totalCost
#             elif hasattr(solution, 'cost'):
#                 return solution.cost
#             elif hasattr(solution, 'getTotalCost'):
#                 return solution.getTotalCost()
#             elif hasattr(solution, 'objective'):
#                 return solution.objective
        
#         return None

#     except Exception as e:
#         print("Error running heuristic: %s" % str(e))
#         import traceback
#         traceback.print_exc()
#         return None


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