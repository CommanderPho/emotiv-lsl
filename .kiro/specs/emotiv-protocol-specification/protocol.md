# Emotiv Epoc Headset Communication Protocol Specification

## Document Information

**Version:** 1.0  
**Date:** 2025  
**Status:** Complete Technical Specification  
**Purpose:** Platform and language-independent specification for communicating with Emotiv Epoc family headsets

## Executive Summary

This document provides a complete, platform-independent specification for establishing communication with Emotiv Epoc family headsets (Epoc, Epoc+, Epoc X), receiving encrypted data packets via USB HID, decrypting those packets, and decoding EEG sensor data, motion sensor data, and electrode quality metrics. This specification is derived from analysis of the CyKit and emotiv-lsl reference implementations and validated against multiple working implementations.

## Table of Contents

1. Hardware Overview
2. USB HID Device Discovery
3. Serial Number Extraction and Key Derivation
4. Data Packet Reception
5. Packet Decryption (Model-Specific)
6. Packet Type Identification
7. EEG Data Decoding
8. Motion Data Decoding (Epoc X Only)
9. Electrode Quality Extraction
10. Data Stream Specifications
11. Error Handling
12. Implementation Validation
13. Known Discrepancies and Notes

---

## 1. Hardware Overview

### Supported Models

| Model | KeyModel ID | Motion Data | Bit Depth | Notes |
|-------|-------------|-------------|-----------|-------|
| Epoc (Original) | 1 or 2 | No | 14-bit | Legacy model |
| Epoc+ | 5 | No | 14-bit | 14-bit mode |
| Epoc+ | 6 | No | 16-bit | 16-bit mode (default) |
| Epoc X | 8 | Yes | 16-bit | Latest model with IMU |


### EEG Channels

All models provide 14 EEG channels following the international 10-20 system:

**Channel Order:** AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4

**Electrode Positions:**
- **Frontal:** AF3, AF4, F3, F4, F7, F8
- **Fronto-Central:** FC5, FC6
- **Temporal:** T7, T8
- **Parietal:** P7, P8
- **Occipital:** O1, O2

### Motion Sensors (Epoc X Only)

The Epoc X includes an ICM-20948 9-axis IMU providing:
- **3-axis Accelerometer:** ±2g range, scaled to g units
- **3-axis Gyroscope:** ±250 deg/s range, scaled to degrees/second

---

## 2. USB HID Device Discovery

### Discovery Algorithm

```
FOR EACH USB HID device in system:
    IF device.manufacturer_string == "Emotiv":
        IF (device.usage == 2) OR (device.usage == 0 AND device.interface_number == 1):
            RETURN device
        END IF
    END IF
END FOR
RAISE Exception("Emotiv headset not found")
```

### Device Identification Criteria

1. **Manufacturer String:** Must exactly match "Emotiv"
2. **Usage Field:** Must be 2, OR must be 0 with interface_number == 1
3. **Interface Selection:** For multi-interface devices, select interface 1

### Platform-Specific Notes

- **Windows:** Use `hid.enumerate()` from hidapi library
- **Linux:** Requires udev rules for non-root access (see `/dev/hidraw*` permissions)
- **macOS:** May require system extension approval for USB access



---

## 3. Serial Number Extraction and Key Derivation

### Serial Number Extraction

1. Read the `serial_number` field from the USB HID device descriptor
2. The serial number is an alphanumeric string (e.g., "SN201234567890AB")
3. Convert each character to its ASCII byte value
4. Store as a bytearray for key derivation

### Encryption Key Derivation

#### For Epoc X and Epoc+ (16-bit mode, KeyModel 6 or 8):

```
Given serial_number as bytearray sn:

crypto_key = bytearray([
    sn[-1], sn[-2], sn[-4], sn[-4], 
    sn[-2], sn[-1], sn[-2], sn[-4], 
    sn[-1], sn[-4], sn[-3], sn[-2], 
    sn[-1], sn[-2], sn[-2], sn[-3]
])
```

**Result:** 16-byte AES key derived from specific positions in the serial number

#### For Epoc+ (14-bit mode, KeyModel 5):

```
crypto_key = bytearray([
    sn[-1], 0x00, sn[-2], 0x15,
    sn[-3], 0x00, sn[-4], 0x0C,
    sn[-3], 0x00, sn[-2], 0x44,
    sn[-1], 0x00, sn[-2], 0x58
])
```

**Note:** The 14-bit mode uses interspersed zero bytes and fixed constants.

### AES Cipher Initialization

```
cipher = AES.new(crypto_key, AES.MODE_ECB)
```

**Encryption Mode:** AES-128 in ECB (Electronic Codebook) mode  
**Key Length:** 16 bytes (128 bits)  
**Block Size:** 16 bytes



---

## 4. Data Packet Reception

### Packet Reading Loop

```
WHILE service_running:
    raw_packet = hid_device.read(32)  // Read exactly 32 bytes
    
    IF length(raw_packet) != 32:
        LOG_WARNING("Invalid packet length")
        CONTINUE
    END IF
    
    packet_count = packet_count + 1
    process_packet(raw_packet)
END WHILE
```

### Packet Structure

- **Packet Size:** Fixed 32 bytes
- **Read Operation:** Blocking read from HID device
- **Packet Rate:** Approximately 128 Hz for EEG data, 16 Hz for motion data
- **Packet Counter:** Recommended for debugging and packet loss detection

### Timing Considerations

- **No Artificial Throttling:** Process packets as they arrive
- **Blocking Reads:** The HID read operation blocks until data is available
- **Packet Interleaving:** EEG and motion packets are interleaved on Epoc X

---

## 5. Packet Decryption (Model-Specific)

### Epoc X Decryption (KeyModel 8)

```
FUNCTION decrypt_epoc_x(raw_packet):
    // Step 1: XOR pre-processing
    xor_packet = bytearray(32)
    FOR i = 0 TO 31:
        xor_packet[i] = raw_packet[i] XOR 0x55
    END FOR
    
    // Step 2: AES decryption
    decrypted_packet = cipher.decrypt(xor_packet)
    
    RETURN decrypted_packet
END FUNCTION
```

**Critical:** The XOR operation with 0x55 is applied to ALL 32 bytes before AES decryption.

### Epoc+ Decryption (KeyModel 5 or 6)

```
FUNCTION decrypt_epoc_plus(raw_packet):
    // Step 1: Skip first byte, join remaining as Latin-1 string
    join_data = ''.join(chr(b) for b in raw_packet[1:])
    
    // Step 2: Convert to bytes using Latin-1 encoding
    byte_data = bytes(join_data, 'latin-1')
    
    // Step 3: AES decryption (first 32 bytes)
    decrypted_packet = cipher.decrypt(byte_data[0:32])
    
    RETURN decrypted_packet
END FUNCTION
```

**Critical:** Epoc+ skips byte[0] and uses Latin-1 encoding, NOT XOR preprocessing.



---

## 6. Packet Type Identification

### Packet Type Detection

```
FUNCTION identify_packet_type(decrypted_packet):
    IF decrypted_packet[1] == 32:  // decimal value
        RETURN "MOTION"
    ELSE:
        RETURN "EEG"
    END IF
END FUNCTION
```

### Packet Type Characteristics

| Packet Type | Byte[1] Value | Contains | Frequency |
|-------------|---------------|----------|-----------|
| EEG | != 32 | 14 EEG channels + quality data | ~128 Hz |
| Motion | == 32 | 6-axis IMU data (Epoc X only) | ~16 Hz |

**Note:** Motion packets are only present on Epoc X (KeyModel 8).

---

## 7. EEG Data Decoding

### Decoding Algorithm

```
FUNCTION decode_eeg_data(decrypted_packet):
    raw_values = []
    
    // Extract first 7 channels from bytes 2-15 (pairs: 2-3, 4-5, 6-7, 8-9, 10-11, 12-13, 14-15)
    FOR i = 2 TO 14 STEP 2:
        value_1 = decrypted_packet[i]
        value_2 = decrypted_packet[i + 1]
        raw_values.append(convert_epoc_value(value_1, value_2))
    END FOR
    
    // Extract remaining 7 channels from bytes 18-31 (pairs: 18-19, 20-21, 22-23, 24-25, 26-27, 28-29, 30-31)
    FOR i = 18 TO 30 STEP 2:
        value_1 = decrypted_packet[i]
        value_2 = decrypted_packet[i + 1]
        raw_values.append(convert_epoc_value(value_1, value_2))
    END FOR
    
    // Apply channel position swaps
    eeg_values = apply_channel_swaps(raw_values)
    
    RETURN eeg_values  // 14 float values in microvolts
END FUNCTION
```

### Value Conversion Formula

```
FUNCTION convert_epoc_value(value_1, value_2):
    result = ((value_1 * 0.128205128205129) + 4201.02564096001) + 
             ((value_2 - 128) * 32.82051289)
    RETURN result  // Format to 8 decimal places
END FUNCTION
```

**Units:** Microvolts (µV)  
**Precision:** 8 decimal places recommended



### Channel Position Swaps

After extracting 14 raw values, apply these swaps to correct channel ordering:

```
FUNCTION apply_channel_swaps(raw_values):
    // Swap AF3 (index 0) with F3 (index 2)
    SWAP(raw_values[0], raw_values[2])
    
    // Swap AF4 (index 13) with F4 (index 11)
    SWAP(raw_values[13], raw_values[11])
    
    // Swap F7 (index 1) with FC5 (index 3)
    SWAP(raw_values[1], raw_values[3])
    
    // Swap FC6 (index 10) with F8 (index 12)
    SWAP(raw_values[10], raw_values[12])
    
    RETURN raw_values
END FUNCTION
```

### Final Channel Order

After swaps, the 14 values correspond to:
**AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4**

---

## 8. Motion Data Decoding (Epoc X Only)

### Motion Packet Structure

Motion data is extracted from specific byte positions in the decrypted packet:

**Byte Positions:** [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31]

### Decoding Algorithm

```
FUNCTION decode_motion_data(decrypted_packet):
    motion_positions = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31]
    raw_motion = []
    
    // Process byte pairs
    FOR i = 0 TO length(motion_positions) STEP 2:
        pos1 = motion_positions[i]
        pos2 = motion_positions[i + 1]
        
        byte1 = decrypted_packet[pos1]
        byte2 = decrypted_packet[pos2]
        
        // Apply motion conversion formula
        value = 8191.88296790168 + (byte1 * 1.00343814821) + 
                ((byte2 - 128.00001) * 64.00318037383)
        
        raw_motion.append(value)
    END FOR
    
    // Extract first 6 values and apply scaling
    motion_data = [
        raw_motion[0] * (1.0 / 16384.0),  // AccX (g)
        raw_motion[1] * (1.0 / 16384.0),  // AccY (g)
        raw_motion[2] * (1.0 / 16384.0),  // AccZ (g)
        raw_motion[3] * (1.0 / 131.0),    // GyroX (deg/s)
        raw_motion[4] * (1.0 / 131.0),    // GyroY (deg/s)
        raw_motion[5] * (1.0 / 131.0)     // GyroZ (deg/s)
    ]
    
    RETURN motion_data  // 6 float values
END FUNCTION
```



### Motion Data Specifications

| Sensor | Channels | Units | Range | Scale Factor |
|--------|----------|-------|-------|--------------|
| Accelerometer | AccX, AccY, AccZ | g | ±2g | 1/16384.0 |
| Gyroscope | GyroX, GyroY, GyroZ | deg/s | ±250 deg/s | 1/131.0 |

**IMU Chip:** ICM-20948 (9-axis, magnetometer not used)  
**Sample Rate:** Approximately 16 Hz  
**Coordinate System:** Right-handed, headset-relative

---

## 9. Electrode Quality Extraction

### Quality Data Location

Electrode contact quality values are embedded in bytes 16-22 of EEG packets.

### Extraction Algorithm

```
FUNCTION extract_quality_values(decrypted_packet):
    quality_map = {
        'AF3':  decrypted_packet[16] & 0xF,
        'F7':   (decrypted_packet[16] >> 4) & 0xF,
        'F3':   decrypted_packet[17] & 0xF,
        'FC5':  (decrypted_packet[17] >> 4) & 0xF,
        'T7':   decrypted_packet[18] & 0xF,
        'P7':   (decrypted_packet[18] >> 4) & 0xF,
        'O1':   decrypted_packet[19] & 0xF,
        'O2':   (decrypted_packet[19] >> 4) & 0xF,
        'P8':   decrypted_packet[20] & 0xF,
        'T8':   (decrypted_packet[20] >> 4) & 0xF,
        'FC6':  decrypted_packet[21] & 0xF,
        'F4':   (decrypted_packet[21] >> 4) & 0xF,
        'F8':   decrypted_packet[22] & 0xF,
        'AF4':  (decrypted_packet[22] >> 4) & 0xF
    }
    
    RETURN quality_map
END FUNCTION
```

### Quality Value Interpretation

- **Data Type:** 4-bit unsigned integer (0-15)
- **Value Range:** 0 (worst) to 15 (best)
- **Encoding:** Two quality values per byte (lower 4 bits, upper 4 bits)
- **Update Rate:** Same as EEG data (~128 Hz)

### Quality Thresholds (Typical)

| Value Range | Quality Level | Interpretation |
|-------------|---------------|----------------|
| 0-3 | Poor | No contact or very poor signal |
| 4-7 | Fair | Marginal contact, high impedance |
| 8-11 | Good | Acceptable signal quality |
| 12-15 | Excellent | Optimal contact and signal |



---

## 10. Data Stream Specifications

### EEG Data Stream

| Parameter | Value |
|-----------|-------|
| **Channels** | 14 (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4) |
| **Sample Rate** | 128 Hz (nominal) |
| **Data Type** | 32-bit float |
| **Units** | Microvolts (µV) |
| **Bandwidth** | Typically 0.16-43 Hz (hardware filtered) |
| **Resolution** | 14-bit or 16-bit ADC (model dependent) |

### Motion Data Stream (Epoc X Only)

| Parameter | Value |
|-----------|-------|
| **Channels** | 6 (AccX, AccY, AccZ, GyroX, GyroY, GyroZ) |
| **Sample Rate** | 16 Hz (nominal) |
| **Data Type** | 32-bit float |
| **Accelerometer Units** | g (gravitational acceleration) |
| **Gyroscope Units** | deg/s (degrees per second) |
| **Accelerometer Range** | ±2g |
| **Gyroscope Range** | ±250 deg/s |

### Electrode Quality Stream

| Parameter | Value |
|-----------|-------|
| **Channels** | 14 (qAF3, qF7, qF3, qFC5, qT7, qP7, qO1, qO2, qP8, qT8, qFC6, qF4, qF8, qAF4) |
| **Sample Rate** | 128 Hz (nominal, same as EEG) |
| **Data Type** | 8-bit or 32-bit integer |
| **Value Range** | 0-15 |
| **Units** | Dimensionless quality metric |

### LSL Stream Metadata (Recommended)

For LabStreamingLayer implementations, include:

```xml
<info>
    <manufacturer>Emotiv</manufacturer>
    <model>Epoc X</model>
    <serial_number>[device_serial]</serial_number>
    <cap>
        <name>easycap-M1</name>
        <labelscheme>10-20</labelscheme>
    </cap>
</info>
```



---

## 11. Error Handling

### Packet-Level Error Handling

```
FUNCTION process_packet(raw_packet):
    TRY:
        // Validate packet length
        IF length(raw_packet) != 32:
            LOG_WARNING("Invalid packet length: " + length(raw_packet))
            RETURN
        END IF
        
        // Decrypt packet
        decrypted = decrypt_packet(raw_packet)
        
        // Identify and decode
        packet_type = identify_packet_type(decrypted)
        
        IF packet_type == "EEG":
            eeg_data = decode_eeg_data(decrypted)
            quality_data = extract_quality_values(decrypted)
            output_eeg_stream(eeg_data)
            output_quality_stream(quality_data)
            
        ELSE IF packet_type == "MOTION":
            motion_data = decode_motion_data(decrypted)
            output_motion_stream(motion_data)
        END IF
        
    CATCH DecryptionError:
        LOG_ERROR("Decryption failed for packet")
        // Continue to next packet
        
    CATCH DecodingError:
        LOG_ERROR("Decoding failed for packet")
        // Continue to next packet
        
    END TRY
END FUNCTION
```

### Device-Level Error Handling

| Error Condition | Recommended Action |
|-----------------|-------------------|
| Device not found | Retry enumeration every 5 seconds |
| Device disconnected | Attempt reconnection with exponential backoff |
| Read timeout | Log warning, continue reading |
| Decryption failure | Skip packet, log error, continue |
| Invalid packet length | Skip packet, log warning, continue |
| Quality extraction failure | Set quality to None, continue with EEG data |

### Robustness Guidelines

1. **Never terminate on single packet errors** - Continue processing subsequent packets
2. **Log all errors with packet numbers** - Enables debugging and quality assessment
3. **Maintain packet counters** - Detect packet loss or timing issues
4. **Implement reconnection logic** - Handle device disconnection gracefully
5. **Validate data ranges** - Detect corrupted packets (e.g., EEG values > 10000 µV)



---

## 12. Implementation Validation

### Reference Implementations

This specification is validated against:

1. **CyKit** (Python, Windows/Linux/macOS)
   - Location: `CyKit/Py3/eeg.py`
   - Version: 3.0
   - Status: Mature, widely used

2. **emotiv-lsl** (Python, cross-platform)
   - Location: `emotiv_lsl/emotiv_epoc_x.py`, `emotiv_lsl/emotiv_epoc_plus.py`
   - Version: 0.2.0
   - Status: Modern, LSL-focused

### Validation Test Cases

#### Test Case 1: Device Discovery
```
GIVEN: Emotiv Epoc X connected via USB
WHEN: enumerate_hid_devices() is called
THEN: Device with manufacturer="Emotiv" is found
AND: Device usage == 2 OR (usage == 0 AND interface_number == 1)
```

#### Test Case 2: Key Derivation
```
GIVEN: Serial number "SN201234567890AB"
WHEN: derive_crypto_key() is called
THEN: 16-byte key is generated from specific serial positions
AND: Key matches reference implementation output
```

#### Test Case 3: EEG Decoding
```
GIVEN: Valid encrypted EEG packet
WHEN: decrypt_and_decode() is called
THEN: 14 float values are returned
AND: Values are in range -10000 to +10000 µV (typical)
AND: Channel order is AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4
```

#### Test Case 4: Motion Decoding (Epoc X)
```
GIVEN: Valid encrypted motion packet (byte[1] == 32)
WHEN: decrypt_and_decode() is called
THEN: 6 float values are returned
AND: Accelerometer values are in range -2 to +2 g
AND: Gyroscope values are in range -250 to +250 deg/s
```

#### Test Case 5: Quality Extraction
```
GIVEN: Valid EEG packet
WHEN: extract_quality_values() is called
THEN: 14 integer values are returned
AND: All values are in range 0-15
AND: Values correspond to correct channels
```



---

## 13. Known Discrepancies and Notes

### Discrepancy Analysis: CyKit vs emotiv-lsl

#### 1. Epoc+ Key Derivation (RESOLVED)

**CyKit Implementation:**
```python
# 16-bit mode
k = [sn[-1],sn[-2],sn[-2],sn[-3],sn[-3],sn[-3],sn[-2],sn[-4],
     sn[-1],sn[-4],sn[-2],sn[-2],sn[-4],sn[-4],sn[-2],sn[-1]]
```

**emotiv-lsl Implementation:**
```python
# Uses same pattern as Epoc X
bytearray([sn[-1], sn[-2], sn[-4], sn[-4], sn[-2], sn[-1], sn[-2], sn[-4],
           sn[-1], sn[-4], sn[-3], sn[-2], sn[-1], sn[-2], sn[-2], sn[-3]])
```

**Status:** CyKit's Epoc+ key derivation differs from Epoc X. The emotiv-lsl implementation uses the Epoc X pattern for both, which may not work correctly for Epoc+ devices. **Recommendation:** Use CyKit's Epoc+ specific key derivation for KeyModel 5 and 6.

#### 2. Epoc+ Decryption Method (CONFIRMED DIFFERENCE)

**CyKit:** Uses Latin-1 string joining after skipping byte[0]  
**emotiv-lsl:** Correctly implements this for Epoc+  
**Status:** Both implementations agree. This is the correct method for Epoc+.

#### 3. Motion Data Availability (CONFIRMED)

**CyKit:** Motion data only for Epoc X  
**emotiv-lsl:** Motion data only for Epoc X  
**Status:** Consistent. Epoc+ does NOT provide motion data despite having byte[1]==32 packets.

#### 4. Quality Value Extraction (CONSISTENT)

Both implementations use identical bit-masking logic for bytes 16-22.  
**Status:** No discrepancy.

#### 5. Channel Swapping Logic (CONSISTENT)

Both implementations apply the same four swap operations.  
**Status:** No discrepancy.



### Critical Implementation Notes

#### 1. XOR Preprocessing (Epoc X ONLY)

**CRITICAL:** The XOR operation with 0x55 is ONLY applied to Epoc X (KeyModel 8). Do NOT apply to Epoc+ or original Epoc models.

```python
# CORRECT for Epoc X
data = [el ^ 0x55 for el in data]
data = cipher.decrypt(bytearray(data))

# CORRECT for Epoc+
join_data = ''.join(map(chr, data[1:]))
data = cipher.decrypt(bytes(join_data,'latin-1')[0:32])
```

#### 2. Byte[0] Handling

- **Epoc X:** Byte[0] is included in XOR and decryption
- **Epoc+:** Byte[0] is SKIPPED before decryption
- **Reason:** Different firmware encryption implementations

#### 3. Motion Packet Detection

The check `if data[1] == 32` must be performed on the DECRYPTED data, not the raw packet.

#### 4. Sample Rate Variability

The nominal sample rates (128 Hz EEG, 16 Hz motion) are approximate. Actual rates may vary by ±2% due to:
- USB polling intervals
- Firmware timing
- System load

**Recommendation:** Use timestamps for precise timing, not sample counts.

#### 5. Coordinate System (Motion Data)

The accelerometer and gyroscope coordinate system is headset-relative:
- **X-axis:** Left-right (positive = right)
- **Y-axis:** Front-back (positive = forward)
- **Z-axis:** Up-down (positive = up)

**Note:** This may differ from standard IMU conventions. Validate with physical testing.



---

## 14. Complete Implementation Pseudocode

### Main Loop

```
FUNCTION main_emotiv_client():
    // Initialize
    device = discover_emotiv_device()
    serial_number = extract_serial_number(device)
    crypto_key = derive_crypto_key(serial_number, model)
    cipher = initialize_aes_cipher(crypto_key)
    
    // Open HID device
    hid_device = open_hid_device(device.path)
    
    // Initialize output streams
    eeg_stream = create_eeg_stream()
    quality_stream = create_quality_stream()
    
    IF model == EPOC_X:
        motion_stream = create_motion_stream()
    END IF
    
    packet_count = 0
    
    // Main processing loop
    WHILE running:
        TRY:
            // Read packet
            raw_packet = hid_device.read(32)
            packet_count = packet_count + 1
            
            // Validate
            IF length(raw_packet) != 32:
                LOG_WARNING("Invalid packet length")
                CONTINUE
            END IF
            
            // Decrypt (model-specific)
            IF model == EPOC_X:
                decrypted = decrypt_epoc_x(raw_packet, cipher)
            ELSE IF model == EPOC_PLUS:
                decrypted = decrypt_epoc_plus(raw_packet, cipher)
            END IF
            
            // Identify packet type
            IF decrypted[1] == 32 AND model == EPOC_X:
                // Motion packet
                motion_data = decode_motion_data(decrypted)
                motion_stream.push(motion_data)
                
            ELSE:
                // EEG packet
                eeg_data = decode_eeg_data(decrypted)
                quality_data = extract_quality_values(decrypted)
                
                eeg_stream.push(eeg_data)
                quality_stream.push(quality_data)
            END IF
            
        CATCH Exception as e:
            LOG_ERROR("Packet processing error: " + e)
            // Continue to next packet
        END TRY
    END WHILE
    
    // Cleanup
    close_hid_device(hid_device)
    close_streams()
END FUNCTION
```



---

## 15. Platform-Specific Implementation Guidance

### Windows

**HID Library:** `hidapi` or `pywinusb`  
**Permissions:** Administrator rights may be required for initial device access  
**Driver:** Windows automatically installs HID driver  

**Key Considerations:**
- Use `hid.enumerate()` for device discovery
- No special udev rules needed
- May need to handle Windows service context for background operation

### Linux

**HID Library:** `hidapi` with libusb backend  
**Permissions:** Requires udev rules for non-root access  

**udev Rule Example:**
```
# /etc/udev/rules.d/99-emotiv.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="ed02", MODE="0666"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="ed02", MODE="0666"
```

**Key Considerations:**
- Reload udev rules: `sudo udevadm control --reload-rules`
- May need to unplug/replug device after rule installation
- Check `/dev/hidraw*` permissions

### macOS

**HID Library:** `hidapi` with IOKit backend  
**Permissions:** May require system extension approval  

**Key Considerations:**
- System Preferences → Security & Privacy → Privacy → Input Monitoring
- May need to grant terminal/application USB access permissions
- Use `hid.enumerate()` for device discovery



---

## 16. Bluetooth Communication (Future Consideration)

### Current Status

This specification covers **USB HID communication only**. The Emotiv headsets also support Bluetooth LE communication, but the protocol differs significantly.

### Bluetooth Protocol Differences

Based on references in the codebase:

1. **Connection Method:** Bluetooth LE GATT services instead of USB HID
2. **Encryption:** May use different key derivation or encryption scheme
3. **Packet Structure:** Likely different packet format and size
4. **Discovery:** Uses BLE scanning instead of USB enumeration

### Bluetooth Implementation Notes

From `README.md` and log files:
- CyKit supports Bluetooth with `bluetooth` flag
- Requires `EEGBtleLib64.dll` on Windows
- Auto-detection of Bluetooth devices by name pattern (e.g., "EPOCX (E50202E9)")
- May require different decryption keys

**Status:** Bluetooth protocol specification is OUT OF SCOPE for this document. A separate specification would be required for Bluetooth LE implementation.

---

## 17. Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Emotiv headset not found"

**Possible Causes:**
1. Device not connected or powered off
2. USB cable issue
3. Driver not installed (Windows)
4. Insufficient permissions (Linux)
5. Wrong interface selected

**Solutions:**
- Verify device appears in system USB devices
- Try different USB port
- Check device power/battery
- Install/update drivers
- Check udev rules (Linux)
- Verify manufacturer_string == "Emotiv"

#### Issue: "Decryption produces garbage data"

**Possible Causes:**
1. Wrong encryption key
2. Wrong decryption method for model
3. Corrupted serial number
4. Wrong KeyModel selected

**Solutions:**
- Verify serial number extraction
- Confirm KeyModel matches physical device
- Check XOR preprocessing (Epoc X only)
- Verify AES cipher initialization
- Compare key with reference implementation



#### Issue: "EEG values are unrealistic"

**Possible Causes:**
1. Incorrect channel swapping
2. Wrong conversion formula
3. Decryption error not caught
4. Poor electrode contact

**Solutions:**
- Verify all four channel swaps are applied
- Check conversion formula constants (8 decimal places)
- Validate decrypted data before decoding
- Check electrode quality values
- Compare with reference implementation output

#### Issue: "Motion data not appearing (Epoc X)"

**Possible Causes:**
1. Not checking for byte[1] == 32
2. Checking raw packet instead of decrypted
3. Motion stream not initialized
4. Headset not moving (motion packets are intermittent)

**Solutions:**
- Verify packet type check on decrypted data
- Initialize motion stream before main loop
- Move headset to trigger motion packets
- Check motion packet frequency (~16 Hz)

#### Issue: "Packet loss or timing issues"

**Possible Causes:**
1. System load too high
2. USB bandwidth issues
3. Processing too slow
4. Buffer overflow

**Solutions:**
- Reduce processing in main loop
- Use separate thread for data output
- Monitor packet counter for gaps
- Check system CPU usage
- Use faster USB port (USB 3.0)

---

## 18. Testing and Validation

### Unit Tests

```
TEST decode_eeg_packet:
    GIVEN: Known encrypted packet from reference implementation
    WHEN: decrypt_and_decode() is called
    THEN: Output matches reference implementation exactly
    
TEST extract_quality:
    GIVEN: Packet with known quality values
    WHEN: extract_quality_values() is called
    THEN: All 14 values match expected values
    
TEST channel_swaps:
    GIVEN: Array [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
    WHEN: apply_channel_swaps() is called
    THEN: Result is [2,3,0,1,4,5,6,7,8,9,12,13,10,11]
```



### Integration Tests

```
TEST end_to_end_epoc_x:
    GIVEN: Epoc X device connected
    WHEN: main_loop() runs for 10 seconds
    THEN: EEG packets received at ~128 Hz
    AND: Motion packets received at ~16 Hz
    AND: Quality values updated continuously
    AND: No decryption errors
    
TEST device_reconnection:
    GIVEN: Running client
    WHEN: Device is unplugged and replugged
    THEN: Client detects disconnection
    AND: Client reconnects automatically
    AND: Data streaming resumes
```

### Validation Against Reference Data

To validate a new implementation:

1. **Capture Reference Data:**
   - Run CyKit or emotiv-lsl
   - Record raw encrypted packets
   - Record decrypted/decoded output
   - Save to file with timestamps

2. **Compare Outputs:**
   - Feed same raw packets to new implementation
   - Compare decrypted data byte-by-byte
   - Compare decoded EEG values (tolerance: 0.001 µV)
   - Compare motion values (tolerance: 0.0001 g or deg/s)
   - Compare quality values (exact match)

3. **Statistical Validation:**
   - Mean EEG values should be near 4200 µV (baseline)
   - Standard deviation should be 50-500 µV (typical)
   - Motion values should be near 0 when stationary
   - Quality values should be stable over time

---

## 19. Appendix A: Byte-Level Packet Structure

### EEG Packet Structure (Decrypted)

| Byte Index | Content | Description |
|------------|---------|-------------|
| 0 | Counter | Packet sequence counter |
| 1 | Type | != 32 for EEG packets |
| 2-3 | Channel 1 | Raw value pair (before swapping) |
| 4-5 | Channel 2 | Raw value pair |
| 6-7 | Channel 3 | Raw value pair |
| 8-9 | Channel 4 | Raw value pair |
| 10-11 | Channel 5 | Raw value pair |
| 12-13 | Channel 6 | Raw value pair |
| 14-15 | Channel 7 | Raw value pair |
| 16 | Quality 1-2 | AF3 (low 4 bits), F7 (high 4 bits) |
| 17 | Quality 3-4 | F3 (low), FC5 (high) |
| 18 | Quality 5-6 | T7 (low), P7 (high) |
| 19 | Quality 7-8 | O1 (low), O2 (high) |
| 20 | Quality 9-10 | P8 (low), T8 (high) |
| 21 | Quality 11-12 | FC6 (low), F4 (high) |
| 22 | Quality 13-14 | F8 (low), AF4 (high) |
| 23-17 | Reserved | Unknown/unused |
| 18-19 | Channel 8 | Raw value pair |
| 20-21 | Channel 9 | Raw value pair |
| 22-23 | Channel 10 | Raw value pair |
| 24-25 | Channel 11 | Raw value pair |
| 26-27 | Channel 12 | Raw value pair |
| 28-29 | Channel 13 | Raw value pair |
| 30-31 | Channel 14 | Raw value pair |



### Motion Packet Structure (Decrypted, Epoc X Only)

| Byte Index | Content | Description |
|------------|---------|-------------|
| 0 | Counter | Packet sequence counter |
| 1 | Type | == 32 (0x20) for motion packets |
| 2-3 | Motion 1 | Raw value pair |
| 4-5 | Motion 2 | Raw value pair |
| 6-7 | Motion 3 | Raw value pair |
| 8-9 | Motion 4 | Raw value pair |
| 10-11 | Motion 5 | Raw value pair |
| 12-13 | Motion 6 | Raw value pair |
| 14-15 | Motion 7 | Raw value pair |
| 16-17 | Motion 8 | Raw value pair |
| 18-29 | Reserved | Unknown/unused |
| 30-31 | Motion 9 | Raw value pair |

**Note:** Only first 6 decoded motion values are used (AccX, AccY, AccZ, GyroX, GyroY, GyroZ)

---

## 20. Appendix B: Mathematical Formulas

### EEG Value Conversion

```
Given:
    value_1 = byte[i]     (0-255)
    value_2 = byte[i+1]   (0-255)

Calculate:
    term1 = value_1 * 0.128205128205129
    term2 = 4201.02564096001
    term3 = (value_2 - 128) * 32.82051289
    
    result_microvolts = term1 + term2 + term3
```

**Derivation:** Based on Emotiv SDK conversion formula for 14-bit and 16-bit ADC values.

### Motion Value Conversion

```
Given:
    byte1 = decrypted_packet[pos1]  (0-255)
    byte2 = decrypted_packet[pos2]  (0-255)

Calculate:
    raw_value = 8191.88296790168 + 
                (byte1 * 1.00343814821) + 
                ((byte2 - 128.00001) * 64.00318037383)
    
For accelerometer (indices 0-2):
    value_g = raw_value * (1.0 / 16384.0)
    
For gyroscope (indices 3-5):
    value_deg_per_sec = raw_value * (1.0 / 131.0)
```

**Derivation:** Based on ICM-20948 IMU specifications and CyKit gyro conversion formula.



---

## 21. Appendix C: Reference Implementation Comparison

### Key Differences Between CyKit and emotiv-lsl

| Aspect | CyKit | emotiv-lsl | Recommendation |
|--------|-------|------------|----------------|
| **Epoc+ Key (16-bit)** | Custom pattern | Uses Epoc X pattern | Use CyKit pattern |
| **Epoc+ Key (14-bit)** | Interspersed zeros | Not implemented | Use CyKit pattern |
| **Architecture** | Monolithic | Modular OOP | Either acceptable |
| **LSL Integration** | Optional | Primary focus | Depends on use case |
| **Web Interface** | Included | Not included | CyKit advantage |
| **Code Style** | Procedural | Object-oriented | Preference |
| **Motion Data** | Epoc X only | Epoc X only | Consistent |
| **Quality Extraction** | Identical | Identical | Consistent |
| **Channel Swaps** | Identical | Identical | Consistent |

### Validation Status

✅ **Validated and Consistent:**
- USB HID device discovery
- Epoc X key derivation
- Epoc X XOR preprocessing
- Epoc+ Latin-1 decryption
- EEG value conversion formula
- Motion value conversion formula
- Quality value extraction
- Channel swap operations
- Packet type identification

⚠️ **Requires Attention:**
- Epoc+ key derivation (use CyKit's pattern)
- Epoc+ 14-bit mode (not implemented in emotiv-lsl)

❌ **Not Validated:**
- Bluetooth communication (out of scope)
- Original Epoc (KeyModel 1, 2) - limited testing

---

## 22. Appendix D: Glossary of Terms

| Term | Definition |
|------|------------|
| **AES** | Advanced Encryption Standard, symmetric encryption algorithm |
| **ECB** | Electronic Codebook mode, AES block cipher mode |
| **HID** | Human Interface Device, USB device class |
| **IMU** | Inertial Measurement Unit, accelerometer + gyroscope |
| **LSL** | Lab Streaming Layer, real-time data streaming protocol |
| **µV** | Microvolt, unit of electrical potential (10^-6 volts) |
| **10-20 System** | International electrode placement system for EEG |
| **KeyModel** | Integer identifier for headset model/encryption variant |
| **Packet** | 32-byte data unit transmitted by headset |
| **Quality Value** | 4-bit metric (0-15) indicating electrode contact quality |



---

## 23. Appendix E: Quick Reference Card

### Device Discovery
```
manufacturer_string == "Emotiv"
AND (usage == 2 OR (usage == 0 AND interface_number == 1))
```

### Key Derivation (Epoc X, KeyModel 8)
```
key = [sn[-1], sn[-2], sn[-4], sn[-4], sn[-2], sn[-1], sn[-2], sn[-4],
       sn[-1], sn[-4], sn[-3], sn[-2], sn[-1], sn[-2], sn[-2], sn[-3]]
```

### Decryption (Epoc X)
```
1. XOR each byte with 0x55
2. AES-ECB decrypt
```

### Decryption (Epoc+)
```
1. Skip byte[0]
2. Join bytes[1:31] as Latin-1 string
3. AES-ECB decrypt first 32 bytes
```

### Packet Type
```
IF decrypted[1] == 32: MOTION
ELSE: EEG
```

### EEG Conversion
```
result = (value_1 * 0.128205128205129) + 4201.02564096001 + 
         ((value_2 - 128) * 32.82051289)
```

### Channel Swaps
```
SWAP(0, 2)   // AF3 ↔ F3
SWAP(13, 11) // AF4 ↔ F4
SWAP(1, 3)   // F7 ↔ FC5
SWAP(10, 12) // FC6 ↔ F8
```

### Quality Extraction
```
quality[channel] = byte[16+offset] & 0xF  (lower 4 bits)
quality[channel] = (byte[16+offset] >> 4) & 0xF  (upper 4 bits)
```

### Sample Rates
- **EEG:** 128 Hz
- **Motion:** 16 Hz (Epoc X only)
- **Quality:** 128 Hz

---

## 24. Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025 | AI Assistant | Initial comprehensive specification |

---

## 25. License and Usage

This specification document is provided for educational and development purposes. It is derived from analysis of open-source implementations (CyKit, emotiv-lsl) and publicly available information.

**Disclaimer:** This is a reverse-engineered specification. Emotiv Systems Inc. has not officially endorsed or validated this document. Use at your own risk.

**Recommended Citation:**
```
Emotiv Epoc Headset Communication Protocol Specification v1.0 (2025)
Derived from CyKit and emotiv-lsl reference implementations
```

---

**END OF SPECIFICATION**

