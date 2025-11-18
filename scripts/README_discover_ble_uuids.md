# BLE UUID Discovery Utility

## Overview

The `discover_ble_uuids.py` script is a utility for discovering and documenting the Bluetooth Low Energy (BLE) GATT services and characteristics used by Emotiv EPOC X headsets.

## Purpose

Before implementing BLE connectivity, we need to know the specific UUIDs that the Emotiv headset uses for:
- EEG data streaming
- Motion sensor data
- Device control
- Battery status
- Other headset features

This script automates the discovery process and saves the results to a JSON configuration file.

## Prerequisites

Install the `bleak` library:
```bash
pip install bleak>=0.21.0
```

Or if using uv:
```bash
uv pip install bleak>=0.21.0
```

## Usage

### Basic Usage (Auto-discover)
```bash
python scripts/discover_ble_uuids.py
```
This will scan for Emotiv devices and connect to the first one found.

### Specify Device Address
```bash
python scripts/discover_ble_uuids.py --address AA:BB:CC:DD:EE:FF
```
Connect to a specific device by MAC address.

### Extended Discovery Timeout
```bash
python scripts/discover_ble_uuids.py --timeout 60
```
Increase the discovery timeout to 60 seconds (useful in noisy BLE environments).

### Debug Mode
```bash
python scripts/discover_ble_uuids.py --debug
```
Enable detailed debug logging.

## Output

The script generates `emotiv_lsl/ble_uuids.json` containing:
- Device information (name, MAC address)
- All GATT services with their UUIDs
- All characteristics with their UUIDs and properties (read, write, notify, indicate)
- Sample values for readable characteristics
- Descriptor information

Example output structure:
```json
{
  "device_address": "AA:BB:CC:DD:EE:FF",
  "device_name": "EPOC X-1234",
  "services": [
    {
      "uuid": "service-uuid-here",
      "description": "Service Name",
      "characteristics": [
        {
          "uuid": "characteristic-uuid-here",
          "description": "Characteristic Name",
          "properties": ["notify", "read"],
          "sample_value": "hex-encoded-value"
        }
      ]
    }
  ]
}
```

## Next Steps

After running the discovery:

1. Review the generated `ble_uuids.json` file
2. Identify which characteristics correspond to:
   - EEG data (likely has "notify" property, high-frequency data)
   - Motion data (likely has "notify" property, lower-frequency data)
   - Device control/configuration
3. Update `emotiv_lsl/ble_connection.py` with the discovered UUIDs:
   ```python
   EMOTIV_SERVICE_UUID = "discovered-service-uuid"
   EEG_CHARACTERISTIC_UUID = "discovered-eeg-uuid"
   MOTION_CHARACTERISTIC_UUID = "discovered-motion-uuid"
   ```

## Troubleshooting

### No devices found
- Ensure the headset is powered on
- Verify Bluetooth is enabled on your computer
- Make sure the headset is not connected to another device
- Try increasing the timeout with `--timeout 60`

### Connection timeout
- Move closer to the headset
- Ensure no other devices are trying to connect
- Check that your Bluetooth adapter supports BLE

### Permission errors (Linux)
- Add your user to the `bluetooth` group: `sudo usermod -a -G bluetooth $USER`
- Ensure BlueZ 5.43+ is installed: `bluetoothctl --version`

### Platform-specific notes
- **Windows**: Should work out of the box with Windows 10+
- **macOS**: May require Bluetooth permissions in System Preferences
- **Linux**: Requires BlueZ and proper permissions
