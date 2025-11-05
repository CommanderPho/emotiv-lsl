"""
Service Controller

Orchestrates all service components and manages the main service loop.
Coordinates shutdown procedures and handles service lifecycle.
"""

import logging
import signal
import sys
import threading
import time
from typing import Optional, Callable, Any
from .platform_adapter import ServiceStatus

logger = logging.getLogger(__name__)


class ServiceController:
    """Controls the main service execution and coordinates all components"""
    
    def __init__(self, service_name: str = "EmotivLSLService"):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Service state
        self._running = False
        self._shutdown_event = threading.Event()
        self._main_thread: Optional[threading.Thread] = None
        
        # Service components (to be set by service implementation)
        self._service_main_function: Optional[Callable] = None
        self._shutdown_callback: Optional[Callable] = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def set_service_main_function(self, main_function: Callable):
        """Set the main service function to run"""
        self._service_main_function = main_function
    
    def set_shutdown_callback(self, callback: Callable):
        """Set callback function to call during shutdown"""
        self._shutdown_callback = callback
    
    def start_service(self) -> bool:
        """Start the service controller"""
        if self._running:
            self.logger.warning("Service is already running")
            return True
            
        if self._service_main_function is None:
            self.logger.error("No service main function set")
            return False
        
        try:
            self.logger.info(f"Starting service controller for '{self.service_name}'")
            self._running = True
            self._shutdown_event.clear()
            
            # Start the main service loop in a separate thread
            self._main_thread = threading.Thread(
                target=self._run_service_loop,
                name=f"{self.service_name}-MainLoop",
                daemon=False
            )
            self._main_thread.start()
            
            self.logger.info("Service controller started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting service controller: {e}")
            self._running = False
            return False
    
    def stop_service(self) -> bool:
        """Stop the service controller"""
        if not self._running:
            self.logger.warning("Service is not running")
            return True
        
        try:
            self.logger.info(f"Stopping service controller for '{self.service_name}'")
            
            # Signal shutdown
            self._shutdown_event.set()
            self._running = False
            
            # Call shutdown callback if provided
            if self._shutdown_callback:
                try:
                    self._shutdown_callback()
                except Exception as e:
                    self.logger.error(f"Error in shutdown callback: {e}")
            
            # Wait for main thread to finish
            if self._main_thread and self._main_thread.is_alive():
                self.logger.info("Waiting for main service thread to finish...")
                self._main_thread.join(timeout=30)  # 30 second timeout
                
                if self._main_thread.is_alive():
                    self.logger.warning("Main service thread did not finish within timeout")
            
            self.logger.info("Service controller stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping service controller: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart the service controller"""
        self.logger.info("Restarting service controller")
        
        if not self.stop_service():
            return False
            
        # Wait a moment before restarting
        time.sleep(2)
        
        return self.start_service()
    
    def is_running(self) -> bool:
        """Check if the service controller is running"""
        return self._running and not self._shutdown_event.is_set()
    
    def get_status(self) -> ServiceStatus:
        """Get current service controller status"""
        if self.is_running():
            return ServiceStatus.RUNNING
        elif self._running and self._shutdown_event.is_set():
            return ServiceStatus.STOPPING
        else:
            return ServiceStatus.STOPPED
    
    def wait_for_shutdown(self):
        """Wait for shutdown signal (blocking)"""
        try:
            self._shutdown_event.wait()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            self._shutdown_event.set()
    
    def _run_service_loop(self):
        """Main service loop (runs in separate thread)"""
        try:
            self.logger.info("Starting main service loop")
            
            # Call the main service function
            if self._service_main_function:
                self._service_main_function(self._shutdown_event)
            else:
                # Default loop if no main function provided
                while not self._shutdown_event.is_set():
                    time.sleep(1)
            
            self.logger.info("Main service loop finished")
            
        except Exception as e:
            self.logger.error(f"Error in main service loop: {e}")
        finally:
            self._running = False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            self._shutdown_event.set()
        
        # Handle common shutdown signals
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)
        
        # Windows-specific signals
        if sys.platform == 'win32':
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, signal_handler)
    
    def handle_shutdown_signal(self, signum: int):
        """Handle shutdown signal"""
        self.logger.info(f"Handling shutdown signal {signum}")
        self._shutdown_event.set()