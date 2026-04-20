"""Exercise 1 Agent - Observe and understand the agent loop.

This is a complete, working agent that participants observe, then break,
then repair. It implements the full perceive → reason → act → observe cycle.
"""

from core.llm import call_llm, extract_message, has_tool_calls, extract_tool_calls
from core.tools import dispatch_tool, get_tool_definitions, TOOL_REGISTRY


def run_agent(user_message: str, max_iterations: int = 10) -> dict:
    """Run the agent loop on a user message.

    Args:
        user_message: The initial prompt from the user.
        max_iterations: Maximum iterations before forced stop.

    Returns:
        Dict with answer, iterations, tool_calls_made, tokens_used, history, stopped_by.
    """
    # System prompt
    system_prompt = "You are a helpful research assistant."

    # Initialize messages with system and user
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # Get all registered tools
    tools = get_tool_definitions()
    tool_defs = tools if tools else None

    result = {
        "answer": "",
        "iterations": 0,
        "tool_calls_made": 0,
        "tokens_used": 0,
        "history": [],
        "stopped_by": "max_iterations",
    }

    llm_calls = 0
    tool_calls_so_far = 0

    # ─────────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────────
    for iteration in range(max_iterations):
        result["iterations"] = iteration + 1
        llm_calls += 1

        # ── PERCEIVE ─────────────────────────────
        # The agent perceives the current message history
        print(f"[Step {iteration + 1}] LLM call #{llm_calls}, tool calls so far: {tool_calls_so_far}, tokens so far: {result['tokens_used']}")

        # ── REASON ───────────────────────────────
        # Call the LLM with current messages and tools
        response = call_llm(
            messages=messages,
            tools=tool_defs,
            tool_choice="auto",
        )

        # Count tokens
        result["tokens_used"] += response.get("usage", {}).get("total_tokens", 0)

        # Extract the message from response
        message = extract_message(response)

        # Append response to history
        messages.append(message)
        result["history"] = messages.copy()

        # ── ACT ───────────────────────────────
        # Check if model wants to call tools
        if has_tool_calls(message):
            # Dispatch each tool call
            for tool_call in extract_tool_calls(message):
                tool_calls_so_far += 1
                result["tool_calls_made"] += 1
                tool_result = dispatch_tool(tool_call)

                # Append tool result to history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                })
            print(f"  → Called tools, now {tool_calls_so_far} total tool calls")
        else:
            # ── STOP CHECK ──────────────────────────
            # No tool calls - model is done
            result["answer"] = message.get("content", "")
            result["stopped_by"] = "model"
            print(f"  → Model provided final answer")
            break

    return result


if __name__ == "__main__":
    prompt = "What year was Python first released, and who created it?"
    print(f"User: {prompt}")
    print("-" * 60)

    result = run_agent(prompt)

    print("-" * 60)
    print(f"Answer: {result['answer']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Tool calls: {result['tool_calls_made']}")
    print(f"Tokens used: {result['tokens_used']}")
    print(f"Stopped by: {result['stopped_by']}")