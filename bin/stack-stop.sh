#!/usr/bin/env bash
# Stop the VTN stack: VTN-RI + callback service.
# Mosquitto is left running (managed by brew/systemctl separately).

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/vtn-stop.sh"

if tmux kill-session -t "vtn-callbk-svc" 2>/dev/null; then
    echo "vtn-callbk-svc stopped."
else
    echo "vtn-callbk-svc is not running."
fi

echo "Stack stopped. (Mosquitto left running)"
