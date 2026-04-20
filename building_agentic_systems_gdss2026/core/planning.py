"""Planning prompts and utilities for prompt-based planning.

This module contains system prompt templates and helper functions
for extracting plan and scratchpad blocks from LLM responses.
"""

import re

# System prompts for different planning approaches

SYSTEM_PROMPT_BASELINE = """You are a helpful research assistant. Answer the user's question using the tools
available to you. Be accurate and cite your sources when using search results."""

SYSTEM_PROMPT_WITH_PLAN = """You are a helpful research assistant. Before taking any action, you must output
a <plan> block that lists the exact steps you will take to answer the question.
Format your plan as:

<plan>
1. [step]
2. [step]
...
</plan>

After writing the plan, execute it step by step using the available tools.
Be accurate and cite your sources."""

SYSTEM_PROMPT_WITH_SCRATCHPAD = """You are a helpful research assistant. You have access to a private scratchpad
for reasoning. Before each action, think through your reasoning in a <scratchpad>
block. The scratchpad is not shown to the user — use it freely.

Format:
<scratchpad>
[your private reasoning here]
</scratchpad>

Then take your action. Be accurate and cite your sources."""

SYSTEM_PROMPT_REACT = """You are a helpful research assistant using the ReAct reasoning pattern.
For every step, alternate between:

Thought: [your reasoning about what to do next]
Action: [the tool call you will make]
Observation: [what you learned from the tool — filled in automatically]

Continue this pattern until you have enough information to answer.
Then write:

Final Answer: [your complete response]"""


def extract_plan(response_text: str) -> str | None:
    """Extract content from <plan>...</plan> blocks.

    Args:
        response_text: The LLM response text.

    Returns:
        The plan content stripped of whitespace, or None if not found.
    """
    match = re.search(r'<plan>(.*?)</plan>', response_text, re.DOTALL)
    print("match", match)
    if match:
        return match.group(1).strip()
    return None


def extract_scratchpad(response_text: str) -> str | None:
    """Extract content from <scratchpad>...</scratchpad> blocks.

    Args:
        response_text: The LLM response text.

    Returns:
        The scratchpad content stripped of whitespace, or None if not found.
    """
    match = re.search(r'<scratchpad>(.*?)</scratchpad>', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def count_plan_steps(plan_text: str) -> int:
    """Count the number of numbered steps in a plan string.

    Args:
        plan_text: The plan text to analyze.

    Returns:
        Number of lines matching the pattern "digit." as steps.
    """
    if not plan_text:
        return 0

    # Match lines starting with digits followed by a period
    pattern = r'^\d+\.'
    count = 0
    for line in plan_text.split('\n'):
        if re.match(pattern, line.strip()):
            count += 1
    return count