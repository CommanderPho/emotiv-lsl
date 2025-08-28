#!/usr/bin/env bash
# ------------------------------------------------------------
# Direct launcher for Emotiv LSL – *Unix / Bash* version
# ------------------------------------------------------------

set -euo pipefail

# ----------  ANSI colours ----------
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

## Switch between micromamba/mamba/conda based on what is installed:
if command -v conda &> /dev/null; then
    PKG_MANAGER="conda"
    eval "$(conda shell.bash hook)"
elif command -v mamba &> /dev/null; then
    PKG_MANAGER="mamba"
    eval "$(mamba shell hook --shell=bash)"
elif command -v micromamba &> /dev/null; then
    PKG_MANAGER="micromamba"
    eval "$(micromamba shell hook --shell=bash)"
else
    echo "Error: None of mamba, micromamba, or conda found." >&2
    exit 1
fi

# # Diba Lab Workstation:
# EEG_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG'
# MOTION_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG/MOTION_RECORDINGS'

# rMBP 2025-08-27:
EEG_RECORDING_ARG="/Users/pho/Dropbox (Personal)/Databases/UnparsedData/EmotivEpocX_EEGRecordings" # rMBP
MOTION_RECORDING_ARG="/Users/pho/Dropbox (Personal)/Databases/UnparsedData/EmotivEpocX_EEGRecordings/MOTION_RECORDINGS" # rMBP


echo -e "${GREEN}Launching Emotiv LSL components...${RESET}"

# ----------  Determine repository root (portable, no realpath) ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ----------  Helper: open a new terminal window ----------
# Tries common terminal emulators; falls back to background process.
start_command_window() {
  local title=$1
  local cmd=$2

  # macOS (Darwin) – use Terminal.app via AppleScript
  if [[ "$(uname)" == "Darwin" ]]; then
      osascript -e "tell application \"Terminal\" to do script \"bash -lc 'echo -e \\\"${CYAN}Starting ${title}...${RESET}\\\"; ${cmd//$'\n'/ }'\""
      return 0
  fi


  if command -v gnome-terminal &>/dev/null; then
    gnome-terminal --title="$title" -- bash -c "echo -e '${CYAN}Starting $title...${RESET}'; $cmd; exec bash"
  elif command -v konsole &>/dev/null; then
    konsole --new-tab --hold -p tabtitle="$title" -e bash -c "echo -e '${CYAN}Starting $title...${RESET}'; $cmd"
  elif command -v xterm &>/dev/null; then
    xterm -T "$title" -e bash -c "echo -e '${CYAN}Starting $title...${RESET}'; $cmd; exec bash"
  else
    echo -e "${YELLOW}No GUI terminal found – running $title in background...${RESET}"
    bash -c "$cmd" &
  fi
}


# ----------  Build optional recording args (pass only if directory exists) ----------

if [[ -n "${EEG_RECORDING_PATH:-}" ]]; then
  if [[ -d "$EEG_RECORDING_PATH" ]]; then
    EEG_RECORDING_ARG="--record_dir '$EEG_RECORDING_PATH'"
  else
    echo -e "${YELLOW}EEG_RECORDING_PATH does not exist, skipping --record_dir for EEG: '$EEG_RECORDING_PATH'${RESET}"
  fi
fi

if [[ -n "${MOTION_RECORDING_PATH:-}" ]]; then
  if [[ -d "$MOTION_RECORDING_PATH" ]]; then
    MOTION_RECORDING_ARG="--record_dir '$MOTION_RECORDING_PATH'"
  else
    echo -e "${YELLOW}MOTION_RECORDING_PATH does not exist, skipping --record_dir for Motion: '$MOTION_RECORDING_PATH'${RESET}"
  fi
fi

# ----------  Launch the Viewers ----------
echo -e "${CYAN}Starting BSL viewers...${RESET}"

start_command_window "BSL EEG Viewer" "
  cd '$REPO_ROOT'
  $PKG_MANAGER activate lsl_env
  bsl_stream_viewer \
     --stream_name 'Epoc X' \
     ${EEG_RECORDING_ARG} \
     --bp_low 1.0 --bp_high 58.0
"

start_command_window "BSL Motion Viewer" "
  cd '$REPO_ROOT'
  $PKG_MANAGER activate lsl_env
  bsl_stream_viewer \
     --stream_name 'Epoc X Motion' \
     ${MOTION_RECORDING_ARG} \
     --bp_off
"

echo -e "${GREEN}All components launched successfully!${RESET}"
