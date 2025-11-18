# Implementation Plan

- [x] 1. Create connection abstraction layer




  - Create `emotiv_lsl/connection_base.py` with `EmotivConnectionBase` abstract class defining `connect()`, `disconnect()`, `read_packet()`, `is_connected()`, and `get_device_info()` methods
  - Add custom exception classes: `EmotivConnectionError`, `DeviceNotFoundError`, `ConnectionTimeoutError`, `PacketValidationError`, `BLENotSupportedError`
  - _Requirements: 1.1, 4.1, 4.2, 5.1_

- [x] 2. Implement BLE connection handler





  - [x] 2.1 Create BLEConnection class with device discovery






    - Create `emotiv_lsl/ble_connection.py` with `BLEConnection` class inheriting from `EmotivConnectionBase`
    - Implement `discover_devices()` method using `BleakScanner` to find Emotiv headsets with 30-second timeout
    - Implement device filtering by name containing 'EPOC' and return list of `BLEDeviceInfo` objects with name, MAC address, and RSSI
    - _Requirements: 1.1, 1.2, 1.5_

  - [x] 2.2 Implement BLE connection and GATT subscription







    - Implement `connect()` method using `BleakClient` with 10-second timeout
    - Add GATT service and characteristic UUID placeholders (to be discovered later)
    - Implement `start_notify()` for EEG and motion characteristics
    - Add connection state tracking with `_connected` flag
    - _Requirements: 1.3, 1.4, 9.5_

  - [x] 2.3 Implement packet reception via BLE notifications


    - Create `_notification_handler()` callback that receives BLE notifications and queues packets
    - Implement `asyncio.Queue` with maxsize=100 for packet buffering
    - Implement `read_packet()` method that retrieves packets from queue with 1-second timeout
    - Add queue overflow handling that logs warnings when packets are dropped
    - _Requirements: 2.5, 5.4, 10.1, 10.5_

  - [x] 2.4 Add BLE connection monitoring and error handling


    - Implement `disconnect()` method that stops notifications and closes BleakClient
    - Add RSSI monitoring that checks signal strength every 10 seconds
    - Implement warning logging when RSSI drops below -80 dBm
    - Add `is_connected()` and `get_device_info()` methods
    - _Requirements: 5.2, 8.2, 8.3_

- [x] 3. Implement USB HID connection wrapper




  - Create `emotiv_lsl/usb_connection.py` with `USBHIDConnection` class inheriting from `EmotivConnectionBase`
  - Move existing `get_hid_device()` logic into `_find_hid_device()` method
  - Implement `connect()` method that wraps existing USB HID device initialization
  - Implement `read_packet()` using `asyncio.run_in_executor()` to wrap synchronous `hid.Device.read(32)`
  - Implement `disconnect()`, `is_connected()`, and `get_device_info()` methods
  - _Requirements: 7.1, 7.2, 7.3_
-

- [x] 4. Update EmotivBase to use connection abstraction





  - [x] 4.1 Add connection abstraction fields to EmotivBase

    - Add `connection: EmotivConnectionBase` field to EmotivBase class
    - Add `connection_type: str` field with default value 'usb' for backward compatibility
    - Add `connection_config: dict` field for connection-specific configuration
    - _Requirements: 4.1, 4.2, 4.4, 7.5_



  - [x] 4.2 Implement connection initialization logic





    - Create `initialize_connection()` async method that instantiates appropriate connection class based on `connection_type`
    - Implement 'ble' mode that creates `BLEConnection` instance
    - Implement 'usb' mode that creates `USBHIDConnection` instance
    - Implement 'auto' mode that tries BLE first, falls back to USB on failure
    - Add connection logging with device type and identifier
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 8.1_
-

  - [x] 4.3 Convert main_loop to async and integrate connection abstraction






    - Create `main_loop_async()` method that calls `initialize_connection()` and uses `await connection.read_packet()`
    - Replace direct `hid.Device.read()` calls with `await self.connection.read_packet()`
    - Add reconnection logic with 3 retry attempts and 5-second delays between attempts
    - Implement graceful termination when max reconnection attempts are exceeded
    - Keep existing `main_loop()` as synchronous wrapper calling `asyncio.run(self.main_loop_async())`
    - _Requirements: 5.2, 5.3, 7.1, 7.2_
-

- [x] 5. Update EmotivEpocX for connection abstraction compatibility




  - Remove direct HID device access from `__attrs_post_init__`
  - Update `get_hid_device()` to work with connection abstraction or mark as deprecated
  - Ensure `decode_data()` and `validate_data()` work identically for both USB and BLE packets
  - Verify LSL stream info methods remain unchanged
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 7.4_
-

- [x] 6. Add command-line interface for connection type selection




  - Update `main.py` to accept `--connection` argument with choices ['usb', 'ble', 'auto']
  - Add `--ble-address` argument for specifying MAC address of specific device
  - Set default connection type to 'auto' when no argument provided
  - Pass connection parameters to EmotivEpocX constructor
  - Add startup logging that displays selected connection mode
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
-

- [x] 7. Create BLE UUID discovery utility




  - Create `scripts/discover_ble_uuids.py` script that scans for Emotiv devices
  - Implement async function that connects to discovered device and enumerates all GATT services
  - List all characteristics with their UUIDs and properties (read, write, notify, indicate)
  - Save discovered UUIDs to `emotiv_lsl/ble_uuids.json` configuration file
  - Add command-line option to specify device MAC address
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 8. Implement connection status monitoring and logging




  - [x] 8.1 Add ConnectionStatus dataclass


    - Create `emotiv_lsl/connection_status.py` with `ConnectionStatus` dataclass
    - Include fields: `connected`, `connection_type`, `device_id`, `signal_strength`, `packet_rate`, `error_count`, `last_packet_time`
    - Add method to calculate packet rate from packet timestamps
    - _Requirements: 8.1, 8.4_

  - [x] 8.2 Implement packet rate monitoring


    - Add packet timestamp tracking in main_loop_async
    - Calculate actual packet reception rate every 5 seconds
    - Log warning when packet rate drops below 90% of expected rate (115 Hz for EEG)
    - Track and log error count for invalid packets
    - _Requirements: 5.5, 8.4_

  - [x] 8.3 Add debug logging for BLE packets


    - Add conditional logging of raw packet hex dumps when `enable_debug_logging` is True
    - Log BLE notification events with sender characteristic UUID
    - Add latency measurement from notification to LSL push
    - Log performance warning when latency exceeds 50 milliseconds
    - _Requirements: 8.5, 10.4_

- [x] 9. Add BLE configuration and optimization





  - Create `emotiv_lsl/ble_config.py` with `BLEConfig` dataclass containing connection parameters
  - Set connection timeout to 10 seconds, discovery timeout to 30 seconds
  - Configure reconnect attempts to 3 with 5-second delay
  - Set RSSI threshold to -80 dBm for signal warnings
  - Request minimum BLE connection interval of 7.5ms for low latency
  - _Requirements: 5.1, 5.2, 8.3, 10.2, 10.3_
-

- [x] 10. Update dependencies and platform documentation




  - Add `bleak>=0.21.0` to `requirements.txt` and `pyproject.toml`
  - Update README.md with BLE connection instructions and command-line examples
  - Document platform-specific requirements: Windows (none), macOS (Bluetooth permissions), Linux (BlueZ 5.43+)
  - Add troubleshooting section for common BLE connection issues
  - Document discovered BLE service and characteristic UUIDs
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 9.4_

- [-] 11. Verify LSL stream compatibility between USB and BLE



  - Test that BLE connection produces identical LSL stream names as USB connection
  - Verify EEG stream metadata (channel names, units, sampling rate) matches between connection types
  - Verify motion stream metadata matches between connection types
  - Verify quality stream metadata matches between connection types
  - Confirm source_id format is consistent across connection types
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 12. Create integration tests for BLE functionality
  - [ ]* 12.1 Write BLE connection tests
    - Create `tests/test_ble_connection.py` with mocked BleakClient and BleakScanner
    - Test device discovery returns correct device list
    - Test connection establishment and timeout handling
    - Test notification handler queues packets correctly
    - Test queue overflow behavior drops packets and logs warnings
    - _Requirements: 1.1, 1.2, 1.3, 5.4_

  - [ ]* 12.2 Write USB connection wrapper tests
    - Create `tests/test_usb_connection.py` with mocked hid.Device
    - Test device enumeration finds Emotiv headset
    - Test read_packet wraps synchronous read correctly
    - Verify backward compatibility with existing USB behavior
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 12.3 Write connection manager tests
    - Create `tests/test_connection_manager.py` testing connection type selection
    - Test 'usb' mode creates USBHIDConnection
    - Test 'ble' mode creates BLEConnection
    - Test 'auto' mode tries BLE then falls back to USB
    - Test reconnection logic with simulated connection failures
    - _Requirements: 4.1, 4.2, 4.3, 5.2, 5.3_

  - [ ]* 12.4 Write packet decoding compatibility tests
    - Create `tests/test_packet_compatibility.py` with sample packet data
    - Verify decode_data produces identical output for USB and BLE packets
    - Test EEG packet decoding (14 channels)
    - Test motion packet decoding (6 channels)
    - Test quality value extraction
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
