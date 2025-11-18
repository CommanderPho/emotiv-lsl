"""
USB HID connection handler for Emotiv headsets.

This module provides a wrapper around the existing USB HID functionality,
implementing the EmotivConnectionBase interface for consistent connection handling.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

try:
    import hid
except ImportError:
    hid = None

from emotiv_lsl.connection_base import (
    EmotivConnectionBase,
    DeviceNotFoundError,
    EmotivConnectionError
)


logger = logging.getLogger(__name__)


class USBHIDConnection(EmotivConnectionBase):
    """
    USB HID connection handler for Emotiv headsets.
    
    This class wraps the existing USB HID device access logic and provides
    an async interface compatible with the connection abstraction layer.
    Maintains backward compatibility with the original synchronous USB implementation.
    """
    
    def __init__(self):
        """Initialize USB HID connection handler."""
        self.hid_device: Optional[hid.Device] = None
        self._connected: bool = False
        self._device_info: Optional[Dict[str, Any]] = None
        
    def _find_hid_device(self) -> Dict[str, Any]:
        """
        Find Emotiv device via USB HID enumeration.
        
        This method contains the existing logic from EmotivBase.get_hid_device()
        for finding Emotiv headsets connected via USB dongle.
        
        Returns:
            Dict[str, Any]: Device information dictionary from hid.enumerate()
            
        Raises:
            DeviceNotFoundError: If no Emotiv device is found
        """
        if hid is None:
            raise EmotivConnectionError(
                "hidapi library not available. Please install 'hid' package."
            )
            
        for device in hid.enumerate():
            manufacturer = device.get('manufacturer_string', '')
            usage = device.get('usage', 0)
            interface_number = device.get('interface_number', 0)
            
            # Match Emotiv devices with specific usage patterns
            if manufacturer == 'Emotiv' and (
                usage == 2 or (usage == 0 and interface_number == 1)
            ):
                logger.info(
                    f"Found Emotiv device: {device.get('product_string', 'Unknown')} "
                    f"(Serial: {device.get('serial_number', 'N/A')})"
                )
                return device
                
        raise DeviceNotFoundError('Emotiv Epoc X not found via USB')
    
    async def connect(self) -> bool:
        """
        Establish USB HID connection to Emotiv device.
        
        Returns:
            bool: True if connection was successful
            
        Raises:
            DeviceNotFoundError: If no Emotiv device is found
            EmotivConnectionError: If connection fails
        """
        try:
            # Find the device
            self._device_info = self._find_hid_device()
            
            # Open the HID device
            device_path = self._device_info['path']
            self.hid_device = hid.Device(path=device_path)
            
            self._connected = True
            logger.info(
                f"USB HID connection established: "
                f"{self._device_info.get('product_string', 'Emotiv Device')}"
            )
            return True
            
        except DeviceNotFoundError:
            raise
        except Exception as e:
            self._connected = False
            raise EmotivConnectionError(f"Failed to connect to USB HID device: {e}")
    
    async def disconnect(self) -> None:
        """
        Close USB HID connection gracefully.
        
        Closes the HID device handle and releases resources.
        """
        if self.hid_device is not None:
            try:
                self.hid_device.close()
                logger.info("USB HID connection closed")
            except Exception as e:
                logger.warning(f"Error closing USB HID device: {e}")
            finally:
                self.hid_device = None
                self._connected = False
    
    async def read_packet(self) -> Optional[bytes]:
        """
        Read one data packet from USB HID device.
        
        Wraps the synchronous hid.Device.read() call using asyncio.run_in_executor()
        to avoid blocking the event loop. This allows USB reads to work in an
        async context alongside BLE connections.
        
        Returns:
            Optional[bytes]: Raw packet data (32 bytes), or None if read fails/times out
            
        Raises:
            EmotivConnectionError: If device is not connected
        """
        if not self._connected or self.hid_device is None:
            raise EmotivConnectionError("USB HID device not connected")
        
        try:
            # Run blocking read in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                self.hid_device.read,
                32  # Read 32 bytes (standard Emotiv packet size)
            )
            
            if data:
                return bytes(data)
            return None
            
        except Exception as e:
            logger.error(f"Error reading from USB HID device: {e}")
            raise EmotivConnectionError(f"Failed to read packet: {e}")
    
    def is_connected(self) -> bool:
        """
        Check if USB HID connection is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self.hid_device is not None
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return USB HID device identification information.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - device_id: Serial number
                - device_name: Product string
                - connection_type: 'usb'
                - manufacturer: Manufacturer string
                - vendor_id: USB vendor ID
                - product_id: USB product ID
        """
        if self._device_info is None:
            return {
                'connection_type': 'usb',
                'connected': self._connected
            }
        
        return {
            'device_id': self._device_info.get('serial_number', 'Unknown'),
            'device_name': self._device_info.get('product_string', 'Emotiv Device'),
            'connection_type': 'usb',
            'manufacturer': self._device_info.get('manufacturer_string', 'Emotiv'),
            'vendor_id': self._device_info.get('vendor_id'),
            'product_id': self._device_info.get('product_id'),
            'connected': self._connected
        }
