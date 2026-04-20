# evals/eval_efficiency.py
import json
from pathlib import Path
from collections import Counter

# Import load_run_logs from the sibling module using absolute import
from eval_correctness import load_run_logs

# -------------------------------------------------------------------
# Check efficiency
# -------------------------------------------------------------------

def check_efficiency(run_log: dict) -> dict:
    task_id = run_log.get("task_id", "")
    min_tool_calls = run_log.get("metadata", {}).get("min_tool_calls", 0)
    messages = run_log.get("messages", [])
    actual_tool_calls = sum(1 for m in messages if m.get("role") == "tool")
    ratio = actual_tool_calls / (min_tool_calls or 1)
    flagged = ratio >= 2.0
    passed = actual_tool_calls <= (min_tool_calls * 2)
    return {
        "task_id": task_id,
        "passed": passed,
        "actual_tool_calls": actual_tool_calls,
        "min_tool_calls": min_tool_calls,
        "ratio": ratio,
        "flagged": flagged,
    }

# -------------------------------------------------------------------
# Run efficiency eval
# -------------------------------------------------------------------

def run_efficiency_eval(logs_dir: str = "data/run_logs") -> dict:
    logs = load_run_logs(logs_dir)
    results = [check_efficiency(log) for log in logs]
    total = len(results)
    passed = sum(r["passed"] for r in results)
    flagged_tasks = [r["task_id"] for r in results if r["flagged"]]
    avg_ratio = sum(r["ratio"] for r in results) / total if total else 0.0
    worst_task = max(results, key=lambda r: r["ratio"], default=None)
    return {
        "total": total,
        "passed": passed,
        "flagged": flagged_tasks,
        "average_ratio": avg_ratio,
        "worst_task": worst_task["task_id"] if worst_task else None,
        "results": results,
    }
