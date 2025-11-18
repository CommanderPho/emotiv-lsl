---
inclusion: always
---

# Technology Stack

## Core Technologies

- **Python**: 3.8+ (3.8 recommended for compatibility)
- **Package Manager**: uv (modern), conda/micromamba (legacy support)
- **LSL**: pylsl for Lab Streaming Layer protocol
- **Crypto**: PyCryptodome for AES decryption of headset data
- **HID**: hidapi for USB device communication
- **Signal Processing**: MNE-Python, scipy, numpy

## Key Dependencies

- `pylsl>=1.16.2` - Lab Streaming Layer
- `pycryptodome>=3.23.0` - AES encryption for data packets
- `hid==1.0.4` - USB HID device access
- `mne[hdf5]>=1.6.1` - EEG data processing
- `attrs>=25.3.0` - Class definitions
- `pyqt5` - GUI components
- `bsl` - Stream viewer (custom fork)

## Platform-Specific Requirements

### Windows
- hidapi DLL from `hidapi-win/x64/` or `hidapi-win/x86/`
- DLL must be copied to Python environment's `Library/bin/` or added to PATH
- PyInstaller for executable builds

### macOS
- `brew install hidapi labstreaminglayer/tap/lsl`
- Use `hidapi` package (not `hid`)

### Linux
- `liblsl` and `liblsl-dev` packages
- `libhidapi-dev`, `libhidapi-hidraw0`, `libhidapi-libusb0`
- udev rules in `udev_rules/` for device permissions

## Common Commands

### Setup (uv - preferred)
```bash
uv sync --all-extras
source .venv/bin/activate  # Unix
.venv\Scripts\Activate.ps1  # Windows
```

### Setup (conda/micromamba - legacy)
```bash
micromamba create -n lsl_env python=3.8
micromamba activate lsl_env
micromamba install -c conda-forge liblsl
pip install -r requirements.txt
```

### Running
```bash
python main.py  # Start LSL server
```

### Visualization
```bash
bsl_stream_viewer  # View all streams
bsl_stream_viewer --stream_name 'Epoc X'  # View EEG only
```

### Building Executables
```bash
python scripts/build_exe.py  # Windows
python scripts/build_macOS_app.py  # macOS
python scripts/build_linux_exe.py  # Linux
```

### Docker
```bash
sudo docker-compose build
sudo docker-compose up
```

## Build System

- **PyInstaller**: Creates standalone executables
- **spec files**: `main.spec` defines build configuration
- **Docker**: Multi-stage builds for containerized deployment
