"""
Main entry point for Emotiv LSL Service

Provides command-line interface for service management operations.
Handles cross-platform service installation, start, stop, and status operations.
"""

import sys
import logging
import argparse
from typing import Optional

from .service_manager import EmotivLSLService
from .service_controller import ServiceController
from .service_wrapper import EmotivServiceWrapper
from .platform_adapter import detect_platform

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for service management"""
    parser = argparse.ArgumentParser(
        description='Emotiv LSL Service Management',
        prog='python -m emotiv_lsl.service'
    )
    
    parser.add_argument(
        'command',
        choices=['install', 'uninstall', 'start', 'stop', 'restart', 'status', 'run'],
        help='Service management command'
    )
    
    parser.add_argument(
        '--service-name',
        default='EmotivLSLService',
        help='Service name (default: EmotivLSLService)'
    )
    
    parser.add_argument(
        '--display-name',
        default='Emotiv LSL Data Capture Service',
        help='Service display name'
    )
    
    parser.add_argument(
        '--description',
        default='Captures EEG data from Emotiv devices and streams via LSL',
        help='Service description'
    )
    
    parser.add_argument(
        '--user-service',
        action='store_true',
        help='Install as user service (Linux/macOS only)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create service manager
    service_manager = EmotivLSLService(
        service_name=args.service_name,
        display_name=args.display_name,
        description=args.description
    )
    
    # Execute command
    try:
        if args.command == 'install':
            success = install_service(service_manager, args)
        elif args.command == 'uninstall':
            success = uninstall_service(service_manager)
        elif args.command == 'start':
            success = start_service(service_manager)
        elif args.command == 'stop':
            success = stop_service(service_manager)
        elif args.command == 'restart':
            success = restart_service(service_manager)
        elif args.command == 'status':
            success = show_status(service_manager)
        elif args.command == 'run':
            success = run_service_directly(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {e}")
        sys.exit(1)


def install_service(service_manager: EmotivLSLService, args) -> bool:
    """Install the service"""
    logger.info(f"Installing service on {detect_platform()}")
    
    kwargs = {}
    if args.user_service:
        kwargs['user_service'] = True
    
    success = service_manager.install(**kwargs)
    
    if success:
        logger.info("Service installed successfully")
        logger.info("Use 'start' command to start the service")
    else:
        logger.error("Failed to install service")
    
    return success


def uninstall_service(service_manager: EmotivLSLService) -> bool:
    """Uninstall the service"""
    logger.info("Uninstalling service")
    
    success = service_manager.uninstall()
    
    if success:
        logger.info("Service uninstalled successfully")
    else:
        logger.error("Failed to uninstall service")
    
    return success


def start_service(service_manager: EmotivLSLService) -> bool:
    """Start the service"""
    logger.info("Starting service")
    
    success = service_manager.start()
    
    if success:
        logger.info("Service started successfully")
    else:
        logger.error("Failed to start service")
    
    return success


def stop_service(service_manager: EmotivLSLService) -> bool:
    """Stop the service"""
    logger.info("Stopping service")
    
    success = service_manager.stop()
    
    if success:
        logger.info("Service stopped successfully")
    else:
        logger.error("Failed to stop service")
    
    return success


def restart_service(service_manager: EmotivLSLService) -> bool:
    """Restart the service"""
    logger.info("Restarting service")
    
    success = service_manager.restart()
    
    if success:
        logger.info("Service restarted successfully")
    else:
        logger.error("Failed to restart service")
    
    return success


def show_status(service_manager: EmotivLSLService) -> bool:
    """Show service status"""
    try:
        status = service_manager.get_status()
        
        print(f"Service Name: {status['service_name']}")
        print(f"Display Name: {status['display_name']}")
        print(f"Status: {status['status']}")
        print(f"Installed: {status['is_installed']}")
        print(f"Platform: {status['platform']}")
        
        if 'platform_version' in status:
            print(f"Platform Version: {status['platform_version']}")
        
        if 'error' in status:
            print(f"Error: {status['error']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return False


def run_service_directly(args) -> bool:
    """Run the service directly (not as a system service)"""
    logger.info("Running Emotiv LSL service directly")
    
    try:
        # Create service controller
        controller = ServiceController(args.service_name)
        
        # Create service wrapper
        wrapper = EmotivServiceWrapper()
        
        # Set up service controller
        def service_main(shutdown_event):
            wrapper.start(shutdown_event)
            shutdown_event.wait()
            wrapper.stop()
        
        controller.set_service_main_function(service_main)
        controller.set_shutdown_callback(lambda: wrapper.stop())
        
        # Start service
        if not controller.start_service():
            logger.error("Failed to start service controller")
            return False
        
        logger.info("Service running. Press Ctrl+C to stop.")
        
        # Wait for shutdown
        controller.wait_for_shutdown()
        
        # Stop service
        controller.stop_service()
        
        logger.info("Service stopped")
        return True
        
    except Exception as e:
        logger.error(f"Error running service directly: {e}")
        return False


if __name__ == '__main__':
    main()