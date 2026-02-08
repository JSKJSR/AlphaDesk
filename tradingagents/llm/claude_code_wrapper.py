"""
Claude Code CLI and Anthropic API Wrapper for LangChain

This module provides a LangChain-compatible ChatModel that supports:
1. Claude Code CLI (use your Claude Pro subscription)
2. Anthropic API (use your API key for cloud deployment)
"""

import subprocess
import json
import re
import os
from typing import Any, List, Optional, Iterator, Sequence, Union
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessageChunk,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import Field


class ClaudeCodeChat(BaseChatModel):
    """
    A LangChain ChatModel that uses Claude Code CLI as the backend.

    This allows using your Claude Pro subscription instead of paying for API access.

    Requirements:
        - Claude Code CLI must be installed and authenticated
        - Install: npm install -g @anthropic-ai/claude-code
        - Auth: Run 'claude' once and follow prompts to authenticate

    Usage:
        from tradingagents.llm.claude_code_wrapper import ClaudeCodeChat

        llm = ClaudeCodeChat()
        response = llm.invoke("Hello, how are you?")
    """

    model_name: str = Field(default="claude-code", description="Model identifier")
    timeout: int = Field(default=300, description="Timeout in seconds for CLI calls")
    max_turns: int = Field(default=10, description="Max conversation turns for multi-step tasks")
    bound_tools: List[Any] = Field(default_factory=list, description="Bound tools")

    @property
    def _llm_type(self) -> str:
        return "claude-code"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name}

    def bind_tools(
        self,
        tools: Sequence[Union[dict, type, callable, BaseTool]],
        **kwargs: Any,
    ) -> "ClaudeCodeChat":
        """Bind tools to the model for function calling."""
        # Create a new instance with tools bound
        new_instance = ClaudeCodeChat(
            model_name=self.model_name,
            timeout=self.timeout,
            max_turns=self.max_turns,
            bound_tools=list(tools),
        )
        return new_instance

    def _format_tools_for_prompt(self) -> str:
        """Format bound tools as a string for the prompt."""
        if not self.bound_tools:
            return ""

        tool_descriptions = []
        for tool in self.bound_tools:
            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                # It's a BaseTool or similar
                name = tool.name
                desc = tool.description
                # Get args schema if available
                if hasattr(tool, 'args_schema') and tool.args_schema:
                    schema = tool.args_schema.schema()
                    args_desc = json.dumps(schema.get('properties', {}), indent=2)
                elif hasattr(tool, 'args'):
                    args_desc = str(tool.args)
                else:
                    args_desc = "No arguments"
                tool_descriptions.append(f"- {name}: {desc}\n  Arguments: {args_desc}")
            elif isinstance(tool, dict):
                name = tool.get('name', 'unknown')
                desc = tool.get('description', 'No description')
                tool_descriptions.append(f"- {name}: {desc}")
            elif callable(tool):
                name = getattr(tool, '__name__', 'unknown')
                desc = getattr(tool, '__doc__', 'No description') or 'No description'
                tool_descriptions.append(f"- {name}: {desc}")

        return "\n".join(tool_descriptions)

    def _format_messages_for_cli(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string for Claude Code CLI."""
        parts = []

        # Add tool instructions if tools are bound
        if self.bound_tools:
            tools_text = self._format_tools_for_prompt()
            parts.append(f"""[System Instructions]
You have access to the following tools:
{tools_text}

When you need to use a tool, respond with a JSON block in this EXACT format:
```tool_call
{{"tool": "tool_name", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}
```

After using tools and receiving results, provide your final analysis.
If you don't need to use any tools, just respond normally.
""")

        for msg in messages:
            if isinstance(msg, SystemMessage):
                parts.append(f"[System Instructions]\n{msg.content}\n")
            elif isinstance(msg, HumanMessage):
                parts.append(f"[User]\n{msg.content}\n")
            elif isinstance(msg, AIMessage):
                parts.append(f"[Assistant]\n{msg.content}\n")
            elif isinstance(msg, ToolMessage):
                parts.append(f"[Tool Result for {msg.tool_call_id}]\n{msg.content}\n")
            else:
                parts.append(f"{msg.content}\n")

        return "\n".join(parts)

    def _parse_tool_calls(self, response_text: str) -> tuple[str, List[dict]]:
        """Parse tool calls from the response text.

        Returns:
            tuple: (cleaned_text, list_of_tool_calls)
        """
        tool_calls = []

        # Look for tool call blocks
        pattern = r'```tool_call\s*\n?(.*?)\n?```'
        matches = re.findall(pattern, response_text, re.DOTALL)

        for match in matches:
            try:
                tool_data = json.loads(match.strip())
                tool_name = tool_data.get('tool', tool_data.get('name', 'unknown'))
                tool_args = tool_data.get('arguments', tool_data.get('args', {}))
                tool_calls.append({
                    'name': tool_name,
                    'args': tool_args,
                    'id': f"call_{len(tool_calls)}",
                })
            except json.JSONDecodeError:
                continue

        # Remove tool call blocks from text
        cleaned_text = re.sub(pattern, '', response_text, flags=re.DOTALL).strip()

        return cleaned_text, tool_calls

    def _call_claude_code(self, prompt: str, retry_count: int = 0) -> str:
        """Call Claude Code CLI and return the response."""
        import time
        max_retries = 3

        try:
            # Truncate very long prompts to avoid CLI issues
            max_prompt_len = 50000
            if len(prompt) > max_prompt_len:
                prompt = prompt[:max_prompt_len] + "\n\n[Prompt truncated due to length]"

            # Use claude CLI with print mode (non-interactive)
            # --print (-p): Print response and exit
            # --output-format text: Get plain text output
            result = subprocess.run(
                [
                    "claude",
                    "-p", prompt,
                    "--output-format", "text",
                    "--max-turns", str(self.max_turns),
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else ""
                stdout_msg = result.stdout.strip() if result.stdout else ""

                # Combine error info
                full_error = f"stderr: {error_msg}" if error_msg else ""
                if stdout_msg:
                    full_error += f" stdout: {stdout_msg[:500]}" if full_error else f"stdout: {stdout_msg[:500]}"
                if not full_error:
                    full_error = f"Exit code {result.returncode}"

                # Retry on transient errors
                if retry_count < max_retries:
                    print(f"Claude CLI error (attempt {retry_count + 1}/{max_retries}): {full_error[:200]}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    return self._call_claude_code(prompt, retry_count + 1)

                raise RuntimeError(f"Claude Code CLI error: {full_error}")

            response = result.stdout.strip()
            if not response:
                if retry_count < max_retries:
                    print(f"Empty response (attempt {retry_count + 1}/{max_retries}), retrying...")
                    time.sleep(2 ** retry_count)
                    return self._call_claude_code(prompt, retry_count + 1)
                raise RuntimeError("Claude Code CLI returned empty response")

            return response

        except subprocess.TimeoutExpired:
            if retry_count < max_retries:
                print(f"Timeout (attempt {retry_count + 1}/{max_retries}), retrying...")
                return self._call_claude_code(prompt, retry_count + 1)
            raise RuntimeError(f"Claude Code CLI timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude Code CLI not found. Please install it:\n"
                "  npm install -g @anthropic-ai/claude-code\n"
                "Then authenticate by running 'claude' once."
            )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response using Claude Code CLI."""
        prompt = self._format_messages_for_cli(messages)
        response_text = self._call_claude_code(prompt)

        # Handle stop sequences if provided
        if stop:
            for stop_seq in stop:
                if stop_seq in response_text:
                    response_text = response_text.split(stop_seq)[0]

        # Parse tool calls if tools are bound
        if self.bound_tools:
            cleaned_text, tool_calls = self._parse_tool_calls(response_text)
            if tool_calls:
                message = AIMessage(
                    content=cleaned_text,
                    tool_calls=tool_calls,
                )
            else:
                message = AIMessage(content=response_text)
        else:
            message = AIMessage(content=response_text)

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream is not supported by CLI, so we simulate it with a single chunk."""
        # Claude Code CLI doesn't support true streaming via subprocess
        # So we generate the full response and yield it as one chunk
        prompt = self._format_messages_for_cli(messages)
        response_text = self._call_claude_code(prompt)

        if stop:
            for stop_seq in stop:
                if stop_seq in response_text:
                    response_text = response_text.split(stop_seq)[0]

        chunk = ChatGenerationChunk(message=AIMessageChunk(content=response_text))
        yield chunk


class AnthropicAPIChat(BaseChatModel):
    """
    A LangChain ChatModel that uses Anthropic API directly.

    This is for cloud deployments where Claude CLI is not available.

    Usage:
        from tradingagents.llm.claude_code_wrapper import AnthropicAPIChat

        llm = AnthropicAPIChat(api_key="sk-ant-...")
        response = llm.invoke("Hello, how are you?")
    """

    api_key: str = Field(default="", description="Anthropic API key")
    model_name: str = Field(default="claude-3-5-sonnet-20241022", description="Model to use")
    max_tokens: int = Field(default=4096, description="Maximum tokens in response")
    timeout: int = Field(default=120, description="Request timeout in seconds")
    bound_tools: List[Any] = Field(default_factory=list, description="Bound tools")

    def __init__(self, **kwargs):
        # Get API key from environment if not provided
        if 'api_key' not in kwargs or not kwargs['api_key']:
            kwargs['api_key'] = os.environ.get('ANTHROPIC_API_KEY', '')
        super().__init__(**kwargs)

    @property
    def _llm_type(self) -> str:
        return "anthropic-api"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name}

    def bind_tools(
        self,
        tools: Sequence[Union[dict, type, callable, BaseTool]],
        **kwargs: Any,
    ) -> "AnthropicAPIChat":
        """Bind tools to the model for function calling."""
        new_instance = AnthropicAPIChat(
            api_key=self.api_key,
            model_name=self.model_name,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            bound_tools=list(tools),
        )
        return new_instance

    def _format_messages_for_api(self, messages: List[BaseMessage]) -> tuple[str, List[dict]]:
        """Convert LangChain messages to Anthropic API format.

        Returns:
            tuple: (system_prompt, messages_list)
        """
        system_prompt = ""
        api_messages = []

        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_prompt += msg.content + "\n"
            elif isinstance(msg, HumanMessage):
                api_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                api_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, ToolMessage):
                # Add tool result as user message
                api_messages.append({
                    "role": "user",
                    "content": f"[Tool Result for {msg.tool_call_id}]\n{msg.content}"
                })

        return system_prompt.strip(), api_messages

    def _call_anthropic_api(self, messages: List[BaseMessage]) -> str:
        """Call Anthropic API and return the response."""
        import requests

        if not self.api_key:
            raise RuntimeError(
                "Anthropic API key not set. Please provide api_key or set ANTHROPIC_API_KEY environment variable."
            )

        system_prompt, api_messages = self._format_messages_for_api(messages)

        # Ensure we have at least one message
        if not api_messages:
            api_messages = [{"role": "user", "content": "Hello"}]

        request_body = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": api_messages,
        }

        if system_prompt:
            request_body["system"] = system_prompt

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=request_body,
                timeout=self.timeout
            )

            if response.status_code != 200:
                error_detail = response.json().get('error', {}).get('message', response.text)
                raise RuntimeError(f"Anthropic API error ({response.status_code}): {error_detail}")

            result = response.json()
            content = result.get('content', [])

            # Extract text from content blocks
            text_parts = []
            for block in content:
                if block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))

            return '\n'.join(text_parts)

        except requests.exceptions.Timeout:
            raise RuntimeError(f"Anthropic API timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Could not connect to Anthropic API")

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response using Anthropic API."""
        response_text = self._call_anthropic_api(messages)

        # Handle stop sequences if provided
        if stop:
            for stop_seq in stop:
                if stop_seq in response_text:
                    response_text = response_text.split(stop_seq)[0]

        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream is simulated with a single chunk (full streaming not implemented)."""
        response_text = self._call_anthropic_api(messages)

        if stop:
            for stop_seq in stop:
                if stop_seq in response_text:
                    response_text = response_text.split(stop_seq)[0]

        chunk = ChatGenerationChunk(message=AIMessageChunk(content=response_text))
        yield chunk


# Convenience functions
def get_claude_code_llm(**kwargs) -> ClaudeCodeChat:
    """Create a Claude Code CLI chat model instance."""
    return ClaudeCodeChat(**kwargs)


def get_anthropic_api_llm(api_key: str = None, **kwargs) -> AnthropicAPIChat:
    """Create an Anthropic API chat model instance."""
    if api_key:
        kwargs['api_key'] = api_key
    return AnthropicAPIChat(**kwargs)


def get_best_llm(api_key: str = None, prefer_cli: bool = True, **kwargs):
    """
    Get the best available LLM based on what's configured.

    Args:
        api_key: Optional Anthropic API key
        prefer_cli: If True, prefer CLI over API when both available
        **kwargs: Additional arguments passed to the LLM

    Returns:
        Either ClaudeCodeChat or AnthropicAPIChat instance
    """
    import shutil

    cli_available = shutil.which("claude") is not None
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY', '')

    if prefer_cli and cli_available:
        return ClaudeCodeChat(**kwargs)
    elif api_key:
        return AnthropicAPIChat(api_key=api_key, **kwargs)
    elif cli_available:
        return ClaudeCodeChat(**kwargs)
    else:
        raise RuntimeError(
            "No LLM backend available. Either:\n"
            "1. Install Claude Code CLI: npm install -g @anthropic-ai/claude-code\n"
            "2. Set ANTHROPIC_API_KEY environment variable\n"
            "3. Pass api_key parameter"
        )
