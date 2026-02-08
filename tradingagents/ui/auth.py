"""
AlphaDesk Authentication Module.

Supports two authentication methods:
1. Claude Code CLI (local usage with Claude Pro subscription)
2. Anthropic API Key (for Streamlit Cloud deployment)
"""

import subprocess
import shutil
import os
from typing import Dict, Tuple, Optional
from enum import Enum


class AuthStatus(Enum):
    """Authentication status states."""
    UNKNOWN = "unknown"
    CHECKING = "checking"
    CONNECTED = "connected"
    NOT_INSTALLED = "not_installed"
    NOT_AUTHENTICATED = "not_authenticated"
    ERROR = "error"
    API_KEY_VALID = "api_key_valid"
    API_KEY_INVALID = "api_key_invalid"


class AuthMethod(Enum):
    """Authentication method types."""
    CLAUDE_CLI = "claude_cli"
    ANTHROPIC_API = "anthropic_api"
    NONE = "none"


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


def validate_anthropic_api_key(api_key: str) -> Dict:
    """
    Validate an Anthropic API key by making a test request.

    Args:
        api_key: The Anthropic API key to validate

    Returns:
        Dict with status and message
    """
    if not api_key or not api_key.strip():
        return {
            "valid": False,
            "message": "API key is empty"
        }

    api_key = api_key.strip()

    # Check format (Anthropic keys start with 'sk-ant-')
    if not api_key.startswith('sk-ant-'):
        return {
            "valid": False,
            "message": "Invalid format. Anthropic API keys start with 'sk-ant-'"
        }

    # Try to make a minimal API call to validate
    try:
        import requests

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=15
        )

        if response.status_code == 200:
            return {
                "valid": True,
                "message": "API key validated successfully"
            }
        elif response.status_code == 401:
            return {
                "valid": False,
                "message": "Invalid API key"
            }
        elif response.status_code == 403:
            return {
                "valid": False,
                "message": "API key lacks required permissions"
            }
        elif response.status_code == 429:
            # Rate limited but key is valid
            return {
                "valid": True,
                "message": "API key valid (rate limited)"
            }
        else:
            return {
                "valid": False,
                "message": f"API error: {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {
            "valid": False,
            "message": "Connection timed out"
        }
    except requests.exceptions.ConnectionError:
        return {
            "valid": False,
            "message": "Could not connect to Anthropic API"
        }
    except ImportError:
        # requests not installed, just check format
        return {
            "valid": True,
            "message": "Format valid (could not verify online)"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }


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


def get_best_auth_method() -> AuthMethod:
    """
    Determine the best available authentication method.

    Priority:
    1. Claude CLI (if available and working)
    2. Anthropic API key (from environment)
    3. None

    Returns:
        AuthMethod enum
    """
    # Check CLI first
    if check_claude_installed():
        result = verify_claude_connection()
        if result["status"] == AuthStatus.CONNECTED:
            return AuthMethod.CLAUDE_CLI

    # Check for API key in environment
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        validation = validate_anthropic_api_key(api_key)
        if validation["valid"]:
            return AuthMethod.ANTHROPIC_API

    return AuthMethod.NONE


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


def get_api_key_instructions() -> str:
    """Get instructions for obtaining an Anthropic API key."""
    return """
To get your Anthropic API key:

1. Visit: https://console.anthropic.com
2. Sign in or create an account
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with 'sk-ant-')
6. Paste it in the field above
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
        },
        AuthStatus.API_KEY_VALID: {
            "icon": "✓",
            "color": "#34c759",
            "title": "API Key Valid",
            "description": "Connected via Anthropic API"
        },
        AuthStatus.API_KEY_INVALID: {
            "icon": "✗",
            "color": "#ff3b30",
            "title": "Invalid API Key",
            "description": "Please check your API key"
        }
    }

    return status_map.get(status, status_map[AuthStatus.UNKNOWN])
