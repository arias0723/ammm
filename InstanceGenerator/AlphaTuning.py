"""
AMMM Project Heuristics
Alpha parameter tuning for GRASP constructive phase.
"""

import os
import time
from statistics import mean, stdev
from AMMMGlobals import AMMMException


class AlphaTuning(object):
    """
    Tune the alpha parameter for GRASP constructive phase.
    Tests different alpha values and reports performance metrics.

    Note: This class expects your heuristic to have:
    - A method to set alpha value
    - A method to run the heuristic
    - A method to get the solution objective
    """

    def __init__(self, config):
        """
        Initialize the tuning process.

        Args:
            config: Configuration object with tuning parameters
        """
        self.config = config
        self.verbose = config.verbose
        self.results = {}

    def _print(self, message, end='\n'):
        """Print message only if verbose is True."""
        if self.verbose:
            print(message, end=end)

    def get_instance_files(self):
        """Get all instance files from the directory."""
        instancesDirectory = self.config.instancesDirectory

        if not os.path.isdir(instancesDirectory):
            raise AMMMException('Directory(%s) does not exist' % instancesDirectory)

        files = []
        for filename in os.listdir(instancesDirectory):
            if filename.endswith('.' + self.config.fileNameExtension):
                files.append(os.path.join(instancesDirectory, filename))

        if not files:
            raise AMMMException('No .%s files found in %s' % (self.config.fileNameExtension, instancesDirectory))

        return sorted(files)

    def test_alpha_value(self, alpha, instance_file, num_runs, run_heuristic_func):
        """
        Test a specific alpha value on one instance multiple times.

        Args:
            alpha: Alpha value to test
            instance_file: Path to instance file
            num_runs: Number of runs for this alpha value
            run_heuristic_func: Function that takes (alpha, instance_file) and returns objective value

        Returns:
            Dictionary with statistics (mean, best, worst, std)
        """
        objective_values = []
        execution_times = []

        for run in range(num_runs):
            # Run heuristic with current alpha
            start_time = time.time()
            objective = run_heuristic_func(alpha, instance_file)
            elapsed_time = time.time() - start_time

            if objective is not None:
                objective_values.append(objective)
                execution_times.append(elapsed_time)

        if not objective_values:
            return None

        stats = {
            'mean_objective': mean(objective_values),
            'best_objective': min(objective_values),
            'worst_objective': max(objective_values),
            'std_objective': stdev(objective_values) if len(objective_values) > 1 else 0.0,
            'mean_time': mean(execution_times),
            'num_feasible': len(objective_values),
            'num_runs': num_runs
        }

        return stats

    def run_tuning(self, run_heuristic_func):
        """
        Run the complete tuning process.

        Args:
            run_heuristic_func: Function that takes (alpha, instance_file) and returns objective value
        """
        alphaValues = self.config.alphaValues
        numRunsPerAlpha = self.config.numRunsPerAlpha
        instance_files = self.get_instance_files()

        self._print("=" * 80)
        self._print("ALPHA PARAMETER TUNING FOR GRASP")
        self._print("=" * 80)
        self._print("Number of instances: %d" % len(instance_files))
        self._print("Number of alpha values to test: %d" % len(alphaValues))
        self._print("Runs per alpha per instance: %d" % numRunsPerAlpha)
        self._print("Total executions: %d" % (len(instance_files) * len(alphaValues) * numRunsPerAlpha))
        self._print("=" * 80)
        self._print("")

        # Initialize results structure
        for alpha in alphaValues:
            self.results[alpha] = {
                'instances': {},
                'overall_mean': 0.0,
                'overall_best': float('inf'),
                'overall_worst': 0.0,
                'success_rate': 0.0
            }

        # Test each alpha value on each instance
        for instance_idx, instance_file in enumerate(instance_files):
            instance_name = os.path.basename(instance_file)
            self._print("\nTesting instance %d/%d: %s" % (instance_idx + 1, len(instance_files), instance_name))
            self._print("-" * 80)

            for alpha in alphaValues:
                self._print("  Alpha = %.1f..." % alpha, end=' ')

                stats = self.test_alpha_value(alpha, instance_file, numRunsPerAlpha, run_heuristic_func)

                if stats is not None:
                    self.results[alpha]['instances'][instance_name] = stats
                    self._print("Mean: %.2f, Best: %.2f, Success: %d/%d" %
                                (stats['mean_objective'], stats['best_objective'],
                                 stats['num_feasible'], stats['num_runs']))
                else:
                    self._print("No feasible solutions found")

        # Compute overall statistics
        self._print("\n" + "=" * 80)
        self._print("COMPUTING OVERALL STATISTICS")
        self._print("=" * 80)

        for alpha in alphaValues:
            instance_means = []
            instance_bests = []
            total_feasible = 0
            total_runs = 0

            for instance_name, stats in self.results[alpha]['instances'].items():
                instance_means.append(stats['mean_objective'])
                instance_bests.append(stats['best_objective'])
                total_feasible += stats['num_feasible']
                total_runs += stats['num_runs']

            if instance_means:
                self.results[alpha]['overall_mean'] = mean(instance_means)
                self.results[alpha]['overall_best'] = min(instance_bests)
                self.results[alpha]['overall_worst'] = max(instance_means)
                self.results[alpha]['success_rate'] = (total_feasible / total_runs) * 100

        self.print_summary()
        self.save_results()

        return self.get_best_alpha()

    def print_summary(self):
        """Print summary of tuning results."""
        self._print("\n" + "=" * 80)
        self._print("TUNING RESULTS SUMMARY")
        self._print("=" * 80)
        self._print("%-10s %-15s %-15s %-15s %-12s" % ('Alpha', 'Mean Obj', 'Best Obj', 'Worst Obj', 'Success %'))
        self._print("-" * 80)

        alphaValues = self.config.alphaValues
        for alpha in alphaValues:
            res = self.results[alpha]
            if res['overall_mean'] > 0:
                self._print("%-10.1f %-15.2f %-15.2f %-15.2f %-12.1f" %
                            (alpha, res['overall_mean'], res['overall_best'],
                             res['overall_worst'], res['success_rate']))

        self._print("=" * 80)

    def get_best_alpha(self):
        """Determine the best alpha value based on mean objective."""
        best_alpha = None
        best_mean = float('inf')

        alphaValues = self.config.alphaValues
        for alpha in alphaValues:
            if self.results[alpha]['overall_mean'] > 0 and self.results[alpha]['overall_mean'] < best_mean:
                best_mean = self.results[alpha]['overall_mean']
                best_alpha = alpha

        if best_alpha is not None:
            self._print("\n*** BEST ALPHA: %.1f with mean objective %.2f ***\n" % (best_alpha, best_mean))

        return best_alpha

    def save_results(self):
        """Save detailed results to a file."""
        output_file = self.config.outputFile
        alphaValues = self.config.alphaValues

        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("ALPHA PARAMETER TUNING RESULTS\n")
            f.write("=" * 80 + "\n\n")

            # Summary table
            f.write("%-10s %-15s %-15s %-15s %-12s\n" % ('Alpha', 'Mean Obj', 'Best Obj', 'Worst Obj', 'Success %'))
            f.write("-" * 80 + "\n")

            for alpha in alphaValues:
                res = self.results[alpha]
                if res['overall_mean'] > 0:
                    f.write("%-10.1f %-15.2f %-15.2f %-15.2f %-12.1f\n" %
                            (alpha, res['overall_mean'], res['overall_best'],
                             res['overall_worst'], res['success_rate']))

            # Detailed results per instance
            f.write("\n" + "=" * 80 + "\n")
            f.write("DETAILED RESULTS PER INSTANCE\n")
            f.write("=" * 80 + "\n\n")

            for alpha in alphaValues:
                f.write("\nAlpha = %.1f\n" % alpha)
                f.write("-" * 80 + "\n")

                for instance_name, stats in self.results[alpha]['instances'].items():
                    f.write("  %s:\n" % instance_name)
                    f.write("    Mean: %.2f, Best: %.2f, Worst: %.2f, StdDev: %.2f\n" %
                            (stats['mean_objective'], stats['best_objective'],
                             stats['worst_objective'], stats['std_objective']))
                    f.write("    Success rate: %d/%d\n" % (stats['num_feasible'], stats['num_runs']))
                    f.write("    Average time: %.3fs\n" % stats['mean_time'])

        self._print("Detailed results saved to: %s" % output_file)