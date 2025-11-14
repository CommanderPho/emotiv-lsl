# Requirements Document

## Introduction

This document specifies the requirements for implementing a client that can successfully communicate with, receive data from, and decode data packets from Emotiv Epoc family headsets (Epoc, Epoc+, and Epoc X). The specification is platform-independent and language-agnostic, providing all necessary information to build a compatible client implementation.

## Glossary

- **Emotiv_Headset**: An EEG (electroencephalography) headset manufactured by Emotiv Systems, including models Epoc (original), Epoc+, and Epoc X
- **HID_Device**: Human Interface Device, a USB device class used by Emotiv headsets for communication
- **Data_Packet**: A 32-byte encrypted data structure transmitted by the headset containing EEG sensor readings, motion data, or quality metrics
- **Crypto_Key**: A 16-byte AES encryption key derived from the headset's serial number
- **EEG_Channel**: One of 14 electrode positions on the headset following the 10-20 system: AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4
- **Motion_Data**: Accelerometer and gyroscope readings from the headset's IMU (Inertial Measurement Unit)
- **Quality_Value**: A 4-bit integer (0-15) indicating the contact quality of an electrode with the scalp
- **LSL_Stream**: Lab Streaming Layer data stream for real-time data transmission
- **Cipher**: AES-ECB encryption/decryption object initialized with the Crypto_Key
- **Serial_Number**: A unique alphanumeric identifier string embedded in the headset's USB HID descriptor

## Requirements

### Requirement 1: USB HID Device Discovery

**User Story:** As a client application, I want to discover and identify Emotiv headsets connected via USB, so that I can establish communication with the correct device.

#### Acceptance Criteria

1. WHEN the client application starts, THE Client_Application SHALL enumerate all connected USB HID devices
2. WHEN examining each HID device, THE Client_Application SHALL check the manufacturer_string field for the value "Emotiv"
3. WHEN an Emotiv device is found, THE Client_Application SHALL verify that either the usage field equals 2 OR (usage equals 0 AND interface_number equals 1)
4. WHEN multiple matching devices are found, THE Client_Application SHALL select the first valid device
5. IF no matching device is found, THEN THE Client_Application SHALL raise an exception with message "Emotiv [Model] not found"

### Requirement 2: Serial Number Extraction

**User Story:** As a client application, I want to extract the headset's serial number from the USB device descriptor, so that I can derive the correct encryption key.

#### Acceptance Criteria

1. WHEN a valid Emotiv HID device is identified, THE Client_Application SHALL read the serial_number field from the device descriptor
2. THE Client_Application SHALL store the serial number as a string of alphanumeric characters
3. THE Client_Application SHALL convert each character of the serial number to its ASCII byte value
4. THE Client_Application SHALL create a bytearray containing all converted byte values in order

### Requirement 3: Encryption Key Derivation

**User Story:** As a client application, I want to derive the AES encryption key from the serial number, so that I can decrypt incoming data packets.

#### Acceptance Criteria

1. WHEN the serial number bytearray is available, THE Client_Application SHALL extract specific byte positions to form a 16-byte key
2. FOR Epoc X and Epoc+ models, THE Client_Application SHALL construct the key using bytes at positions: [-1, -2, -4, -4, -2, -1, -2, -4, -1, -4, -3, -2, -1, -2, -2, -3] (negative indices from end)
3. THE Client_Application SHALL initialize an AES cipher in ECB mode using the derived 16-byte key
4. THE Client_Application SHALL store the cipher object for use in packet decryption

### Requirement 4: Data Packet Reception

**User Story:** As a client application, I want to continuously read data packets from the headset, so that I can process EEG and motion data in real-time.

#### Acceptance Criteria

1. WHEN the HID device is opened, THE Client_Application SHALL continuously call the HID read function with size parameter 32
2. THE Client_Application SHALL read exactly 32 bytes per packet
3. WHEN a packet is received, THE Client_Application SHALL validate that the packet length equals 32 bytes
4. THE Client_Application SHALL process packets in an infinite loop until explicitly terminated
5. THE Client_Application SHALL maintain a packet counter for debugging and logging purposes

### Requirement 5: Packet Decryption for Epoc X

**User Story:** As an Epoc X client, I want to decrypt received data packets using the XOR pre-processing step, so that I can access the encrypted payload.

#### Acceptance Criteria

1. WHEN a 32-byte packet is received from Epoc X, THE Client_Application SHALL apply XOR operation with 0x55 to each byte
2. THE Client_Application SHALL perform the XOR operation: decrypted_byte = original_byte XOR 0x55
3. WHEN XOR pre-processing is complete, THE Client_Application SHALL decrypt the result using the AES cipher
4. THE Client_Application SHALL pass the 32-byte XOR-processed data to the AES decrypt function
5. THE Client_Application SHALL store the decrypted 32-byte result for further processing

### Requirement 6: Packet Decryption for Epoc+

**User Story:** As an Epoc+ client, I want to decrypt received data packets without XOR pre-processing, so that I can access the encrypted payload.

#### Acceptance Criteria

1. WHEN a 32-byte packet is received from Epoc+, THE Client_Application SHALL skip bytes at index 0
2. THE Client_Application SHALL join bytes 1-31 into a string using Latin-1 encoding
3. THE Client_Application SHALL decrypt the first 32 bytes of the joined string using the AES cipher
4. THE Client_Application SHALL store the decrypted 32-byte result for further processing

### Requirement 7: Packet Type Identification

**User Story:** As a client application, I want to identify whether a decrypted packet contains EEG data or motion data, so that I can route it to the appropriate decoder.

#### Acceptance Criteria

1. WHEN a packet is decrypted, THE Client_Application SHALL examine byte at index 1
2. IF byte[1] equals 32 (decimal), THEN THE Client_Application SHALL classify the packet as Motion_Data
3. IF byte[1] does not equal 32, THEN THE Client_Application SHALL classify the packet as EEG_Data
4. THE Client_Application SHALL route Motion_Data packets to the motion decoder
5. THE Client_Application SHALL route EEG_Data packets to the EEG decoder

### Requirement 8: EEG Data Decoding

**User Story:** As a client application, I want to decode EEG sensor values from data packets, so that I can output calibrated microvolts readings for all 14 channels.

#### Acceptance Criteria

1. WHEN an EEG packet is identified, THE Client_Application SHALL extract 14 channel values from specific byte positions
2. THE Client_Application SHALL process byte pairs starting at index 2, incrementing by 2, up to index 15 (bytes 2-3, 4-5, 6-7, 8-9, 10-11, 12-13, 14-15)
3. THE Client_Application SHALL process byte pairs starting at index 18, incrementing by 2, up to index 31 (bytes 18-19, 20-21, 22-23, 24-25, 26-27, 28-29, 30-31)
4. FOR each byte pair (value_1, value_2), THE Client_Application SHALL compute: result = ((value_1 * 0.128205128205129) + 4201.02564096001) + ((value_2 - 128) * 32.82051289)
5. THE Client_Application SHALL format each result as a floating-point number with 8 decimal places
6. THE Client_Application SHALL apply channel position swaps: swap indices [0,2], swap indices [13,11], swap indices [1,3], swap indices [10,12]
7. THE Client_Application SHALL output 14 floating-point values in the order: AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4

### Requirement 9: Motion Data Decoding for Epoc X

**User Story:** As an Epoc X client, I want to decode accelerometer and gyroscope data from motion packets, so that I can output 6-axis IMU readings.

#### Acceptance Criteria

1. WHEN a motion packet is identified for Epoc X, THE Client_Application SHALL extract motion values from byte positions: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31]
2. THE Client_Application SHALL process bytes in pairs from the position array
3. FOR each byte pair (byte1, byte2), THE Client_Application SHALL compute: raw_value = 8191.88296790168 + (byte1 * 1.00343814821) + ((byte2 - 128.00001) * 64.00318037383)
4. THE Client_Application SHALL extract the first 6 computed values
5. THE Client_Application SHALL scale values 0-2 (accelerometer) by multiplying by (1.0 / 16384.0) to convert to g units
6. THE Client_Application SHALL scale values 3-5 (gyroscope) by multiplying by (1.0 / 131.0) to convert to degrees/second
7. THE Client_Application SHALL output 6 floating-point values in the order: AccX, AccY, AccZ, GyroX, GyroY, GyroZ

### Requirement 10: Electrode Quality Extraction

**User Story:** As a client application, I want to extract electrode contact quality values from EEG packets, so that I can monitor signal quality for each channel.

#### Acceptance Criteria

1. WHEN an EEG packet is decoded, THE Client_Application SHALL extract quality values from bytes 16-22
2. THE Client_Application SHALL extract the lower 4 bits (value & 0xF) and upper 4 bits ((value >> 4) & 0xF) from each byte
3. THE Client_Application SHALL map quality values to channels in order: byte[16] lower→AF3, byte[16] upper→F7, byte[17] lower→F3, byte[17] upper→FC5, byte[18] lower→T7, byte[18] upper→P7, byte[19] lower→O1, byte[19] upper→O2, byte[20] lower→P8, byte[20] upper→T8, byte[21] lower→FC6, byte[21] upper→F4, byte[22] lower→F8, byte[22] upper→AF4
4. THE Client_Application SHALL output 14 integer values in range 0-15
5. THE Client_Application SHALL output quality values in the same channel order as EEG data

### Requirement 11: Data Stream Output Rates

**User Story:** As a client application, I want to output data at the correct sampling rates, so that downstream analysis tools receive properly timed data.

#### Acceptance Criteria

1. THE Client_Application SHALL output EEG data at a nominal sample rate of 128 Hz
2. THE Client_Application SHALL output motion data at a nominal sample rate of 16 Hz
3. THE Client_Application SHALL output electrode quality data at a nominal sample rate of 128 Hz
4. THE Client_Application SHALL maintain consistent timing between packets
5. THE Client_Application SHALL not artificially throttle or buffer data beyond what is received from the device

### Requirement 12: Model-Specific Key Identification

**User Story:** As a client application, I want to identify which Emotiv model is connected, so that I can apply the correct decryption and decoding procedures.

#### Acceptance Criteria

1. THE Client_Application SHALL support KeyModel value 1 for Epoc (original)
2. THE Client_Application SHALL support KeyModel value 2 for Epoc (original)
3. THE Client_Application SHALL support KeyModel value 5 for Epoc+ (14-bit mode)
4. THE Client_Application SHALL support KeyModel value 6 for Epoc+ (16-bit mode)
5. THE Client_Application SHALL support KeyModel value 8 for Epoc X
6. WHEN Epoc X is detected, THE Client_Application SHALL apply XOR pre-processing before AES decryption
7. WHEN Epoc+ is detected, THE Client_Application SHALL skip XOR pre-processing and use Latin-1 string joining
8. THE Client_Application SHALL use the same EEG decoding formula for all models
9. THE Client_Application SHALL only decode motion data for Epoc X model

### Requirement 13: Error Handling and Validation

**User Story:** As a client application, I want to validate and handle errors in data packets, so that I can maintain robust operation and provide diagnostic information.

#### Acceptance Criteria

1. WHEN a packet length is not 32 bytes, THE Client_Application SHALL log a warning and skip the packet
2. WHEN decryption fails, THE Client_Application SHALL log the error and continue to the next packet
3. WHEN quality value extraction fails, THE Client_Application SHALL set quality values to None and continue processing EEG data
4. WHEN motion data decoding produces fewer than 6 values, THE Client_Application SHALL output zeros for missing values
5. THE Client_Application SHALL not terminate on individual packet errors
6. THE Client_Application SHALL provide debug logging capability for packet-level diagnostics
