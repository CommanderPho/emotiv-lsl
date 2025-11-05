"""
Emotiv LSL Service Module

Cross-platform service infrastructure for running Emotiv LSL data capture as a background service.
Supports Windows (Windows Service), Linux (systemd), and macOS (launchd).
"""

from .service_manager import EmotivLSLService
from .platform_adapter import PlatformAdapter, get_platform_adapter
from .service_controller import ServiceController

__all__ = [
    'EmotivLSLService',
    'PlatformAdapter', 
    'get_platform_adapter',
    'ServiceController'
]