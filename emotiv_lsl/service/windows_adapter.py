"""
Windows Service Adapter

Windows-specific service implementation using pywin32 framework.
Integrates with Windows Service Control Manager (SCM).
"""

import logging
import subprocess
import sys
import os
from typing import Dict, Any, Optional

from .platform_adapter import PlatformAdapter, ServiceStatus

logger = logging.getLogger(__name__)


class WindowsServiceAdapter(PlatformAdapter):
    """Windows Service Control Manager adapter"""
    
    def __init__(self, service_name: str, display_name: str, description: str):
        super().__init__(service_name, display_name, description)
        self._check_pywin32_availability()
    
    def _check_pywin32_availability(self):
        """Check if pywin32 is available, log warning if not"""
        try:
            import win32service
            import win32serviceutil
            self._pywin32_available = True
        except ImportError:
            self.logger.warning(
                "pywin32 not available. Windows service functionality will be limited. "
                "Install with: pip install pywin32"
            )
            self._pywin32_available = False
    
    def install_service(self, executable_path: str, **kwargs) -> bool:
        """Install Windows service using pywin32 or sc command"""
        if self._pywin32_available:
            return self._install_service_pywin32(executable_path, **kwargs)
        else:
            return self._install_service_sc_command(executable_path, **kwargs)
    
    def _install_service_pywin32(self, executable_path: str, **kwargs) -> bool:
        """Install service using pywin32"""
        try:
            import win32serviceutil
            import win32service
            
            # Service configuration
            service_class_string = kwargs.get('service_class', 'emotiv_lsl.service.windows_service.EmotivLSLWindowsService')
            start_type = win32service.SERVICE_AUTO_START
            
            # Install the service
            win32serviceutil.InstallService(
                pythonClassString=service_class_string,
                serviceName=self.service_name,
                displayName=self.display_name,
                description=self.description,
                startType=start_type,
                exeName=executable_path
            )
            
            self.logger.info(f"Windows service '{self.service_name}' installed successfully using pywin32")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Windows service using pywin32: {e}")
            return False
    
    def _install_service_sc_command(self, executable_path: str, **kwargs) -> bool:
        """Install service using Windows sc command as fallback"""
        try:
            # Create service using sc command
            cmd = [
                'sc', 'create', self.service_name,
                'binPath=', f'"{executable_path}" -m emotiv_lsl.service',
                'DisplayName=', self.display_name,
                'start=', 'auto'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                # Set service description
                desc_cmd = ['sc', 'description', self.service_name, self.description]
                subprocess.run(desc_cmd, capture_output=True, text=True, shell=True)
                
                self.logger.info(f"Windows service '{self.service_name}' installed successfully using sc command")
                return True
            else:
                self.logger.error(f"Failed to install service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install Windows service using sc command: {e}")
            return False
    
    def uninstall_service(self) -> bool:
        """Uninstall Windows service"""
        if self._pywin32_available:
            return self._uninstall_service_pywin32()
        else:
            return self._uninstall_service_sc_command()
    
    def _uninstall_service_pywin32(self) -> bool:
        """Uninstall service using pywin32"""
        try:
            import win32serviceutil
            
            # Stop service first if running
            try:
                win32serviceutil.StopService(self.service_name)
            except:
                pass  # Service might not be running
            
            # Remove the service
            win32serviceutil.RemoveService(self.service_name)
            
            self.logger.info(f"Windows service '{self.service_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall Windows service: {e}")
            return False
    
    def _uninstall_service_sc_command(self) -> bool:
        """Uninstall service using sc command"""
        try:
            # Stop service first
            subprocess.run(['sc', 'stop', self.service_name], capture_output=True, shell=True)
            
            # Delete service
            result = subprocess.run(['sc', 'delete', self.service_name], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.logger.info(f"Windows service '{self.service_name}' uninstalled successfully")
                return True
            else:
                self.logger.error(f"Failed to uninstall service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to uninstall Windows service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start Windows service"""
        if self._pywin32_available:
            return self._start_service_pywin32()
        else:
            return self._start_service_sc_command()
    
    def _start_service_pywin32(self) -> bool:
        """Start service using pywin32"""
        try:
            import win32serviceutil
            
            win32serviceutil.StartService(self.service_name)
            self.logger.info(f"Windows service '{self.service_name}' started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Windows service: {e}")
            return False
    
    def _start_service_sc_command(self) -> bool:
        """Start service using sc command"""
        try:
            result = subprocess.run(['sc', 'start', self.service_name], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.logger.info(f"Windows service '{self.service_name}' started successfully")
                return True
            else:
                self.logger.error(f"Failed to start service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start Windows service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop Windows service"""
        if self._pywin32_available:
            return self._stop_service_pywin32()
        else:
            return self._stop_service_sc_command()
    
    def _stop_service_pywin32(self) -> bool:
        """Stop service using pywin32"""
        try:
            import win32serviceutil
            
            win32serviceutil.StopService(self.service_name)
            self.logger.info(f"Windows service '{self.service_name}' stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Windows service: {e}")
            return False
    
    def _stop_service_sc_command(self) -> bool:
        """Stop service using sc command"""
        try:
            result = subprocess.run(['sc', 'stop', self.service_name], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.logger.info(f"Windows service '{self.service_name}' stopped successfully")
                return True
            else:
                self.logger.error(f"Failed to stop service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to stop Windows service: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart Windows service"""
        self.logger.info(f"Restarting Windows service '{self.service_name}'")
        
        if not self.stop_service():
            return False
        
        # Wait a moment before starting
        import time
        time.sleep(2)
        
        return self.start_service()
    
    def get_service_status(self) -> ServiceStatus:
        """Get Windows service status"""
        if self._pywin32_available:
            return self._get_service_status_pywin32()
        else:
            return self._get_service_status_sc_command()
    
    def _get_service_status_pywin32(self) -> ServiceStatus:
        """Get service status using pywin32"""
        try:
            import win32serviceutil
            import win32service
            
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            state = status[1]
            
            if state == win32service.SERVICE_STOPPED:
                return ServiceStatus.STOPPED
            elif state == win32service.SERVICE_START_PENDING:
                return ServiceStatus.STARTING
            elif state == win32service.SERVICE_RUNNING:
                return ServiceStatus.RUNNING
            elif state == win32service.SERVICE_STOP_PENDING:
                return ServiceStatus.STOPPING
            else:
                return ServiceStatus.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"Failed to get Windows service status: {e}")
            return ServiceStatus.ERROR
    
    def _get_service_status_sc_command(self) -> ServiceStatus:
        """Get service status using sc command"""
        try:
            result = subprocess.run(['sc', 'query', self.service_name], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'running' in output:
                    return ServiceStatus.RUNNING
                elif 'stopped' in output:
                    return ServiceStatus.STOPPED
                elif 'start_pending' in output:
                    return ServiceStatus.STARTING
                elif 'stop_pending' in output:
                    return ServiceStatus.STOPPING
                else:
                    return ServiceStatus.UNKNOWN
            else:
                return ServiceStatus.ERROR
                
        except Exception as e:
            self.logger.error(f"Failed to get Windows service status: {e}")
            return ServiceStatus.ERROR
    
    def is_service_installed(self) -> bool:
        """Check if Windows service is installed"""
        if self._pywin32_available:
            return self._is_service_installed_pywin32()
        else:
            return self._is_service_installed_sc_command()
    
    def _is_service_installed_pywin32(self) -> bool:
        """Check if service is installed using pywin32"""
        try:
            import win32serviceutil
            
            # Try to query the service
            win32serviceutil.QueryServiceStatus(self.service_name)
            return True
            
        except Exception:
            return False
    
    def _is_service_installed_sc_command(self) -> bool:
        """Check if service is installed using sc command"""
        try:
            result = subprocess.run(['sc', 'query', self.service_name], capture_output=True, text=True, shell=True)
            return result.returncode == 0
            
        except Exception:
            return False