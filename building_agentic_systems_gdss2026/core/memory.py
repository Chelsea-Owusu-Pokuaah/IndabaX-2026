import json
from core.llm import call_llm


class RollingMemory:
    """Simple in-context memory that compresses past turns into a summary."""

    def __init__(self, max_summary_tokens: int = 300, model_summarizes: bool = True):
        """Initialize the rolling memory.

        Args:
            max_summary_tokens: Target token budget for the summary (approximate).
            model_summarizes: If True, use the LLM to compress; otherwise use simple truncation.
        """
        self.max_summary_tokens = max_summary_tokens
        self.model_summarizes = model_summarizes
        self.summary: str = ""
        self.turn_count: int = 0

    def update(self, user_message: str, assistant_response: str) -> None:
        """Update memory with a new conversation turn.

        Args:
            user_message: The user's message.
            assistant_response: The assistant's response.
        """
        self.turn_count += 1

        new_turn = f"User: {user_message}\nAssistant: {assistant_response}"

        if self.model_summarizes:
            # Use LLM to summarize
            prompt = f"""You are a memory compressor. Given the current memory summary and a new conversation turn,
                    produce an updated summary that captures all key facts, decisions, and context.
                    Keep it under {self.max_summary_tokens} tokens. Be dense — no filler phrases.
                    
                    Current summary:
                    {self.summary or "(empty)"}
                    
                    New turn:
                    {new_turn}
                    
                    Updated summary:"""

            response = call_llm([
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please provide the updated summary:"},
            ])
            self.summary = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            # Simple truncation
            if self.summary:
                self.summary += f"\n\n{new_turn}"
            else:
                self.summary = new_turn

            # Truncate if too long (approx 4 chars per token)
            max_chars = self.max_summary_tokens * 4
            if len(self.summary) > max_chars:
                self.summary = self.summary[-max_chars:]


    def inject(self, messages: list[dict]) -> list[dict]:
        """Inject memory summary into the messages list.

        Args:
            messages: The messages list to inject into.

        Returns:
            New messages list with memory injected.
        """
        if not self.summary:
            return messages

        memory_message = {"role": "system", "content": f"[Memory from previous turns]\n{self.summary}"}

        # Find first user message or insert at position 0
        for i, msg in enumerate(messages):
            if msg.get("role") == "system" and i < len(messages) - 1:
                # Insert after first system message if there's more content
                if i < len(messages) - 1 and messages[i + 1].get("role") != "system":
                    new_messages = messages.copy()
                    new_messages.insert(i + 1, memory_message)
                    return new_messages

        # Insert at position 0 if no system message found or other conditions
        new_messages = messages.copy()
        new_messages.insert(0, memory_message)
        return new_messages

    def reset(self) -> None:
        """Clear memory and reset turn count."""
        self.summary = ""
        self.turn_count = 0

    def __repr__(self) -> str:
        return f"RollingMemory(turns={self.turn_count}, summary_len={len(self.summary)}chars)"


class EpisodicMemory:
    """Simple persistent memory using a JSON file.

    This is a stub — participants extend it in stretch exercises.
    """

    def __init__(self, filepath: str = "memory_store.json"):
        """Initialize the episodic memory store.

        Args:
            filepath: Path to the JSON file for persistence.
        """
        self.filepath = filepath

    def save(self, key: str, value: any) -> None:
        """Save a value to the memory store.

        Args:
            key: The key to save under.
            value: The value to serialize and store.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[key] = value

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, key: str, default: any = None) -> any:
        """Load a value from the memory store.

        Args:
            key: The key to load.
            default: Value to return if key not found.

        Returns:
            The stored value or default.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(key, default)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def list_keys(self) -> list[str]:
        """Return all keys in the store."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return []