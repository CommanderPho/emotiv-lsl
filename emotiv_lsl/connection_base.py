"""
Connection abstraction layer for Emotiv headsets.

This module provides an abstract base class for different connection types
(USB HID, BLE) and custom exception classes for connection error handling.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


# Custom Exception Classes
class EmotivConnectionError(Exception):
    """Base exception for all Emotiv connection-related errors."""
    pass


class DeviceNotFoundError(EmotivConnectionError):
    """Raised when no Emotiv device is found during discovery or connection."""
    pass


class ConnectionTimeoutError(EmotivConnectionError):
    """Raised when a connection attempt exceeds the timeout period."""
    pass


class PacketValidationError(EmotivConnectionError):
    """Raised when a received packet fails validation checks."""
    pass


class BLENotSupportedError(EmotivConnectionError):
    """Raised when BLE functionality is not available on the current platform."""
    pass


# Abstract Base Class
class EmotivConnectionBase(ABC):
    """
    Abstract base class defining the interface for Emotiv headset connections.
    
    This class provides a unified interface for different connection types
    (USB HID, BLE) to enable runtime selection and maintain consistent behavior
    across connection methods.
    """
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the Emotiv device.
        
        Returns:
            bool: True if connection was successful, False otherwise.
            
        Raises:
            DeviceNotFoundError: If no compatible device is found.
            ConnectionTimeoutError: If connection attempt times out.
            EmotivConnectionError: For other connection-related errors.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the connection to the device gracefully.
        
        This method should clean up all resources associated with the connection,
        including stopping notifications, closing clients, and releasing hardware.
        """
        pass
    
    @abstractmethod
    async def read_packet(self) -> Optional[bytes]:
        """
        Read one data packet from the device.
        
        Returns:
            Optional[bytes]: Raw packet data (typically 32 bytes for Emotiv devices),
                           or None if no packet is available or read times out.
                           
        Raises:
            EmotivConnectionError: If a critical error occurs during packet reading.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection to the device is currently active.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return device identification and status information.
        
        Returns:
            Dict[str, Any]: Dictionary containing device information such as:
                - 'device_id': Device identifier (serial number, MAC address, etc.)
                - 'device_name': Human-readable device name
                - 'connection_type': Type of connection ('usb', 'ble', etc.)
                - Additional connection-specific metadata
        """
        pass
