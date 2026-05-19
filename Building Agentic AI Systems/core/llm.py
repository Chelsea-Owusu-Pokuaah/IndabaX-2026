import os
import json
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)


def call_llm(
    messages: list[dict],
    tools: list[dict] | None = None,
    tool_choice: str = "auto",
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> dict:
    """Call the configured LLM and return the raw API response as a dict.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        tools: Optional list of tool definitions in OpenAI function-calling format.
        tool_choice: How the model selects tools. Default "auto".
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature.

    Returns:
        Raw API response dict. Key path to content:
        response["choices"][0]["message"] — contains 'content' and/or 'tool_calls'.
    """
    model = os.getenv("LLM_MODEL", "qwen3-coder")

    if tools:
        response = _client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        response = _client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    return response.model_dump()


def extract_message(response: dict) -> dict:
    """Extract the message dict from an LLM response."""
    return response["choices"][0]["message"]


def has_tool_calls(message: dict) -> bool:
    """Check if a message contains tool calls."""
    tool_calls = message.get("tool_calls")
    return isinstance(tool_calls, list) and len(tool_calls) > 0


def extract_tool_calls(message: dict) -> list[dict]:
    """Extract tool calls from a message."""
    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list) and len(tool_calls) > 0:
        return tool_calls
    return []


if __name__ == "__main__":
    test_messages = [{"role": "user", "content": "Say hello in exactly 5 words."}]
    response = call_llm(test_messages)
    message = extract_message(response)
    print(message.get("content", ""))