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
if command -v mamba &> /dev/null; then
    PKG_MANAGER="mamba"
elif command -v micromamba &> /dev/null; then
    PKG_MANAGER="micromamba"
elif command -v conda &> /dev/null; then
    PKG_MANAGER="conda"
else
    echo "Error: None of mamba, micromamba, or conda found." >&2
    exit 1
fi


EEG_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG'
MOTION_RECORDING_PATH='/media/halechr/MAX/cloud/University of Michigan Dropbox/Pho Hale/Personal/LabRecordedEEG/MOTION_RECORDINGS'

echo -e "${GREEN}Launching Emotiv LSL components...${RESET}"

# ----------  Determine repository root ----------
SCRIPT_PATH=$(realpath "${BASH_SOURCE[0]}")
REPO_ROOT=$(dirname "$(dirname "$SCRIPT_PATH")")   # two levels up
cd "$REPO_ROOT"

# ----------  Helper: open a new terminal window ----------
# Tries common terminal emulators; falls back to background process.
start_command_window() {
  local title=$1
  local cmd=$2

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


# ----------  Launch the Viewers ----------
echo -e "${CYAN}Starting BSL viewers...${RESET}"
# NOTE: Update the --record_dir paths to valid Unix paths.
start_command_window "BSL EEG Viewer" "
  cd '$REPO_ROOT'
  $PKG_MANAGER activate lsl_env
  bsl_stream_viewer  \
     --stream_name 'Epoc X' \
     --record_dir '$EEG_RECORDING_PATH' \ 
     --bp_low 1.0 --bp_high 58.0
"

start_command_window "BSL Motion Viewer" "
  cd '$REPO_ROOT'
  $PKG_MANAGER activate lsl_env
  bsl_stream_viewer  \
     --stream_name 'Epoc X Motion' \
     --record_dir '$MOTION_RECORDING_PATH' \ 
     --bp_off
"

echo -e "${GREEN}All components launched successfully!${RESET}"
