"""
Linux systemd Service Adapter

Linux-specific service implementation using systemd.
Manages systemd service unit files and service control.
"""

import logging
import subprocess
import os
import pwd
import grp
from typing import Dict, Any, Optional
from pathlib import Path

from .platform_adapter import PlatformAdapter, ServiceStatus

logger = logging.getLogger(__name__)


class LinuxServiceAdapter(PlatformAdapter):
    """Linux systemd service adapter"""
    
    def __init__(self, service_name: str, display_name: str, description: str):
        super().__init__(service_name, display_name, description)
        self.service_file_name = f"{service_name.lower().replace(' ', '-')}.service"
        self.system_service_path = Path(f"/etc/systemd/system/{self.service_file_name}")
        self.user_service_path = Path(f"~/.config/systemd/user/{self.service_file_name}").expanduser()
        
    def install_service(self, executable_path: str, **kwargs) -> bool:
        """Install systemd service unit file"""
        try:
            # Determine if we should install as system or user service
            install_as_user = kwargs.get('user_service', False)
            user_name = kwargs.get('user', 'emotiv')
            group_name = kwargs.get('group', 'emotiv')
            
            if install_as_user:
                service_path = self.user_service_path
                service_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                service_path = self.system_service_path
                
            # Create systemd service unit content
            service_content = self._generate_service_unit_content(
                executable_path, user_name, group_name, **kwargs
            )
            
            # Write service file
            if install_as_user:
                service_path.write_text(service_content)
            else:
                # Need sudo for system service
                self._write_system_service_file(service_path, service_content)
            
            # Reload systemd daemon
            if install_as_user:
                subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            self.logger.info(f"Linux systemd service '{self.service_name}' installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install Linux systemd service: {e}")
            return False
    
    def _generate_service_unit_content(self, executable_path: str, user: str, group: str, **kwargs) -> str:
        """Generate systemd service unit file content"""
        working_dir = kwargs.get('working_directory', '/opt/emotiv-lsl')
        environment_vars = kwargs.get('environment', {})
        restart_policy = kwargs.get('restart_policy', 'always')
        restart_delay = kwargs.get('restart_delay', '10')
        
        # Build environment variables section
        env_section = ""
        if environment_vars:
            for key, value in environment_vars.items():
                env_section += f"Environment={key}={value}\n"
        
        service_content = f"""[Unit]
Description={self.description}
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
Group={group}
WorkingDirectory={working_dir}
ExecStart={executable_path} -m emotiv_lsl.service
Restart={restart_policy}
RestartSec={restart_delay}
StandardOutput=journal
StandardError=journal
{env_section}
# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/emotiv-lsl /var/run/emotiv-lsl

[Install]
WantedBy=multi-user.target
"""
        return service_content
    
    def _write_system_service_file(self, service_path: Path, content: str):
        """Write system service file with sudo"""
        try:
            # Use sudo to write the service file
            process = subprocess.Popen(
                ['sudo', 'tee', str(service_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=content)
            
            if process.returncode != 0:
                raise Exception(f"Failed to write service file: {stderr}")
                
        except Exception as e:
            raise Exception(f"Error writing system service file: {e}")
    
    def uninstall_service(self) -> bool:
        """Uninstall systemd service"""
        try:
            # Stop and disable service first
            self.stop_service()
            self._disable_service()
            
            # Remove service file
            if self.system_service_path.exists():
                subprocess.run(['sudo', 'rm', str(self.system_service_path)], check=True)
            elif self.user_service_path.exists():
                self.user_service_path.unlink()
            
            # Reload systemd daemon
            try:
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            except:
                subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
            
            self.logger.info(f"Linux systemd service '{self.service_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall Linux systemd service: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start systemd service"""
        try:
            if self._is_user_service():
                subprocess.run(['systemctl', '--user', 'start', self.service_file_name], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'start', self.service_file_name], check=True)
            
            self.logger.info(f"Linux systemd service '{self.service_name}' started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Linux systemd service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop systemd service"""
        try:
            if self._is_user_service():
                subprocess.run(['systemctl', '--user', 'stop', self.service_file_name], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'stop', self.service_file_name], check=True)
            
            self.logger.info(f"Linux systemd service '{self.service_name}' stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Linux systemd service: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart systemd service"""
        try:
            if self._is_user_service():
                subprocess.run(['systemctl', '--user', 'restart', self.service_file_name], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'restart', self.service_file_name], check=True)
            
            self.logger.info(f"Linux systemd service '{self.service_name}' restarted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart Linux systemd service: {e}")
            return False
    
    def get_service_status(self) -> ServiceStatus:
        """Get systemd service status"""
        try:
            if self._is_user_service():
                result = subprocess.run(
                    ['systemctl', '--user', 'is-active', self.service_file_name],
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['systemctl', 'is-active', self.service_file_name],
                    capture_output=True, text=True
                )
            
            status_output = result.stdout.strip().lower()
            
            if status_output == 'active':
                return ServiceStatus.RUNNING
            elif status_output == 'inactive':
                return ServiceStatus.STOPPED
            elif status_output == 'activating':
                return ServiceStatus.STARTING
            elif status_output == 'deactivating':
                return ServiceStatus.STOPPING
            elif status_output == 'failed':
                return ServiceStatus.ERROR
            else:
                return ServiceStatus.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"Failed to get Linux systemd service status: {e}")
            return ServiceStatus.ERROR
    
    def is_service_installed(self) -> bool:
        """Check if systemd service is installed"""
        return self.system_service_path.exists() or self.user_service_path.exists()
    
    def _is_user_service(self) -> bool:
        """Check if this is a user service"""
        return self.user_service_path.exists() and not self.system_service_path.exists()
    
    def _enable_service(self) -> bool:
        """Enable systemd service for automatic startup"""
        try:
            if self._is_user_service():
                subprocess.run(['systemctl', '--user', 'enable', self.service_file_name], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'enable', self.service_file_name], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable service: {e}")
            return False
    
    def _disable_service(self) -> bool:
        """Disable systemd service"""
        try:
            if self._is_user_service():
                subprocess.run(['systemctl', '--user', 'disable', self.service_file_name], check=True)
            else:
                subprocess.run(['sudo', 'systemctl', 'disable', self.service_file_name], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable service: {e}")
            return False
    
    def get_service_logs(self, lines: int = 50) -> str:
        """Get recent service logs from journald"""
        try:
            if self._is_user_service():
                result = subprocess.run(
                    ['journalctl', '--user', '-u', self.service_file_name, '-n', str(lines)],
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ['journalctl', '-u', self.service_file_name, '-n', str(lines)],
                    capture_output=True, text=True
                )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting logs: {result.stderr}"
                
        except Exception as e:
            return f"Error getting service logs: {e}"