# Windows 10 VM Deployment Guide for emotiv-lsl

## Overview

The emotiv-lsl project runs on Windows 10 VMs with a multi-component architecture:
1. **LSL Server** (`main.py`) - Connects to Emotiv headset, creates LSL outlets for EEG and Motion streams
2. **BSL EEG Recorder** - Records EEG stream to disk (XDF format)
3. **BSL Motion Recorder** - Records Motion stream to disk (XDF format)

All components run concurrently in separate PowerShell windows, managed by `launch_emotiv_lsl.ps1`.

---

## Quick Start

### Prerequisites

- **Windows 10 VM** (VirtualBox, VMware, or Hyper-V)
- **Emotiv EPOC X headset + USB dongle**
- **Micromamba** installed (see [setup](#environment-setup) section)
- **Admin privileges** (launcher auto-escalates)
- **VMware shared folder** (or local path) for recording output

### Running the System

1. **Open PowerShell as Administrator**
   ```powershell
   # Right-click PowerShell → "Run as administrator"
   ```

2. **Navigate to repository**
   ```powershell
   cd C:\Users\pho\repos\EmotivEpoc\emotiv-lsl
   ```

3. **Execute the launcher**
   ```powershell
   .\scripts\launch_emotiv_lsl.ps1
   ```

4. **Observe component windows**
   - **LSL Server** window: Shows device initialization and LSL outlet logs
   - **BSL EEG Recorder** window: Shows XDF recording progress for EEG stream
   - **BSL Motion Recorder** window: Shows XDF recording progress for Motion stream

5. **Stop the system**
   - Close each PowerShell window individually, or press Ctrl+C in each window

---

## Environment Setup

### Initial Setup (One-time)

1. **Install Micromamba** (if not already installed)
   ```powershell
   # Download and run the installer from: https://mamba.readthedocs.io/en/latest/installation.html
   # Or use conda/anaconda if preferred
   ```

2. **Create Python 3.8 environment**
   ```powershell
   micromamba create -n lsl_env python=3.8
   ```

3. **Activate environment**
   ```powershell
   micromamba activate lsl_env
   ```

4. **Install conda-forge liblsl**
   ```powershell
   micromamba install -c conda-forge liblsl
   ```

5. **Install Python dependencies**
   ```powershell
   pip install -r requirements_for_mamba.txt
   ```

6. (No Python hid/hidapi step) Device I/O is handled via the Flutter `hid4flutter` plugin.

7. **Verify environment**
   ```powershell
   python main.py  # Should show device info and LSL outlets created
   # Press Ctrl+C to stop
   ```

---

## Script Details

### `launch_emotiv_lsl.ps1` (GUI with Recording)

**Location**: `scripts/launch_emotiv_lsl.ps1`

**Behavior**:
1. Checks admin privileges; auto-escalates if needed
2. Stops any running official Emotiv services (`Stop-Service Emotiv*`)
3. Activates `lsl_env` environment
4. **Starts LSL Server** in window titled "LSL Server"
   - Runs: `python main.py`
   - Waits 5 seconds for device initialization
5. **Starts BSL EEG Recorder** in window titled "BSL EEG Recorder"
   - Runs: `bsl_stream_recorder --stream_name 'Epoc X' -d '<vmware-shared-folder-path>'`
   - Records to: `\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings...`
6. **Starts BSL Motion Recorder** in window titled "BSL MotionRecorder"
   - Runs: `bsl_stream_recorder --stream_name 'Epoc X Motion' -d '<motion-recordings-path>'`
   - Records to: `...MOTION_RECORDINGS/`

**Recording Output**: XDF files (Lab Streaming Layer format) with samples + metadata

### `launch_emotiv_lsl_no_gui.ps1` (Headless Server Only)

**Location**: `scripts/launch_emotiv_lsl_no_gui.ps1`

**Behavior**:
1. Activates `lsl_env`
2. Runs `python main.py` in current terminal (does not spawn windows)
3. Blocks until Ctrl+C is pressed

**Use case**: Remote SSH sessions or continuous server deployments

---

## File Structure

```
emotiv-lsl/
├── main.py                          # LSL server entry point
├── emotiv_lsl/
│   ├── emotiv_base.py              # Base class for device drivers
│   └── emotiv_epoc_x.py            # EPOC X driver implementation
├── scripts/
│   ├── launch_emotiv_lsl.ps1       # Multi-component launcher with recorders
│   ├── launch_emotiv_lsl_no_gui.ps1# Headless server-only launcher
│   └── launch_lsl_viewer.ps1       # Optional: Start BSL viewer for real-time display
├── logs_and_notes/
│   ├── DEPLOYMENT.md               # This file
│   └── *.md                        # Setup logs and troubleshooting
└── requirements_for_mamba.txt       # Python dependencies
```

---

## Troubleshooting

### Issue: "micromamba is not recognized"

**Cause**: Micromamba not in system PATH or not installed

**Solution**:
1. Install micromamba from https://mamba.readthedocs.io/en/latest/installation.html
2. Restart PowerShell after installation
3. Verify: `micromamba --version`

### Issue: "lsl_env not found"

**Cause**: Environment not created yet

**Solution**:
```powershell
micromamba create -n lsl_env python=3.8
```

### Issue: "Unable to open device"

**Cause**: 
- Headset not powered on
- USB dongle not connected
- Wrong USB permissions

**Solution**:
1. Ensure headset is powered on
2. Ensure USB dongle is firmly connected
3. Check Device Manager for "Emotiv EPOC" device
4. Restart headset and re-run launcher

### Issue: "Stop-Service failed" in launcher

**Cause**: Script not running with admin privileges

**Solution**:
- The launcher auto-escalates. If it doesn't, manually run PowerShell as Administrator

### Issue: Recorder not writing to VMware shared folder

**Cause**: Path incorrect or shared folder not mounted

**Solution**:
1. Open File Explorer → Map shared folder from VMware
2. Verify path: `\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\`
3. Update recorder paths in `launch_emotiv_lsl.ps1` if needed

### Issue: LSL outlets not created (Device not found)

**Cause**: Device driver or connection issues

**Solution**:
1. Verify Emotiv EPOC dongle VID:PID is `1234:ed02` (Device Manager)
2. Ensure the Flutter app using `hid4flutter` is running and exposing the device interface if applicable
3. Power-cycle the dongle or try a different USB port

---

## Workflow: Recording Data

1. **Start launcher** → all components begin
2. **Device discovery**: LSL server finds Emotiv EPOC X dongle (should print device info)
3. **LSL outlets created**: EEG (14 channels @ 128 Hz) and Motion (9 channels @ 128 Hz)
4. **Recorders subscribe**: Both BSL recorders find and subscribe to named streams
5. **Data written to disk**: XDF files accumulate in shared folder
6. **Stop all**: Close each PowerShell window to stop recording

**Output files**:
- `*.xdf` files in `\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings...`
- `*.xdf` files in `...MOTION_RECORDINGS\`
- Can be loaded with MNE, LabRecorder, or custom XDF readers

---

## Platform Differences

### Windows 10 VM (This Guide)
- Uses PowerShell for orchestration
- Requires micromamba/conda environment
- Uses hidapi-win DLL
- Records to VMware shared folder

### macOS
- Uses `brew install hidapi`
- `uv` or `micromamba` for environment
- Requires DYLD_LIBRARY_PATH for LSL

### Linux
- Uses apt: `libhidapi-dev`, `libhidapi-hidraw0`
- `sudo chmod 0666 /dev/hidraw*` for permissions
- mamba/conda environment
- Records to local filesystem

See `logs_and_notes/` for platform-specific setup notes.

---

## References

- **LSL (Lab Streaming Layer)**: https://labstreaminglayer.readthedocs.io/
- **BSL (Brain Streaming Layer)**: https://github.com/CommanderPho/bsl
- **Emotiv EPOC X**: https://www.emotiv.com/
- **XDF Format**: https://github.com/sccn/xdf/wiki/Specification

---

## Support

For issues or questions:
1. Check `logs_and_notes/` for similar problems
2. Review LSL server console output for error messages
3. Check Device Manager for Emotiv dongle presence
4. Verify all dependencies: `pip list | grep -E "pylsl|hid|mne|bsl"`
