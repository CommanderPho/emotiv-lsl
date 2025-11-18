---
inclusion: always
---

# Project Structure

## Core Application

- `main.py` - Entry point, initializes EmotivEpocX and starts main loop
- `config.py` - Global configuration (sampling rates: EEG 128Hz, Motion 16Hz)

## emotiv_lsl/ Package

Core library implementing the LSL server:

- `emotiv_base.py` - Abstract base class with common functionality
  - LSL stream setup and metadata
  - Data decoding interface
  - Electrode quality extraction
  - Main acquisition loop
- `emotiv_epoc_x.py` - Epoc X implementation
  - AES decryption using device serial
  - EEG data decoding (14 channels)
  - Motion data decoding (6 DOF IMU)
  - LSL stream info for EEG, motion, and quality
- `emotiv_epoc_plus.py` - Epoc+ implementation
- `emotiv_epoc_x_pyshark.py` - Alternative Wireshark-based capture
- `recorder_service.py` - Background recording service
- `service/` - Windows service implementation

## Examples

- `read_data.py` - Basic LSL stream reading
- `read_and_export_mne.py` - Export to MNE .fif format
- `pho_read_and_export_mne.py` - Extended recording with metadata
- `pho_analyze.ipynb` - Analysis notebook
- `40_epochs.ipynb` - Epoch extraction examples
- `common.py` - Shared utilities

## Scripts

- `build_exe.py` - Windows executable builder
- `build_macOS_app.py` - macOS app bundle builder
- `build_linux_exe.py` - Linux executable builder
- `lsl_reciever.py` - Test LSL stream reception
- `setup_hidapi.py` - HIDAPI installation helper
- `launch_*.ps1` - PowerShell launch scripts
- `unix/` - Unix-specific scripts

## Platform Support

- `hidapi-win/` - Windows HIDAPI binaries (x64/x86)
- `udev_rules/` - Linux USB device permissions
- `Dockerfile` + `docker-compose.yml` - Container deployment

## Configuration & Logs

- `logs_and_notes/` - Setup guides and troubleshooting logs
- `.python-version` - Python version specification
- `pyproject.toml` - Modern Python project config (uv)
- `requirements.txt` - Pip dependencies
- `environment.yml` - Conda environment spec
- `uv.lock` - Locked dependencies

## Architecture Patterns

### Class Hierarchy
- `EmotivBase` - Abstract base with shared LSL/decoding logic
- `EmotivEpocX` - Concrete implementation for Epoc X hardware
- Uses `attrs` for dataclass definitions with `@define(slots=False)`

### Data Flow
1. USB HID device → raw encrypted packets (32 bytes)
2. XOR with 0x55 → AES decryption
3. Packet validation → decode to EEG/motion/quality
4. Push to appropriate LSL outlet

### LSL Streams
- "Epoc X" - EEG data (14 channels, 128Hz, float32)
- "Epoc X Motion" - IMU data (6 channels, 16Hz, float32)
- "Epoc X eQuality" - Electrode quality (14 channels, 128Hz, float32)
- "Epoc X DebugRaw" - Raw packets (debug mode only)

## Code Style

- Type hints using `typing` module
- Logging via Python `logging` module
- NumPy for array operations
- attrs for class definitions
- LSL metadata in XML format via `pylsl.StreamInfo.desc()`
