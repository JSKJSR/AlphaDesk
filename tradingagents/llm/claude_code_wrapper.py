"""
Claude Code CLI Wrapper for LangChain

This module provides a LangChain-compatible ChatModel that uses the Claude Code CLI
instead of the Anthropic API, allowing you to use your Claude Pro subscription.
"""

import subprocess
import json
from typing import Any, List, Optional, Iterator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessageChunk,
)
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
from langchain_core.callbacks import CallbackManagerForLLMRun
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
    max_turns: int = Field(default=1, description="Max conversation turns")

    @property
    def _llm_type(self) -> str:
        return "claude-code"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name}

    def _format_messages_for_cli(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string for Claude Code CLI."""
        parts = []

        for msg in messages:
            if isinstance(msg, SystemMessage):
                parts.append(f"[System Instructions]\n{msg.content}\n")
            elif isinstance(msg, HumanMessage):
                parts.append(f"[User]\n{msg.content}\n")
            elif isinstance(msg, AIMessage):
                parts.append(f"[Assistant]\n{msg.content}\n")
            else:
                parts.append(f"{msg.content}\n")

        return "\n".join(parts)

    def _call_claude_code(self, prompt: str) -> str:
        """Call Claude Code CLI and return the response."""
        try:
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
                error_msg = result.stderr or "Unknown error"
                raise RuntimeError(f"Claude Code CLI error: {error_msg}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
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
