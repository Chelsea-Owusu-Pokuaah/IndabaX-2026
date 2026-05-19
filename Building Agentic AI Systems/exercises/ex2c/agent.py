"""Exercise 2C Agent - Planning Starting Point.

This is the starting point for Exercise 2C. Participants must implement
different planning approaches using the system prompts from core.planning.

Tasks:
    1. Import and use SYSTEM_PROMPT_BASELINE
    2. Run with SYSTEM_PROMPT_WITH_PLAN
    3. Run with SYSTEM_PROMPT_WITH_SCRATCHPAD
    4. (Stretch) Swap search_web for run_code
"""

from core.llm import call_llm, extract_message, has_tool_calls, extract_tool_calls
from core.tools import dispatch_tool, get_tool_definitions
from core.memory import RollingMemory
from core.planning import (
    SYSTEM_PROMPT_BASELINE,
    SYSTEM_PROMPT_WITH_PLAN,
    SYSTEM_PROMPT_WITH_SCRATCHPAD,
    SYSTEM_PROMPT_REACT,
    extract_plan,
    count_plan_steps,
)

# Memory instance for tracking conversation history
memory = RollingMemory()

# System prompt
system_prompt = "You are a helpful research assistant that can use tools."

# User prompt for the first turn
user_message = ""


def run_agent(user_message: str, system_prompt: str = SYSTEM_PROMPT_BASELINE) -> str:
    """Run the agent loop with tool use and memory enabled.

    Args:
        user_message: The user's prompt.
        system_prompt: The system prompt to use (baseline, plan, scratchpad, etc.)

    Returns:
        The final answer from the model.
    """
    # Initialize messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # Get tool definitions
    tools = get_tool_definitions()

    for i in range(10):
        # Inject memory
        messages = memory.inject(messages)

        # Call LLM and extract message
        response = call_llm(messages=messages, tools=tools if tools else None)
        message = extract_message(response)

        # Append response to history
        messages.append(message)

        # Log plan detection if present
        message_content = message.get("content", "")
        if message_content is not None:
            plan = extract_plan(message_content)
            if plan:
                plan_steps = count_plan_steps(plan)
                print(f"[Plan detected] {plan_steps} steps")

        # Check for tool calls
        if has_tool_calls(message):
            for tool_call in extract_tool_calls(message):
                tool_result = dispatch_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                })
        else:
            # No more tool calls - we're done
            answer = message.get("content", "")
            # Update memory
            memory.update(user_message, answer)
            return answer

    return ""


if __name__ == "__main__":
    QUERY = "Find the founding year of OpenAI, Anthropic, and DeepMind. Tell me which is oldest and by how many years."

    print("Exercise 2C Agent - Planning")
    print("=" * 60)

    # # Run 1: No planning
    # print("\n--- Run 1: Baseline (no planning) ---")
    # result_baseline = run_agent(QUERY, system_prompt=SYSTEM_PROMPT_BASELINE)
    # print(f"Answer: {result_baseline}")

    # # TODO: Task 2 — Run 2: With plan block
    print("\n--- Run 2: With plan block ---")
    result_plan = run_agent(QUERY, system_prompt=SYSTEM_PROMPT_WITH_PLAN)
    print(f"Answer: {result_plan}")

    # TODO: Task 3 — Run 3: With scratchpad
    # print("\n--- Run 3: With scratchpad ---")
    # result_scratchpad = run_agent(QUERY, system_prompt=SYSTEM_PROMPT_WITH_SCRATCHPAD)
    # print(f"Answer: {result_scratchpad}")

    # TODO: Task 4 (stretch) — swap search_web for run_code and run the math version
