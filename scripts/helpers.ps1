#!/usr/bin/env powershell

# Returns a command string that activates the project's Python environment.
# Preference order (Windows):
# 1) Local venv at ./.venv (PowerShell activation script)
# 2) micromamba environment named 'lsl_env'
function Get-PythonEnvActivationCommand {
	param (
		[string]$RepoRoot
	)

	if (-not $RepoRoot -or -not (Test-Path $RepoRoot)) {
		$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
	}

	$venvActivate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"
	if (Test-Path $venvActivate) {
		# Use call operator to execute the activation script
		return "& `"$venvActivate`""
	}

	# Fallback to micromamba if available
	$mamba = Get-Command micromamba -ErrorAction SilentlyContinue
	if ($mamba) {
		return "micromamba activate lsl_env"
	}

	return $null
}


