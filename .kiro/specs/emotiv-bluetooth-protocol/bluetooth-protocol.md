# Emotiv Epoc Bluetooth LE Protocol Specification

## Document Information

**Version:** 1.0  
**Date:** 2025  
**Status:** Preliminary Specification  
**Purpose:** Platform-independent specification for Bluetooth LE communication with Emotiv Epoc headsets

## Executive Summary

This document specifies the Bluetooth Low Energy (BLE) communication protocol for Emotiv Epoc family headsets. Unlike USB HID communication, BLE uses GATT (Generic Attribute Profile) services and characteristics for data transmission. This specification is derived from analysis of CyKit's Windows BLE implementation (`EEGBtleLib64.dll`) and cross-platform BLE requirements.

**Important:** BLE protocol differs significantly from USB HID protocol in connection method, packet structure, and data flow, but uses the same encryption and decoding algorithms after packet reception.

## Table of Contents

1. BLE vs USB Protocol Differences
2. GATT Service and Characteristic UUIDs
3. Device Discovery and Connection
4. GATT Service Discovery
5. Data Stream Initialization
6. Data Reception and Decoding
7. Encryption and Decryption (BLE-Specific)
8. Platform-Specific Implementation
9. Known Limitations and Issues

---

## 1. BLE vs USB Protocol Differences

### Communication Method

| Aspect | USB HID | Bluetooth LE |
|--------|---------|--------------|
| **Transport** | USB cable | Wireless (2.4 GHz) |
| **Protocol** | HID over USB | GATT over BLE |
| **Connection** | Plug-and-play | Pairing + connection |
| **Packet Size** | 32 bytes | 20 bytes (typical) |
| **Data Flow** | Blocking read | Asynchronous notifications |
| **Discovery** | USB enumeration | BLE scanning |
| **Serial Number** | USB descriptor | GATT characteristic read |
| **Power** | Bus-powered | Battery-powered |
| **Latency** | ~1ms | ~10-50ms (variable) |
| **Jitter** | Very low | Moderate |


### Key Similarities

Despite transport differences, BLE and USB share:
- **Same encryption algorithms** (AES-ECB with serial-derived keys)
- **Same key derivation** (from serial number)
- **Same EEG decoding formulas** (convertEPOC_PLUS)
- **Same channel ordering** (after swaps)
- **Same quality extraction** (from bytes 16-22)
- **Same motion data decoding** (Epoc X only)

### Critical Difference: Packet Structure

**USB HID:**
```
Read 32 bytes → Decrypt → Decode
```

**BLE GATT:**
```
Receive 20-byte notification → Reassemble if needed → Decrypt → Decode
```

---

## 2. GATT Service and Characteristic UUIDs

### Primary Data Service

**Service UUID:** (To be determined from CyKit implementation or PDF)

### EEG Data Characteristic

**Characteristic UUID:** (To be determined)
- **Properties:** NOTIFY
- **Description:** Streams encrypted EEG sensor data
- **Packet Rate:** ~128 Hz
- **Packet Size:** 20 bytes

### Motion Data Characteristic (Epoc X Only)

**Characteristic UUID:** `81072F42-9F3D-11E3-A9DC-0002A5D5C51B` (from grep results)
- **Properties:** NOTIFY
- **Description:** Streams encrypted motion sensor data (gyroscope/accelerometer)
- **Packet Rate:** ~16 Hz
- **Packet Size:** 20 bytes

### Device Information Service

**Service UUID:** `0000180A-0000-1000-8000-00805F9B34FB` (Standard BLE DIS)

#### Serial Number String Characteristic

**Characteristic UUID:** `00002A25-0000-1000-8000-00805F9B34FB` (Standard)
- **Properties:** READ
- **Description:** Device serial number for encryption key derivation
- **Format:** UTF-8 string (e.g., "SN201234567890AB")

---

## 3. Device Discovery and Connection

### BLE Scanning Algorithm

```
START BLE scan with timeout (e.g., 30 seconds)

FOR EACH discovered device:
    IF device.name CONTAINS "EPOC" OR device.name CONTAINS "Emotiv":
        STORE device.address
        STORE device.name
        ADD to candidate list
    END IF
END FOR

IF candidate list is empty:
    RAISE Exception("No Emotiv headset found via BLE")
END IF

RETURN candidate list
```

### Device Name Patterns

| Model | Typical BLE Name Pattern |
|-------|--------------------------|
| Epoc+ | "EPOCX-XXXX" or "Emotiv EPOC+" |
| Epoc X | "EPOCX (XXXXXXXX)" |

**Note:** Exact patterns may vary by firmware version.


### Connection Establishment

```
FUNCTION connect_to_device(device_address):
    connection_handle = NULL
    retry_count = 0
    max_retries = 3
    
    WHILE retry_count < max_retries AND connection_handle == NULL:
        TRY:
            connection_handle = ble_connect(device_address, timeout=10)
            
            IF connection_handle != NULL:
                LOG("Connected to device: " + device_address)
                RETURN connection_handle
            END IF
            
        CATCH ConnectionError as e:
            LOG_ERROR("Connection attempt " + retry_count + " failed: " + e)
            retry_count = retry_count + 1
            SLEEP(2^retry_count)  // Exponential backoff
        END TRY
    END WHILE
    
    RAISE Exception("Failed to connect after " + max_retries + " attempts")
END FUNCTION
```

### Connection Parameters

Recommended BLE connection parameters:
- **Connection Interval:** 7.5-15 ms (for 128 Hz EEG data)
- **Slave Latency:** 0 (for real-time streaming)
- **Supervision Timeout:** 4000 ms
- **MTU Size:** 23 bytes minimum (20-byte payload + 3-byte ATT header)

---

## 4. GATT Service Discovery

### Service Enumeration

```
FUNCTION discover_services(connection_handle):
    services = ble_enumerate_services(connection_handle)
    
    emotiv_service = NULL
    device_info_service = NULL
    
    FOR EACH service IN services:
        IF service.uuid == EMOTIV_DATA_SERVICE_UUID:
            emotiv_service = service
        ELSE IF service.uuid == DEVICE_INFORMATION_SERVICE_UUID:
            device_info_service = service
        END IF
    END FOR
    
    IF emotiv_service == NULL:
        RAISE Exception("Emotiv data service not found")
    END IF
    
    RETURN (emotiv_service, device_info_service)
END FUNCTION
```

### Characteristic Discovery

```
FUNCTION discover_characteristics(service):
    characteristics = ble_enumerate_characteristics(service)
    
    eeg_characteristic = NULL
    motion_characteristic = NULL
    
    FOR EACH characteristic IN characteristics:
        IF characteristic.uuid == EEG_DATA_CHARACTERISTIC_UUID:
            eeg_characteristic = characteristic
        ELSE IF characteristic.uuid == MOTION_DATA_CHARACTERISTIC_UUID:
            motion_characteristic = characteristic
        END IF
    END FOR
    
    IF eeg_characteristic == NULL:
        RAISE Exception("EEG data characteristic not found")
    END IF
    
    // Verify NOTIFY property
    IF NOT characteristic_has_property(eeg_characteristic, NOTIFY):
        RAISE Exception("EEG characteristic does not support notifications")
    END IF
    
    RETURN (eeg_characteristic, motion_characteristic)
END FUNCTION
```

---

## 5. Data Stream Initialization

### Enable Notifications

```
FUNCTION enable_notifications(characteristic):
    // Find Client Characteristic Configuration Descriptor (CCCD)
    cccd = find_descriptor(characteristic, CCCD_UUID)
    
    IF cccd == NULL:
        RAISE Exception("CCCD not found for characteristic")
    END IF
    
    // Write 0x0001 to enable notifications
    notification_enable_value = [0x01, 0x00]  // Little-endian
    write_descriptor(cccd, notification_enable_value)
    
    LOG("Notifications enabled for characteristic: " + characteristic.uuid)
END FUNCTION
```

### Register Notification Callback

```
FUNCTION register_callback(characteristic, callback_function):
    ble_register_notification_handler(characteristic, callback_function)
    LOG("Callback registered for characteristic: " + characteristic.uuid)
END FUNCTION
```


### Complete Initialization Sequence

```
FUNCTION initialize_ble_streaming(device_address):
    // 1. Connect
    connection_handle = connect_to_device(device_address)
    
    // 2. Discover services
    (emotiv_service, device_info_service) = discover_services(connection_handle)
    
    // 3. Read serial number
    serial_number = read_serial_number(device_info_service)
    
    // 4. Derive encryption key
    crypto_key = derive_crypto_key(serial_number, model)
    cipher = initialize_aes_cipher(crypto_key)
    
    // 5. Discover characteristics
    (eeg_char, motion_char) = discover_characteristics(emotiv_service)
    
    // 6. Enable notifications
    enable_notifications(eeg_char)
    IF motion_char != NULL:
        enable_notifications(motion_char)
    END IF
    
    // 7. Register callbacks
    register_callback(eeg_char, eeg_data_callback)
    IF motion_char != NULL:
        register_callback(motion_char, motion_data_callback)
    END IF
    
    LOG("BLE streaming initialized successfully")
    RETURN connection_handle
END FUNCTION
```

---

## 6. Data Reception and Decoding

### Notification Callback Structure

```
FUNCTION eeg_data_callback(characteristic, data):
    // data is a bytearray of length 20 (typical BLE packet size)
    
    IF length(data) != 20:
        LOG_WARNING("Unexpected packet size: " + length(data))
        RETURN
    END IF
    
    packet_count = packet_count + 1
    
    // Process packet (may need reassembly)
    process_ble_packet(data)
END FUNCTION
```

### Packet Reassembly (If Needed)

**Note:** If the headset sends data in 20-byte chunks that need to be reassembled into 32-byte packets for decryption:

```
GLOBAL packet_buffer = []
GLOBAL expected_packet_size = 32

FUNCTION process_ble_packet(data):
    packet_buffer.append(data)
    
    current_size = sum(length(chunk) for chunk in packet_buffer)
    
    IF current_size >= expected_packet_size:
        // Reassemble full packet
        full_packet = concatenate(packet_buffer)
        packet_buffer = []
        
        // Decrypt and decode
        decrypted = decrypt_packet(full_packet[0:32])
        decoded = decode_eeg_data(decrypted)
        
        output_eeg_stream(decoded)
    END IF
END FUNCTION
```

**Alternative:** If the headset sends complete encrypted packets in 20-byte notifications, no reassembly is needed. The exact behavior depends on the firmware implementation.

---

## 7. Encryption and Decryption (BLE-Specific)

### Serial Number Extraction via BLE

```
FUNCTION read_serial_number(device_info_service):
    serial_char = find_characteristic(device_info_service, SERIAL_NUMBER_UUID)
    
    IF serial_char == NULL:
        RAISE Exception("Serial number characteristic not found")
    END IF
    
    serial_bytes = read_characteristic(serial_char)
    serial_string = decode_utf8(serial_bytes)
    
    LOG("Serial number: " + serial_string)
    RETURN serial_string
END FUNCTION
```

### Key Derivation (Same as USB)

The key derivation algorithm is **identical** to USB HID:

```
// For Epoc X and Epoc+ (16-bit mode)
crypto_key = bytearray([
    sn[-1], sn[-2], sn[-4], sn[-4], 
    sn[-2], sn[-1], sn[-2], sn[-4], 
    sn[-1], sn[-4], sn[-3], sn[-2], 
    sn[-1], sn[-2], sn[-2], sn[-3]
])

cipher = AES.new(crypto_key, AES.MODE_ECB)
```


### Packet Decryption (Same as USB)

The decryption algorithm is **identical** to USB HID:

**For Epoc X:**
```
FUNCTION decrypt_epoc_x_ble(packet):
    // XOR preprocessing
    xor_packet = bytearray(length(packet))
    FOR i = 0 TO length(packet)-1:
        xor_packet[i] = packet[i] XOR 0x55
    END FOR
    
    // AES decryption
    decrypted = cipher.decrypt(xor_packet)
    RETURN decrypted
END FUNCTION
```

**For Epoc+:**
```
FUNCTION decrypt_epoc_plus_ble(packet):
    // Skip first byte, Latin-1 encoding
    join_data = ''.join(chr(b) for b in packet[1:])
    byte_data = bytes(join_data, 'latin-1')
    
    // AES decryption
    decrypted = cipher.decrypt(byte_data[0:32])
    RETURN decrypted
END FUNCTION
```

### EEG Data Decoding (Same as USB)

After decryption, use the **same** EEG decoding algorithm as USB:

```
FUNCTION decode_eeg_data(decrypted_packet):
    // Extract 14 channels from byte pairs
    raw_values = []
    
    FOR i = 2 TO 14 STEP 2:
        value_1 = decrypted_packet[i]
        value_2 = decrypted_packet[i + 1]
        raw_values.append(convertEPOC_PLUS(value_1, value_2))
    END FOR
    
    FOR i = 18 TO 30 STEP 2:
        value_1 = decrypted_packet[i]
        value_2 = decrypted_packet[i + 1]
        raw_values.append(convertEPOC_PLUS(value_1, value_2))
    END FOR
    
    // Apply channel swaps
    eeg_values = apply_channel_swaps(raw_values)
    
    RETURN eeg_values
END FUNCTION

FUNCTION convertEPOC_PLUS(value_1, value_2):
    result = ((value_1 * 0.128205128205129) + 4201.02564096001) + 
             ((value_2 - 128) * 32.82051289)
    RETURN result
END FUNCTION
```

---

## 8. Platform-Specific Implementation

### Windows Implementation (Using Windows Bluetooth GATT API)

**Key Functions:**
- `BluetoothGATTGetServices()` - Enumerate services
- `BluetoothGATTGetCharacteristics()` - Enumerate characteristics
- `BluetoothGATTGetDescriptors()` - Get CCCD
- `BluetoothGATTRegisterEvent()` - Register for notifications
- `BluetoothGATTSetDescriptorValue()` - Enable notifications

**Event Structure:**
```c
typedef struct _BTH_LE_GATT_CHARACTERISTIC_VALUE {
    ULONG DataSize;
    UCHAR Data[20];
} BTH_LE_GATT_CHARACTERISTIC_VALUE;

void CALLBACK ProcessEvent(
    BTH_LE_GATT_EVENT_TYPE EventType,
    PVOID EventOutParameter,
    PVOID Context
) {
    BLUETOOTH_GATT_VALUE_CHANGED_EVENT* event = 
        (BLUETOOTH_GATT_VALUE_CHANGED_EVENT*)EventOutParameter;
    
    if (event->CharacteristicValue->DataSize != 0) {
        // Process data
        process_packet(event->CharacteristicValue->Data, 
                      event->CharacteristicValue->DataSize);
    }
}
```

**CyKit Implementation:**
- Uses `EEGBtleLib64.dll` (C++ wrapper around Windows GATT API)
- Exports functions for Python ctypes binding
- Handles callback marshaling between C++ and Python


### Linux Implementation (Using BlueZ)

**Recommended Library:** `bluepy` or `bleak` (Python)

**Key Operations:**
```python
import bluepy.btle as btle

# Scanning
scanner = btle.Scanner()
devices = scanner.scan(timeout=10.0)

# Connection
peripheral = btle.Peripheral(device_address)

# Service discovery
services = peripheral.getServices()
emotiv_service = peripheral.getServiceByUUID(EMOTIV_SERVICE_UUID)

# Characteristic discovery
characteristics = emotiv_service.getCharacteristics()
eeg_char = emotiv_service.getCharacteristics(EEG_CHAR_UUID)[0]

# Enable notifications
class NotificationDelegate(btle.DefaultDelegate):
    def handleNotification(self, handle, data):
        process_packet(data)

peripheral.setDelegate(NotificationDelegate())
peripheral.writeCharacteristic(eeg_char.handle + 1, b"\x01\x00")

# Wait for notifications
while True:
    peripheral.waitForNotifications(1.0)
```

### macOS Implementation (Using CoreBluetooth)

**Recommended Library:** `bleak` (Python, cross-platform)

**Key Operations:**
```python
from bleak import BleakScanner, BleakClient

# Scanning
devices = await BleakScanner.discover(timeout=10.0)

# Connection
async with BleakClient(device_address) as client:
    # Service discovery (automatic)
    services = client.services
    
    # Enable notifications
    def notification_handler(sender, data):
        process_packet(data)
    
    await client.start_notify(EEG_CHAR_UUID, notification_handler)
    
    # Keep connection alive
    await asyncio.sleep(3600)
```

### Cross-Platform Abstraction

**Recommended Approach:** Use `bleak` library for unified API across Windows, Linux, and macOS.

```python
import asyncio
from bleak import BleakScanner, BleakClient

class EmotivBLEClient:
    def __init__(self, device_name_pattern="EPOC"):
        self.device_name_pattern = device_name_pattern
        self.client = None
        
    async def scan_and_connect(self):
        devices = await BleakScanner.discover(timeout=10.0)
        
        for device in devices:
            if self.device_name_pattern in device.name:
                self.client = BleakClient(device.address)
                await self.client.connect()
                return True
        
        return False
    
    async def start_streaming(self, callback):
        # Read serial number
        serial_bytes = await self.client.read_gatt_char(SERIAL_NUMBER_UUID)
        serial_number = serial_bytes.decode('utf-8')
        
        # Derive key
        self.crypto_key = derive_crypto_key(serial_number)
        
        # Enable notifications
        await self.client.start_notify(EEG_CHAR_UUID, callback)
```

---

## 9. Known Limitations and Issues

### BLE-Specific Challenges

1. **Connection Stability**
   - BLE connections are less stable than USB
   - Interference from other 2.4 GHz devices
   - Distance and obstacles affect signal quality
   - Automatic reconnection logic is essential

2. **Latency and Jitter**
   - BLE has higher latency than USB (~10-50ms vs ~1ms)
   - Packet timing is less consistent
   - Use timestamps for precise timing analysis

3. **Packet Loss**
   - BLE may experience packet loss in noisy environments
   - Implement packet counter and loss detection
   - Consider forward error correction if needed

4. **MTU Limitations**
   - Default MTU is 23 bytes (20-byte payload)
   - MTU negotiation may increase this on some platforms
   - Packet reassembly may be required

5. **Platform Differences**
   - Windows, Linux, and macOS have different BLE APIs
   - Behavior may vary across platforms
   - Thorough testing on all target platforms is required


### Model-Specific Notes

**Epoc+ via BLE:**
- Confirmed working in CyKit implementation
- Uses same encryption as USB Epoc+
- 20-byte BLE packets
- No motion data

**Epoc X via BLE:**
- Motion data available via separate characteristic
- Uses same encryption as USB Epoc X (with XOR preprocessing)
- 20-byte BLE packets
- Motion characteristic UUID: `81072F42-9F3D-11E3-A9DC-0002A5D5C51B`

### Firmware Considerations

- BLE behavior may vary by firmware version
- Some firmware versions may use different UUIDs
- Always verify UUIDs through service discovery
- Document firmware version for reproducibility

### Power Management

**Battery Life:**
- BLE mode significantly extends battery life vs USB
- Typical battery life: 6-12 hours (model dependent)
- Connection interval affects power consumption
- Notification rate affects power consumption

**Connection Parameters for Power Optimization:**
- Longer connection intervals (15-30ms) reduce power
- Slave latency can be used for further optimization
- Trade-off between latency and battery life

---

## 10. Comparison Table: USB vs BLE

| Feature | USB HID | Bluetooth LE |
|---------|---------|--------------|
| **Connection Type** | Wired | Wireless |
| **Setup Complexity** | Low (plug-and-play) | Medium (pairing, discovery) |
| **Packet Size** | 32 bytes | 20 bytes (typical) |
| **Data Flow** | Synchronous (blocking read) | Asynchronous (notifications) |
| **Latency** | ~1ms | ~10-50ms |
| **Jitter** | Very low | Moderate |
| **Packet Loss** | Rare | Possible |
| **Power Source** | Bus-powered | Battery |
| **Battery Life** | N/A | 6-12 hours |
| **Range** | Cable length (~2m) | ~10m (line of sight) |
| **Interference** | None | 2.4 GHz band |
| **Encryption** | AES-ECB | AES-ECB (same) |
| **Key Derivation** | From USB descriptor | From GATT characteristic (same algorithm) |
| **EEG Decoding** | convertEPOC_PLUS | convertEPOC_PLUS (same) |
| **Quality Extraction** | Bytes 16-22 | Bytes 16-22 (same) |
| **Motion Data** | Byte[1]==32 | Separate characteristic |
| **Platform Support** | Windows, Linux, macOS | Windows, Linux, macOS |
| **Library Complexity** | Low (hidapi) | Medium (platform-specific BLE) |

---

## 11. Implementation Checklist

### Phase 1: Basic BLE Connection
- [ ] Implement BLE scanning
- [ ] Implement device filtering by name
- [ ] Implement connection establishment
- [ ] Implement connection error handling
- [ ] Test on target platform(s)

### Phase 2: GATT Operations
- [ ] Implement service discovery
- [ ] Implement characteristic discovery
- [ ] Implement descriptor discovery (CCCD)
- [ ] Implement characteristic read (serial number)
- [ ] Test GATT operations

### Phase 3: Data Streaming
- [ ] Implement notification enable
- [ ] Implement notification callback
- [ ] Implement packet reassembly (if needed)
- [ ] Test data reception
- [ ] Verify packet rate

### Phase 4: Decryption and Decoding
- [ ] Implement key derivation (reuse USB code)
- [ ] Implement packet decryption (reuse USB code)
- [ ] Implement EEG decoding (reuse USB code)
- [ ] Implement quality extraction (reuse USB code)
- [ ] Implement motion decoding (Epoc X, reuse USB code)
- [ ] Verify decoded values match USB

### Phase 5: Robustness
- [ ] Implement disconnection detection
- [ ] Implement automatic reconnection
- [ ] Implement packet loss detection
- [ ] Implement error logging
- [ ] Test long-duration streaming

### Phase 6: Cross-Platform
- [ ] Test on Windows
- [ ] Test on Linux
- [ ] Test on macOS
- [ ] Document platform-specific issues
- [ ] Create unified API

---

## 12. Troubleshooting Guide

### Issue: "Device not found during scan"

**Possible Causes:**
1. Headset not powered on
2. Headset already connected to another device
3. Headset out of range
4. Bluetooth disabled on host

**Solutions:**
- Verify headset is powered on (LED indicator)
- Disconnect from other devices
- Move headset closer to host
- Enable Bluetooth on host
- Increase scan timeout

### Issue: "Connection fails repeatedly"

**Possible Causes:**
1. Weak signal
2. Interference
3. Headset battery low
4. Pairing required but not completed

**Solutions:**
- Move headset closer
- Remove interference sources
- Charge headset
- Complete pairing process
- Restart Bluetooth stack


### Issue: "Notifications not received"

**Possible Causes:**
1. CCCD not written correctly
2. Callback not registered
3. Connection lost
4. Characteristic does not support notifications

**Solutions:**
- Verify CCCD write (0x0001)
- Verify callback registration
- Check connection state
- Verify characteristic properties
- Check platform-specific notification handling

### Issue: "Decrypted data is garbage"

**Possible Causes:**
1. Wrong encryption key
2. Wrong decryption method
3. Packet reassembly error
4. Wrong model selected

**Solutions:**
- Verify serial number read correctly
- Verify key derivation algorithm
- Check packet size and reassembly logic
- Verify model-specific decryption (XOR for Epoc X)
- Compare with USB implementation

### Issue: "High packet loss"

**Possible Causes:**
1. Weak signal
2. Interference
3. Host CPU overload
4. Connection interval too long

**Solutions:**
- Move headset closer
- Remove interference sources
- Reduce host CPU load
- Negotiate shorter connection interval
- Use faster hardware

---

## 13. Reference Implementation Pseudocode

### Complete BLE Client

```
FUNCTION main_ble_client():
    // Phase 1: Discovery and Connection
    LOG("Starting BLE scan...")
    devices = scan_for_emotiv_devices(timeout=30)
    
    IF length(devices) == 0:
        RAISE Exception("No Emotiv headset found")
    END IF
    
    target_device = devices[0]
    LOG("Connecting to: " + target_device.name)
    
    connection_handle = connect_to_device(target_device.address)
    
    // Phase 2: Service Discovery
    LOG("Discovering services...")
    (emotiv_service, device_info_service) = discover_services(connection_handle)
    
    // Phase 3: Serial Number and Key Derivation
    LOG("Reading serial number...")
    serial_number = read_serial_number(device_info_service)
    
    LOG("Deriving encryption key...")
    crypto_key = derive_crypto_key(serial_number, model=EPOC_X)
    cipher = initialize_aes_cipher(crypto_key)
    
    // Phase 4: Characteristic Discovery
    LOG("Discovering characteristics...")
    (eeg_char, motion_char) = discover_characteristics(emotiv_service)
    
    // Phase 5: Initialize Streaming
    LOG("Enabling notifications...")
    enable_notifications(eeg_char)
    
    IF motion_char != NULL:
        enable_notifications(motion_char)
    END IF
    
    // Phase 6: Register Callbacks
    LOG("Registering callbacks...")
    register_callback(eeg_char, eeg_notification_handler)
    
    IF motion_char != NULL:
        register_callback(motion_char, motion_notification_handler)
    END IF
    
    // Phase 7: Initialize Output Streams
    eeg_stream = create_lsl_outlet("EmotivEEG", 14, 128)
    quality_stream = create_lsl_outlet("EmotivQuality", 14, 128)
    
    IF motion_char != NULL:
        motion_stream = create_lsl_outlet("EmotivMotion", 6, 16)
    END IF
    
    LOG("Streaming started. Press Ctrl+C to stop.")
    
    // Phase 8: Main Loop (keep connection alive)
    WHILE running:
        check_connection_state(connection_handle)
        SLEEP(1)
    END WHILE
    
    // Cleanup
    disconnect(connection_handle)
    close_streams()
    LOG("Streaming stopped.")
END FUNCTION

FUNCTION eeg_notification_handler(characteristic, data):
    TRY:
        // Decrypt
        decrypted = decrypt_packet(data, cipher, model=EPOC_X)
        
        // Decode EEG
        eeg_values = decode_eeg_data(decrypted)
        quality_values = extract_quality_values(decrypted)
        
        // Output
        eeg_stream.push_sample(eeg_values)
        quality_stream.push_sample(quality_values)
        
    CATCH Exception as e:
        LOG_ERROR("EEG processing error: " + e)
    END TRY
END FUNCTION

FUNCTION motion_notification_handler(characteristic, data):
    TRY:
        // Decrypt
        decrypted = decrypt_packet(data, cipher, model=EPOC_X)
        
        // Decode motion
        motion_values = decode_motion_data(decrypted)
        
        // Output
        motion_stream.push_sample(motion_values)
        
    CATCH Exception as e:
        LOG_ERROR("Motion processing error: " + e)
    END TRY
END FUNCTION
```

---

## 14. Future Work and Open Questions

### Questions Requiring PDF/CyKit Analysis

1. **Exact GATT Service UUID** - Need to extract from CyKit or PDF
2. **Exact EEG Characteristic UUID** - Need to extract from CyKit or PDF
3. **Packet Reassembly Requirements** - Does firmware send 20-byte or 32-byte chunks?
4. **Pairing Requirements** - Is pairing mandatory or optional?
5. **Firmware Version Differences** - Do UUIDs change across firmware versions?

### Potential Enhancements

1. **MTU Negotiation** - Request larger MTU for efficiency
2. **Connection Parameter Optimization** - Tune for latency vs power
3. **Packet Loss Recovery** - Implement forward error correction
4. **Multi-Device Support** - Connect to multiple headsets simultaneously
5. **Firmware Update via BLE** - OTA update capability

---

## 15. Appendix A: GATT Attribute Table

| Attribute Type | UUID | Properties | Description |
|----------------|------|------------|-------------|
| **Primary Service** | TBD | - | Emotiv Data Service |
| Characteristic | TBD | NOTIFY | EEG Data Stream |
| CCCD | 0x2902 | READ, WRITE | Enable/disable EEG notifications |
| Characteristic | 81072F42-9F3D-11E3-A9DC-0002A5D5C51B | NOTIFY | Motion Data Stream (Epoc X) |
| CCCD | 0x2902 | READ, WRITE | Enable/disable motion notifications |
| **Primary Service** | 0x180A | - | Device Information Service |
| Characteristic | 0x2A25 | READ | Serial Number String |
| Characteristic | 0x2A29 | READ | Manufacturer Name String |
| Characteristic | 0x2A24 | READ | Model Number String |
| Characteristic | 0x2A26 | READ | Firmware Revision String |

**Note:** UUIDs marked "TBD" require extraction from CyKit implementation or PDF documentation.

---

## 16. Appendix B: Error Codes

### BLE-Specific Error Codes

| Error Code | Description | Recommended Action |
|------------|-------------|-------------------|
| CONNECTION_TIMEOUT | Connection attempt timed out | Retry with exponential backoff |
| CONNECTION_REFUSED | Device refused connection | Check pairing status |
| SERVICE_NOT_FOUND | Required service not discovered | Verify device model |
| CHARACTERISTIC_NOT_FOUND | Required characteristic not found | Verify firmware version |
| NOTIFICATION_FAILED | Failed to enable notifications | Check CCCD write |
| DISCONNECTED | Connection lost | Attempt reconnection |
| ENCRYPTION_ERROR | Decryption failed | Verify serial number and key |
| PACKET_SIZE_ERROR | Unexpected packet size | Log and skip packet |

---

## 17. Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025 | AI Assistant | Initial specification based on CyKit analysis |

---

## 18. References

1. **CyKit Implementation** - `Py3/eeg.py`, `Py3/EEGBtleLib/`
2. **Bluetooth Core Specification** - Version 5.0+
3. **GATT Specification** - Bluetooth SIG
4. **Device Information Service** - Bluetooth SIG Assigned Numbers
5. **Emotiv USB Protocol Specification** - `protocol.md` (companion document)

---

**END OF BLUETOOTH PROTOCOL SPECIFICATION**

**Note to Implementers:** This specification is based on analysis of CyKit's BLE implementation and cross-platform BLE requirements. Some UUIDs and implementation details require extraction from the CyKit source code or the official Bluetooth Development PDF. Please refer to those resources for complete implementation details.
