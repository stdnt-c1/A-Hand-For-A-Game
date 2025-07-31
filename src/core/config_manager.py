"""
Configuration loader and manager for AzimuthControl gesture recognition system.
Provides centralized access to all configuration settings.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Centralized configuration management for AzimuthControl."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files. 
                       Defaults to 'config' in project root.
        """
        if config_dir is None:
            # Get project root (two levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            config_dir = str(project_root / "config")
        
        self.config_dir = Path(config_dir)
        self._controls_config = None
        self._performance_config = None
        self._system_config = None
        
    def load_controls_config(self) -> Dict[str, Any]:
        """Load gesture controls configuration."""
        if self._controls_config is None:
            config_path = self.config_dir / "controls.json"
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self._controls_config = data.get('gesture_controls', {})
            except FileNotFoundError:
                # Return default config if file not found
                self._controls_config = self._get_default_controls_config()
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in controls config: {e}")
        
        return self._controls_config
    
    def _get_default_controls_config(self) -> Dict[str, Any]:
        """Get default controls configuration."""
        return {
            "MovementControl": {"enabled": True},
            "ActionControl": {"enabled": True},
            "CameraControl": {"enabled": True},
            "NavigationControl": {"enabled": True}
        }
    
    def load_performance_config(self) -> Dict[str, Any]:
        """Load performance configuration settings."""
        if self._performance_config is None:
            config_path = self.config_dir / "controls.json"
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self._performance_config = data.get('performance_settings', {})
            except FileNotFoundError:
                # Use defaults if config not found
                self._performance_config = {
                    "target_fps": 30,
                    "max_processing_time_ms": 20,
                    "enable_caching": True,
                    "cache_duration_ms": 100,
                    "enable_jit_compilation": True
                }
        
        return self._performance_config
    
    def load_system_config(self) -> Dict[str, Any]:
        """Load system configuration settings."""
        if self._system_config is None:
            config_path = self.config_dir / "controls.json"
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self._system_config = data.get('system_settings', {})
            except FileNotFoundError:
                # Use defaults if config not found
                self._system_config = {
                    "camera_index": 0,
                    "window_width": 1280,
                    "window_height": 720,
                    "enable_debug_output": False,
                    "enable_performance_monitoring": True
                }
        
        return self._system_config


# Global config manager instance
config_manager = ConfigManager()


def get_controls_config() -> Dict[str, Any]:
    """Get gesture controls configuration."""
    return config_manager.load_controls_config()


def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration."""
    return config_manager.load_performance_config()


def get_system_config() -> Dict[str, Any]:
    """Get system configuration."""
    return config_manager.load_system_config()
