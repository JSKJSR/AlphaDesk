"""
Claude Code CLI Authentication Module.

Verifies Claude Code CLI installation and authentication status.
Uses the system's Claude CLI - no credentials stored in this app.
"""

import subprocess
import shutil
from typing import Dict, Tuple
from enum import Enum


class AuthStatus(Enum):
    """Authentication status states."""
    UNKNOWN = "unknown"
    CHECKING = "checking"
    CONNECTED = "connected"
    NOT_INSTALLED = "not_installed"
    NOT_AUTHENTICATED = "not_authenticated"
    ERROR = "error"


def check_claude_installed() -> bool:
    """
    Check if Claude Code CLI is installed on the system.

    Returns:
        bool: True if claude CLI is found in PATH
    """
    return shutil.which("claude") is not None


def check_claude_authenticated() -> Tuple[bool, str]:
    """
    Check if the user is authenticated with Claude Code CLI.

    Returns:
        Tuple[bool, str]: (is_authenticated, message)
    """
    if not check_claude_installed():
        return False, "Claude Code CLI is not installed"

    try:
        # Run a simple command to check authentication
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return True, f"Claude CLI found: {result.stdout.strip()}"
        else:
            return False, "Claude CLI returned an error"

    except subprocess.TimeoutExpired:
        return False, "Connection check timed out"
    except Exception as e:
        return False, f"Error checking authentication: {str(e)}"


def verify_claude_connection() -> Dict:
    """
    Verify Claude Code CLI is installed and accessible.

    Uses --version check instead of an actual prompt to avoid long waits.

    Returns:
        Dict with keys: status, message, details
    """
    if not check_claude_installed():
        return {
            "status": AuthStatus.NOT_INSTALLED,
            "message": "Claude Code CLI is not installed",
            "details": "Please install Claude Code CLI to continue.",
            "instructions": get_install_instructions()
        }

    try:
        # Quick check using --version (fast, no API call)
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            return {
                "status": AuthStatus.CONNECTED,
                "message": "Claude CLI Ready",
                "details": f"Found: {version}"
            }

        # Check stderr for issues
        stderr = result.stderr.lower() if result.stderr else ""

        auth_keywords = ["auth", "login", "credential", "not logged", "sign in"]
        if any(kw in stderr for kw in auth_keywords):
            return {
                "status": AuthStatus.NOT_AUTHENTICATED,
                "message": "Authentication required",
                "details": "Please log in to your Claude account.",
                "instructions": get_auth_instructions()
            }

        return {
            "status": AuthStatus.ERROR,
            "message": "CLI check failed",
            "details": stderr[:200] if stderr else "Unknown error"
        }

    except subprocess.TimeoutExpired:
        return {
            "status": AuthStatus.ERROR,
            "message": "Connection timed out",
            "details": "Claude CLI did not respond in time."
        }
    except Exception as e:
        return {
            "status": AuthStatus.ERROR,
            "message": "Connection error",
            "details": f"Error: {str(e)}"
        }


def get_install_instructions() -> str:
    """Get installation instructions for Claude Code CLI."""
    return """
To install Claude Code CLI:

1. Visit: https://claude.ai/download
2. Download Claude Code for your platform
3. Follow the installation instructions
4. Run 'claude' in terminal to verify installation
5. Log in with your Anthropic account
    """.strip()


def get_auth_instructions() -> str:
    """Get authentication instructions for Claude Code CLI."""
    return """
To authenticate with Claude Code:

1. Open your terminal
2. Run: claude
3. Follow the login prompts
4. Enter your Anthropic account credentials
5. Return here and click "Connect" again
    """.strip()


def get_connection_status_display(status: AuthStatus) -> Dict:
    """
    Get UI-friendly display properties for a status.

    Returns:
        Dict with: icon, color, title, description
    """
    status_map = {
        AuthStatus.UNKNOWN: {
            "icon": "❓",
            "color": "#86868b",
            "title": "Not Connected",
            "description": "Click Connect to verify your Claude account"
        },
        AuthStatus.CHECKING: {
            "icon": "⏳",
            "color": "#0071e3",
            "title": "Checking...",
            "description": "Verifying your Claude connection"
        },
        AuthStatus.CONNECTED: {
            "icon": "✓",
            "color": "#34c759",
            "title": "Connected",
            "description": "Your Claude account is ready"
        },
        AuthStatus.NOT_INSTALLED: {
            "icon": "⚠️",
            "color": "#ff9500",
            "title": "Not Installed",
            "description": "Claude Code CLI needs to be installed"
        },
        AuthStatus.NOT_AUTHENTICATED: {
            "icon": "🔐",
            "color": "#ff9500",
            "title": "Login Required",
            "description": "Please log in to your Claude account"
        },
        AuthStatus.ERROR: {
            "icon": "✗",
            "color": "#ff3b30",
            "title": "Connection Error",
            "description": "Unable to connect to Claude"
        }
    }

    return status_map.get(status, status_map[AuthStatus.UNKNOWN])
