# evals/run_evals.py

# Import the eval functions
from eval_correctness import run_correctness_eval
from eval_efficiency import run_efficiency_eval
from eval_safety import run_safety_eval

# --------------------------
# Run all evals and print report
# --------------------------

def run_all_evals(logs_dir: str = "data/run_logs") -> None:
    try:
        correctness = run_correctness_eval(logs_dir)
        efficiency = run_efficiency_eval(logs_dir)
        safety = run_safety_eval(logs_dir)
    except FileNotFoundError as e:
        print(str(e))
        return

    print("═══════════════════════════════════════")
    print(" EVAL RESULTS — Agentic Systems Tutorial")
    print("═══════════════════════════════════════")

    # Correctness
    print(f"[CORRECTNESS]  Passed: {correctness['passed']}/{correctness['total']}  ({correctness['pass_rate']*100:.1f}%)")
    print(f"  Most common failure: missing keyword \"{correctness['most_common_failure']}\"")
    print()

    # Efficiency
    flagged_str = f"Flagged ({len(efficiency['flagged'])}x+ tool calls): {', '.join(efficiency['flagged'])}" if efficiency['flagged'] else ""
    print(f"[EFFICIENCY]   Passed: {efficiency['passed']}/{efficiency['total']}  ({(efficiency['passed']/efficiency['total']*100):.1f}%)")
    if flagged_str:
        print(f"  {flagged_str}")
    print(f"  Average ratio: {efficiency['average_ratio']:.1f}x")
    print()

    # Safety
    print(f"[SAFETY]       Passed: {safety['passed']}/{safety['total']} ({(safety['passed']/safety['total']*100):.1f}%)")
    print(f"  Total violations: {safety['total_violations']}")
    print()

    print("─────────────────────────────────────────")
    total_checks = correctness['total'] + efficiency['total'] + safety['total']
    total_passes = correctness['passed'] + efficiency['passed'] + safety['passed']
    print(f"Overall: {total_passes}/{total_checks} checks passed")


if __name__ == "__main__":
    run_all_evals()