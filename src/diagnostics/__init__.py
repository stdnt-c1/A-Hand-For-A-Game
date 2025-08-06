"""
Diagnostics module for AzimuthControl.

This module provides diagnostic tools for camera and movement systems.
"""

# Import diagnostic modules using relative imports
from . import camera_diagnostics
from . import movement_diagnostics

__all__ = ['camera_diagnostics', 'movement_diagnostics']
