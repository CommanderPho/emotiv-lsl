# Requirements Document

## Introduction

This feature adds Bluetooth Low Energy (BLE) connectivity support to the Emotiv-LSL system, enabling wireless data acquisition from Emotiv EPOC X headsets via BLE in addition to the existing USB HID dongle connection. The implementation will maintain the same LSL streaming architecture while providing users with flexible connection options based on their hardware setup and use case requirements.

## Glossary

- **BLE System**: The Bluetooth Low Energy connection subsystem that discovers, connects to, and receives data from Emotiv EPOC X headsets
- **Connection Manager**: The component responsible for abstracting connection types (USB HID or BLE) and providing a unified interface
- **USB HID System**: The existing USB Human Interface Device connection subsystem using the hidapi library
- **LSL Server**: The Lab Streaming Layer server that publishes EEG, motion, and quality data streams
- **GATT**: Generic Attribute Profile - the BLE protocol layer for data exchange
- **Service UUID**: Unique identifier for BLE services exposed by the Emotiv headset
- **Characteristic UUID**: Unique identifier for specific data channels within a BLE service
- **Packet Decoder**: The component that decrypts and parses raw data packets into EEG/motion/quality values
- **Device Discovery**: The process of scanning for and identifying available Emotiv headsets via BLE

## Requirements

### Requirement 1

**User Story:** As a researcher, I want to connect to my Emotiv EPOC X headset via Bluetooth, so that I can acquire EEG data without requiring a USB dongle

#### Acceptance Criteria

1. WHEN THE BLE System initiates device discovery, THE BLE System SHALL scan for Emotiv EPOC X headsets advertising BLE services
2. WHEN an Emotiv EPOC X headset is discovered, THE BLE System SHALL retrieve the device name, MAC address, and signal strength
3. WHEN THE BLE System attempts connection to a discovered headset, THE BLE System SHALL establish a GATT connection within 10 seconds or report a timeout error
4. WHEN THE BLE System successfully connects, THE BLE System SHALL subscribe to all required GATT characteristics for EEG data reception
5. WHERE multiple Emotiv headsets are available, THE BLE System SHALL allow selection by device name or MAC address

### Requirement 2

**User Story:** As a developer, I want the BLE connection to use the same data decoding pipeline as USB HID, so that I maintain consistent data quality and processing

#### Acceptance Criteria

1. WHEN THE BLE System receives a raw data packet, THE Packet Decoder SHALL apply the same XOR and AES decryption as the USB HID System
2. WHEN THE Packet Decoder processes BLE packets, THE Packet Decoder SHALL produce EEG data with 14 channels at 128Hz sampling rate
3. WHEN THE Packet Decoder processes BLE motion packets, THE Packet Decoder SHALL produce motion data with 6 channels at 16Hz sampling rate
4. WHEN THE Packet Decoder extracts electrode quality values, THE Packet Decoder SHALL use the same bit-field extraction logic as the USB HID System
5. THE BLE System SHALL validate packet structure before passing to THE Packet Decoder

### Requirement 3

**User Story:** As a researcher, I want the LSL streams to be identical regardless of connection type, so that my analysis tools work without modification

#### Acceptance Criteria

1. WHEN THE LSL Server publishes EEG data from BLE connection, THE LSL Server SHALL use stream name "Epoc X" with identical metadata as USB HID connection
2. WHEN THE LSL Server publishes motion data from BLE connection, THE LSL Server SHALL use stream name "Epoc X Motion" with identical channel names and units
3. WHEN THE LSL Server publishes quality data from BLE connection, THE LSL Server SHALL use stream name "Epoc X eQuality" with identical channel configuration
4. THE LSL Server SHALL maintain the same source_id format for BLE connections as USB HID connections
5. THE LSL Server SHALL apply the same timestamp synchronization mechanism regardless of connection type

### Requirement 4

**User Story:** As a user, I want to specify my preferred connection method at startup, so that I can choose between USB dongle and Bluetooth based on my setup

#### Acceptance Criteria

1. WHEN the application starts with connection type parameter "ble", THE Connection Manager SHALL initialize THE BLE System
2. WHEN the application starts with connection type parameter "usb", THE Connection Manager SHALL initialize THE USB HID System
3. WHEN the application starts with connection type parameter "auto", THE Connection Manager SHALL attempt BLE connection first and fall back to USB HID if unavailable
4. WHERE no connection type is specified, THE Connection Manager SHALL default to "auto" mode
5. THE Connection Manager SHALL log the active connection type and device identifier upon successful connection

### Requirement 5

**User Story:** As a developer, I want proper error handling for BLE connection failures, so that users receive clear feedback when connections fail

#### Acceptance Criteria

1. WHEN THE BLE System fails to discover any Emotiv headsets within 30 seconds, THE BLE System SHALL raise a DeviceNotFoundError with message "No Emotiv EPOC X headsets found via Bluetooth"
2. WHEN THE BLE System loses connection during data acquisition, THE BLE System SHALL attempt reconnection up to 3 times with 5-second intervals
3. IF reconnection attempts fail, THEN THE BLE System SHALL terminate gracefully and log the disconnection event
4. WHEN THE BLE System encounters GATT communication errors, THE BLE System SHALL log the error details and continue attempting to read data
5. WHEN THE BLE System detects invalid packet structure, THE BLE System SHALL increment an error counter and skip the packet without crashing

### Requirement 6

**User Story:** As a researcher, I want BLE connection to work across Windows, macOS, and Linux, so that I can use the same codebase on different platforms

#### Acceptance Criteria

1. THE BLE System SHALL use the bleak library for cross-platform BLE communication
2. WHEN running on Windows, THE BLE System SHALL utilize the Windows BLE stack without requiring additional drivers
3. WHEN running on macOS, THE BLE System SHALL utilize the Core Bluetooth framework via bleak
4. WHEN running on Linux, THE BLE System SHALL utilize BlueZ via bleak and require bluez version 5.43 or higher
5. THE BLE System SHALL document platform-specific prerequisites in the README

### Requirement 7

**User Story:** As a developer, I want to maintain backward compatibility with existing USB HID code, so that current users are not affected by the BLE addition

#### Acceptance Criteria

1. THE Connection Manager SHALL preserve all existing EmotivBase and EmotivEpocX class interfaces
2. WHEN THE USB HID System is active, THE USB HID System SHALL function identically to the pre-BLE implementation
3. THE Connection Manager SHALL not modify existing USB HID packet processing logic
4. THE Connection Manager SHALL allow instantiation of EmotivEpocX with explicit connection type parameter
5. WHERE connection type is not specified, THE EmotivEpocX SHALL default to USB HID behavior for backward compatibility

### Requirement 8

**User Story:** As a researcher, I want to see connection status and data quality metrics, so that I can verify my BLE connection is working properly

#### Acceptance Criteria

1. WHEN THE BLE System establishes connection, THE BLE System SHALL log the device name, MAC address, and connection timestamp
2. WHILE THE BLE System is connected, THE BLE System SHALL monitor RSSI (signal strength) every 10 seconds
3. WHEN RSSI drops below -80 dBm, THE BLE System SHALL log a warning about weak signal strength
4. THE BLE System SHALL track packet reception rate and log warnings when rate drops below 90% of expected rate
5. WHEN THE BLE System is in debug mode, THE BLE System SHALL log raw packet hex dumps for troubleshooting

### Requirement 9

**User Story:** As a developer, I want to discover BLE service and characteristic UUIDs for Emotiv headsets, so that I can implement proper GATT communication

#### Acceptance Criteria

1. THE BLE System SHALL provide a discovery utility that scans and lists all GATT services and characteristics
2. WHEN the discovery utility connects to an Emotiv headset, THE discovery utility SHALL enumerate all service UUIDs
3. WHEN the discovery utility examines a service, THE discovery utility SHALL list all characteristic UUIDs with their properties (read, write, notify)
4. THE discovery utility SHALL save discovered UUIDs to a configuration file for reference
5. THE BLE System SHALL use documented or discovered UUIDs for production data acquisition

### Requirement 10

**User Story:** As a user, I want minimal latency in BLE data transmission, so that real-time applications remain responsive

#### Acceptance Criteria

1. WHEN THE BLE System receives a notification from the headset, THE BLE System SHALL process and push to LSL within 10 milliseconds
2. THE BLE System SHALL request the minimum BLE connection interval supported by the headset (typically 7.5ms)
3. THE BLE System SHALL disable BLE connection parameter updates that would increase latency
4. WHEN THE BLE System detects latency exceeding 50 milliseconds, THE BLE System SHALL log a performance warning
5. THE BLE System SHALL use asynchronous I/O to prevent blocking during packet reception
