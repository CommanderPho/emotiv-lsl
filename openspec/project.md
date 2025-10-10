# Project Context

## Purpose
Provide a reliable Lab Streaming Layer (LSL) server for Emotiv EPOC-series headsets (EPOC X and EPOC+) to acquire, decrypt, decode, and stream EEG and motion data in real time for visualization, recording, and analysis.

## Tech Stack
- **Language**: Python (3.8+; pinned to 3.8 for widest device/lib compatibility)
- **Streaming**: LSL via `pylsl`
- **BLE/USB**: BLE via `bleak`; USB via `hidapi` (system DLLs on Windows/macOS/Linux)
- **Crypto**: AES (ECB) via `pycryptodome`
- **Data/Science**: `numpy`, `scipy`, `mne`, `mne-qt-browser`, `pyqtgraph`, `matplotlib`, `seaborn`, `plotly`
- **Structuring**: `attrs` for data classes and config
- **UI/Viewer**: `bsl` (`bsl_stream_viewer`) for real-time visualization
- **Packaging**: `pyinstaller` (optional app bundling)
- **CLI/Env**: Conda/Micromamba, Docker (Linux USB), `requirements*.txt`, `pyproject.toml`

## Project Conventions

### Code Style
- PEP8, type hints for public APIs, explicit return types where helpful
- Classes/use-cases in CamelCase; functions, methods, and variables in snake_case
- Prefer `attrs` for simple data containers; avoid deep inheritance trees
- Logging via `logging` with module/component-specific loggers; INFO by default, DEBUG for reverse engineering
- Avoid catch-all exceptions; validate inputs explicitly; prefer early returns

### Architecture Patterns
- **Device abstraction**: `EmotivBase` defines the contract (get crypto key, decode, validate, stream builders). Model-specific subclasses implement details:
  - `EmotivEpocX` (KeyModel 8)
  - `EmotivEpocPlus` (KeyModel 6)
- **Hardware backend strategy**: `HardwareConnectionBackend` selects USB vs BLE. BLE uses `BleHidLikeDevice`; USB uses system `hidapi` where supported.
- **Streaming pipeline**: main loop reads packets → validates → decodes → pushes to LSL outlets:
  - EEG stream: name `Epoc X` or `Epoc+`, type `EEG`, 14 channels, `float32`, nominal srate 128 Hz
  - Motion stream (if present): name `Epoc X Motion`, 6 channels (AccX/Y/Z, GyroX/Y/Z), nominal srate 16 Hz
  - Optional raw/debug stream when reverse-engineering: name `Epoc X DebugRaw`
- **LSL metadata**: channel labels follow 10–20 scheme; includes cap metadata; consistent `source_id` built from device + key/serial
- **Config constants**: `SRATE = 128`, `MOTION_SRATE = 16` in `config.py`

### Testing Strategy
- Manual integration testing with physical headsets
- Run server: `python main.py` (USB/EPOC+) or `python main_BLE.py` (BLE/EPOC X/EPOC+)
- Verify streams with `bsl_stream_viewer` (e.g., `--stream_name 'Epoc X'` and `--stream_name 'Epoc X Motion'`)
- Optional recording with LabRecorder; analysis via MNE notebooks in `examples/` and `examples_jupyter/`
- Platform checks on Windows/macOS/Linux; validate HID/BLE setup and runtime logs

### Git Workflow
- Default: feature branches merged via PR into `main` (e.g., `feature/BLE_support`)
- Suggested prefixes: `feature/`, `fix/`, `chore/`, `docs/`, `refactor/`
- Prefer Conventional Commits style messages (e.g., `feat: add BLE discovery for EPOC X`)
- Keep edits cohesive; one logical change per commit; rebase before merge when feasible

## Domain Context
- Emotiv EPOC-series headsets transmit encrypted 32-byte packets. Decryption uses AES-128 (ECB) with model-specific key derivation from serial/advertised BLE name (CyKit-compatible formulas).
- EEG: 14 channels with 10–20 labels; additional per-channel contact quality (optional `eQuality` stream).
- Motion: EPOC X includes 6-DOF IMU data decoded to Acc/Gyro units.
- Streams are published to LSL for downstream tools (viewer, recorder, Python clients).
- Naming conventions matter for downstream consumers (e.g., `bsl_stream_viewer` expects generic types like `EEG`/`SIGNAL`).

## Important Constraints
- Python 3.8 baseline; some dependencies and HID/BLE stacks assume 3.8.x
- Real-time constraints: decoding must keep up with 128 Hz EEG, 16 Hz motion
- Platform specifics:
  - Windows: requires `hidapi.dll` present in env when using USB; BLE requires OS Bluetooth stack
  - macOS: `hidapi` via Homebrew; BLE uses CoreBluetooth via `bleak`
  - Linux: USB access requires udev rules; Docker needs `--privileged` and USB device mapping
- AES keys and serial handling must be correct per model; incorrect keys yield invalid packets
- Avoid breaking LSL stream names/types to keep compatibility with existing viewers/recorders

## External Dependencies
- Emotiv EPOC hardware (EPOC X, EPOC+)
- Lab Streaming Layer runtime and clients (`pylsl`, `bsl_stream_viewer`, LabRecorder)
- System Bluetooth stack (for BLE) and HIDAPI (for USB)
- Optional Docker for Linux deployments with USB passthrough
- MNE and plotting stacks for analysis/visualization workflows
