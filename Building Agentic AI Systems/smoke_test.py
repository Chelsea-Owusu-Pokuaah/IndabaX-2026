#!/usr/bin/env python3
"""Smoke test for the Agentic Systems tutorial.

The script performs a series of quick checks and prints a concise summary.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Use ASCII for summary symbols to avoid encoding issues on Windows
PASS_SYMBOL = "+"
FAIL_SYMBOL = "-"

# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------

def print_ok(msg: str) -> None:
    print(f"[OK] {msg}")


def print_fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


# -------------------------------------------------------------
# Check 1 – Python version
# -------------------------------------------------------------
all_passed = True

try:
    if sys.version_info >= (3, 11):
        print_ok("Python 3.11+")
    else:
        print_fail(f"Python version is {sys.version_info.major}.{sys.version_info.minor} — need 3.11+")
        all_passed = False
except Exception as e:
    print_fail(f"Python version check failed: {e}")
    all_passed = False

# -------------------------------------------------------------
# Check 2 – Dependencies importable
# -------------------------------------------------------------
packages = ["openai", "numpy", "dotenv", "tiktoken"]
for pkg in packages:
    try:
        __import__(pkg)
        print_ok(f"{pkg}")
    except Exception:
        print_fail(f"{pkg} not installed — run: pip install {pkg}")
        all_passed = False

# -------------------------------------------------------------
# Check 3 – .env file exists
# -------------------------------------------------------------
root_dir = Path(__file__).resolve().parent
env_file = root_dir / ".env"
if env_file.is_file():
    print_ok(".env found")
else:
    print("[WARN] .env not found — copy .env.example to .env and fill in values")
    # Do not fail; let LLM check catch real error

# -------------------------------------------------------------
# Check 4 – Environment variables set
# -------------------------------------------------------------
missing_vars = []
for var in ["LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"]:
    if not os.getenv(var):
        missing_vars.append(var)
if missing_vars:
    print_fail(f"missing: {', '.join(missing_vars)}")
    all_passed = False
else:
    print_ok("environment variables set")

# -------------------------------------------------------------
# Check 5 – LLM reachable
# -------------------------------------------------------------
llm_ok = False
try:
    from core.llm import call_llm
    # Call with timeout
    try:
        response = call_llm([
            {"role": "user", "content": "Reply with the single word: ready"}
        ], max_tokens=10, temperature=0)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if "ready" in content.lower():
            print_ok("LLM reachable — model responded")
            llm_ok = True
        else:
            print_fail("LLM did not respond with 'ready'")
    except Exception as e:
        print_fail(f"LLM not reachable — {e}")
except Exception as e:
    print_fail(f"LLM import failed — {e}")

all_passed = all_passed and llm_ok

# -------------------------------------------------------------
# Check 6 – Tools importable
# -------------------------------------------------------------
try:
    from core.tools import dispatch_tool, get_tool_definitions
    defs = get_tool_definitions()
    if len(defs) == 3:
        print_ok("3 tools registered")
    else:
        print_fail(f"tools: expected 3, got {len(defs)}")
        all_passed = False
except Exception as e:
    print_fail(f"tools import failed — {e}")
    all_passed = False

# -------------------------------------------------------------
# Check 7 – Data files present
# -------------------------------------------------------------
docs_dir = root_dir / "data" / "documents"
logs_dir = root_dir / "data" / "run_logs"

try:
    txt_files = list(docs_dir.glob("*.txt"))
    if len(txt_files) >= 20:
        print_ok("20+ documents found")
    else:
        print_fail(f"documents: {len(txt_files)} files found, need at least 20")
        all_passed = False
except Exception as e:
    print_fail(f"documents check failed: {e}")
    all_passed = False

try:
    json_files = list(logs_dir.glob("*.json"))
    if len(json_files) >= 10:
        print_ok("10+ run logs found")
    else:
        print_fail(f"run logs: {len(json_files)} files found, need at least 10")
        all_passed = False
except Exception as e:
    print_fail(f"run logs check failed: {e}")
    all_passed = False

# -------------------------------------------------------------
# Final summary
# -------------------------------------------------------------
print("\n")
if all_passed:
    print(f"{PASS_SYMBOL} ready")
    sys.exit(0)
else:
    print(f"{FAIL_SYMBOL} setup incomplete — fix the [FAIL] items above before the tutorial")
    sys.exit(1)
