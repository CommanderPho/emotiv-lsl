# LSL Stream Compatibility Verification Report

## Overview

This document verifies that BLE and USB connections produce identical LSL stream metadata, ensuring compatibility with existing analysis tools regardless of connection type.

## Verification Date

November 18, 2025

## Requirements Tested

- **Requirement 3.1**: EEG stream name "Epoc X" with identical metadata
- **Requirement 3.2**: Motion stream name "Epoc X Motion" with identical channel names and units
- **Requirement 3.3**: Quality stream name "Epoc X eQuality" with identical channel configuration
- **Requirement 3.4**: source_id format consistency across connection types
- **Requirement 3.5**: Timestamp synchronization mechanism consistency

## Verification Method

The verification was performed using the `scripts/verify_lsl_stream_compatibility.py` script, which:

1. Creates EmotivEpocX instances with both USB and BLE connection types
2. Generates LSL StreamInfo objects for each stream type (EEG, Motion, Quality)
3. Extracts and compares all metadata fields
4. Reports any differences found

## Test Results

### ✓ PASS: EEG Stream (Requirement 3.1)

**Stream Properties:**
- Stream Name: `Epoc X`
- Stream Type: `EEG`
- Channel Count: `14`
- Sampling Rate: `128.0 Hz`
- Channel Format: `cf_float32`
- Channels: `AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4`
- Units: `microvolts`
- Cap: `easycap-M1` (10-20 system)

**Verification:**
- ✓ Stream name identical for USB and BLE
- ✓ Channel count identical (14 channels)
- ✓ Sampling rate identical (128 Hz)
- ✓ Channel names identical and in same order
- ✓ Channel units identical (microvolts)
- ✓ Channel types identical (EEG)
- ✓ Cap configuration identical

### ✓ PASS: Motion Stream (Requirement 3.2)

**Stream Properties:**
- Stream Name: `Epoc X Motion`
- Stream Type: `SIGNAL`
- Channel Count: `6`
- Sampling Rate: `16.0 Hz`
- Channel Format: `cf_float32`
- Channels:
  - `AccX`: g (ACC)
  - `AccY`: g (ACC)
  - `AccZ`: g (ACC)
  - `GyroX`: deg/s (GYRO)
  - `GyroY`: deg/s (GYRO)
  - `GyroZ`: deg/s (GYRO)

**Verification:**
- ✓ Stream name identical for USB and BLE
- ✓ Channel count identical (6 channels)
- ✓ Sampling rate identical (16 Hz)
- ✓ Channel names identical and in same order
- ✓ Channel units identical (g for accelerometer, deg/s for gyroscope)
- ✓ Channel types identical (ACC for accelerometer, GYRO for gyroscope)

### ✓ PASS: Quality Stream (Requirement 3.3)

**Stream Properties:**
- Stream Name: `Epoc X eQuality`
- Stream Type: `Raw`
- Channel Count: `14`
- Sampling Rate: `128.0 Hz`
- Channel Format: `cf_float32`
- Channels: `qAF3, qF7, qF3, qFC5, qT7, qP7, qO1, qO2, qP8, qT8, qFC6, qF4, qF8, qAF4`
- Units: `microvolts`
- Cap: `easycap-M1` (10-20 system)

**Verification:**
- ✓ Stream name identical for USB and BLE
- ✓ Channel count identical (14 channels)
- ✓ Sampling rate identical (128 Hz)
- ✓ Channel names identical and in same order (with 'q' prefix)
- ✓ Channel units identical (microvolts)
- ✓ Channel types identical (RAW)
- ✓ Cap configuration identical

### ✓ PASS: source_id Format (Requirement 3.4)

**Format Structure:**
```
{device_name}_{key_model}_{crypto_key_hex}
```

**Example:**
```
Emotiv Epoc X_8_46454343454645434643444546454544
```

**Verification:**
- ✓ source_id format has 3 parts for both USB and BLE
- ✓ Device name component identical: `Emotiv Epoc X`
- ✓ Key model component identical: `8`
- ✓ Crypto key component identical (when using same serial number)
- ✓ Format structure consistent across connection types

**Note:** The crypto key component will differ between devices (based on serial number) but the format structure remains consistent.

### ✓ PASS: Timestamp Synchronization (Requirement 3.5)

**Verification Method:**
Code inspection of `emotiv_base.py` confirms that both USB and BLE connections use the same timestamp synchronization mechanism.

**Implementation:**
- Both connection types inherit from `EmotivBase`
- `EmotivBase` uses `EasyTimeSyncParsingMixin` for timestamp synchronization
- The `add_lsl_outlet_info_common()` method calls `EasyTimeSyncParsingMixin_add_lsl_outlet_info()` for all streams
- This ensures identical timestamp metadata for both USB and BLE connections

**Verification:**
- ✓ Both USB and BLE use `EasyTimeSyncParsingMixin`
- ✓ Same timestamp metadata added to all stream types
- ✓ Timestamp synchronization mechanism identical

## Summary

**All requirements verified successfully:**

| Requirement | Status | Description |
|-------------|--------|-------------|
| 3.1 | ✓ PASS | EEG stream metadata identical |
| 3.2 | ✓ PASS | Motion stream metadata identical |
| 3.3 | ✓ PASS | Quality stream metadata identical |
| 3.4 | ✓ PASS | source_id format consistent |
| 3.5 | ✓ PASS | Timestamp synchronization identical |

## Conclusion

The verification confirms that **BLE and USB connections produce fully compatible LSL streams**. Analysis tools and recording software that work with USB connections will work identically with BLE connections without any modifications.

### Key Findings:

1. **Stream Names**: Identical across connection types
   - EEG: "Epoc X"
   - Motion: "Epoc X Motion"
   - Quality: "Epoc X eQuality"

2. **Channel Configuration**: Identical for all streams
   - Same channel names, order, units, and types
   - Same sampling rates (128 Hz for EEG/Quality, 16 Hz for Motion)

3. **Metadata**: Identical for all streams
   - Same manufacturer, version, description
   - Same cap configuration for EEG streams
   - Same timestamp synchronization mechanism

4. **source_id Format**: Consistent structure
   - Format: `{device_name}_{key_model}_{crypto_key_hex}`
   - Same format for both connection types

### Implications:

- Existing analysis pipelines will work without modification
- LSL recording tools (e.g., LabRecorder) will recognize streams identically
- MNE-Python export scripts will work with both connection types
- Stream viewers (e.g., bsl_stream_viewer) will display streams identically

## Running the Verification

To re-run the verification:

```bash
python scripts/verify_lsl_stream_compatibility.py
```

The script will output detailed comparison results and return exit code 0 if all tests pass, or 1 if any test fails.

## Code References

- **EmotivBase**: `emotiv_lsl/emotiv_base.py`
  - Connection abstraction layer
  - Common LSL metadata methods
  - Timestamp synchronization

- **EmotivEpocX**: `emotiv_lsl/emotiv_epoc_x.py`
  - EEG stream info: `get_lsl_outlet_eeg_stream_info()`
  - Motion stream info: `get_lsl_outlet_motion_stream_info()`
  - Quality stream info: `get_lsl_outlet_electrode_quality_stream_info()`
  - source_id generation: `get_lsl_source_id()`

- **Connection Implementations**:
  - BLE: `emotiv_lsl/ble_connection.py`
  - USB: `emotiv_lsl/usb_connection.py`

## Notes

- The verification uses a test serial number to ensure identical crypto keys for comparison
- In production, different devices will have different serial numbers and thus different source_id values
- The format structure of source_id remains consistent regardless of the actual values
- All stream metadata is generated by the same methods in EmotivEpocX, ensuring consistency
