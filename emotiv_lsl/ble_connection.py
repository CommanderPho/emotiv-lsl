"""
BLE (Bluetooth Low Energy) connection handler for Emotiv headsets.

This module implements BLE connectivity for Emotiv EPOC X headsets using the
bleak library for cross-platform BLE support.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from .connection_base import (
    EmotivConnectionBase,
    DeviceNotFoundError,
    ConnectionTimeoutError,
    EmotivConnectionError
)


logger = logging.getLogger(__name__)


@dataclass
class BLEDeviceInfo:
    """Information about a discovered BLE device."""
    name: str
    address: str  # MAC address
    rssi: int  # Signal strength in dBm
    
    def __str__(self) -> str:
        return f"{self.name} ({self.address}) - RSSI: {self.rssi} dBm"


class BLEConnection(EmotivConnectionBase):
    """
    BLE connection handler for Emotiv EPOC X headsets.
    
    This class manages BLE device discovery, connection establishment,
    GATT characteristic subscriptions, and packet reception via notifications.
    """
    
    # UUIDs to be discovered/documented - placeholders for now
    EMOTIV_SERVICE_UUID = "81072f40-9f3d-11e3-a9dc-0002a5d5c51b"  # Main (Device) service UUID
    EEG_CHARACTERISTIC_UUID = "81072f41-9f3d-11e3-a9dc-0002a5d5c51b"  # EEG (Data) data characteristic
    MOTION_CHARACTERISTIC_UUID = "81072f42-9f3d-11e3-a9dc-0002a5d5c51b"  # Motion (MEMS) data characteristic
    
    def __init__(self, device_address: Optional[str] = None):
        """
        Initialize BLE connection handler.
        
        Args:
            device_address: Optional MAC address of specific device to connect to.
                          If None, will discover and connect to first available device.
        """
        self.device_address = device_address
        self.client: Optional[BleakClient] = None
        self.packet_queue: Optional[asyncio.Queue] = None
        self._connected = False
        self.rssi = 0
        self.device_name = ""
        
        # Metadata for latency tracking
        self._last_notification_time = None
        self._last_sender = None
        
    async def discover_devices(self, timeout: float = 30.0) -> List[BLEDeviceInfo]:
        """
        Scan for Emotiv headsets via BLE.
        
        Args:
            timeout: Maximum time in seconds to scan for devices.
            
        Returns:
            List of BLEDeviceInfo objects for discovered Emotiv headsets.
            
        Raises:
            DeviceNotFoundError: If no Emotiv headsets are found within timeout.
        """
        logger.info(f"Scanning for Emotiv headsets (timeout: {timeout}s)...")
        
        try:
            devices = await BleakScanner.discover(timeout=timeout)
        except Exception as e:
            logger.error(f"BLE scan failed: {e}")
            raise EmotivConnectionError(f"BLE scan failed: {e}")
        
        # Filter for Emotiv devices (name contains 'EPOC')
        emotiv_devices = []
        for device in devices:
            if device.name and 'EPOC' in device.name.upper():
                device_info = BLEDeviceInfo(
                    name=device.name,
                    address=device.address,
                    rssi=device.rssi if hasattr(device, 'rssi') else 0
                )
                emotiv_devices.append(device_info)
                logger.info(f"Found Emotiv device: {device_info}")
        
        if not emotiv_devices:
            raise DeviceNotFoundError(
                "No Emotiv EPOC X headsets found via Bluetooth. "
                "Ensure the headset is powered on and in pairing mode."
            )
        
        logger.info(f"Discovered {len(emotiv_devices)} Emotiv device(s)")
        return emotiv_devices

    async def connect(self) -> bool:
        """
        Establish BLE connection to Emotiv headset.
        
        If no device address was specified during initialization, this method
        will first discover available devices and connect to the first one found.
        
        Returns:
            bool: True if connection was successful.
            
        Raises:
            DeviceNotFoundError: If no Emotiv device is found.
            ConnectionTimeoutError: If connection attempt times out.
            EmotivConnectionError: For other connection-related errors.
        """
        # If no device address specified, discover devices first
        if not self.device_address:
            logger.info("No device address specified, discovering devices...")
            devices = await self.discover_devices()
            if not devices:
                raise DeviceNotFoundError("No Emotiv EPOC X headsets found")
            # Connect to first discovered device
            self.device_address = devices[0].address
            self.device_name = devices[0].name
            self.rssi = devices[0].rssi
            logger.info(f"Selected device: {devices[0]}")
        
        logger.info(f"Connecting to device at {self.device_address}...")
        
        try:
            # Create BleakClient with timeout
            self.client = BleakClient(self.device_address, timeout=10.0)
            await self.client.connect()
            
            if not self.client.is_connected:
                raise ConnectionTimeoutError(
                    f"Failed to connect to device at {self.device_address}"
                )
            
            logger.info(f"Successfully connected to {self.device_address}")
            
            # Initialize packet queue
            self.packet_queue = asyncio.Queue(maxsize=100)
            
            # Subscribe to GATT characteristics for notifications
            # Note: UUIDs are placeholders and need to be discovered
            if self.EEG_CHARACTERISTIC_UUID != "TBD":
                await self.client.start_notify(
                    self.EEG_CHARACTERISTIC_UUID,
                    self._notification_handler
                )
                logger.info(f"Subscribed to EEG characteristic: {self.EEG_CHARACTERISTIC_UUID}")
            
            if self.MOTION_CHARACTERISTIC_UUID != "TBD":
                await self.client.start_notify(
                    self.MOTION_CHARACTERISTIC_UUID,
                    self._notification_handler
                )
                logger.info(f"Subscribed to motion characteristic: {self.MOTION_CHARACTERISTIC_UUID}")
            
            # Mark as connected
            self._connected = True
            
            logger.info("BLE connection established successfully")
            return True
            
        except asyncio.TimeoutError:
            raise ConnectionTimeoutError(
                f"Connection to {self.device_address} timed out after 10 seconds"
            )
        except Exception as e:
            logger.error(f"BLE connection failed: {e}")
            raise EmotivConnectionError(f"BLE connection failed: {e}")

    def _notification_handler(self, sender, data: bytearray) -> None:
        """
        Handle incoming BLE notifications from GATT characteristics.
        
        This callback is invoked when the headset sends data via BLE notifications.
        Packets are queued for processing by the main loop.
        
        Args:
            sender: The characteristic handle that sent the notification.
            data: Raw packet data received from the device.
        """
        from datetime import datetime
        
        notification_time = datetime.now()
        
        try:
            # Convert bytearray to bytes and queue it
            packet = bytes(data)
            
            # Store notification timestamp with packet for latency tracking
            packet_with_metadata = (packet, notification_time, sender)
            self.packet_queue.put_nowait(packet_with_metadata)
            
            logger.debug(f"Queued packet from {sender}: {len(packet)} bytes")
        except asyncio.QueueFull:
            logger.warning(
                "Packet queue full (100 packets), dropping packet. "
                "This may indicate the processing loop is too slow."
            )
    
    async def read_packet(self) -> Optional[bytes]:
        """
        Read one data packet from the queue.
        
        This method retrieves packets that were received via BLE notifications
        and queued by the notification handler.
        
        Returns:
            Optional[bytes]: Raw packet data (typically 32 bytes), or None if
                           no packet is available within the timeout period.
        """
        if not self._connected or self.packet_queue is None:
            return None
        
        try:
            # Wait up to 1 second for a packet
            packet_data = await asyncio.wait_for(
                self.packet_queue.get(),
                timeout=1.0
            )
            
            # Extract packet and metadata if available
            if isinstance(packet_data, tuple) and len(packet_data) == 3:
                packet, notification_time, sender = packet_data
                
                # Store metadata for potential latency tracking
                self._last_notification_time = notification_time
                self._last_sender = sender
                
                return packet
            else:
                # Fallback for packets without metadata
                return packet_data
                
        except asyncio.TimeoutError:
            # No packet available within timeout - this is normal
            return None
        except Exception as e:
            logger.error(f"Error reading packet from queue: {e}")
            return None

    async def disconnect(self) -> None:
        """
        Close the BLE connection gracefully.
        
        This method stops all notifications, disconnects the BleakClient,
        and cleans up resources.
        """
        if not self._connected:
            logger.info("Already disconnected")
            return
        
        logger.info("Disconnecting from BLE device...")
        
        try:
            if self.client and self.client.is_connected:
                # Stop notifications if UUIDs are configured
                if self.EEG_CHARACTERISTIC_UUID != "TBD":
                    try:
                        await self.client.stop_notify(self.EEG_CHARACTERISTIC_UUID)
                        logger.debug("Stopped EEG notifications")
                    except Exception as e:
                        logger.warning(f"Error stopping EEG notifications: {e}")
                
                if self.MOTION_CHARACTERISTIC_UUID != "TBD":
                    try:
                        await self.client.stop_notify(self.MOTION_CHARACTERISTIC_UUID)
                        logger.debug("Stopped motion notifications")
                    except Exception as e:
                        logger.warning(f"Error stopping motion notifications: {e}")
                
                # Disconnect the client
                await self.client.disconnect()
                logger.info("BLE client disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._connected = False
            self.client = None
            self.packet_queue = None
    
    def is_connected(self) -> bool:
        """
        Check if the BLE connection is currently active.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        return self._connected and self.client is not None and self.client.is_connected
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return device identification and status information.
        
        Returns:
            Dict containing device information including MAC address, name,
            connection type, and signal strength.
        """
        return {
            'device_id': self.device_address or 'Unknown',
            'device_name': self.device_name or 'Unknown',
            'connection_type': 'ble',
            'rssi': self.rssi,
            'connected': self._connected
        }
    
    async def monitor_rssi(self, interval: float = 10.0, threshold: int = -80) -> None:
        """
        Monitor RSSI (signal strength) periodically.
        
        This method should be run as a background task to continuously monitor
        the connection quality.
        
        Args:
            interval: Time in seconds between RSSI checks.
            threshold: RSSI threshold in dBm below which to log warnings.
        """
        logger.info(f"Starting RSSI monitoring (interval: {interval}s, threshold: {threshold} dBm)")
        
        while self._connected:
            try:
                if self.client and self.client.is_connected:
                    # Note: Not all BLE backends support RSSI reading during connection
                    # This is a placeholder for platforms that support it
                    # On some platforms, we may need to use platform-specific APIs
                    
                    # For now, log the last known RSSI from discovery
                    if self.rssi < threshold:
                        logger.warning(
                            f"Weak signal strength detected: RSSI = {self.rssi} dBm "
                            f"(threshold: {threshold} dBm). Connection may be unstable."
                        )
                    else:
                        logger.debug(f"Signal strength: RSSI = {self.rssi} dBm")
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error monitoring RSSI: {e}")
                await asyncio.sleep(interval)
