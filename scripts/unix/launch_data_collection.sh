#!/usr/bin/env bash
# ------------------------------------------------------------
# Direct launcher for Emotiv LSL – *Unix / Bash* version
# ------------------------------------------------------------


# sudo chmod 0666 /dev/hidraw*
# python main.py

set -euo pipefail

# ----------  ANSI colours ----------
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

## Switch between micromamba/mamba/conda based on what is installed:
if command -v conda &> /dev/null; then
    PKG_MANAGER="conda"
elif command -v mamba &> /dev/null; then
    PKG_MANAGER="mamba"
elif command -v micromamba &> /dev/null; then
    PKG_MANAGER="micromamba"
else
    echo "Error: None of mamba, micromamba, or conda found." >&2
    exit 1
fi


# EEG_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG'
# MOTION_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG/MOTION_RECORDINGS'

echo -e "${GREEN}Launching Emotiv LSL components...${RESET}"

echo -e "${YELLOW}Setting USB access permissions for '/dev/hidraw*' to 0666...${RESET}"
sudo chmod 0666 /dev/hidraw*

# # ----------  Stop official Emotiv services ----------
# echo -e "${YELLOW}Stopping official Emotiv services...${RESET}"

# # Re-run via sudo if we are not root (needed to stop system services)
# if [[ $EUID -ne 0 ]]; then
#   echo -e "${YELLOW}Elevating privileges with sudo...${RESET}"
#   exec sudo --preserve-env=PATH "$0" "$@"
# fi

# # If the vendor provides systemd units (adapt name pattern if necessary)
# if command -v systemctl &>/dev/null; then
#   mapfile -t EMOTIV_SERVICES < <(systemctl list-units --type=service --all | awk '/[Ee]motiv/ {print $1}')
#   for svc in "${EMOTIV_SERVICES[@]}"; do
#     echo -e "${CYAN}Stopping $svc ...${RESET}"
#     systemctl stop "$svc" || true
#   done
# fi

# # Fallback: kill running executables that start with “Emotiv”
# pkill -f -i "Emotiv" 2>/dev/null || true

# ----------  Determine repository root ----------
SCRIPT_PATH=$(realpath "${BASH_SOURCE[0]}")
REPO_ROOT=$(dirname "$(dirname "$SCRIPT_PATH")")   # two levels up
echo "SCRIPT_PATH: $SCRIPT_PATH"
echo "REPO_ROOT: $REPO_ROOT"
# cd "$REPO_ROOT"

# ----------  Launch the LSL server ----------
echo -e "${CYAN}Starting LSL Server...${RESET}"
# cd '$REPO_ROOT'
$PKG_MANAGER activate lsl_env
python main.py

echo -e "${GREEN}All components launched successfully!${RESET}"
