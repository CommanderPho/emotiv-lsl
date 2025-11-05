"""
macOS launchd Service Adapter

macOS-specific service implementation using launchd.
Manages launchd plist files and service control via launchctl.
"""

import logging
import subprocess
import os
import plistlib
from typing import Dict, Any, Optional
from pathlib import Path

from .platform_adapter import PlatformAdapter, ServiceStatus

logger = logging.getLogger(__name__)


class MacOSServiceAdapter(PlatformAdapter):
    """macOS launchd service adapter"""
    
    def __init__(self, service_name: str, display_name: str, description: str):
        super().__init__(service_name, display_name, description)
        
        # Generate reverse domain name style identifier
        self.service_identifier = f"com.emotiv.lsl.{service_name.lower().replace(' ', '-')}"
        self.plist_filename = f"{self.service_identifier}.plist"
        
        # Service paths
        self.system_plist_path = Path(f"/Library/LaunchDaemons/{self.plist_filename}")
        self.user_plist_path = Path(f"~/Library/LaunchAgents/{self.plist_filename}").expanduser()
        
    def install_service(self, executable_path: str, **kwargs) -> bool:
        """Install launchd service plist file"""
        try:
            # Determine if we should install as system daemon or user agent
            install_as_user = kwargs.get('user_service', False)
            
            if install_as_user:
                plist_path = self.user_plist_path
                plist_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                plist_path = self.system_plist_path
            
            # Create launchd plist content
            plist_content = self._generate_plist_content(executable_path, **kwargs)
            
            # Write plist file
            if install_as_user:
                with open(plist_path, 'wb') as f:
                    plistlib.dump(plist_content, f)
            else:
                # Need sudo for system daemon
                self._write_system_plist_file(plist_path, plist_content)
            
            # Set appropriate permissions
            if not install_as_user:
                subprocess.run(['sudo', 'chown', 'root:wheel', str(plist_path)], check=True)
                subprocess.run(['sudo', 'chmod', '644', str(plist_path)], check=True)
            
            self.logger.info(f"macOS launchd service '{self.service_name}' installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install macOS launchd service: {e}")
            return False
    
    def _generate_plist_content(self, executable_path: str, **kwargs) -> Dict[str, Any]:
        """Generate launchd plist content"""
        user_name = kwargs.get('user', 'emotiv')
        group_name = kwargs.get('group', 'staff')
        working_dir = kwargs.get('working_directory', '/usr/local/var/emotiv-lsl')
        environment_vars = kwargs.get('environment', {})
        run_at_load = kwargs.get('run_at_load', True)
        keep_alive = kwargs.get('keep_alive', True)
        
        # Base plist structure
        plist_content = {
            'Label': self.service_identifier,
            'ProgramArguments': [executable_path, '-m', 'emotiv_lsl.service'],
            'RunAtLoad': run_at_load,
            'KeepAlive': keep_alive,
            'WorkingDirectory': working_dir,
            'StandardOutPath': f'/usr/local/var/log/emotiv-lsl/{self.service_name}.log',
            'StandardErrorPath': f'/usr/local/var/log/emotiv-lsl/{self.service_name}.error.log',
        }
        
        # Add user/group if not running as user service
        if not kwargs.get('user_service', False):
            plist_content['UserName'] = user_name
            plist_content['GroupName'] = group_name
        
        # Add environment variables if provided
        if environment_vars:
            plist_content['EnvironmentVariables'] = environment_vars
        
        # Add restart behavior
        if keep_alive:
            plist_content['KeepAlive'] = {
                'SuccessfulExit': False,  # Restart on unexpected exit
                'Crashed': True,          # Restart on crash
            }
        
        # Add resource limits
        plist_content['SoftResourceLimits'] = {
            'NumberOfFiles': 1024,
            'NumberOfProcesses': 100
        }
        
        # Add nice level (lower priority)
        plist_content['Nice'] = 1
        
        return plist_content
    
    def _write_system_plist_file(self, plist_path: Path, content: Dict[str, Any]):
        """Write system plist file with sudo"""
        try:
            # Create temporary file first
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.plist') as temp_file:
                plistlib.dump(content, temp_file)
                temp_path = temp_file.name
            
            # Copy to system location with sudo
            subprocess.run(['sudo', 'cp', temp_path, str(plist_path)], check=True)
            
            # Clean up temp file
            os.unlink(temp_path)
            
        except Exception as e:
            raise Exception(f"Error writing system plist file: {e}")
    
    def uninstall_service(self) -> bool:
        """Uninstall launchd service"""
        try:
            # Stop and unload service first
            self.stop_service()
            self._unload_service()
            
            # Remove plist file
            if self.system_plist_path.exists():
                subprocess.run(['sudo', 'rm', str(self.system_plist_path)], check=True)
            elif self.user_plist_path.exists():
                self.user_plist_path.unlink()
            
            self.logger.info(f"macOS launchd service '{self.service_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall macOS launchd service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start launchd service"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'load', '-w', str(self.user_plist_path)], check=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'load', '-w', str(self.system_plist_path)], check=True)
            
            self.logger.info(f"macOS launchd service '{self.service_name}' started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start macOS launchd service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop launchd service"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'unload', str(self.user_plist_path)], check=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'unload', str(self.system_plist_path)], check=True)
            
            self.logger.info(f"macOS launchd service '{self.service_name}' stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop macOS launchd service: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart launchd service"""
        try:
            # Stop and start the service
            self.stop_service()
            
            # Wait a moment before restarting
            import time
            time.sleep(2)
            
            return self.start_service()
            
        except Exception as e:
            self.logger.error(f"Failed to restart macOS launchd service: {e}")
            return False
    
    def get_service_status(self) -> ServiceStatus:
        """Get launchd service status"""
        try:
            # Use launchctl list to check service status
            result = subprocess.run(
                ['launchctl', 'list', self.service_identifier],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Service is loaded, check if it's running
                output = result.stdout
                if '"PID"' in output and '"PID" = 0' not in output:
                    return ServiceStatus.RUNNING
                else:
                    return ServiceStatus.STOPPED
            else:
                # Service not loaded
                return ServiceStatus.STOPPED
                
        except Exception as e:
            self.logger.error(f"Failed to get macOS launchd service status: {e}")
            return ServiceStatus.ERROR
    
    def is_service_installed(self) -> bool:
        """Check if launchd service is installed"""
        return self.system_plist_path.exists() or self.user_plist_path.exists()
    
    def _is_user_service(self) -> bool:
        """Check if this is a user service"""
        return self.user_plist_path.exists() and not self.system_plist_path.exists()
    
    def _load_service(self) -> bool:
        """Load launchd service"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'load', str(self.user_plist_path)], check=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'load', str(self.system_plist_path)], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to load service: {e}")
            return False
    
    def _unload_service(self) -> bool:
        """Unload launchd service"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'unload', str(self.user_plist_path)], check=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'unload', str(self.system_plist_path)], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to unload service: {e}")
            return False
    
    def get_service_logs(self, lines: int = 50) -> str:
        """Get recent service logs"""
        try:
            log_path = f'/usr/local/var/log/emotiv-lsl/{self.service_name}.log'
            
            if os.path.exists(log_path):
                result = subprocess.run(
                    ['tail', '-n', str(lines), log_path],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error reading log file: {result.stderr}"
            else:
                return f"Log file not found: {log_path}"
                
        except Exception as e:
            return f"Error getting service logs: {e}"
    
    def bootstrap_service(self) -> bool:
        """Bootstrap the service (macOS 10.11+)"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'bootstrap', 'gui/$(id -u)', str(self.user_plist_path)], check=True, shell=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'bootstrap', 'system', str(self.system_plist_path)], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to bootstrap service: {e}")
            return False
    
    def bootout_service(self) -> bool:
        """Bootout the service (macOS 10.11+)"""
        try:
            if self._is_user_service():
                subprocess.run(['launchctl', 'bootout', 'gui/$(id -u)', self.service_identifier], check=True, shell=True)
            else:
                subprocess.run(['sudo', 'launchctl', 'bootout', 'system', self.service_identifier], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to bootout service: {e}")
            return False