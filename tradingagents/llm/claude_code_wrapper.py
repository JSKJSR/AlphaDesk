"""
Claude Code CLI Wrapper for LangChain

This module provides a LangChain-compatible ChatModel that uses the Claude Code CLI
instead of the Anthropic API, allowing you to use your Claude Pro subscription.
"""

import subprocess
import json
import re
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


# Convenience function to create the chat model
def get_claude_code_llm(**kwargs) -> ClaudeCodeChat:
    """Create a Claude Code chat model instance."""
    return ClaudeCodeChat(**kwargs)
