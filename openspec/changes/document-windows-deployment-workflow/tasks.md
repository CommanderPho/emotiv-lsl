## 1. Specification & Documentation

- [ ] 1.1 Write `openspec/specs/deployment/spec.md` with requirements for Windows 10 VM launcher and component lifecycle
- [ ] 1.2 Document the PowerShell launcher function pattern and responsibilities
- [ ] 1.3 Add LSL server startup and initialization requirements
- [ ] 1.4 Add BSL recorder/viewer component coordination and output requirements
- [ ] 1.5 Add admin privilege and service management requirements
- [ ] 1.6 Add failure handling and retry logic scenarios

## 2. Integration & Validation

- [ ] 2.1 Update `README.md` with Windows 10 VM quick-start section referencing the launcher scripts
- [ ] 2.2 Create `logs_and_notes/DEPLOYMENT.md` with step-by-step Windows deployment guide (remove Python `hid`/`hidapi`; note Flutter `hid4flutter` handles device I/O)
- [ ] 2.3 Validate spec format with `openspec validate document-windows-deployment-workflow --strict`
- [ ] 2.4 Manual test: run `launch_emotiv_lsl.ps1` on Windows 10 VM and verify all components start successfully
- [ ] 2.5 Verify LSL server and recorders output valid streams (validate with `bsl_stream_viewer` or logs)

## 3. Acceptance

- [ ] 3.1 Confirm spec has at least one scenario per requirement
- [ ] 3.2 Confirm documentation is clear for new contributor onboarding
- [ ] 3.3 Ready for review and approval
