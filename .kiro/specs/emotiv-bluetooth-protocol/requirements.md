# Bluetooth Protocol Requirements Document

## Introduction

This document specifies the requirements for implementing Bluetooth Low Energy (BLE) communication with Emotiv Epoc family headsets. Unlike USB HID communication, BLE uses GATT (Generic Attribute Profile) services and characteristics for wireless data transmission. This specification focuses on the protocol differences between USB and BLE implementations.

## Glossary

- **BLE**: Bluetooth Low Energy, a wireless communication protocol optimized for low power consumption
- **GATT**: Generic Attribute Profile, the protocol used for BLE data exchange
- **GATT_Service**: A collection of characteristics and relationships to other services that encapsulate device behavior
- **GATT_Characteristic**: A data value transferred between client and server with associated properties (read, write, notify)
- **UUID**: Universally Unique Identifier used to identify services and characteristics
- **Characteristic_Notification**: A mechanism where the server pushes data to the client when a value changes
- **Client_Characteristic_Configuration_Descriptor**: A descriptor that enables/disables notifications for a characteristic
- **Connection_Handle**: A unique identifier for an active BLE connection
- **Service_Discovery**: The process of enumerating available GATT services and characteristics on a device
- **Pairing**: The process of establishing a secure BLE connection with authentication
- **EEGBtleLib**: Windows-specific C++ library for BLE communication with Emotiv devices (EEGBtleLib64.dll)
- **BluetoothGATT**: Windows API for GATT operations (BluetoothGATTGetServices, BluetoothGATTRegisterEvent)

## Overview

This requirements document provides structured, testable specifications for implementing BLE communication with Emotiv headsets. For complete technical details including GATT UUIDs, connection procedures, and packet structures, refer to the companion **bluetooth-protocol.md** document.

## Requirements

### Requirement 1: BLE Device Discovery

**User Story:** As a client application, I want to discover Emotiv headsets via Bluetooth LE scanning, so that I can establish a wireless connection.

#### Acceptance Criteria

1. WHEN the client application starts, THE Client_Application SHALL initiate a BLE scan for nearby devices
2. THE Client_Application SHALL filter discovered devices by device name pattern matching "EPOC" or "Emotiv"
3. THE Client_Application SHALL retrieve the device's advertised name and MAC address
4. THE Client_Application SHALL support scanning with a configurable timeout period (minimum 10 seconds)
5. IF no matching device is found within the timeout, THEN THE Client_Application SHALL raise an exception with message "Emotiv headset not found via BLE"

### Requirement 2: BLE Connection Establishment

**User Story:** As a client application, I want to establish a GATT connection to a discovered Emotiv headset, so that I can access its services and characteristics.

#### Acceptance Criteria

1. WHEN a target device is selected, THE Client_Application SHALL initiate a GATT connection using the device's MAC address
2. THE Client_Application SHALL wait for connection establishment with a timeout of at least 10 seconds
3. WHEN the connection is established, THE Client_Application SHALL retrieve a connection handle
4. THE Client_Application SHALL verify the connection state before proceeding to service discovery
5. IF connection fails, THEN THE Client_Application SHALL retry up to 3 times with exponential backoff

### Requirement 3: GATT Service Discovery

**User Story:** As a client application, I want to discover available GATT services on the connected headset, so that I can locate the data streaming characteristics.

#### Acceptance Criteria

1. WHEN a GATT connection is established, THE Client_Application SHALL enumerate all available services
2. THE Client_Application SHALL identify the primary Emotiv data service by its UUID
3. THE Client_Application SHALL enumerate all characteristics within the identified service
4. THE Client_Application SHALL identify EEG data characteristics and motion data characteristics by their UUIDs
5. THE Client_Application SHALL verify that required characteristics support the NOTIFY property

### Requirement 4: Characteristic Notification Registration

**User Story:** As a client application, I want to enable notifications for data characteristics, so that I can receive real-time EEG and motion data.

#### Acceptance Criteria

1. WHEN data characteristics are identified, THE Client_Application SHALL write to the Client Characteristic Configuration Descriptor to enable notifications
2. THE Client_Application SHALL write the value 0x0001 to enable notifications
3. THE Client_Application SHALL register a callback function to handle incoming notifications
4. THE Client_Application SHALL verify that notification registration succeeds before proceeding
5. IF notification registration fails, THEN THE Client_Application SHALL raise an exception with diagnostic information

### Requirement 5: BLE Data Packet Reception

**User Story:** As a client application, I want to receive data packets via GATT notifications, so that I can process EEG and motion data in real-time.

#### Acceptance Criteria

1. WHEN notifications are enabled, THE Client_Application SHALL receive data packets asynchronously via the registered callback
2. THE Client_Application SHALL extract the packet payload from the notification event structure
3. THE Client_Application SHALL validate that each packet contains 20 bytes of data
4. THE Client_Application SHALL maintain a packet counter for debugging and loss detection
5. THE Client_Application SHALL process packets in the order received without blocking the callback thread

### Requirement 6: BLE Packet Structure Differences

**User Story:** As a client application, I want to understand BLE packet structure differences from USB, so that I can correctly decode the data.

#### Acceptance Criteria

1. THE Client_Application SHALL recognize that BLE packets are 20 bytes in length (not 32 bytes like USB)
2. THE Client_Application SHALL recognize that BLE packets may require reassembly if data spans multiple notifications
3. THE Client_Application SHALL identify packet type based on characteristic UUID (not byte[1] value)
4. THE Client_Application SHALL apply the same decryption algorithm as USB after packet reassembly
5. THE Client_Application SHALL apply the same EEG decoding formulas as USB after decryption

### Requirement 7: Serial Number Extraction via BLE

**User Story:** As a client application, I want to extract the headset's serial number via BLE, so that I can derive the correct encryption key.

#### Acceptance Criteria

1. WHEN the GATT connection is established, THE Client_Application SHALL read the Device Information Service
2. THE Client_Application SHALL locate the Serial Number String characteristic (UUID 0x2A25)
3. THE Client_Application SHALL read the serial number value as a UTF-8 string
4. THE Client_Application SHALL convert the serial number to a bytearray for key derivation
5. THE Client_Application SHALL use the same key derivation algorithm as USB HID

### Requirement 8: BLE Encryption Key Derivation

**User Story:** As a client application, I want to derive the AES encryption key from the BLE-obtained serial number, so that I can decrypt data packets.

#### Acceptance Criteria

1. WHEN the serial number is obtained via BLE, THE Client_Application SHALL apply the same key derivation algorithm as USB
2. FOR Epoc X via BLE, THE Client_Application SHALL use the same key pattern as USB Epoc X
3. FOR Epoc+ via BLE, THE Client_Application SHALL use the same key pattern as USB Epoc+
4. THE Client_Application SHALL initialize an AES cipher in ECB mode with the derived key
5. THE Client_Application SHALL store the cipher for packet decryption

### Requirement 9: BLE Packet Decryption

**User Story:** As a client application, I want to decrypt BLE data packets, so that I can extract EEG sensor values.

#### Acceptance Criteria

1. WHEN a complete data packet is received via BLE, THE Client_Application SHALL apply the same decryption method as USB
2. FOR Epoc X via BLE, THE Client_Application SHALL apply XOR preprocessing with 0x55 before AES decryption
3. FOR Epoc+ via BLE, THE Client_Application SHALL skip XOR preprocessing and use Latin-1 string joining
4. THE Client_Application SHALL handle 20-byte BLE packets differently from 32-byte USB packets during reassembly
5. THE Client_Application SHALL produce the same decrypted output format as USB for downstream processing

### Requirement 10: BLE Connection Management

**User Story:** As a client application, I want to manage BLE connection lifecycle, so that I can handle disconnections and reconnections gracefully.

#### Acceptance Criteria

1. THE Client_Application SHALL monitor connection state continuously
2. WHEN a disconnection is detected, THE Client_Application SHALL log the event with timestamp
3. THE Client_Application SHALL attempt automatic reconnection with exponential backoff
4. THE Client_Application SHALL re-register for notifications after successful reconnection
5. THE Client_Application SHALL provide a manual disconnect method for clean shutdown

### Requirement 11: Platform-Specific BLE Implementation (Windows)

**User Story:** As a Windows client application, I want to use the Windows Bluetooth GATT API, so that I can communicate with Emotiv headsets via BLE.

#### Acceptance Criteria

1. THE Client_Application SHALL use BluetoothGATTGetServices to enumerate services
2. THE Client_Application SHALL use BluetoothGATTGetCharacteristics to enumerate characteristics
3. THE Client_Application SHALL use BluetoothGATTRegisterEvent to register for notifications
4. THE Client_Application SHALL use BluetoothGATTGetDescriptors to access the CCCD
5. THE Client_Application SHALL handle Windows-specific GATT event structures (BTH_LE_GATT_EVENT_TYPE, BLUETOOTH_GATT_VALUE_CHANGED_EVENT)

### Requirement 12: Platform-Specific BLE Implementation (Linux/macOS)

**User Story:** As a Linux or macOS client application, I want to use platform-appropriate BLE libraries, so that I can communicate with Emotiv headsets via BLE.

#### Acceptance Criteria

1. FOR Linux, THE Client_Application SHALL use BlueZ D-Bus API or equivalent BLE library
2. FOR macOS, THE Client_Application SHALL use CoreBluetooth framework
3. THE Client_Application SHALL abstract platform differences behind a common interface
4. THE Client_Application SHALL provide the same functional behavior across all platforms
5. THE Client_Application SHALL handle platform-specific connection parameters appropriately

### Requirement 13: BLE vs USB Protocol Differences

**User Story:** As a developer, I want to understand key differences between BLE and USB protocols, so that I can implement both correctly.

#### Acceptance Criteria

1. THE Documentation SHALL specify that BLE uses 20-byte packets while USB uses 32-byte packets
2. THE Documentation SHALL specify that BLE uses GATT notifications while USB uses HID reads
3. THE Documentation SHALL specify that BLE requires service/characteristic discovery while USB uses device enumeration
4. THE Documentation SHALL specify that BLE requires pairing while USB is plug-and-play
5. THE Documentation SHALL specify that BLE and USB use the same encryption and decoding algorithms after packet reception

### Requirement 14: BLE Data Stream Output Rates

**User Story:** As a client application, I want to output BLE data at the correct sampling rates, so that downstream analysis tools receive properly timed data.

#### Acceptance Criteria

1. THE Client_Application SHALL output EEG data at a nominal sample rate of 128 Hz via BLE
2. THE Client_Application SHALL output motion data at a nominal sample rate of 16 Hz via BLE (Epoc X only)
3. THE Client_Application SHALL output electrode quality data at a nominal sample rate of 128 Hz via BLE
4. THE Client_Application SHALL recognize that BLE sample rates may have higher jitter than USB due to wireless transmission
5. THE Client_Application SHALL use timestamps for precise timing rather than assuming fixed intervals

### Requirement 15: BLE Error Handling

**User Story:** As a client application, I want to handle BLE-specific errors gracefully, so that I can maintain robust operation.

#### Acceptance Criteria

1. WHEN a BLE connection is lost, THE Client_Application SHALL log the error and attempt reconnection
2. WHEN a notification callback fails, THE Client_Application SHALL log the error and continue processing subsequent packets
3. WHEN service discovery fails, THE Client_Application SHALL retry up to 3 times before raising an exception
4. WHEN characteristic read/write fails, THE Client_Application SHALL log the error with GATT error code
5. THE Client_Application SHALL provide diagnostic information for all BLE-specific errors

### Requirement 16: BLE Pairing and Security

**User Story:** As a client application, I want to handle BLE pairing securely, so that I can establish authenticated connections.

#### Acceptance Criteria

1. THE Client_Application SHALL support BLE pairing when required by the headset
2. THE Client_Application SHALL handle pairing requests with appropriate security level
3. THE Client_Application SHALL store pairing information for subsequent connections
4. THE Client_Application SHALL support both Just Works and Passkey Entry pairing methods
5. THE Client_Application SHALL verify that the connection is encrypted after pairing

### Requirement 17: BLE Power Management

**User Story:** As a client application, I want to be aware of BLE power characteristics, so that I can optimize battery life.

#### Acceptance Criteria

1. THE Documentation SHALL specify that BLE communication consumes less power than USB
2. THE Documentation SHALL specify that notification intervals affect power consumption
3. THE Documentation SHALL specify that connection interval parameters can be negotiated
4. THE Client_Application SHALL support configurable connection parameters for power optimization
5. THE Client_Application SHALL document recommended connection parameters for different use cases
