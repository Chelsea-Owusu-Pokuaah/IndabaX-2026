# evals/eval_correctness.py
import json
import re
from pathlib import Path

# -------------------------------------------------------------------
# Load logs
# -------------------------------------------------------------------

def load_run_logs(logs_dir: str = "data/run_logs") -> list[dict]:
    log_path = Path(logs_dir)
    if not log_path.is_dir():
        raise FileNotFoundError(f"Run logs not found at {logs_dir}/")
    logs = []
    for file in sorted(log_path.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            logs.append(json.load(f))
    return logs

# -------------------------------------------------------------------
# Check correctness
# -------------------------------------------------------------------

def check_correctness(run_log: dict) -> dict:
    task_id = run_log.get("task_id", "")
    expected_keywords = [kw.lower() for kw in run_log.get("expected_keywords", [])]
    final_answer = run_log.get("final_answer", "") or ""
    answer_lower = final_answer.lower()

    missing = [kw for kw in expected_keywords if kw not in answer_lower]
    keywords_found = not missing
    non_empty = bool(final_answer.strip())

    return {
        "task_id": task_id,
        "passed": keywords_found and non_empty,
        "checks": {
            "keywords_found": keywords_found,
            "missing_keywords": missing,
            "non_empty": non_empty,
        },
        "final_answer_preview": final_answer[:100],
    }

# -------------------------------------------------------------------
# Run correctness eval
# -------------------------------------------------------------------

def run_correctness_eval(logs_dir: str = "data/run_logs") -> dict:
    logs = load_run_logs(logs_dir)
    results = [check_correctness(log) for log in logs]
    total = len(results)
    passed = sum(r["passed"] for r in results)
    failed = total - passed
    pass_rate = passed / total if total else 0.0

    # Find most common missing keyword across failures
    from collections import Counter
    all_missing = [kw for r in results for kw in r["checks"]["missing_keywords"]]
    most_common_failure = Counter(all_missing).most_common(1)
    most_common_failure = most_common_failure[0][0] if most_common_failure else ""

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": results,
        "most_common_failure": most_common_failure,
    }