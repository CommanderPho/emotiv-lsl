"""
Windows Service Implementation

Concrete Windows service class that integrates with Windows Service Control Manager.
Uses pywin32 framework for Windows service lifecycle management.
"""

import logging
import sys
import os
import threading
import time

# Setup logging before importing other modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\ProgramData\\EmotivLSL\\logs\\service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    PYWIN32_AVAILABLE = True
except ImportError:
    logger.warning("pywin32 not available - Windows service functionality disabled")
    PYWIN32_AVAILABLE = False
    # Create dummy classes to prevent import errors
    class win32serviceutil:
        class ServiceFramework: pass
    class win32service: pass
    class win32event: pass
    class servicemanager: pass


class EmotivLSLWindowsService(win32serviceutil.ServiceFramework):
    """Windows Service implementation for Emotiv LSL"""
    
    _svc_name_ = "EmotivLSLService"
    _svc_display_name_ = "Emotiv LSL Data Capture Service"
    _svc_description_ = "Captures EEG data from Emotiv devices and streams via LSL"
    
    def __init__(self, args):
        if not PYWIN32_AVAILABLE:
            raise ImportError("pywin32 is required for Windows service functionality")
            
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.running = False
        self.service_thread = None
        
    def SvcStop(self):
        """Called when the service is asked to stop"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Signal the main thread to stop
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        
        # Wait for service thread to finish
        if self.service_thread and self.service_thread.is_alive():
            self.service_thread.join(timeout=30)
        
        self.logger.info("Service stopped")
    
    def SvcDoRun(self):
        """Called when the service is asked to start"""
        self.logger.info("Service starting")
        
        # Log service start to Windows Event Log
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            self.running = True
            
            # Start the main service logic in a separate thread
            self.service_thread = threading.Thread(target=self._run_service_main, daemon=False)
            self.service_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f"Error in service main loop: {e}")
            servicemanager.LogErrorMsg(f"Service error: {e}")
        finally:
            self.logger.info("Service main loop finished")
    
    def _run_service_main(self):
        """Main service logic - runs the Emotiv LSL capture"""
        try:
            self.logger.info("Starting Emotiv LSL service main loop")
            
            # Import and run the main Emotiv LSL functionality
            from emotiv_lsl.service.service_wrapper import EmotivServiceWrapper
            
            # Create service wrapper
            wrapper = EmotivServiceWrapper()
            
            # Run the service until stop is requested
            while self.running and not win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
                try:
                    wrapper.run_iteration()
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                except Exception as e:
                    self.logger.error(f"Error in service iteration: {e}")
                    time.sleep(1)  # Wait longer on error
            
            # Clean shutdown
            wrapper.shutdown()
            self.logger.info("Service main loop completed")
            
        except Exception as e:
            self.logger.error(f"Fatal error in service main: {e}")
            servicemanager.LogErrorMsg(f"Fatal service error: {e}")


def main():
    """Main entry point for Windows service"""
    if not PYWIN32_AVAILABLE:
        print("Error: pywin32 is required for Windows service functionality")
        print("Install with: pip install pywin32")
        sys.exit(1)
    
    if len(sys.argv) == 1:
        # Called with no arguments - start the service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(EmotivLSLWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Called with arguments - handle install/remove/etc
        win32serviceutil.HandleCommandLine(EmotivLSLWindowsService)


if __name__ == '__main__':
    main()