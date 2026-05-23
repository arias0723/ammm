"""
AMMM Benchmark Runner
=====================
Runs Greedy, Greedy+LS, GRASP, GRASP+LS on a list of instances
and produces the same CSV structure as InstanceGenerator/output/.

Usage: run from ammm-main/ directory:
    python run_benchmark.py
"""

import csv
import os
import re
import subprocess
import sys
import tempfile
import time
from statistics import mean, median, stdev

# ============================================================
#  CONFIGURATION  –  edit this section
# ============================================================

# Paths relative to ammm-main/
INSTANCES = [
    "InstanceGenerator/output/instances/s30_p80_instance_0.dat",
    "InstanceGenerator/output/instances/s45_p150_instance_0.dat",
    "InstanceGenerator/output/instances/s70_p300_instance_0.dat",
    "InstanceGenerator/output/instances/s70_p400_instance_0.dat",
    "InstanceGenerator/output/instances/s80_p500_instance_0.dat",
    "InstanceGenerator/output/instances/s85_p550_instance_0.dat",
    "InstanceGenerator/output/instances/s110_p500_instance_0.dat",
    "InstanceGenerator/output/instances/s100_p750_instance_0.dat",
]

NUM_RUNS             = 10
MAX_EXEC_TIME        = 60
GRASP_ALPHA          = 0.15
GRASP_MAX_ITERATIONS = 100
MIN_CUT              = "Karger"
LS_NEIGHBORHOOD      = "Both"
LS_POLICY            = "BestImprovement"
OUTPUT_DIR           = "benchmark_output"

# ============================================================
#  SOLVER CONFIGURATIONS
# ============================================================

SOLVERS = [
    {"label": "greedy",    "solver": "Greedy", "localSearch": False},
    {"label": "greedy_ls", "solver": "Greedy", "localSearch": True},
    {"label": "grasp",     "solver": "GRASP",  "localSearch": False},
    {"label": "grasp_ls",  "solver": "GRASP",  "localSearch": True},
]

# ============================================================
#  HELPERS
# ============================================================

ROOT        = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(ROOT, "Heuristics", "Main.py")


def make_temp_config(instance_rel, solver_cfg):
    """
    Write config using ONLY relative paths (forward slashes).
    The DATParser regex only matches [\w/.\-] — parentheses in absolute
    paths on Windows would break parsing.
    Both paths must be relative to the cwd (ammm-main/).
    """
    ls_flag = "True" if solver_cfg["localSearch"] else "False"
    # forward slashes, relative to ammm-main/
    inst_rel = instance_rel.replace("\\", "/")
    sol_rel  = OUTPUT_DIR + "/tmp.sol"

    lines = [
        f"inputDataFile = {inst_rel};",
        f"solutionFile = {sol_rel};",
        f"solver = {solver_cfg['solver']};",
        f"maxExecTime = {MAX_EXEC_TIME};",
        f"verbose = False;",
        f"minCut = {MIN_CUT};",
        f"maxExecIterations = {GRASP_MAX_ITERATIONS};",
        f"alpha = {GRASP_ALPHA};",
        f"localSearch = {ls_flag};",
        f"neighborhoodStrategy = {LS_NEIGHBORHOOD};",
        f"policy = {LS_POLICY};",
    ]
    # Write config into ammm-main/ so relative paths resolve correctly
    cfg_path = os.path.join(ROOT, "_tmp_benchmark_config.dat")
    with open(cfg_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return cfg_path


def run_once(instance_rel, solver_cfg):
    cfg_path = make_temp_config(instance_rel, solver_cfg)
    try:
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, MAIN_SCRIPT, "-c", cfg_path],
            capture_output=True,
            text=True,
            cwd=ROOT,   # <-- run from ammm-main/ so relative paths work
        )
        elapsed = time.time() - t0
        stdout  = result.stdout

        # Parse "z = <value>;"
        match = re.search(r"z\s*=\s*([\d.]+)", stdout)
        if match:
            val = float(match.group(1))
            if val < 1e15:
                return val, elapsed

        # Fallback: "Total cost: <int>"
        match2 = re.search(r"Total cost:\s*([\d]+)", stdout)
        if match2:
            return float(match2.group(1)), elapsed

        return None, elapsed

    except Exception as e:
        print(f"    [ERROR] {e}")
        return None, 0.0
    finally:
        if os.path.exists(cfg_path):
            os.remove(cfg_path)


def run_solver_on_instance(instance_rel, solver_cfg):
    objectives = []
    times      = []

    for run_idx in range(1, NUM_RUNS + 1):
        print(f"      run {run_idx}/{NUM_RUNS} ...", end=" ", flush=True)
        obj, t = run_once(instance_rel, solver_cfg)
        if obj is not None:
            objectives.append(obj)
            times.append(t)
            print(f"obj={obj:.2f}  t={t:.3f}s")
        else:
            print("no feasible solution")

    if not objectives:
        return None

    std = stdev(objectives) if len(objectives) > 1 else 0.0
    return {
        "instance":        os.path.basename(instance_rel),
        "mean_objective":  mean(objectives),
        "best_objective":  min(objectives),
        "worst_objective": max(objectives),
        "std_objective":   std,
        "min_time":        min(times),
        "max_time":        max(times),
        "median_time":     median(times),
        "mean_time":       mean(times),
        "feasible_runs":   len(objectives),
        "total_runs":      NUM_RUNS,
        "success_rate":    100.0 * len(objectives) / NUM_RUNS,
    }


def save_instance_csv(out_dir, stats):
    stem = os.path.splitext(stats["instance"])[0]
    path = os.path.join(out_dir, stem + ".csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "instance", "mean_objective", "best_objective", "worst_objective",
            "std_objective", "min_time", "max_time", "median_time", "mean_time",
            "feasible_runs", "total_runs", "success_rate",
        ])
        writer.writerow([
            stats["instance"],
            f"{stats['mean_objective']:.2f}",
            f"{stats['best_objective']:.2f}",
            f"{stats['worst_objective']:.2f}",
            f"{stats['std_objective']:.2f}",
            f"{stats['min_time']:.3f}",
            f"{stats['max_time']:.3f}",
            f"{stats['median_time']:.3f}",
            f"{stats['mean_time']:.3f}",
            stats["feasible_runs"],
            stats["total_runs"],
            f"{stats['success_rate']:.1f}",
        ])


def save_results_csv(out_dir, all_stats, solver_label):
    valid = [s for s in all_stats if s is not None]
    if not valid:
        return

    total_feasible = sum(s["feasible_runs"] for s in valid)
    total_runs     = sum(s["total_runs"]     for s in valid)
    overall_sr     = 100.0 * total_feasible / total_runs if total_runs else 0.0

    path = os.path.join(out_dir, "results.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "solver", "mean_objective", "best_objective", "worst_objective",
            "min_time", "max_time", "median_time", "mean_time",
            "success_rate", "num_instances", "feasible_runs", "total_runs",
        ])
        writer.writerow([
            solver_label,
            f"{mean(s['mean_objective'] for s in valid):.2f}",
            f"{min(s['best_objective']  for s in valid):.2f}",
            f"{max(s['worst_objective'] for s in valid):.2f}",
            f"{min(s['min_time']        for s in valid):.3f}",
            f"{max(s['max_time']        for s in valid):.3f}",
            f"{median([s['median_time'] for s in valid]):.3f}",
            f"{mean(s['mean_time']      for s in valid):.3f}",
            f"{overall_sr:.1f}",
            len(valid),
            total_feasible,
            total_runs,
        ])


# ============================================================
#  MAIN
# ============================================================

def main():
    os.makedirs(os.path.join(ROOT, OUTPUT_DIR), exist_ok=True)

    # Validate instances exist
    valid_instances = []
    for p in INSTANCES:
        full = os.path.join(ROOT, p)
        if not os.path.exists(full):
            print(f"[WARNING] Instance not found, skipping: {full}")
        else:
            valid_instances.append(p)   # keep relative path

    if not valid_instances:
        print("[ERROR] No valid instance files found.")
        sys.exit(1)

    print("=" * 70)
    print("AMMM BENCHMARK RUNNER")
    print("=" * 70)
    print(f"Instances  : {len(valid_instances)}")
    print(f"Solvers    : {[s['label'] for s in SOLVERS]}")
    print(f"Runs/combo : {NUM_RUNS}")
    print(f"Max time   : {MAX_EXEC_TIME}s per run")
    print("=" * 70)

    for solver_cfg in SOLVERS:
        label   = solver_cfg["label"]
        out_dir = os.path.join(ROOT, OUTPUT_DIR, label)
        os.makedirs(out_dir, exist_ok=True)

        print(f"\n{'='*70}")
        print(f"  SOLVER: {label.upper()}")
        print(f"{'='*70}")

        all_stats = []
        for inst_rel in valid_instances:
            print(f"\n  Instance: {os.path.basename(inst_rel)}")
            stats = run_solver_on_instance(inst_rel, solver_cfg)
            all_stats.append(stats)

            if stats:
                save_instance_csv(out_dir, stats)
                print(f"    => mean={stats['mean_objective']:.2f}  "
                      f"best={stats['best_objective']:.2f}  "
                      f"success={stats['success_rate']:.0f}%")
            else:
                print(f"    => no feasible solutions found")

        save_results_csv(out_dir, all_stats, label)
        print(f"\n  Results saved to: {out_dir}/")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print(f"Output: {os.path.join(ROOT, OUTPUT_DIR)}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
