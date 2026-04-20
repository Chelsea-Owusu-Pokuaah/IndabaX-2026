"""Exercise 2A Agent - Tool Use Starting Point.

This is the starting point for Exercise 2A. Participants must complete the
run_agent function to enable tool calling and dispatching.

Tasks:
    1. Call call_llm and extract the message
    2. Check for tool calls and dispatch them
    3. Append tool results to messages
    4. If no tool calls, return the answer
"""

from core.llm import call_llm, extract_message, has_tool_calls, extract_tool_calls
from core.tools import dispatch_tool, get_tool_definitions


def run_agent(user_message: str) -> str:
    """Run the agent loop with tool use enabled.

    Args:
        user_message: The user's prompt.

    Returns:
        The final answer from the model.
    """
    # System prompt
    system_prompt = "You are a helpful research assistant that can use tools."

    # Initialize messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # Get tool definitions
    tools = get_tool_definitions()

    # TODO: Task 1 — Implement the agent loop
    # Hint: Follow the pattern from ex1/agent.py but handle tool calls
    for i in range(10):
        # TODO: Task 1 — call call_llm and extract the message

        # TODO: Task 1 — check for tool calls and dispatch them

        # TODO: Task 1 — append tool results to messages

        # TODO: Task 1 — if no tool calls, return the answer

        pass

    return ""  # Return final answer here


if __name__ == "__main__":
    # Test prompts for Exercise 2A
    # Test 1 (needs search_web): "Who won the 2024 Nobel Prize in Physics?"
    # Test 2 (needs search_web): "What is the current Python version?"
    # Test 3 (needs read_file): "What is in the requirements.txt file?"
    # Test 4 (needs read_file): "Read the first 5 lines of core/llm.py"
    # Test 5 (no tool needed): "What is the capital of France?"

    print("Exercise 2A Agent - Tool Use")
    print("=" * 60)

    # Uncomment and test each prompt:
    # prompt = "Who won the 2024 Nobel Prize in Physics?"
    # prompt = "What is the current Python version?"
    # prompt = "What is in the requirements.txt file?"
    # prompt = "Read the first 5 lines of core/llm.py"
    # prompt = "What is the capital of France?"

    # print(f"User: {prompt}")
    # result = run_agent(prompt)
    # print(f"Answer: {result}")