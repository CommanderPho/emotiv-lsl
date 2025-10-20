## Why

The emotiv-lsl project runs on multiple platforms (Windows, macOS, Linux), but Windows 10 VM is the primary reproducible environment for development and testing. The launcher scripts (`launch_emotiv_lsl.ps1`, `launch_emotiv_lsl_no_gui.ps1`) orchestrate the startup of multiple components (LSL server, BSL recorders, viewers), but this workflow is not formally documented as part of the project specification. New contributors and users lack clear guidance on the deployment process, service management, and component lifecycle.

## What Changes

- **ADD** a formal spec for Windows 10 VM deployment process covering environment activation, service management, multi-component orchestration, and reproducibility requirements.
- **ADD** documentation of the PowerShell launcher scripts and their responsibilities.
- **ADD** specifications for LSL server startup, BSL component coordination, and output recording.
- **ADD** failure handling and validation requirements for the deployment workflow.
- **UPDATE** device connection approach: use Flutter `hid4flutter` for device I/O instead of Python `hid`/`hidapi`; remove Python HID dependency from environment docs.

This ensures:
- New contributors understand the standard deployment pattern.
- The workflow is reproducible and testable.
- Component dependencies and lifecycle are explicit.

## Impact

- **Affected specs**: New capability `deployment` (deployment orchestration on Windows 10 VM)
- **Affected code**: 
  - `scripts/launch_emotiv_lsl.ps1` (multi-component launcher with recorders)
  - `scripts/launch_emotiv_lsl_no_gui.ps1` (headless launcher)
  - `main.py` (LSL server entry point)
  - `emotiv_lsl/emotiv_epoc_x.py` (device/stream initialization)
- **Documentation**: `logs_and_notes/` (setup logs), `README.md`, `openspec/specs/deployment/spec.md`
- **Dependencies**: Remove Python `hid`/`hidapi` setup from Windows steps; device I/O handled via Flutter `hid4flutter` integration.
