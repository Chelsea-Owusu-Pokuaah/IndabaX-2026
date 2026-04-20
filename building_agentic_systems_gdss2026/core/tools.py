import json
import tempfile
import subprocess
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests

TOOL_REGISTRY: dict[str, callable] = {}


def register_tool(func):
    """Decorator to register a tool in the TOOL_REGISTRY."""
    TOOL_REGISTRY[func.__name__] = func
    return func


@register_tool
def search_web(query: str, num_results: int = 5) -> list:
    """
    Search the web using DuckDuckGo's Instant Answer API.

    Args:
        query: Search query string
        num_results: Maximum number of results to return

    Returns:
        List of dicts with 'title', 'url', and 'snippet' keys
    """
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        results = []

        # Extract from RelatedTopics (main results)
        for topic in data.get('RelatedTopics', []):
            if len(results) >= num_results:
                break

            # Some topics are nested in sections
            if 'Topics' in topic:
                for subtopic in topic['Topics']:
                    if len(results) >= num_results:
                        break
                    if 'Text' in subtopic and 'FirstURL' in subtopic:
                        results.append({
                            'title': subtopic.get('Text', '').split(' - ')[0][:100],
                            'url': subtopic['FirstURL'],
                            'snippet': subtopic.get('Text', '')
                        })
            elif 'Text' in topic and 'FirstURL' in topic:
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0][:100],
                    'url': topic['FirstURL'],
                    'snippet': topic.get('Text', '')
                })

        # If no RelatedTopics, try Abstract
        if not results and data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Result'),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('Abstract', '')
            })

        print(f"Successfully found {len(results)} results")
        return results

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Parsing failed: {e}")
        return []


@register_tool
def read_file(path: str, start_line: int = 0, end_line: int | None = None) -> dict:
    """Read a file from the local filesystem and return its contents.

    Args:
        path: Relative or absolute path to the file.
        start_line: Line number to start reading from (0-indexed, default 0).
        end_line: Line number to stop reading at (exclusive). None means read to end.

    Returns:
        Dict with keys:
            - "path": str — the resolved path
            - "content": str — file contents
            - "total_lines": int — total number of lines in the file
            - "lines_returned": int — number of lines in this response
    """
    resolved_path = Path(path).resolve()

    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {"error": f"File not found: {path}", "path": str(resolved_path)}
    except UnicodeDecodeError:
        return {"error": "File is not valid UTF-8 text", "path": str(resolved_path)}

    total_lines = len(lines)
    sliced_lines = lines[start_line:end_line]
    content = "".join(sliced_lines)

    return {
        "path": str(resolved_path),
        "content": content,
        "total_lines": total_lines,
        "lines_returned": len(sliced_lines),
    }


@register_tool
def run_code(code: str, language: str = "python", timeout_seconds: int = 10) -> dict:
    """Execute a code snippet and return the output.

    Args:
        code: The code string to execute.
        language: Programming language. Currently only "python" is supported.
        timeout_seconds: Maximum execution time before timeout (default 10).

    Returns:
        Dict with keys:
            - "stdout": str — standard output from execution
            - "stderr": str — standard error output
            - "exit_code": int — 0 for success, non-zero for error
            - "timed_out": bool — True if execution exceeded timeout
    """
    # WARNING: This executes arbitrary code. Tutorial use only.
    stdout = ""
    stderr = ""
    exit_code = 1
    timed_out = False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "timed_out": timed_out,
    }


class DDGParser(HTMLParser):
    """HTML parser for DuckDuckGo search results."""

    def __init__(self, num_results: int = 5):
        super().__init__()
        self.num_results = num_results
        self.results = []
        self.in_title = False
        self.in_snippet = False
        self.current_title = ""
        self.current_url = ""
        self.current_snippet = ""
        self.current_class = ""
        self.result_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")

        # Title: <a class="result__a" href="...">
        if tag == "a" and "result__a" in class_name:
            self.in_title = True
            self.current_url = attrs_dict.get("href", "")
            self.current_title = ""
        elif tag == "a" and "result__url" in class_name:
            self.current_url = attrs_dict.get("href", "")

        # Snippet: <a class="result__snippet" or <div class="result__snippet">
        if tag in ("a", "div") and "result__snippet" in class_name:
            self.in_snippet = True
            self.current_snippet = ""

        self.current_class = class_name

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.in_title:
            # When we hit the end of title anchor, finalize the result
            if self.current_title and self.current_url:
                self.results.append({
                    "title": self.current_title,
                    "url": self.current_url,
                    "snippet": self.current_snippet,
                })
            self.in_title = False
            self.current_title = ""
            self.current_url = ""
        elif tag == "a" and self.in_snippet:
            self.in_snippet = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.current_title += data
        if self.in_snippet:
            self.current_snippet += data

    def feed(self, data: str) -> None:
        super().feed(data)
        # Limit results to num_results
        self.results = self.results[: self.num_results]


def dispatch_tool(tool_call: dict) -> str:
    """Dispatch a tool call from the LLM to the correct registered function.

    Args:
        tool_call: A tool call dict from the LLM response, with keys:
            - "id": str
            - "function": dict with "name" (str) and "arguments" (JSON string)

    Returns:
        JSON string of the tool's return value, or a JSON error dict.
    """
    tool_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])

    if tool_name not in TOOL_REGISTRY:
        return json.dumps({
            "error": f"Unknown tool: {tool_name}",
            "available_tools": list(TOOL_REGISTRY.keys())
        })

    try:
        result = TOOL_REGISTRY[tool_name](**arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": tool_name})


def get_tool_definitions(tool_names: list[str] | None = None) -> list[dict]:
    """Return tool definitions in OpenAI function-calling format.

    Args:
        tool_names: List of tool names to include. None means all tools.

    Returns:
        List of tool definition dicts in OpenAI format.
    """
    all_definitions = {}

    # search_web definition
    all_definitions["search_web"] = {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for the given query and return results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query string"},
                    "num_results": {"type": "integer", "description": "Number of results to return", "default": 5}
                },
                "required": ["query"]
            }
        }
    }

    # read_file definition
    all_definitions["read_file"] = {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the local filesystem and return its contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "start_line": {"type": "integer", "description": "Line to start from (0-indexed)", "default": 0},
                    "end_line": {"type": ["integer", "null"], "description": "Line to stop at (exclusive). Null for end of file.", "default": None}
                },
                "required": ["path"]
            }
        }
    }

    # run_code definition
    all_definitions["run_code"] = {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Execute a code snippet and return the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to execute"},
                    "language": {"type": "string", "description": "Programming language. Only 'python' supported.", "default": "python"},
                    "timeout_seconds": {"type": "integer", "description": "Max execution time in seconds", "default": 10}
                },
                "required": ["code"]
            }
        }
    }

    if tool_names is None:
        return list(all_definitions.values())

    return [all_definitions[name] for name in tool_names if name in all_definitions]


if __name__ == "__main__":
    # Test search_web
    print("Testing search_web...")
    results = search_web("python programming", num_results=5)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Snippet: {result['snippet'][:150]}...")

    # Test read_file
    print("\nTesting read_file...")
    contents = read_file("../requirements.txt")
    # print(f"Read {contents['lines_returned']} lines from {contents['path']}")
    print(f"Read {contents}")
    print(f"First 100 chars: {contents['content'][:100]}")

    # Test run_code
    print("\nTesting run_code...")
    result = run_code("print(4 + 2)")
    print(f"stdout: {result['stdout']!r}")
    print(f"stderr: {result['stderr']!r}")
    print(f"exit_code: {result['exit_code']}")
    print(f"timed_out: {result['timed_out']}")
