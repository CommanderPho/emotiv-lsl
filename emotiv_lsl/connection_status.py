"""
Connection status monitoring for Emotiv headsets.

This module provides data structures and utilities for tracking connection
status, signal quality, and packet reception metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from collections import deque


@dataclass
class ConnectionStatus:
    """
    Tracks the current status and performance metrics of a device connection.
    
    This class maintains real-time information about connection health,
    including signal strength, packet reception rate, and error counts.
    """
    
    connected: bool = False
    connection_type: str = 'unknown'  # 'usb', 'ble', or 'auto'
    device_id: str = 'unknown'
    signal_strength: Optional[int] = None  # RSSI for BLE, None for USB
    packet_rate: float = 0.0  # Packets per second
    error_count: int = 0
    last_packet_time: Optional[datetime] = None
    
    # Internal tracking for packet rate calculation
    _packet_timestamps: deque = field(default_factory=lambda: deque(maxlen=1000), repr=False)
    
    def record_packet(self, timestamp: Optional[datetime] = None) -> None:
        """
        Record a successfully received packet.
        
        Args:
            timestamp: Time when packet was received. If None, uses current time.
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self.last_packet_time = timestamp
        self._packet_timestamps.append(timestamp)
    
    def record_error(self) -> None:
        """Increment the error counter for invalid or failed packets."""
        self.error_count += 1
    
    def calculate_packet_rate(self, window_seconds: float = 5.0) -> float:
        """
        Calculate the current packet reception rate.
        
        This method computes packets per second based on timestamps recorded
        within the specified time window.
        
        Args:
            window_seconds: Time window in seconds to calculate rate over.
                          Default is 5 seconds.
        
        Returns:
            float: Packet rate in packets per second (Hz).
        """
        if len(self._packet_timestamps) < 2:
            return 0.0
        
        now = datetime.now()
        cutoff_time = now.timestamp() - window_seconds
        
        # Count packets within the time window
        recent_packets = [
            ts for ts in self._packet_timestamps
            if ts.timestamp() >= cutoff_time
        ]
        
        if len(recent_packets) < 2:
            return 0.0
        
        # Calculate rate based on time span of recent packets
        time_span = recent_packets[-1].timestamp() - recent_packets[0].timestamp()
        
        if time_span > 0:
            # Subtract 1 because we're counting intervals between packets
            rate = (len(recent_packets) - 1) / time_span
            self.packet_rate = rate
            return rate
        
        return 0.0
    
    def update_from_device_info(self, device_info: dict) -> None:
        """
        Update connection status from device info dictionary.
        
        Args:
            device_info: Dictionary containing device information from
                        connection.get_device_info()
        """
        self.device_id = device_info.get('device_id', 'unknown')
        self.connection_type = device_info.get('connection_type', 'unknown')
        self.connected = device_info.get('connected', False)
        
        # Update signal strength if available (BLE only)
        if 'rssi' in device_info:
            self.signal_strength = device_info['rssi']
    
    def reset(self) -> None:
        """Reset all status metrics to initial values."""
        self.connected = False
        self.packet_rate = 0.0
        self.error_count = 0
        self.last_packet_time = None
        self._packet_timestamps.clear()
    
    def __str__(self) -> str:
        """Return a human-readable status summary."""
        status_parts = [
            f"Connected: {self.connected}",
            f"Type: {self.connection_type}",
            f"Device: {self.device_id}",
        ]
        
        if self.signal_strength is not None:
            status_parts.append(f"RSSI: {self.signal_strength} dBm")
        
        status_parts.extend([
            f"Rate: {self.packet_rate:.1f} Hz",
            f"Errors: {self.error_count}",
        ])
        
        if self.last_packet_time:
            elapsed = (datetime.now() - self.last_packet_time).total_seconds()
            status_parts.append(f"Last packet: {elapsed:.1f}s ago")
        
        return " | ".join(status_parts)
