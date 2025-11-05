"""
Platform Adapter for Cross-Platform Service Management

Provides platform abstraction layer for service operations across Windows, Linux, and macOS.
Uses factory pattern to create appropriate platform-specific adapters.
"""

import platform
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific service adapters"""
    
    def __init__(self, service_name: str, display_name: str, description: str):
        self.service_name = service_name
        self.display_name = display_name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def install_service(self, executable_path: str, **kwargs) -> bool:
        """Install the service on the platform"""
        pass
    
    @abstractmethod
    def uninstall_service(self) -> bool:
        """Uninstall the service from the platform"""
        pass
    
    @abstractmethod
    def start_service(self) -> bool:
        """Start the service"""
        pass
    
    @abstractmethod
    def stop_service(self) -> bool:
        """Stop the service"""
        pass
    
    @abstractmethod
    def restart_service(self) -> bool:
        """Restart the service"""
        pass
    
    @abstractmethod
    def get_service_status(self) -> ServiceStatus:
        """Get current service status"""
        pass
    
    @abstractmethod
    def is_service_installed(self) -> bool:
        """Check if service is installed"""
        pass
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get platform information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }


def get_platform_adapter(service_name: str, display_name: str, description: str) -> PlatformAdapter:
    """Factory function to create appropriate platform adapter"""
    system = platform.system().lower()
    
    if system == 'windows':
        from .windows_adapter import WindowsServiceAdapter
        return WindowsServiceAdapter(service_name, display_name, description)
    elif system == 'linux':
        from .linux_adapter import LinuxServiceAdapter
        return LinuxServiceAdapter(service_name, display_name, description)
    elif system == 'darwin':  # macOS
        from .macos_adapter import MacOSServiceAdapter
        return MacOSServiceAdapter(service_name, display_name, description)
    else:
        raise NotImplementedError(f"Platform '{system}' is not supported")


def detect_platform() -> str:
    """Detect the current platform"""
    return platform.system().lower()


def get_platform_specific_paths() -> Dict[str, str]:
    """Get platform-specific default paths for configuration and logs"""
    system = platform.system().lower()
    
    if system == 'windows':
        import os
        return {
            'config_dir': os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'EmotivLSL'),
            'log_dir': os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'EmotivLSL', 'logs'),
            'service_dir': os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'EmotivLSL')
        }
    elif system == 'linux':
        return {
            'config_dir': '/etc/emotiv-lsl',
            'log_dir': '/var/log/emotiv-lsl',
            'service_dir': '/usr/local/bin'
        }
    elif system == 'darwin':  # macOS
        return {
            'config_dir': '/usr/local/etc/emotiv-lsl',
            'log_dir': '/usr/local/var/log/emotiv-lsl',
            'service_dir': '/usr/local/bin'
        }
    else:
        # Fallback to user directory
        import os
        home = os.path.expanduser('~')
        return {
            'config_dir': os.path.join(home, '.emotiv-lsl'),
            'log_dir': os.path.join(home, '.emotiv-lsl', 'logs'),
            'service_dir': os.path.join(home, '.emotiv-lsl', 'bin')
        }