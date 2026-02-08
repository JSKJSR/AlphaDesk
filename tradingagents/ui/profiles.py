"""
Profile Management for TradingAgents.

Manages user profiles/personas for Claude CLI. Since Claude CLI only supports
one authenticated account at a time, this provides a UI similar to Google/AWS
account switcher for managing profile names and organizing sessions.

Profiles are stored in ~/.tradingagents/profiles.json
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import random

PROFILES_DIR = os.path.expanduser('~/.tradingagents')
PROFILES_FILE = 'profiles.json'

# Default avatar colors (professional palette)
AVATAR_COLORS = [
    '#0066cc',  # Blue
    '#007a3d',  # Green
    '#6b4c9a',  # Purple
    '#c41e3a',  # Red
    '#b5850b',  # Gold
    '#2e7d32',  # Forest green
    '#1565c0',  # Royal blue
    '#6a1b9a',  # Deep purple
]


@dataclass
class UserProfile:
    """Represents a user profile."""
    id: str
    name: str
    email: str = ""
    avatar_initial: str = ""
    color: str = ""
    created_at: str = ""
    last_used: str = ""
    is_active: bool = False
    notes: str = ""

    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.avatar_initial:
            self.avatar_initial = self.name[0].upper() if self.name else "U"
        if not self.color:
            self.color = random.choice(AVATAR_COLORS)
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class ProfileManager:
    """
    Manages user profiles for TradingAgents.

    Features:
    - Create, read, update, delete profiles
    - Switch between profiles
    - Persist to ~/.tradingagents/profiles.json
    - Default profile created on first use
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize the profile manager.

        Args:
            config_dir: Directory for config files. Defaults to ~/.tradingagents/
        """
        self.config_dir = config_dir or PROFILES_DIR
        self.profiles_path = os.path.join(self.config_dir, PROFILES_FILE)
        self._ensure_config_dir()
        self._load_profiles()

    def _ensure_config_dir(self):
        """Ensure config directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)

    def _load_profiles(self):
        """Load profiles from disk."""
        self.profiles: Dict[str, UserProfile] = {}
        self.active_profile_id: Optional[str] = None

        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, 'r') as f:
                    data = json.load(f)
                    for pid, pdata in data.get('profiles', {}).items():
                        self.profiles[pid] = UserProfile(**pdata)
                    self.active_profile_id = data.get('active_profile_id')
            except (json.JSONDecodeError, IOError, TypeError):
                self._create_default_profile()
        else:
            self._create_default_profile()

    def _create_default_profile(self):
        """Create a default profile."""
        default = UserProfile(
            id='default',
            name='Default User',
            email='',
            color='#0066cc',
            is_active=True,
            notes='Default profile'
        )
        self.profiles['default'] = default
        self.active_profile_id = 'default'
        self._save_profiles()

    def _save_profiles(self):
        """Save profiles to disk."""
        data = {
            'profiles': {pid: asdict(p) for pid, p in self.profiles.items()},
            'active_profile_id': self.active_profile_id,
            'version': '1.0'
        }
        try:
            with open(self.profiles_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save profiles: {e}")

    def get_active_profile(self) -> Optional[UserProfile]:
        """
        Get the currently active profile.

        Returns:
            Active UserProfile or None
        """
        if self.active_profile_id and self.active_profile_id in self.profiles:
            return self.profiles[self.active_profile_id]
        # Fallback to first profile
        if self.profiles:
            first_id = list(self.profiles.keys())[0]
            return self.profiles[first_id]
        return None

    def get_all_profiles(self) -> List[UserProfile]:
        """
        Get all profiles sorted by last used.

        Returns:
            List of UserProfile objects
        """
        profiles = list(self.profiles.values())
        # Sort: active first, then by last_used
        profiles.sort(key=lambda p: (not p.is_active, p.last_used or ''), reverse=True)
        return profiles

    def add_profile(self, name: str, email: str = "", color: str = None) -> UserProfile:
        """
        Add a new profile.

        Args:
            name: Display name for the profile
            email: Optional email address
            color: Optional avatar color (hex)

        Returns:
            Created UserProfile
        """
        # Generate unique ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        pid = f"profile_{len(self.profiles)}_{timestamp}"

        profile = UserProfile(
            id=pid,
            name=name,
            email=email,
            color=color or random.choice(AVATAR_COLORS),
            is_active=False
        )
        self.profiles[pid] = profile
        self._save_profiles()
        return profile

    def switch_profile(self, profile_id: str) -> bool:
        """
        Switch to a different profile.

        Args:
            profile_id: ID of profile to switch to

        Returns:
            True if switch successful
        """
        if profile_id not in self.profiles:
            return False

        # Deactivate current profile
        if self.active_profile_id and self.active_profile_id in self.profiles:
            self.profiles[self.active_profile_id].is_active = False

        # Activate new profile
        self.profiles[profile_id].is_active = True
        self.profiles[profile_id].last_used = datetime.now().isoformat()
        self.active_profile_id = profile_id
        self._save_profiles()
        return True

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile. Cannot delete the last remaining profile.

        Args:
            profile_id: ID of profile to delete

        Returns:
            True if deletion successful
        """
        # Cannot delete last profile
        if len(self.profiles) <= 1:
            return False

        if profile_id not in self.profiles:
            return False

        del self.profiles[profile_id]

        # If deleted active profile, switch to another
        if self.active_profile_id == profile_id:
            new_active = list(self.profiles.keys())[0]
            self.active_profile_id = new_active
            self.profiles[new_active].is_active = True

        self._save_profiles()
        return True

    def update_profile(self, profile_id: str, **kwargs) -> bool:
        """
        Update profile properties.

        Args:
            profile_id: ID of profile to update
            **kwargs: Properties to update (name, email, color, notes)

        Returns:
            True if update successful
        """
        if profile_id not in self.profiles:
            return False

        profile = self.profiles[profile_id]
        allowed_fields = {'name', 'email', 'color', 'notes', 'avatar_initial'}

        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(profile, key):
                setattr(profile, key, value)

        # Update avatar initial if name changed
        if 'name' in kwargs and kwargs['name']:
            profile.avatar_initial = kwargs['name'][0].upper()

        self._save_profiles()
        return True

    def get_profile_count(self) -> int:
        """Get the number of profiles."""
        return len(self.profiles)


# Singleton instance
_manager = None


def get_profile_manager() -> ProfileManager:
    """
    Get the singleton profile manager instance.

    Returns:
        ProfileManager instance
    """
    global _manager
    if _manager is None:
        _manager = ProfileManager()
    return _manager


def get_active_profile() -> Optional[UserProfile]:
    """
    Convenience function to get the active profile.

    Returns:
        Active UserProfile or None
    """
    return get_profile_manager().get_active_profile()
