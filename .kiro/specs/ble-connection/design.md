# Design Document

## Overview

This design implements BLE connectivity for Emotiv EPOC X headsets by creating a parallel connection pathway alongside the existing USB HID implementation. The architecture uses the bleak library for cross-platform BLE support and maintains the existing EmotivBase abstraction to ensure LSL stream compatibility. The design introduces a connection abstraction layer that allows runtime selection between USB HID and BLE while preserving all existing functionality.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│                  (Application Entry)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Connection Manager                          │
│  - Parse connection type (usb/ble/auto)                     │
│  - Instantiate appropriate connection class                  │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐   ┌──────────────────────────────┐
│   EmotivEpocXUSB       │   │    EmotivEpocXBLE            │
│   (USB HID)            │   │    (Bluetooth LE)            │
│                        │   │                              │
│ - hid.Device           │   │ - BleakClient                │
│ - Synchronous read     │   │ - Async notifications        │
└────────┬───────────────┘   └──────────┬───────────────────┘
         │                              │
         └──────────────┬───────────────┘
                        ▼
         ┌──────────────────────────────┐
         │      EmotivBase              │
         │  (Shared Logic)              │
         │                              │
         │ - Packet decryption (AES)    │
         │ - Data decoding              │
         │ - LSL stream setup           │
         │ - Quality extraction         │
         └──────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │    LSL StreamOutlets         │
         │                              │
         │ - EEG (128Hz, 14 channels)   │
         │ - Motion (16Hz, 6 channels)  │
         │ - Quality (128Hz, 14 ch)     │
         └──────────────────────────────┘
```

### Connection Abstraction Strategy

Rather than modifying EmotivBase extensively, we create two concrete implementations:
- **EmotivEpocXUSB**: Wraps existing USB HID logic (minimal changes to current code)
- **EmotivEpocXBLE**: New BLE implementation using bleak

Both inherit from EmotivBase and override the connection-specific methods while sharing decryption, decoding, and LSL streaming logic.

## Components and Interfaces

### 1. EmotivConnectionBase (Abstract Interface)

New abstract base class defining the connection interface:

```python
from abc import ABC, abstractmethod
from typing import Optional

class EmotivConnectionBase(ABC):
    """Abstract interface for Emotiv headset connections"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection gracefully"""
        pass
    
    @abstractmethod
    async def read_packet(self) -> Optional[bytes]:
        """Read one data packet (32 bytes)"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active"""
        pass
    
    @abstractmethod
    def get_device_info(self) -> dict:
        """Return device identification info"""
        pass
```

### 2. BLEConnection (BLE Implementation)

```python
from bleak import BleakClient, BleakScanner
import asyncio
from typing import Optional, Callable

class BLEConnection(EmotivConnectionBase):
    """BLE connection handler for Emotiv EPOC X"""
    
    # UUIDs to be discovered/documented
    EMOTIV_SERVICE_UUID = "TBD"  # Main service UUID
    EEG_CHARACTERISTIC_UUID = "TBD"  # EEG data characteristic
    MOTION_CHARACTERISTIC_UUID = "TBD"  # Motion data characteristic
    
    def __init__(self, device_address: Optional[str] = None):
        self.device_address = device_address
        self.client: Optional[BleakClient] = None
        self.packet_queue = asyncio.Queue(maxsize=100)
        self._connected = False
        self.rssi = 0
        
    async def discover_devices(self, timeout: float = 30.0) -> list:
        """Scan for Emotiv headsets"""
        devices = await BleakScanner.discover(timeout=timeout)
        emotiv_devices = [
            d for d in devices 
            if d.name and 'EPOC' in d.name.upper()
        ]
        return emotiv_devices
    
    async def connect(self) -> bool:
        """Establish BLE connection"""
        if not self.device_address:
            devices = await self.discover_devices()
            if not devices:
                raise DeviceNotFoundError("No Emotiv EPOC X headsets found")
            self.device_address = devices[0].address
            
        self.client = BleakClient(self.device_address)
        await self.client.connect(timeout=10.0)
        
        # Subscribe to notifications
        await self.client.start_notify(
            self.EEG_CHARACTERISTIC_UUID,
            self._notification_handler
        )
        
        self._connected = True
        return True
    
    def _notification_handler(self, sender, data: bytearray):
        """Handle incoming BLE notifications"""
        try:
            self.packet_queue.put_nowait(bytes(data))
        except asyncio.QueueFull:
            logging.warning("Packet queue full, dropping packet")
    
    async def read_packet(self) -> Optional[bytes]:
        """Read packet from queue"""
        try:
            packet = await asyncio.wait_for(
                self.packet_queue.get(),
                timeout=1.0
            )
            return packet
        except asyncio.TimeoutError:
            return None
```

### 3. USBHIDConnection (USB Wrapper)

Wraps existing USB HID logic:

```python
import hid

class USBHIDConnection(EmotivConnectionBase):
    """USB HID connection handler (wraps existing code)"""
    
    def __init__(self):
        self.hid_device: Optional[hid.Device] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """Establish USB HID connection"""
        device_info = self._find_hid_device()
        self.hid_device = hid.Device(path=device_info['path'])
        self._connected = True
        return True
    
    def _find_hid_device(self) -> dict:
        """Find Emotiv device (existing logic)"""
        for device in hid.enumerate():
            if (device.get('manufacturer_string') == 'Emotiv' and 
                (device.get('usage') == 2 or 
                 (device.get('usage') == 0 and device.get('interface_number') == 1))):
                return device
        raise DeviceNotFoundError("Emotiv Epoc X not found via USB")
    
    async def read_packet(self) -> Optional[bytes]:
        """Read packet from USB (wraps synchronous read)"""
        if not self.hid_device:
            return None
        # Run blocking read in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, 
            self.hid_device.read, 
            32
        )
        return bytes(data) if data else None
```

### 4. Modified EmotivBase

Update EmotivBase to use connection abstraction:

```python
@define(slots=False)
class EmotivBase(EasyTimeSyncParsingMixin):
    connection: EmotivConnectionBase = field(default=None)
    connection_type: str = field(default='usb')  # 'usb', 'ble', 'auto'
    
    # ... existing fields ...
    
    async def initialize_connection(self):
        """Set up connection based on connection_type"""
        if self.connection_type == 'ble':
            self.connection = BLEConnection()
        elif self.connection_type == 'usb':
            self.connection = USBHIDConnection()
        elif self.connection_type == 'auto':
            # Try BLE first, fall back to USB
            try:
                self.connection = BLEConnection()
                await self.connection.connect()
            except (DeviceNotFoundError, Exception) as e:
                logging.info(f"BLE connection failed: {e}, trying USB")
                self.connection = USBHIDConnection()
                await self.connection.connect()
        
        await self.connection.connect()
    
    async def main_loop_async(self):
        """Async version of main loop"""
        await self.initialize_connection()
        
        # Create LSL outlets (same as before)
        eeg_outlet = StreamOutlet(self.get_lsl_outlet_eeg_stream_info())
        motion_outlet = None
        if self.has_motion_data:
            motion_outlet = StreamOutlet(self.get_lsl_outlet_motion_stream_info())
        
        packet_count = 0
        reconnect_attempts = 0
        max_reconnect_attempts = 3
        
        while True:
            try:
                data = await self.connection.read_packet()
                
                if data is None:
                    continue
                
                packet_count += 1
                
                if self.validate_data(data):
                    decoded, quality = self.decode_data(data)
                    
                    if decoded and len(decoded) == 14:
                        eeg_outlet.push_sample(decoded)
                    elif decoded and len(decoded) == 6:
                        if motion_outlet is None:
                            motion_outlet = StreamOutlet(
                                self.get_lsl_outlet_motion_stream_info()
                            )
                        motion_outlet.push_sample(decoded)
                    
                    if quality is not None:
                        # Handle quality data
                        pass
                        
            except ConnectionError as e:
                logging.error(f"Connection lost: {e}")
                reconnect_attempts += 1
                
                if reconnect_attempts >= max_reconnect_attempts:
                    logging.error("Max reconnection attempts reached")
                    break
                
                logging.info(f"Attempting reconnection {reconnect_attempts}/{max_reconnect_attempts}")
                await asyncio.sleep(5)
                await self.connection.connect()
                reconnect_attempts = 0
```

## Data Models

### BLE Device Info

```python
@dataclass
class BLEDeviceInfo:
    """Information about discovered BLE device"""
    name: str
    address: str  # MAC address
    rssi: int  # Signal strength
    services: List[str]  # Service UUIDs
```

### Connection Status

```python
@dataclass
class ConnectionStatus:
    """Current connection state"""
    connected: bool
    connection_type: str  # 'usb' or 'ble'
    device_id: str  # Serial number or MAC address
    signal_strength: Optional[int]  # RSSI for BLE, None for USB
    packet_rate: float  # Packets per second
    error_count: int
    last_packet_time: datetime
```

### Configuration

```python
@dataclass
class BLEConfig:
    """BLE connection configuration"""
    connection_timeout: float = 10.0
    discovery_timeout: float = 30.0
    reconnect_attempts: int = 3
    reconnect_delay: float = 5.0
    min_rssi_threshold: int = -80
    connection_interval_min: float = 7.5  # milliseconds
    connection_interval_max: float = 15.0
```

## Error Handling

### Exception Hierarchy

```python
class EmotivConnectionError(Exception):
    """Base exception for connection errors"""
    pass

class DeviceNotFoundError(EmotivConnectionError):
    """No Emotiv device found"""
    pass

class ConnectionTimeoutError(EmotivConnectionError):
    """Connection attempt timed out"""
    pass

class PacketValidationError(EmotivConnectionError):
    """Invalid packet structure"""
    pass

class BLENotSupportedError(EmotivConnectionError):
    """BLE not available on this platform"""
    pass
```

### Error Recovery Strategy

1. **Connection Loss**: Automatic reconnection with exponential backoff (5s, 10s, 15s)
2. **Invalid Packets**: Log and skip, increment error counter
3. **Queue Overflow**: Drop oldest packets, log warning
4. **GATT Errors**: Log error, continue operation
5. **Discovery Timeout**: Raise DeviceNotFoundError with helpful message

### Logging Strategy

```python
# Connection events
logger.info(f"BLE connection established: {device_name} ({mac_address})")
logger.warning(f"Weak signal strength: RSSI={rssi} dBm")
logger.error(f"Connection lost after {packet_count} packets")

# Performance monitoring
logger.debug(f"Packet rate: {rate:.1f} Hz (expected: 128 Hz)")
logger.warning(f"Latency spike detected: {latency_ms:.1f} ms")

# Debug mode
if self.enable_debug_logging:
    logger.debug(f"Raw BLE packet: {data.hex()}")
```

## Testing Strategy

### Unit Tests

1. **BLEConnection Tests**
   - Mock BleakClient for connection testing
   - Test notification handler with sample packets
   - Test queue overflow behavior
   - Test reconnection logic

2. **USBHIDConnection Tests**
   - Mock hid.Device for USB testing
   - Verify backward compatibility
   - Test device enumeration

3. **Packet Decoding Tests**
   - Verify identical output for USB and BLE packets
   - Test with known sample data
   - Validate quality extraction

### Integration Tests

1. **End-to-End BLE Flow**
   - Connect to real/simulated device
   - Verify LSL stream creation
   - Validate data integrity
   - Test disconnection handling

2. **Connection Switching**
   - Test auto mode fallback
   - Verify clean resource cleanup
   - Test concurrent connection attempts

3. **Cross-Platform Tests**
   - Windows: Native BLE stack
   - macOS: Core Bluetooth
   - Linux: BlueZ integration

### Manual Testing Checklist

- [ ] BLE device discovery finds headset
- [ ] Connection establishes within timeout
- [ ] EEG data streams at 128Hz
- [ ] Motion data streams at 16Hz
- [ ] Quality values update correctly
- [ ] LSL streams visible in bsl_stream_viewer
- [ ] Reconnection works after power cycle
- [ ] Signal strength warnings appear when appropriate
- [ ] USB mode still works (backward compatibility)
- [ ] Auto mode tries BLE then USB

## Implementation Notes

### BLE UUID Discovery

Before full implementation, we need to discover the actual UUIDs used by Emotiv EPOC X:

```python
# Discovery utility (scripts/discover_ble_uuids.py)
async def discover_emotiv_uuids():
    devices = await BleakScanner.discover()
    for device in devices:
        if 'EPOC' in device.name:
            async with BleakClient(device.address) as client:
                for service in client.services:
                    print(f"Service: {service.uuid}")
                    for char in service.characteristics:
                        print(f"  Characteristic: {char.uuid}")
                        print(f"    Properties: {char.properties}")
```

### Async/Sync Bridge

Since existing code is synchronous, we provide both interfaces:

```python
def main_loop(self):
    """Synchronous wrapper for backward compatibility"""
    asyncio.run(self.main_loop_async())
```

### Platform-Specific Considerations

**Windows**: No additional setup required, uses native BLE stack

**macOS**: Requires Bluetooth permissions in Info.plist for packaged apps

**Linux**: Requires BlueZ 5.43+, may need user in `bluetooth` group

### Performance Optimization

1. Use `asyncio.Queue` with bounded size to prevent memory growth
2. Request minimum BLE connection interval (7.5ms) for low latency
3. Process packets immediately in notification handler
4. Use `asyncio.wait_for` with timeout to prevent blocking
5. Run USB reads in thread executor to avoid blocking event loop

## Dependencies

New dependencies to add to requirements.txt:

```
bleak>=0.21.0  # Cross-platform BLE library
```

Platform-specific notes:
- Windows: No additional packages
- macOS: No additional packages (uses Core Bluetooth)
- Linux: Requires `bluez` system package (apt-get install bluez)

## Migration Path

1. **Phase 1**: Implement BLE connection classes without modifying existing code
2. **Phase 2**: Add connection abstraction to EmotivBase
3. **Phase 3**: Update main.py to accept connection type parameter
4. **Phase 4**: Add UUID discovery utility
5. **Phase 5**: Test with real hardware and document UUIDs
6. **Phase 6**: Update documentation and examples

Existing USB HID functionality remains unchanged and is the default mode for backward compatibility.
