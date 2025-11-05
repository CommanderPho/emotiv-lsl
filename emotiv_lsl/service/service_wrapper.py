"""
Service Wrapper for Emotiv LSL

Wraps existing EmotivBase/EmotivEpocX functionality for service context.
Provides service-specific error handling and monitoring capabilities.
"""

import logging
import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmotivServiceWrapper:
    """Wrapper for Emotiv LSL functionality in service context"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Service state
        self._running = False
        self._emotiv_device = None
        self._last_data_time = None
        self._error_count = 0
        self._recovery_count = 0
        
        # Threading
        self._main_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
    def initialize(self) -> bool:
        """Initialize the Emotiv device and service components"""
        try:
            self.logger.info("Initializing Emotiv LSL service wrapper")
            
            # Import and create Emotiv device
            from emotiv_lsl.emotiv_epoc_x import EmotivEpocX
            
            # Create device instance
            self._emotiv_device = EmotivEpocX(
                enable_debug_logging=False,
                enable_electrode_quality_stream=True,
                has_motion_data=True
            )
            
            self.logger.info("Emotiv device initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Emotiv device: {e}")
            self._error_count += 1
            return False
    
    def start(self, shutdown_event: Optional[threading.Event] = None) -> bool:
        """Start the service wrapper"""
        if self._running:
            self.logger.warning("Service wrapper is already running")
            return True
        
        if shutdown_event:
            self._shutdown_event = shutdown_event
        
        try:
            if not self.initialize():
                return False
            
            self.logger.info("Starting Emotiv LSL service wrapper")
            self._running = True
            
            # Start main loop in separate thread
            self._main_thread = threading.Thread(
                target=self._run_main_loop,
                name="EmotivServiceWrapper-MainLoop",
                daemon=False
            )
            self._main_thread.start()
            
            self.logger.info("Service wrapper started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service wrapper: {e}")
            self._running = False
            return False
    
    def stop(self) -> bool:
        """Stop the service wrapper"""
        if not self._running:
            self.logger.warning("Service wrapper is not running")
            return True
        
        try:
            self.logger.info("Stopping Emotiv LSL service wrapper")
            
            # Signal shutdown
            self._shutdown_event.set()
            self._running = False
            
            # Wait for main thread to finish
            if self._main_thread and self._main_thread.is_alive():
                self.logger.info("Waiting for main thread to finish...")
                self._main_thread.join(timeout=30)
                
                if self._main_thread.is_alive():
                    self.logger.warning("Main thread did not finish within timeout")
            
            self.logger.info("Service wrapper stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping service wrapper: {e}")
            return False
    
    def shutdown(self):
        """Clean shutdown of the service wrapper"""
        self.stop()
    
    def run_iteration(self):
        """Run a single iteration of the service (for Windows service)"""
        if not self._running:
            if not self.initialize():
                time.sleep(5)  # Wait before retry
                return
            self._running = True
        
        try:
            # This would be called repeatedly by Windows service
            # For now, just update last activity time
            self._last_data_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error in service iteration: {e}")
            self._error_count += 1
    
    def _run_main_loop(self):
        """Main service loop (runs in separate thread)"""
        try:
            self.logger.info("Starting Emotiv LSL main loop")
            
            if self._emotiv_device is None:
                self.logger.error("Emotiv device not initialized")
                return
            
            # Run the existing main_loop with error handling
            while self._running and not self._shutdown_event.is_set():
                try:
                    # Call the existing main_loop method
                    # We need to modify this to be interruptible
                    self._run_emotiv_main_loop_iteration()
                    
                except KeyboardInterrupt:
                    self.logger.info("Received keyboard interrupt in main loop")
                    break
                except Exception as e:
                    self.logger.error(f"Error in Emotiv main loop: {e}")
                    self._error_count += 1
                    
                    # Implement recovery logic
                    if self._attempt_recovery():
                        self._recovery_count += 1
                    else:
                        # If recovery fails, wait before retrying
                        time.sleep(5)
            
            self.logger.info("Emotiv LSL main loop finished")
            
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
        finally:
            self._running = False
    
    def _run_emotiv_main_loop_iteration(self):
        """Run a single iteration of the Emotiv main loop"""
        if self._emotiv_device is None:
            raise Exception("Emotiv device not initialized")
        
        # For now, we'll call the existing main_loop method
        # In a production implementation, we'd need to modify the main_loop
        # to be interruptible and run in iterations
        
        # This is a placeholder - the actual implementation would need
        # to break down the main_loop into smaller, interruptible pieces
        try:
            # Simulate data processing
            time.sleep(0.1)
            self._last_data_time = datetime.now()
            
        except Exception as e:
            raise Exception(f"Error in Emotiv main loop iteration: {e}")
    
    def _attempt_recovery(self) -> bool:
        """Attempt to recover from errors"""
        try:
            self.logger.info("Attempting service recovery")
            
            # Try to reinitialize the device
            if self.initialize():
                self.logger.info("Service recovery successful")
                return True
            else:
                self.logger.error("Service recovery failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during recovery attempt: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service wrapper status"""
        return {
            'running': self._running,
            'device_initialized': self._emotiv_device is not None,
            'last_data_time': self._last_data_time.isoformat() if self._last_data_time else None,
            'error_count': self._error_count,
            'recovery_count': self._recovery_count,
            'uptime_seconds': (datetime.now() - self._last_data_time).total_seconds() if self._last_data_time else 0
        }
    
    def is_healthy(self) -> bool:
        """Check if the service wrapper is healthy"""
        if not self._running:
            return False
        
        if self._emotiv_device is None:
            return False
        
        # Check if we've received data recently (within last 30 seconds)
        if self._last_data_time:
            time_since_data = (datetime.now() - self._last_data_time).total_seconds()
            if time_since_data > 30:
                return False
        
        return True