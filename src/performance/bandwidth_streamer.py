"""
High-Bandwidth Frame Streaming Manager for AzimuthControl (SIMPLIFIED)

This module provides a simplified streaming interface that integrates
with the existing application flow without conflicts.
"""

import logging

logger = logging.getLogger(__name__)

def get_cpp_streaming_manager():
    """Return None - C++ streaming disabled to prevent conflicts."""
    logger.info("C++ streaming system disabled - using standard processing")
    return None

class StreamConfig:
    """Placeholder configuration class."""
    def __init__(self):
        pass
