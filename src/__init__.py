"""
AzimuthControl - Hand Gesture Recognition System

Core package for gesture recognition and processing functionality.
"""

__version__ = "1.0.0"
__author__ = "AzimuthControl Project"

from .core.config_manager import get_controls_config, get_performance_config, get_system_config

__all__ = [
    'get_controls_config',
    'get_performance_config', 
    'get_system_config'
]
