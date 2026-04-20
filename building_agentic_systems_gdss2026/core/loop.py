import json
import logging
from typing import Any, Callable
from dataclasses import dataclass, field

from core.llm import call_llm, extract_message, has_tool_calls, extract_tool_calls
from core.tools import dispatch_tool, get_tool_definitions

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the agent loop.

    Attributes:
        system_prompt: The system prompt to initialize the conversation.
        max_iterations: Maximum number of loop iterations before stopping.
        tools: List of tool names to enable. None means all registered tools.
        temperature: LLM sampling temperature.
        max_tokens: Maximum tokens in LLM responses.
        verbose: If True, log each iteration's actions.
    """
    system_prompt: str = "You are a helpful research assistant."
    max_iterations: int = 10
    tools: list[str] | None = None      # None means all registered tools
    temperature: float = 0.2
    max_tokens: int = 2048
    verbose: bool = False


def run_agent(
    user_message: str,
    config: AgentConfig | None = None,
) -> dict:
    """Run the agent loop and return the final result.

    Args:
        user_message: The initial user input message.
        config: Optional AgentConfig for customization.

    Returns:
        Dict with keys:
            - "answer": str — final text response from the model
            - "iterations": int — how many loop iterations ran
            - "tool_calls_made": int — total tool calls across all iterations
            - "tokens_used": int — approximate total tokens (sum across all LLM calls)
            - "history": list[dict] — full message history
            - "stopped_by": str — "model" | "max_iterations" | "error"
    """
    if config is None:
        config = AgentConfig()

    # 1. Build initial messages
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": user_message},
    ]

    # 2. Get tool definitions
    tools = get_tool_definitions(config.tools)
    tool_defs = tools if tools else None

    result = {
        "answer": "",
        "iterations": 0,
        "tool_calls_made": 0,
        "tokens_used": 0,
        "history": [],
        "stopped_by": "max_iterations",
    }

    try:
        # 3. Main loop
        for iteration in range(config.max_iterations):
            result["iterations"] = iteration + 1

            # ── PERCEIVE ─────────────────────────────
            current_messages = messages

            # ── REASON ───────────────────────────────
            response = call_llm(
                messages=current_messages,
                tools=tool_defs,
                tool_choice="auto",
                max_tokens=config.max_tokens,
                temperature=config.temperature,
            )

            # Update token count
            result["tokens_used"] += response.get("usage", {}).get("total_tokens", 0)

            # Extract the response message
            message = extract_message(response)

            # Append response to history
            messages.append(message)
            result["history"] = messages.copy()

            if config.verbose:
                if has_tool_calls(message):
                    logger.info(f"[Step {iteration + 1}] LLM called {len(extract_tool_calls(message))} tools")
                else:
                    logger.info(f"[Step {iteration + 1}] LLM provided final answer")

            # ── ACT + OBSERVE ────────────────────────
            if has_tool_calls(message):
                # Act: dispatch each tool call
                for tool_call in extract_tool_calls(message):
                    result["tool_calls_made"] += 1
                    tool_result = dispatch_tool(tool_call)

                    # Observe: append tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result,
                    })
            else:
                # No tool calls: model is done
                result["answer"] = message.get("content", "")
                result["stopped_by"] = "model"
                break

    except Exception as e:
        logger.exception("Agent loop error")
        result["answer"] = f"Error: {str(e)}"
        result["stopped_by"] = "error"

    return result
