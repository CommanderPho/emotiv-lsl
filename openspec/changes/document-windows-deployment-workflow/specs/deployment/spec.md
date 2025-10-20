## ADDED Requirements

### Requirement: PowerShell Launcher Entry Point
The system SHALL provide a PowerShell launcher script (`launch_emotiv_lsl.ps1`) that serves as the single entry point for multi-component deployment on Windows 10 VM. The launcher MUST orchestrate LSL server startup, component coordination, and optional data recording to configured output directories.

#### Scenario: Successful multi-component launch
- **WHEN** user executes `launch_emotiv_lsl.ps1` with administrator privileges
- **THEN** the script SHALL:
  - Stop any running official Emotiv services to avoid conflicts
  - Activate the `lsl_env` micromamba environment
  - Start LSL server in a new PowerShell window
  - Wait 5 seconds for server initialization
  - Start BSL recorders for EEG and Motion streams in separate windows
  - Display success message and return control

#### Scenario: Permission escalation
- **WHEN** user executes `launch_emotiv_lsl.ps1` without administrator privileges
- **THEN** the script SHALL automatically request admin elevation via `Start-Process -Verb RunAs` and re-execute itself

#### Scenario: Missing environment error
- **WHEN** the `lsl_env` micromamba environment does not exist
- **THEN** the script SHALL fail with a clear error message directing user to create the environment first

### Requirement: LSL Server Component
The system SHALL start the LSL server (`main.py`) in a dedicated PowerShell window with proper environment activation. The server MUST initialize the Emotiv device, create LSL outlets for EEG and Motion streams, and run the main event loop.

#### Scenario: Server startup success
- **WHEN** LSL server launches after 5-second delay
- **THEN** the server SHALL:
  - Activate `lsl_env` environment
  - Execute `python main.py` in the repository root directory
  - Output initialization logs (device detection, crypto key, LSL outlets created)
  - Block indefinitely serving LSL clients

#### Scenario: Server detects and connects to device
- **WHEN** LSL server runs with Emotiv device USB dongle present and headset powered on
- **THEN** the server SHALL successfully establish device connection via the `hid4flutter`-backed interface and begin streaming EEG and Motion data

### Requirement: BSL Recorder Components
The system SHALL start BSL (Brain Streaming Layer) recorder processes to capture LSL streams to disk. Recorders MUST run in separate windows, target specific streams (EEG, Motion), and write to configured output directories.

#### Scenario: EEG recorder startup
- **WHEN** EEG recorder component starts
- **THEN** the recorder SHALL:
  - Activate `lsl_env` environment
  - Execute `bsl_stream_recorder --stream_name 'Epoc X'` with `-d <vmware-shared-folder-path>`
  - Output XDF files to the specified EEG Recordings directory on the shared folder

#### Scenario: Motion recorder startup
- **WHEN** Motion recorder component starts
- **THEN** the recorder SHALL:
  - Activate `lsl_env` environment
  - Execute `bsl_stream_recorder --stream_name 'Epoc X Motion'` with `-d <motion-recordings-path>`
  - Output XDF files to the Motion Recordings subdirectory

#### Scenario: Recorder connection to LSL stream
- **WHEN** recorder component launches and LSL server is already streaming
- **THEN** the recorder SHALL successfully subscribe to the named stream and begin writing samples to disk

### Requirement: Headless Launcher Variant
The system SHALL provide an alternative launcher script (`launch_emotiv_lsl_no_gui.ps1`) for headless deployments. This variant MUST activate the environment and start only the LSL server without launching separate windows.

#### Scenario: Headless server startup
- **WHEN** user executes `launch_emotiv_lsl_no_gui.ps1`
- **THEN** the script SHALL:
  - Activate `lsl_env` environment
  - Start LSL server (`python main.py`) in the current terminal session
  - Block until process terminates or user interrupts

### Requirement: Environment Isolation & Reproducibility
The system SHALL use micromamba environment management to ensure consistent Python version (3.8) and dependencies across different Windows VM instances. Launcher scripts MUST verify environment exists before use and provide guidance on creation if missing.

#### Scenario: Reproducible deployment across VMs
- **WHEN** launcher script executes on any Windows 10 VM with micromamba installed
- **THEN** the script SHALL:
- Use consistent `lsl_env` environment with pinned Python 3.8 and all dependencies (pylsl, pycryptodome, bsl). Device I/O is provided by the Flutter `hid4flutter` plugin (no Python `hid`/`hidapi` dependency).
  - Run identically on different physical or virtual Windows machines
  - Produce same initialization logs and stream outputs

### Requirement: Service Conflict Resolution
The system SHALL manage conflicts between the emotiv-lsl application and official Emotiv client services running on the host. Launcher scripts MUST stop conflicting services before starting the custom LSL server.

#### Scenario: Official Emotiv services present
- **WHEN** launcher detects running Emotiv services (e.g., `Emotiv*` processes or Windows services)
- **THEN** the launcher SHALL:
  - Execute `Stop-Service -Name "Emotiv*" -Verbose` (requires admin)
  - Log the stop action
  - Proceed with LSL component startup

### Requirement: Multi-Window Component Layout
The system SHALL use PowerShell `Start-Process` with custom window titles to organize multiple concurrent processes. Each window MUST display a descriptive title identifying its component role and allow independent monitoring or termination.

#### Scenario: Component window creation
- **WHEN** launcher creates new windows for server, EEG recorder, and Motion recorder
- **THEN** each window SHALL:
  - Display a unique, descriptive title (e.g., "LSL Server", "BSL EEG Recorder", "BSL MotionRecorder")
  - Remain open with `-NoExit` flag to preserve logs and allow inspection
  - Execute its component command in a fresh PowerShell context with environment activated

### Requirement: VMware Shared Folder Integration
The system SHALL support recording to VMware shared folders accessible from Windows guest VMs. Launcher scripts MUST reference shared folder paths using UNC notation (\\vmware-host\Shared Folders\...).

#### Scenario: Recording to shared folder
- **WHEN** launcher records data to `\\vmware-host\Shared Folders\Emotiv Epoc EEG Project\EEG Recordings...`
- **THEN** recorder SHALL:
  - Successfully write XDF files to the network path
  - Persist recordings accessible from the host machine
  - Handle path variations (both UNC \\ and forward slash // styles)

### Requirement: Startup Sequencing & Delays
The system SHALL enforce deterministic startup ordering with appropriate delays to ensure component readiness. LSL server MUST initialize before recorders attempt to subscribe to streams.

#### Scenario: Ordered component startup with delay
- **WHEN** launcher starts components in sequence
- **THEN** the launcher SHALL:
  - Start LSL server first
  - Wait 5 seconds for device initialization and LSL outlet creation
  - Start BSL recorders after delay completes
  - Recorders SHALL successfully subscribe to active LSL streams on first attempt
