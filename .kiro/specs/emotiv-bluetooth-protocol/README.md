# Emotiv Bluetooth LE Protocol Specification

This directory contains a comprehensive specification for Bluetooth Low Energy (BLE) communication with Emotiv Epoc family headsets.

## Documents

### bluetooth-protocol.md
**Complete Technical Specification** - The main document containing:
- BLE vs USB protocol differences
- GATT service and characteristic UUIDs
- Device discovery and connection procedures
- Service and characteristic discovery
- Notification registration and data streaming
- Encryption and decryption (same as USB)
- Platform-specific implementations (Windows, Linux, macOS)
- Complete pseudocode implementations
- Troubleshooting guide
- Reference implementation

**Use this document to:** Build a BLE client implementation for Emotiv headsets

### requirements.md
**Structured Requirements** - EARS-compliant requirements with:
- User stories and acceptance criteria
- Testable specifications for BLE operations
- Clear success criteria for each requirement

**Use this document to:** Validate BLE implementation completeness and correctness

## Key Findings

### BLE vs USB Differences

**Different:**
- ❌ Transport: Wireless vs Wired
- ❌ Packet Size: 20 bytes vs 32 bytes
- ❌ Data Flow: Asynchronous notifications vs Blocking reads
- ❌ Discovery: BLE scanning vs USB enumeration
- ❌ Connection: Pairing required vs Plug-and-play
- ❌ Latency: ~10-50ms vs ~1ms
- ❌ Jitter: Moderate vs Very low

**Same:**
- ✅ Encryption: AES-ECB with serial-derived keys
- ✅ Key Derivation: From serial number (same algorithm)
- ✅ EEG Decoding: convertEPOC_PLUS formula
- ✅ Channel Ordering: After swaps
- ✅ Quality Extraction: From bytes 16-22
- ✅ Motion Decoding: Epoc X only

### Critical Insight

**BLE uses different transport and packet structure, but the same cryptography and data decoding as USB.** This means you can reuse 90% of your USB decoding code for BLE - you just need to handle the BLE connection and notification layer differently.

## Implementation Status

### Validated
✅ BLE connection flow (from CyKit structure)  
✅ GATT service/characteristic pattern  
✅ Notification-based data reception  
✅ Same encryption/decoding as USB  
✅ Windows implementation pattern (EEGBtleLib)  

### Requires Verification
⚠️ **Exact GATT Service UUID** - Need CyKit source or PDF  
⚠️ **Exact EEG Characteristic UUID** - Need CyKit source or PDF  
⚠️ **Packet reassembly requirements** - 20-byte vs 32-byte chunks  
⚠️ **Pairing requirements** - Mandatory or optional?  
⚠️ **Firmware version differences** - UUID variations?  

## Quick Start

To implement a BLE client for Emotiv headsets:

1. **Read bluetooth-protocol.md sections 1-5** for BLE basics
2. **Implement BLE scanning** (section 3)
3. **Implement GATT connection** (section 3)
4. **Discover services and characteristics** (section 4)
5. **Enable notifications** (section 5)
6. **Register callbacks** (section 5)
7. **Reuse USB decryption code** (section 7)
8. **Reuse USB decoding code** (section 7)
9. **Test on target platform** (section 8)

## Supported Models

| Model | BLE Support | Motion Data | Status |
|-------|-------------|-------------|--------|
| Epoc (Original) | Unknown | No | Not documented |
| Epoc+ | Yes | No | Validated in CyKit |
| Epoc X | Yes | Yes | Validated in CyKit |

## Platform Support

| Platform | BLE Library | Status | Notes |
|----------|-------------|--------|-------|
| Windows | Windows GATT API | Validated | CyKit uses EEGBtleLib64.dll |
| Linux | BlueZ (bluepy/bleak) | Recommended | Not tested in CyKit |
| macOS | CoreBluetooth (bleak) | Recommended | Not tested in CyKit |

**Recommendation:** Use `bleak` Python library for cross-platform BLE support.

## Known Limitations

1. **Connection Stability** - BLE less stable than USB, requires reconnection logic
2. **Latency** - Higher and more variable than USB (~10-50ms vs ~1ms)
3. **Packet Loss** - Possible in noisy environments
4. **Platform Differences** - Different BLE APIs across OS
5. **Battery Life** - Headset runs on battery (6-12 hours typical)

## Missing Information

To complete this specification, we need:

1. **CyKit Source Code Access** - Specifically `Py3/eeg.py` and `Py3/EEGBtleLib/`
2. **Bluetooth Development PDF** - From `https://github.com/CymatiCorp/CyKit/blob/git-images/Documentation/Bluetooth_Development-Epoc.pdf`
3. **Exact GATT UUIDs** - For service and characteristics
4. **Packet Structure Details** - Reassembly requirements
5. **Firmware Behavior** - Version-specific differences

## Next Steps

1. **Extract UUIDs** from CyKit or PDF
2. **Verify packet structure** (20-byte vs 32-byte)
3. **Test on real hardware** with BLE connection
4. **Document firmware versions** and any differences
5. **Create reference implementation** using bleak

## Contributing

If you have access to:
- CyKit BLE source code
- Bluetooth Development PDF
- Real Emotiv hardware with BLE
- Firmware version information

Please help complete this specification by providing:
- Exact GATT service and characteristic UUIDs
- Packet structure and reassembly details
- Pairing requirements
- Firmware version differences
- Test results on different platforms

## Related Documents

- **USB Protocol Specification** - `../emotiv-protocol-specification/protocol.md`
- **USB Requirements** - `../emotiv-protocol-specification/requirements.md`
- **CyKit Repository** - https://github.com/CymatiCorp/CyKit

---

**Status:** Preliminary specification based on CyKit structure analysis. Requires validation with actual BLE implementation and hardware testing.
