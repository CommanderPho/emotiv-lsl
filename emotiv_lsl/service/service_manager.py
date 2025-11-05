"""
Emotiv LSL Service Manager

Main service management class that provides unified interface for cross-platform service operations.
"""

import logging
import sys
import os
from typing import Dict, Any, Optional
from .platform_adapter import get_platform_adapter, PlatformAdapter, ServiceStatus

logger = logging.getLogger(__name__)


class EmotivLSLService:
    """Main service manager class for Emotiv LSL Service"""
    
    def __init__(self, 
                 service_name: str = "EmotivLSLService",
                 display_name: str = "Emotiv LSL Data Capture Service", 
                 description: str = "Captures EEG data from Emotiv devices and streams via LSL"):
        
        self.service_name = service_name
        self.display_name = display_name
        self.description = description
        
        # Get platform-specific adapter
        self.platform_adapter: PlatformAdapter = get_platform_adapter(
            service_name, display_name, description
        )
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def install(self, executable_path: Optional[str] = None, **kwargs) -> bool:
        """Install the service on the current platform"""
        if executable_path is None:
            executable_path = sys.executable
            
        try:
            self.logger.info(f"Installing service '{self.service_name}' on {self.platform_adapter.get_platform_info()['system']}")
            success = self.platform_adapter.install_service(executable_path, **kwargs)
            
            if success:
                self.logger.info(f"Service '{self.service_name}' installed successfully")
            else:
                self.logger.error(f"Failed to install service '{self.service_name}'")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error installing service: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall the service from the current platform"""
        try:
            self.logger.info(f"Uninstalling service '{self.service_name}'")
            success = self.platform_adapter.uninstall_service()
            
            if success:
                self.logger.info(f"Service '{self.service_name}' uninstalled successfully")
            else:
                self.logger.error(f"Failed to uninstall service '{self.service_name}'")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error uninstalling service: {e}")
            return False
    
    def start(self) -> bool:
        """Start the service"""
        try:
            self.logger.info(f"Starting service '{self.service_name}'")
            success = self.platform_adapter.start_service()
            
            if success:
                self.logger.info(f"Service '{self.service_name}' started successfully")
            else:
                self.logger.error(f"Failed to start service '{self.service_name}'")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting service: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the service"""
        try:
            self.logger.info(f"Stopping service '{self.service_name}'")
            success = self.platform_adapter.stop_service()
            
            if success:
                self.logger.info(f"Service '{self.service_name}' stopped successfully")
            else:
                self.logger.error(f"Failed to stop service '{self.service_name}'")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error stopping service: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the service"""
        try:
            self.logger.info(f"Restarting service '{self.service_name}'")
            success = self.platform_adapter.restart_service()
            
            if success:
                self.logger.info(f"Service '{self.service_name}' restarted successfully")
            else:
                self.logger.error(f"Failed to restart service '{self.service_name}'")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error restarting service: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status information"""
        try:
            status = self.platform_adapter.get_service_status()
            is_installed = self.platform_adapter.is_service_installed()
            platform_info = self.platform_adapter.get_platform_info()
            
            return {
                'service_name': self.service_name,
                'display_name': self.display_name,
                'status': status.value,
                'is_installed': is_installed,
                'platform': platform_info['system'],
                'platform_version': platform_info['release']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return {
                'service_name': self.service_name,
                'display_name': self.display_name,
                'status': ServiceStatus.ERROR.value,
                'is_installed': False,
                'error': str(e)
            }
    
    def is_installed(self) -> bool:
        """Check if the service is installed"""
        try:
            return self.platform_adapter.is_service_installed()
        except Exception as e:
            self.logger.error(f"Error checking if service is installed: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if the service is currently running"""
        try:
            status = self.platform_adapter.get_service_status()
            return status == ServiceStatus.RUNNING
        except Exception as e:
            self.logger.error(f"Error checking if service is running: {e}")
            return False