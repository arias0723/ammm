"""
AMMM Project Heuristics
Alpha parameter tuning for GRASP constructive phase.
"""

import csv
import os
import time
from statistics import mean, stdev
from AMMMGlobals import AMMMException


class AlphaTuning(object):
    """
    Tune the alpha parameter for GRASP constructive phase.
    Tests different alpha values and reports performance metrics.
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
        self.instance_names = []
        self.output_directory, self.final_results_file = self._resolve_output_paths()

    def _resolve_output_paths(self):
        """Resolve the tuning output directory and final CSV file path."""
        base_directory = os.path.dirname(os.path.abspath(__file__))
        raw_output = self.config.outputFile

        if os.path.isabs(raw_output):
            resolved_output = raw_output
        else:
            resolved_output = os.path.normpath(os.path.join(base_directory, raw_output))

        _, extension = os.path.splitext(resolved_output)
        if extension.lower() == '.csv':
            final_results_file = resolved_output
            output_directory = os.path.dirname(final_results_file)
        else:
            output_directory = resolved_output
            final_results_file = os.path.join(output_directory, 'final_results.csv')

        return output_directory, final_results_file

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
        self.instance_names = [os.path.basename(instance_file) for instance_file in instance_files]

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
                'overall_mean_time': 0.0,
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
            instance_times = []
            total_feasible = 0
            total_runs = 0

            for instance_name, stats in self.results[alpha]['instances'].items():
                instance_means.append(stats['mean_objective'])
                instance_bests.append(stats['best_objective'])
                instance_times.append(stats['mean_time'])
                total_feasible += stats['num_feasible']
                total_runs += stats['num_runs']

            if instance_means:
                self.results[alpha]['overall_mean'] = mean(instance_means)
                self.results[alpha]['overall_best'] = min(instance_bests)
                self.results[alpha]['overall_worst'] = max(instance_means)
                self.results[alpha]['overall_mean_time'] = mean(instance_times)
                self.results[alpha]['success_rate'] = (total_feasible / total_runs) * 100

        self.print_summary()
        self.save_results()

        return self.get_best_alpha()

    def print_summary(self):
        """Print summary of tuning results."""
        self._print("\n" + "=" * 80)
        self._print("TUNING RESULTS SUMMARY")
        self._print("=" * 80)
        self._print("%-10s %-15s %-15s %-15s %-15s %-12s" % ('Alpha', 'Mean Obj', 'Best Obj', 'Worst Obj', 'Mean Time', 'Success %'))
        self._print("-" * 80)

        alphaValues = self.config.alphaValues
        for alpha in alphaValues:
            res = self.results[alpha]
            if res['overall_mean'] > 0:
                self._print("%-10.1f %-15.2f %-15.2f %-15.2f %-15.3f %-12.1f" %
                            (alpha, res['overall_mean'], res['overall_best'],
                             res['overall_worst'], res['overall_mean_time'], res['success_rate']))

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
        """Save detailed results to CSV files."""
        alphaValues = self.config.alphaValues
        if not os.path.isdir(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)

        self._save_instance_csvs()

        self._save_final_csv()

        self._print("CSV results saved to: %s" % self.output_directory)
        self._print("Final summary file: %s" % self.final_results_file)

    def _save_instance_csvs(self):
        """Save one CSV file per tuning instance, with a row for each alpha value."""
        for instance_name in sorted(self.instance_names):
            file_name = os.path.splitext(instance_name)[0] + '.csv'
            file_path = os.path.join(self.output_directory, file_name)

            with open(file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([
                    'alpha', 'instance', 'mean_objective', 'best_objective', 'worst_objective',
                    'std_objective', 'mean_time', 'feasible_runs', 'total_runs', 'success_rate'
                ])

                for alpha in self.config.alphaValues:
                    instance_stats = self.results[alpha]['instances'].get(instance_name)
                    if instance_stats is None:
                        continue

                    success_rate = (instance_stats['num_feasible'] / instance_stats['num_runs']) * 100 if instance_stats['num_runs'] else 0.0
                    writer.writerow([
                        alpha,
                        instance_name,
                        '%.2f' % instance_stats['mean_objective'],
                        '%.2f' % instance_stats['best_objective'],
                        '%.2f' % instance_stats['worst_objective'],
                        '%.2f' % instance_stats['std_objective'],
                        '%.3f' % instance_stats['mean_time'],
                        instance_stats['num_feasible'],
                        instance_stats['num_runs'],
                        '%.1f' % success_rate,
                    ])

    def _save_final_csv(self):
        """Save the aggregated alpha tuning results used for summary charts."""
        with open(self.final_results_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                'alpha', 'mean_objective', 'best_objective', 'worst_objective',
                'mean_time', 'success_rate', 'num_instances', 'feasible_runs', 'total_runs'
            ])

            for alpha in self.config.alphaValues:
                res = self.results[alpha]
                if res['overall_mean'] > 0:
                    total_runs = sum(stats['num_runs'] for stats in res['instances'].values())
                    feasible_runs = sum(stats['num_feasible'] for stats in res['instances'].values())
                    writer.writerow([
                        alpha,
                        '%.2f' % res['overall_mean'],
                        '%.2f' % res['overall_best'],
                        '%.2f' % res['overall_worst'],
                        '%.3f' % res['overall_mean_time'],
                        '%.1f' % res['success_rate'],
                        len(res['instances']),
                        feasible_runs,
                        total_runs,
                    ])