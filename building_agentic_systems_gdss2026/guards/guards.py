import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

IRREVERSIBLE_ACTIONS: list[str] = [
    "delete", "remove", "drop", "truncate", "wipe", "format",
    "overwrite", "destroy", "purge", "erase"
]


class GuardViolation(Exception):
    """Exception raised when a guard blocks an action."""

    def __init__(self, guard_name: str, reason: str, context: dict | None = None):
        self.guard_name = guard_name
        self.reason = reason
        self.context = context or {}
        super().__init__(f"[{guard_name}] {reason}")


class AgentGuards:
    """Security guards for agent operations.

    Four guards protect against:
    1. Infinite loop (iteration limit)
    2. Unknown tool calls (allow-list)
    3. Malformed arguments (type validation)
    4. Irreversible actions (confirmation required)
    """

    def __init__(
        self,
        max_iterations: int = 10,
        allowed_tools: list[str] | None = None,
        require_confirmation_for: list[str] | None = None,
        confirmation_callback: Callable[[str, dict], bool] | None = None,
    ):
        """Initialize the guards.

        Args:
            max_iterations: Max loop iterations before GuardViolation.
            allowed_tools: If set, only these tool names are permitted.
            require_confirmation_for: Action keywords requiring confirmation.
            confirmation_callback: Function (action_description, context) -> bool.
        """
        self.max_iterations = max_iterations
        self.allowed_tools = allowed_tools
        self.require_confirmation_for = require_confirmation_for or []
        self.confirmation_callback = confirmation_callback

    def check_iteration(self, current_iteration: int) -> None:
        """Guard 1: Prevent infinite loops.

        Args:
            current_iteration: The current loop iteration number.

        Raises:
            GuardViolation: If max iterations reached.
        """
        if current_iteration >= self.max_iterations:
            raise GuardViolation(
                "iteration_limit",
                f"Reached max iterations ({self.max_iterations})",
                {"iteration": current_iteration, "max": self.max_iterations}
            )

    def check_tool_call(self, tool_name: str, arguments: dict) -> None:
        """Guard 2 + 3: Tool allow-list and argument validation.

        Args:
            tool_name: Name of the tool being called.
            arguments: Arguments passed to the tool.

        Raises:
            GuardViolation: If tool not allowed or arguments malformed.
        """
        # Guard 2: Check if tool is allowed
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            raise GuardViolation(
                "tool_not_allowed",
                f"Tool '{tool_name}' is not in the allowed list",
                {"tool": tool_name, "allowed": self.allowed_tools}
            )

        # Guard 3: Check arguments is a dict
        if not isinstance(arguments, dict):
            raise GuardViolation(
                "malformed_arguments",
                "Tool arguments must be a dict",
                {"tool": tool_name, "received": str(arguments)}
            )

    def check_irreversible(self, tool_name: str, arguments: dict) -> None:
        """Guard 4: Require confirmation for irreversible actions.

        Args:
            tool_name: Name of the tool being called.
            arguments: Arguments passed to the tool.

        Raises:
            GuardViolation: If irreversible action without confirmation.
        """
        action_description = f"{tool_name}({json.dumps(arguments)})"

        # Check if any irreversible keyword is present
        action_lower = action_description.lower()
        should_require = any(
            kw in action_lower for kw in IRREVERSIBLE_ACTIONS
        )
        should_require = should_require or any(
            kw in action_lower for kw in self.require_confirmation_for
        )

        if should_require:
            if self.confirmation_callback is not None:
                if not self.confirmation_callback(action_description, {"tool": tool_name, "arguments": arguments}):
                    raise GuardViolation(
                        "confirmation_denied",
                        f"Action requires confirmation: {action_description}",
                        {"action": action_description}
                    )
            else:
                raise GuardViolation(
                    "irreversible_action_blocked",
                    f"Action requires confirmation: {action_description}",
                    {"action": action_description}
                )

    def wrap_dispatch(self, tool_call: dict, dispatch_fn: Callable) -> str:
        """Run all guards before dispatching a tool call.

        Args:
            tool_call: The tool call dict from the LLM.
            dispatch_fn: The dispatch_tool function to call if guards pass.

        Returns:
            The result string from dispatch_fn.

        Raises:
            GuardViolation: If any guard blocks the action.
        """
        tool_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        # Run all guards
        self.check_tool_call(tool_name, arguments)
        self.check_irreversible(tool_name, arguments)

        # Dispatch
        return dispatch_fn(tool_call)