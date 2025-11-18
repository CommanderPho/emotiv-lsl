"""BLE configuration and optimization parameters for Emotiv headset connections."""

from dataclasses import dataclass


@dataclass
class BLEConfig:
    """Configuration parameters for BLE connection optimization.
    
    This dataclass contains all tunable parameters for BLE connectivity,
    including timeouts, reconnection behavior, signal quality thresholds,
    and low-latency connection intervals.
    
    Attributes:
        connection_timeout: Maximum time in seconds to wait for connection establishment
        discovery_timeout: Maximum time in seconds to scan for devices
        reconnect_attempts: Number of times to retry connection after failure
        reconnect_delay: Delay in seconds between reconnection attempts
        rssi_threshold: Minimum RSSI (signal strength) in dBm before warning
        connection_interval_min: Minimum BLE connection interval in milliseconds for low latency
        connection_interval_max: Maximum BLE connection interval in milliseconds
        packet_queue_size: Maximum number of packets to buffer in the notification queue
        packet_timeout: Timeout in seconds when waiting for packets from the queue
        rssi_check_interval: Interval in seconds between RSSI signal strength checks
    """
    
    # Connection timeouts
    connection_timeout: float = 10.0  # seconds
    discovery_timeout: float = 30.0  # seconds
    
    # Reconnection behavior
    reconnect_attempts: int = 3
    reconnect_delay: float = 5.0  # seconds
    
    # Signal quality monitoring
    rssi_threshold: int = -80  # dBm - warn if signal weaker than this
    rssi_check_interval: float = 10.0  # seconds between RSSI checks
    
    # Low-latency connection parameters
    connection_interval_min: float = 7.5  # milliseconds - minimum BLE connection interval
    connection_interval_max: float = 15.0  # milliseconds - maximum BLE connection interval
    
    # Packet handling
    packet_queue_size: int = 100  # maximum packets in buffer
    packet_timeout: float = 1.0  # seconds to wait for packet from queue
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        if self.discovery_timeout <= 0:
            raise ValueError("discovery_timeout must be positive")
        if self.reconnect_attempts < 0:
            raise ValueError("reconnect_attempts must be non-negative")
        if self.reconnect_delay < 0:
            raise ValueError("reconnect_delay must be non-negative")
        if self.rssi_threshold > 0:
            raise ValueError("rssi_threshold must be negative (dBm)")
        if self.connection_interval_min <= 0:
            raise ValueError("connection_interval_min must be positive")
        if self.connection_interval_max < self.connection_interval_min:
            raise ValueError("connection_interval_max must be >= connection_interval_min")
        if self.packet_queue_size <= 0:
            raise ValueError("packet_queue_size must be positive")
        if self.packet_timeout <= 0:
            raise ValueError("packet_timeout must be positive")


# Default configuration instance for convenience
DEFAULT_BLE_CONFIG = BLEConfig()
