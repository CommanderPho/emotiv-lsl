# Emotiv Protocol Specification

This directory contains a comprehensive, platform-independent specification for communicating with Emotiv Epoc family headsets.

## Documents

### protocol.md
**Complete Technical Specification** - The main document containing:
- Hardware overview and model specifications
- USB HID device discovery procedures
- Encryption key derivation algorithms
- Packet decryption methods (model-specific)
- EEG, motion, and quality data decoding
- Complete pseudocode implementations
- Validation test cases
- Troubleshooting guide
- Mathematical formulas and byte-level packet structures

**Use this document to:** Build a new client implementation in any language/platform

### requirements.md
**Structured Requirements** - EARS-compliant requirements with:
- User stories and acceptance criteria
- Testable specifications
- Clear success criteria

**Use this document to:** Validate implementation completeness and correctness

## Validation Status

This specification has been validated against two independent reference implementations:

1. **CyKit** (Python, mature, widely-used)
   - Location: `CyKit/Py3/eeg.py`
   - Version: 3.0

2. **emotiv-lsl** (Python, modern, LSL-focused)
   - Location: `emotiv_lsl/emotiv_epoc_x.py`, `emotiv_lsl/emotiv_epoc_plus.py`
   - Version: 0.2.0

## Key Findings

### Validated and Consistent
✅ USB HID device discovery  
✅ Epoc X key derivation and XOR preprocessing  
✅ Epoc+ Latin-1 decryption method  
✅ EEG value conversion formula  
✅ Motion data decoding (Epoc X)  
✅ Quality value extraction  
✅ Channel swap operations  

### Known Discrepancies
⚠️ **Epoc+ Key Derivation:** CyKit uses a different pattern than Epoc X. The emotiv-lsl implementation incorrectly uses the Epoc X pattern for Epoc+. **Recommendation:** Use CyKit's Epoc+ specific key derivation.

⚠️ **Epoc+ 14-bit Mode:** Not implemented in emotiv-lsl, only documented in CyKit.

## Quick Start

To implement a new Emotiv client:

1. Read **protocol.md** sections 1-7 for basic communication
2. Implement device discovery (section 2)
3. Implement key derivation for your target model (section 3)
4. Implement model-specific decryption (section 5)
5. Implement EEG decoding (section 7)
6. Optionally implement motion data (section 8) and quality extraction (section 9)
7. Validate against test cases (section 12)

## Supported Models

| Model | KeyModel | Motion | Status |
|-------|----------|--------|--------|
| Epoc (Original) | 1, 2 | No | Limited validation |
| Epoc+ (14-bit) | 5 | No | Documented, not tested |
| Epoc+ (16-bit) | 6 | No | Validated |
| Epoc X | 8 | Yes | Fully validated |

## Out of Scope

- **Bluetooth LE Communication:** This specification covers USB HID only
- **Emotiv SDK Integration:** This is a reverse-engineered protocol
- **Official Support:** Not endorsed by Emotiv Systems Inc.

## Contributing

If you find discrepancies or have additional validation data, please document them with:
- Model and KeyModel
- Reference implementation used
- Specific byte values and expected vs actual results
- Platform and library versions
