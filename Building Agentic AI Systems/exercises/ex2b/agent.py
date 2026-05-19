"""Exercise 2B Agent - With Memory Starting Point.

This is the starting point for Exercise 2B. Participants must add memory
functionality to the working tool-use agent from Exercise 2A.

Tasks:
    1. Call memory.inject(messages) at the start of each loop iteration
    2. Call memory.update(user_message, answer) at the end of each turn
"""

from core.llm import call_llm, extract_message, has_tool_calls, extract_tool_calls
from core.tools import dispatch_tool, get_tool_definitions
from core.memory import RollingMemory

# Memory instance for tracking conversation history
memory = RollingMemory()

# System prompt
system_prompt = "You are a helpful research assistant that can use tools."

# User prompt for the first turn
user_message = ""


def run_agent(user_message: str) -> str:
    """Run the agent loop with tool use and memory enabled.

    Args:
        user_message: The user's prompt.

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
        # TODO: Task 2 — call memory.inject(messages) here

        # Call LLM and extract message
        response = call_llm(messages=messages, tools=tools if tools else None)
        message = extract_message(response)

        # Append response to history
        messages.append(message)

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
            # TODO: Task 2 — call memory.update(user_message, answer) here
            return answer

    return ""


if __name__ == "__main__":
    # Turn 1: Ask "What is the speed of light?"
    # Turn 2: Ask "What would travel at that speed from Earth to the Moon take?"

    print("Exercise 2B Agent - With Memory")
    print("=" * 60)

    # Turn 1
    turn1_prompt = "What is the speed of light?"
    print(f"Turn 1 User: {turn1_prompt}")
    answer1 = run_agent(turn1_prompt)
    print(f"Turn 1 Answer: {answer1}")
    print()

    # Turn 2 - should remember the speed of light from Turn 1
    turn2_prompt = "What would travel at that speed from Earth to the Moon take?"
    print(f"Turn 2 User: {turn2_prompt}")
    answer2 = run_agent(turn2_prompt)
    print(f"Turn 2 Answer: {answer2}")